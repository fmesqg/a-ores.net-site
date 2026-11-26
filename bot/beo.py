"""BEO: Boletim de Execução Orçamental do Governo Regional dos Açores.

Usage:
  python3 bot/beo.py [data_dir]          add new boletins to data_dir/beo.csv
  python3 bot/beo.py [data_dir] --tudo   download and parse every boletim again

The Direção Regional do Orçamento e Tesouro publishes one PDF a month, by the
end of the following month, with the year-to-date budget execution of the
regional government (GRA), its autonomous services and funds (SFA) and
reclassified public entities (EPR). The listing page on portal.azores.gov.pt
sits behind a Cloudflare challenge, but the PDFs themselves do not, and their
addresses are predictable:

  https://portal.azores.gov.pt/documents/36626/<pasta do ano>/
      BEO_<ano>_<mês>_<Nome do mês>+<ano>.pdf

so new boletins are found by asking for the next expected file. Each year has
its own folder id (FOLDERS): when January's boletim of a new year appears,
copy any of its links from the portal in a browser and add the folder here.
main() fails, so the weekly workflow fails and sends an email, when no new
boletim has been found for too long (STALE_DAYS).

Parsed tables (all values are year-to-date, in euros unless stated):
  Quadro I    Síntese global: rubricas x subsetor (GRA, SFA, EPR, consolidado)
  Quadro III  Receita fiscal do GRA: montante and execução (% do orçamento)
  Quadro IV   Receita não fiscal do GRA: idem
  Quadro V    Despesa do GRA: idem
  Quadro VI   Despesa do GRA por função
  Quadro VII  Despesa do GRA por departamento: rubricas x departamento
Quadros III-V also carry the previous year, which fills in the year before
the first boletim (2023). Quadros II and VIII repeat Quadro I.

PDF text comes from pypdf (pip install pypdf), imported only when a PDF is
read; parsing works on plain text so it can be tested without it.
data/beo.csv is committed and refreshed weekly by .github/workflows/beo.yml;
bot/datasets.py copies it into docs/dados/ and acores.db.
"""

import csv
import datetime as dt
import io
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://portal.azores.gov.pt/documents/36626"
UA = "acores.net open data (github.com/fmesqg/a-ores.net-site)"
PAUSE = 0.5
FIRST = (2024, 1)
STALE_DAYS = 80  # a boletim is due by the end of the next month

# Liferay folder holding each year's boletins.
FOLDERS = {2024: 13933856, 2025: 17740212, 2026: 21646330}
# Files whose name breaks the pattern. The server ignores case, but these
# spellings match the links already announced on açores.net.
FILENAMES = {
    (2025, 6): "BEO_2025_06_junho+2025.pdf",
    (2025, 7): "BEO_2025_07_julho+2025.pdf",
    (2025, 11): "BEO_2025_11_Novembro+05.pdf",
}
MESES = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]

COLS = [
    "quadro",
    "ordem",
    "nivel",
    "rubrica",
    "caminho",
    "dimensao",
    "medida",
    "ano",
    "mes",
    "data",
    "valor",
    "boletim",
]
EUR, EXEC = "Montante (€)", "Execução do orçamento (%)"

# Quadro number -> (name, kind). Kinds:
#   subsetor  4 columns: GRA, SFA, EPR, consolidado
#   execucao  5 columns: previous year, year, VH, execution prev., execution
#   funcao    2 columns: amount, structure (%)
#   orgânica  one column per department, then the total
QUADROS = {
    "I": ("Síntese global", "subsetor"),
    "III": ("Receita fiscal do GRA", "execucao"),
    "IV": ("Receita não fiscal do GRA", "execucao"),
    "V": ("Despesa do GRA", "execucao"),
    "VI": ("Despesa do GRA por função", "funcao"),
    "VII": ("Despesa do GRA por departamento", "organica"),
}
ORDER = [name for name, _ in QUADROS.values()]
SUBSETORES = [
    "Governo Regional (GRA)",
    "Serviços e fundos autónomos (SFA)",
    "Entidades públicas reclassificadas (EPR)",
    "Consolidado",
]
EXPECTED = {"subsetor": 4, "execucao": 5, "funcao": 2}

