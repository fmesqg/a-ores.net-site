"""DGAL: contas, dívida e prazo de pagamento das 19 câmaras dos Açores.

Usage:
  python3 bot/dgal.py [data_dir] [--cache DIR]

The Direção-Geral das Autarquias Locais publishes on the Portal Autárquico
what the 308 municipalities report to it (SISAL). Read here, for the 19
Azorean câmaras:

  contas   Contas de gerência, from the SNC-AP accounts (2020 on): receita
           cobrada líquida and despesa paga líquida by economic code, the
           balance sheet and the income statement. One Excel file per map
           and year, one row per município, one column per code.
           -> data_dir/dgal_contas.csv.gz
  dívida   Dívida total against the legal limit (art. 52.º of Lei 73/2013:
           1.5 times the mean net current revenue of the three previous
           years), 2014 on, one PDF a year. -> data_dir/dgal_divida.csv
  PMP      Prazo médio de pagamentos (days), every quarter from 2020, from
           the yearly PDF of all municipalities (the quarterly ones list
           only those above 60 days). -> data_dir/dgal_pmp.csv

The links are read from the three portal pages each run (file ids change
when the DGAL updates a file). The file URLs all say filetype=pdf; the
server sends the real type (xlsx, ods, pdf) in Content-Disposition. Each
account map comes as an xlsx and an ods copy ("ou em código aberto"); the
xlsx is used. Accounts before 2020 follow POCAL (another classifier, other
maps) and are not read.

main() fails (the weekly workflow emails) when a page or file cannot be read
or parsed, an Azorean câmara is missing, or the newest accounts are more
than two years old.
"""

import csv
import datetime as dt
import gzip
import hashlib
import html
import io
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

SITE = "https://portalautarquico.dgal.gov.pt"
CONTAS = SITE + "/pt-PT/financas-locais/dados-financeiros/contas-de-gerencia"
DIVIDA = SITE + "/pt-PT/financas-locais/endividamento/municipios/evolucao"
PMP = (
    SITE + "/pt-PT/financas-locais/endividamento/municipios/"
    "prazo-medio-de-pagamentos"
)
UA = "acores.net open data (github.com/fmesqg/a-ores.net-site)"
PRIMEIRO_SNC = 2020  # first year of SNC-AP accounts
MAX_ATRASO = 2  # years: the accounts of year N come out in October N+1

# DGAL name -> (INE concelho code, name as in data/ine.csv)
MUNICIPIOS = {
    "VILA DO PORTO": ("2004101", "Vila do Porto"),
    "LAGOA (SÃO MIGUEL)": ("2004201", "Lagoa (R.A.A.)"),
    "NORDESTE": ("2004202", "Nordeste"),
    "PONTA DELGADA": ("2004203", "Ponta Delgada"),
    "POVOAÇÃO": ("2004204", "Povoação"),
    "RIBEIRA GRANDE": ("2004205", "Ribeira Grande"),
    "VILA FRANCA DO CAMPO": ("2004206", "Vila Franca do Campo"),
    "ANGRA DO HEROÍSMO": ("2004301", "Angra do Heroísmo"),
    "PRAIA DA VITÓRIA": ("2004302", "Vila da Praia da Vitória"),
    "SANTA CRUZ DA GRACIOSA": ("2004401", "Santa Cruz da Graciosa"),
    "CALHETA (SÃO JORGE)": ("2004501", "Calheta (R.A.A.)"),
    "VELAS": ("2004502", "Velas"),
    "LAJES DO PICO": ("2004601", "Lajes do Pico"),
    "MADALENA": ("2004602", "Madalena"),
    "SÃO ROQUE DO PICO": ("2004603", "São Roque do Pico"),
    "HORTA": ("2004701", "Horta"),
    "LAJES DAS FLORES": ("2004801", "Lajes das Flores"),
    "SANTA CRUZ DAS FLORES": ("2004802", "Santa Cruz das Flores"),
    "CORVO": ("2004901", "Corvo"),
}
# other spellings seen in the files
ALIAS = {
    "LAGOA (ACORES)": "LAGOA (SÃO MIGUEL)",
    "LAGOA (R.A.A.)": "LAGOA (SÃO MIGUEL)",
    "CALHETA (ACORES)": "CALHETA (SÃO JORGE)",
    "CALHETA (R.A.A.)": "CALHETA (SÃO JORGE)",
    "VILA DA PRAIA DA VITORIA": "PRAIA DA VITÓRIA",
}

# account maps: key, link text pattern
MAPAS = {
    "balanco": r"^balan[çc]o",
    "resultados": r"^demonstra[çc][ãa]o (dos|de) resultados",
    "despesa": r"despesas? pagas? l[íi]quidas?",
    "receita": r"receitas? cobradas? l[íi]quidas?",
}