# Department columns of Quadro VII. Before mid-2024 the header spells out
# the names of the previous government's departments; since 2025 it uses
# codes. Keys are matched against the folded header chunk, in order.
DEPARTAMENTOS = [
    ("ALRAA", ("assembleia", "alraa"), "Assembleia Legislativa"),
    ("VPGR", ("vice",), "Vice-Presidência do Governo"),
    ("PGR", ("presidencia", "pgr"), "Presidência do Governo"),
    (
        "SRFPAP",
        ("financas", "srfpap"),
        "Finanças, Planeamento e Administração Pública",
    ),
    (
        "SRAPC",
        ("parlamentares", "srapc"),
        "Assuntos Parlamentares e Comunidades",
    ),
    ("SREAC", ("assuntos culturais",), "Educação e Assuntos Culturais"),
    ("SRECD", ("cultura e desporto", "srecd"), "Educação, Cultura e Desporto"),
    ("SRSD", ("saude e desporto",), "Saúde e Desporto"),
    ("SRSSS", ("seguranca social", "srsss"), "Saúde e Segurança Social"),
    (
        "SRADR",
        ("desenvolvimento rural",),
        "Agricultura e Desenvolvimento Rural",
    ),
    ("SRAA", ("alimentacao", "sraa"), "Agricultura e Alimentação"),
    ("SRMP", ("pescas", "srmp"), "Mar e Pescas"),
    (
        "SRAAlC",
        ("alteracoes climaticas",),
        "Ambiente e Alterações Climáticas",
    ),
    ("SRAAC", ("acao climatica", "sraac"), "Ambiente e Ação Climática"),
    (
        "SRTMI",
        ("turismo", "srtmi"),
        "Turismo, Mobilidade e Infraestruturas",
    ),
    (
        "SRJQPE",
        ("qualificacao",),
        "Juventude, Qualificação Profissional e Emprego",
    ),
    ("SRJHE", ("habitacao", "srjhe"), "Juventude, Habitação e Emprego"),
    ("TOTAL", ("total",), "Total"),
]

NUM = r"-?\d{1,3}(?:[  ]\d{3})*,\d{2}%?"
LINE = re.compile(rf"^(?P<label>.*?)[  ]*(?P<nums>(?:{NUM}[  ]*)+)$")
QUADRO = re.compile(r"^\s*Quadro\s+([IVX]+)\s*[–-]")


# --- addresses ------------------------------------------------------------


def pdf_url(year: int, month: int) -> str | None:
    """The boletim's address, or None when the year's folder is unknown."""
    folder = FOLDERS.get(year)
    if folder is None:
        return None
    name = FILENAMES.get(
        (year, month), f"BEO_{year}_{month:02d}_{MESES[month - 1]}+{year}.pdf"
    )
    return f"{BASE}/{folder}/" + urllib.parse.quote(name, safe="+")


def expected_months(today: dt.date) -> list[tuple[int, int]]:
    """Every month from FIRST up to last month (this month's boletim is
    never out yet)."""
    out, (y, m) = [], FIRST
    while (y, m) < (today.year, today.month):
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


class Blocked(Exception):
    """The portal answered with something other than the PDF or a 404."""


def download(url: str) -> bytes | None:
    """The PDF, or None if it is not there (yet). The PDFs go through
    Cloudflare too, which in November 2026 challenges the portal's pages but
    not /documents/. If that changes, fail now rather than wait STALE_DAYS."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        why = e.headers.get("cf-mitigated") or e.reason
        raise Blocked(f"{e.code} ({why}) em {url}") from e
    if not body.startswith(b"%PDF"):
        raise Blocked(f"a resposta não é um PDF (Cloudflare?) em {url}")
    return body


def pdf_pages(data: bytes) -> list[str]:
    from pypdf import PdfReader  # only needed to read PDFs

    return [p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages]


# --- parsing --------------------------------------------------------------


def unsplit(text: str) -> str:
    """Some boletins (December 2024) come out of the PDF with a space after
    every s ("As s embleia", "Pres idência"). Undo that, roughly, when a lone
    "s" gives it away: good enough to find department names in a header.
    Rubricas do not need it, see key()."""
    if not re.search(r"\bs [a-zà-ÿ]", text):
        return text
    text = re.sub(r"s (?=[a-zà-ÿ,])", "s", text)
    return re.sub(r"(?<=\S)  +(?=\S)", " ", text)


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9%]+", " ", s).strip()


def number(tok: str) -> float:
    return float(
        tok.rstrip("%").replace(" ", "").replace(" ", "").replace(",", ".")
    )


def split_line(line: str) -> tuple[str, list[str]] | None:
    """'  Impostos diretos 1 234,56 0,00' -> ('  Impostos diretos', [...])."""
    m = LINE.match(line.rstrip())
    if not m:
        return None
    return m.group("label"), re.findall(NUM, m.group("nums"))


def level(label: str) -> int:
    spaces = len(label) - len(label.lstrip())
    return 0 if spaces < 3 else 1 if spaces < 7 else 2


def tidy(label: str) -> str:
    """Display label: collapse spaces, sentence case for ALL CAPS, keep
    acronyms in brackets, drop the COFOG code of Quadro VI."""
    s = re.sub(r"\s+", " ", label).strip()
    s = re.sub(r"^\d{3}\s+", "", s)
    letters = [c for c in s if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) > 0.8 * len(letters):
        s = s.lower().capitalize()
    else:  # Title Case -> sentence case, keeping acronyms and "Estado"
        words = s.split(" ")
        s = " ".join(
            [words[0]]
            + [
                w if w.isupper() or w == "Estado" else w[:1].lower() + w[1:]
                for w in words[1:]
            ]
        )
    s = re.sub(r"\(([^)]*)\)", lambda m: "(" + m.group(1).upper() + ")", s)
    return s.replace("Infraestrururas", "Infraestruturas")


def key(label: str) -> str:
    """Stable key for a rubrica across boletins whose wording changes:
    the COFOG code (Quadro VI), else a bracketed acronym (IRS, IVA...),
    else the folded label."""
    s = label.strip()
    if m := re.match(r"(\d{3})\s", s):
        return m.group(1)
    if m := re.search(r"\(([A-Z]{2,5})\)", s):
        return m.group(1).lower()
    # Without spaces or "s": survives "Des pes as" (December 2024) and
    # "Imposto(s) rodoviários" (2026). Rubricas of one quadro differ by more.
    return re.sub(r"[s ]", "", fold(s))


def departments(header: str) -> list[str]:
    """Department names, in column order, from Quadro VII's header."""
    text = re.sub(r"\s+", " ", unsplit(header))
    text = re.sub(r"Vice-\s*", "Vice-", text)
    if re.search(r"\bALRAA\b", text):
        chunks = re.findall(r"\b[A-Z]{3,7}\b", text[text.find("ALRAA") :])
    else:
        chunks = re.split(
            r"(?=Assembleia|(?<!Vice-)Presid[êe]ncia|Vice-|Sec\.|TOTAL)", text
        )
    names = []
    for chunk in chunks:
        f = fold(chunk).replace(" ", "")
        if not f:
            continue
        for _, keys, name in DEPARTAMENTOS:
            if any(k.replace(" ", "") in f for k in keys):
                names.append(name)
                break
    return names


def parse(pages: list[str], year: int) -> list[dict]:
    """Rows (quadro, rubrica, dimensao, medida, ano, valor...) of one
    boletim, the month being added by the caller. Rows of the previous
    year (Quadros III-V) carry ano=year-1."""
    rows = []
    current, stack, order, header = None, [], 0, []
    for text in pages:
        if "Índice" in text and "...." in text:
            continue
        for line in text.split("\n"):
            if m := QUADRO.match(line):
                current = m.group(1) if m.group(1) in QUADROS else None
                stack, order, header = [], 0, []
                continue
            if current is None:
                continue
            name, kind = QUADROS[current]
            split = split_line(line)
            if split is None:
                header.append(line)
                continue
            raw, nums = split
            if kind == "organica":
                cols = departments("\n".join(header))
                want = len(cols)
            else:
                want = EXPECTED[kind]
            if len(nums) != want or (kind != "funcao" and not raw.strip()):
                continue
            label = raw if raw.strip() else "Total"
            lvl = level(raw) if kind != "funcao" else (1 if raw.strip() else 0)
            while stack and stack[-1][0] >= lvl:
                stack.pop()
            stack.append((lvl, label.strip()))
            order += 1
            base = {
                "quadro": name,
                "ordem": order,
                "nivel": lvl,
                "chave": " / ".join(key(s) for _, s in stack),
                "rubrica": tidy(label),
                "caminho": " › ".join(tidy(s) for _, s in stack),
            }
            vals = [number(t) for t in nums]
            if kind == "subsetor":
                for dim, v in zip(SUBSETORES, vals, strict=True):
                    rows.append(
                        {
                            **base,
                            "dimensao": dim,
                            "medida": EUR,
                            "ano": year,
                            "valor": v,
                        }
                    )
            elif kind == "execucao":
                prev, cur, _, eprev, ecur = vals
                for ano, v, e in ((year, cur, ecur), (year - 1, prev, eprev)):
                    rows.append(
                        {
                            **base,
                            "dimensao": "",
                            "medida": EUR,
                            "ano": ano,
                            "valor": v,
                        }
                    )
                    rows.append(
                        {
                            **base,
                            "dimensao": "",
                            "medida": EXEC,
                            "ano": ano,
                            "valor": e,
                        }
                    )
            elif kind == "funcao":
                rows.append(
                    {
                        **base,
                        "dimensao": "",
                        "medida": EUR,
                        "ano": year,
                        "valor": vals[0],
                    }
                )
            else:
                for dim, v in zip(cols, vals, strict=True):
                    rows.append(
                        {
                            **base,
                            "dimensao": dim,
                            "medida": EUR,
                            "ano": year,
                            "valor": v,
                        }
                    )
    return rows