COLS_CONTAS = [
    "ano",
    "geocod",
    "municipio",
    "mapa",
    "codigo",
    "descricao",
    "tipo",
    "valor",
]
COLS_DIVIDA = [
    "ano",
    "geocod",
    "municipio",
    "limite",
    "divida_total",
    "nao_orcamental",
    "fam",
    "divida",
    "pct_limite",
    "nota",
]
COLS_PMP = ["data", "geocod", "municipio", "dias", "ficheiro"]


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).upper()


FOLDED = {fold(k): k for k in MUNICIPIOS} | {
    fold(k): v for k, v in ALIAS.items()
}


def azorean(name: str) -> str:
    """The MUNICIPIOS key of a DGAL município name, or ""."""
    return FOLDED.get(fold(" ".join(str(name or "").split())), "")


# --- fetching -------------------------------------------------------------

_last = 0.0


def get(url: str, cache: Path | None = None) -> tuple[bytes, str]:
    """Body and file name (from Content-Disposition, "" for pages)."""
    global _last
    key = hashlib.sha1(url.encode()).hexdigest()[:16]
    if cache:
        hit = list(cache.glob(key + ".*"))
        if hit:
            return hit[0].read_bytes(), hit[0].name.split(".", 1)[1]
    wait = 1.0 - (time.monotonic() - _last)
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        body = r.read()
        disp = r.headers.get("Content-Disposition", "")
    _last = time.monotonic()
    m = re.search(r"filename\*=UTF-8''([^;]+)", disp) or re.search(
        r'filename="?([^";]+)"?', disp
    )
    name = urllib.parse.unquote(m.group(1)).strip() if m else ""
    if cache:
        cache.mkdir(parents=True, exist_ok=True)
        (cache / f"{key}.{name or 'page.html'}").write_bytes(body)
    return body, name


def links(page: str) -> list[tuple[str, str]]:
    """(text, absolute url) of the file links of a portal page, in order,
    with the tab titles (years) as ("#", title)."""
    page = re.sub(r"(?s)<(script|style)\b.*?</\1>", "", page)
    out = []
    pat = re.compile(
        r"<a\b[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>"
        r"|<div class=\"titleBlue\">(.*?)</div>",
        re.S,
    )
    for m in pat.finditer(page):
        href, txt, head = m.groups()
        if head is not None:
            t = " ".join(re.sub("<[^>]+>", " ", html.unescape(head)).split())
            if t:
                out.append(("#", t))
            continue
        if "/ficheiros/" not in href:
            continue
        t = " ".join(re.sub("<[^>]+>", " ", html.unescape(txt)).split())
        out.append((t, urllib.parse.urljoin(SITE, html.unescape(href))))
    return out


def contas_links(page: str) -> dict[int, dict[str, str]]:
    """{year: {map: url}} of the SNC-AP accounts: the first link of each
    map in each year's tab (the xlsx; the ods copy follows it)."""
    out: dict[int, dict[str, str]] = {}
    ano = None
    for t, u in links(page):
        if t == "#":
            ano = int(u) if re.fullmatch(r"\d{4}", u) else None
            continue
        if ano is None or ano < PRIMEIRO_SNC:
            continue
        for k, pat in MAPAS.items():
            if re.search(pat, t, re.I):
                out.setdefault(ano, {}).setdefault(k, u)
    return out


def divida_links(page: str) -> dict[int, str]:
    out = {}
    for t, u in links(page):
        m = re.fullmatch(r"Evolução (?:do )?endividamento total (\d{4})", t)
        if m:
            out.setdefault(int(m.group(1)), u)
    return out


def pmp_links(page: str) -> dict[int, str]:
    """The yearly files (link text "2025"): every município, five quarter
    ends from the previous December."""
    out = {}
    for t, u in links(page):
        if re.fullmatch(r"\d{4}", t):
            out.setdefault(int(t), u)
    return out


# --- account maps (xlsx) --------------------------------------------------

CODIGO = re.compile(r"^(\d{10}|[A-Z]{1,3}\d{1,3})$")
NIF = re.compile(r"^\d{9}$")


def text(v) -> str:
    return " ".join(str(v).split()) if v is not None else ""


def parse_mapa(data: bytes, ano: int, mapa: str) -> list[dict]:
    """Rows of the Azorean câmaras in one account map: every sheet, every
    code column with a non-zero value. The code row holds the economic code
    (receita/despesa: 10 digits) or the line code (B01, DR01, AT1); the
    labels are in the row below it (receita/despesa) or above it."""
    import openpyxl  # only needed here: the PDFs use pypdf

    wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True)
    out = []
    for ws in wb.worksheets:
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        hdr = next(
            (
                i
                for i, r in enumerate(rows[:40])
                if sum(bool(CODIGO.match(text(c))) for c in r) >= 3
            ),
            None,
        )
        if hdr is None:
            raise ValueError(f"{mapa} {ano} {ws.title}: no code row")
        cols = [j for j, c in enumerate(rows[hdr]) if CODIGO.match(text(c))]

        def at(i: int, j: int, rows: list = rows) -> str:
            r = rows[i] if 0 <= i < len(rows) else []
            return text(r[j]) if j < len(r) else ""

        nxt = rows[hdr + 1] if hdr + 1 < len(rows) else []
        below = nxt[cols[0]] if cols[0] < len(nxt) else None
        lab = hdr + 1 if isinstance(below, str) and below.strip() else hdr - 1
        tipo = next(
            (
                i
                for i in range(hdr, min(hdr + 8, len(rows)))
                if "Tipo" in [text(c) for c in rows[i][: cols[0]]]
            ),
            None,
        )
        for r in rows[hdr + 1 :]:
            k = next(
                (j for j, c in enumerate(r[: cols[0]]) if NIF.match(text(c))),
                None,
            )
            if k is None:
                continue
            nome = next(
                (
                    text(c)
                    for c in reversed(r[:k])
                    if text(c) and not text(c).isdigit()
                ),
                "",
            )
            m = azorean(nome)
            if not m:
                continue
            geo, nome_ine = MUNICIPIOS[m]
            for j in cols:
                v = r[j] if j < len(r) else None
                if not isinstance(v, int | float) or not v:
                    continue
                out.append(
                    {
                        "ano": ano,
                        "geocod": geo,
                        "municipio": nome_ine,
                        "mapa": mapa,
                        "codigo": text(rows[hdr][j]),
                        "descricao": at(lab, j),
                        "tipo": at(tipo, j) if tipo is not None else "",
                        "valor": round(float(v), 2),
                    }
                )
    return out


# --- debt and PMP (PDF) ---------------------------------------------------

LINHA_RAA = re.compile(r"^R\. ?A\. AÇORES (.+?) (-?\d.*)$")
NOTA = re.compile(r"\s*((?:\*+|[a-z]\))(?:\s*(?:\*+|[a-z]\)))*)\s*$")


def pdf_text(data: bytes) -> str:
    import pypdf

    reader = pypdf.PdfReader(io.BytesIO(data))
    return "\n".join(p.extract_text() or "" for p in reader.pages)


def numbers(tokens: list[str], n: int) -> list[list[int]]:
    """Every way to read the tokens as n integers written with a space as
    thousands separator ("42 534 483 15 942 648" -> 42534483, 15942648):
    each number is a token of 1-3 digits (maybe negative) followed by
    3-digit tokens."""
    out: list[list[int]] = []

    def go(i: int, acc: list[int]) -> None:
        if len(acc) == n:
            if i == len(tokens):
                out.append(acc)
            return
        t = tokens[i] if i < len(tokens) else ""
        if not re.fullmatch(r"-?\d{1,3}", t):
            return
        j = i + 1
        while True:
            go(j, acc + [int("".join(tokens[i:j]))])
            if j < len(tokens) and re.fullmatch(r"\d{3}", tokens[j]):
                j += 1
            else:
                break

    go(0, [])
    return out


def parse_divida(text_: str, ano: int) -> list[dict]:
    """The Azorean rows of a debt PDF: limit (1), total debt (2), debts not
    counted (3: non-budget debts and the exceptions of the law and the
    State budget), FAM contribution (4) and the debt that counts against
    the limit (5) = (2) - (3) - (4). A município marked "**" sent no
    validated accounts and has no figures."""
    out = []
    for line in text_.splitlines():
        m = LINHA_RAA.match(line.strip())
        if not m:
            continue
        nome, resto = m.groups()
        k = azorean(nome)
        if not k:
            raise ValueError(f"dívida {ano}: unknown município {nome!r}")
        nm = NOTA.search(resto)
        nota = nm.group(1) if nm else ""
        resto = resto[: nm.start()] if nm else resto
        if "." in resto:  # 2014: 10.147.343
            vals = [[int(x.replace(".", "")) for x in resto.split()]]
        else:
            vals = numbers(resto.split(), 5)
        ok = [
            v
            for v in vals
            if len(v) == 5 and abs(v[1] - v[2] - v[3] - v[4]) <= 2
        ]
        if len(ok) != 1:
            raise ValueError(f"dívida {ano} {nome}: cannot read {resto!r}")
        lim, tot, nao, fam, div = ok[0]
        geo, nome_ine = MUNICIPIOS[k]
        out.append(
            {
                "ano": ano,
                "geocod": geo,
                "municipio": nome_ine,
                "limite": lim,
                "divida_total": tot,
                "nao_orcamental": nao,
                "fam": fam,
                "divida": div,
                "pct_limite": round(100 * div / lim, 1) if lim else "",
                "nota": nota,
            }
        )
    return out