# --- table ----------------------------------------------------------------


def boletim_rows(
    pages: list[str], year: int, month: int, url: str
) -> list[dict]:
    rows = []
    for r in parse(pages, year):
        if r["ano"] < year and (r["ano"], month) >= FIRST:
            continue  # the year's own boletim has it, possibly revised
        rows.append(
            {
                **r,
                "mes": month,
                "data": f"{r['ano']}-{month:02d}-01",
                "boletim": url,
            }
        )
    return rows


def finish(rows: list[dict]) -> list[dict]:
    """Give every series the labels and order of its latest boletim, so a
    rubrica renamed between years stays one series, and sort."""
    latest: dict[tuple, dict] = {}
    for r in sorted(rows, key=lambda r: r["data"]):
        latest[(r["quadro"], r["chave"])] = r
    out = []
    for r in rows:
        last = latest[(r["quadro"], r["chave"])]
        out.append(
            {
                **{c: r.get(c, "") for c in COLS},
                "ordem": last["ordem"],
                "nivel": last["nivel"],
                "rubrica": last["rubrica"],
                "caminho": last["caminho"],
            }
        )
    out.sort(
        key=lambda r: (
            ORDER.index(r["quadro"]),
            int(r["ordem"]),
            r["dimensao"],
            r["medida"],
            r["data"],
        )
    )
    return out


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(path)


def main(out_dir: Path, everything: bool = False) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "beo.csv"
    old = [] if everything else read_csv(path)
    for r in old:  # the key is not stored: rebuild it from the path
        r["chave"] = " / ".join(key(s) for s in r["caminho"].split(" › "))
    have = {
        (int(r["ano"]), int(r["mes"]))
        for r in old
        if r["quadro"] == "Síntese global"
    }
    today = dt.date.today()
    new = []
    for y, m in expected_months(today):
        if (y, m) in have:
            continue
        url = pdf_url(y, m)
        if url is None:
            print(f"{y}-{m:02d}: pasta do ano desconhecida (FOLDERS)")
            continue
        try:
            data = download(url)
        except Blocked as e:
            print(f"{y}-{m:02d}: bloqueado: {e}")
            return 1
        time.sleep(PAUSE)
        if data is None:
            print(f"{y}-{m:02d}: ainda não publicado")
            continue
        rows = boletim_rows(pdf_pages(data), y, m, url)
        if not any(r["quadro"] == "Síntese global" for r in rows):
            print(f"{y}-{m:02d}: não consegui ler o boletim {url}")
            return 1
        print(f"{y}-{m:02d}: {len(rows)} linhas")
        new += rows
        have.add((y, m))
    if new or everything:
        write_csv(path, finish(old + new))
    if not have:
        print("nenhum boletim")
        return 1
    last = max(have)
    age = (today - dt.date(*last, 1)).days
    if age > STALE_DAYS + 31:
        print(
            f"último boletim é de {last[0]}-{last[1]:02d}, há {age} dias. "
            "Se é um ano novo, junte a pasta do ano a FOLDERS (copie um link "
            "do boletim de janeiro em portal.azores.gov.pt)."
        )
        return 1
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    target = Path(args[0]) if args else Path("data")
    sys.exit(main(target, everything="--tudo" in sys.argv))