PMP_LINHA = re.compile(r"^(\D+?)((?:\s+(?:\d+|N\.d\.|-)){5})\s*$")


def parse_pmp(text_: str, ficheiro: str) -> list[dict]:
    """PMP (days) of the Azorean câmaras at the five quarter ends of a
    yearly file. "N.d." (not available) and "-" (2020: no quarterly
    reports while SNC-AP started) are skipped."""
    datas: list[str] = []
    out = []
    for line in text_.splitlines():
        line = line.strip()
        if not datas:
            ds = re.findall(r"(\d\d)/(\d\d)/(\d{4})", line)
            if len(ds) == 5:
                datas = [f"{a}-{m}-{d}" for d, m, a in ds]
            continue
        m = PMP_LINHA.match(line)
        if not m:
            continue
        k = azorean(m.group(1))
        if not k:
            continue
        geo, nome_ine = MUNICIPIOS[k]
        for data, v in zip(datas, m.group(2).split(), strict=True):
            if v.isdigit():
                out.append(
                    {
                        "data": data,
                        "geocod": geo,
                        "municipio": nome_ine,
                        "dias": int(v),
                        "ficheiro": ficheiro,
                    }
                )
    if not datas:
        raise ValueError(f"PMP {ficheiro}: no quarter dates")
    return out


def merge_pmp(rows: list[dict]) -> list[dict]:
    """One value per câmara and date: each yearly file repeats the previous
    December, and the newer file (revised figure) wins."""
    by: dict = {}
    for r in sorted(rows, key=lambda r: r["ficheiro"]):
        by[(r["data"], r["geocod"])] = r
    return sorted(by.values(), key=lambda r: (r["data"], r["geocod"]))


# --- output ---------------------------------------------------------------


def write_csv(path: Path, cols: list[str], rows: list[dict]) -> None:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    data = buf.getvalue().encode("utf-8")
    if path.suffix == ".gz":
        # fixed mtime: an unchanged CSV gives identical bytes (no commit)
        data = gzip.compress(data, mtime=0)
    path.write_bytes(data)


def check(contas: list, divida: list, pmp: list, hoje: dt.date) -> list[str]:
    erros = []
    for nome, rows, chave in (
        ("contas", contas, "ano"),
        ("dívida", divida, "ano"),
        ("PMP", pmp, "data"),
    ):
        if not rows:
            erros.append(f"{nome}: nothing read")
            continue
        ultimo = max(str(r[chave]) for r in rows)
        n = {r["geocod"] for r in rows if str(r[chave]) == ultimo}
        if len(n) < len(MUNICIPIOS) and nome != "PMP":
            erros.append(f"{nome} {ultimo}: {len(n)} of 19 câmaras")
    if contas:
        ultimo = max(int(r["ano"]) for r in contas)
        if ultimo < hoje.year - MAX_ATRASO:
            erros.append(f"contas: newest year {ultimo} is too old")
    return erros


def main(out_dir: Path, cache: Path | None = None) -> int:
    contas, divida, pmp = [], [], []
    for ano, mapas in sorted(
        contas_links(get(CONTAS, cache)[0].decode()).items()
    ):
        for mapa, url in mapas.items():
            data, name = get(url, cache)
            if not name.lower().endswith(".xlsx"):
                raise ValueError(f"{mapa} {ano}: expected xlsx, got {name!r}")
            contas += parse_mapa(data, ano, mapa)
    for ano, url in sorted(
        divida_links(get(DIVIDA, cache)[0].decode()).items()
    ):
        divida += parse_divida(pdf_text(get(url, cache)[0]), ano)
    for ano, url in sorted(pmp_links(get(PMP, cache)[0].decode()).items()):
        data, name = get(url, cache)
        pmp += parse_pmp(pdf_text(data), name or str(ano))
    pmp = merge_pmp(pmp)
    erros = check(contas, divida, pmp, dt.date.today())
    for e in erros:
        print("::error::" + e, file=sys.stderr)
    if erros:
        return 1
    contas.sort(key=lambda r: (r["ano"], r["geocod"], r["mapa"], r["codigo"]))
    divida.sort(key=lambda r: (r["ano"], r["geocod"]))
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "dgal_contas.csv.gz", COLS_CONTAS, contas)
    write_csv(out_dir / "dgal_divida.csv", COLS_DIVIDA, divida)
    write_csv(out_dir / "dgal_pmp.csv", COLS_PMP, pmp)
    print(
        f"contas {len(contas)} rows "
        f"({min(r['ano'] for r in contas)}-{max(r['ano'] for r in contas)}), "
        f"dívida {len(divida)}, PMP {len(pmp)}"
    )
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    cache_dir = None
    if "--cache" in args:
        i = args.index("--cache")
        cache_dir = Path(args[i + 1])
        del args[i : i + 2]
    sys.exit(main(Path(args[0] if args else "data"), cache_dir))
