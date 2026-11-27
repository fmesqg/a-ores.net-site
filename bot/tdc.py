"""TdC: Parecer do Tribunal de Contas sobre a Conta da Região Autónoma dos Açores.

Usage:
  python3 bot/tdc.py [data_dir]          add new pareceres to data_dir/tdc*.csv
  python3 bot/tdc.py [data_dir] --tudo   download and parse every parecer again

Every year the Secção Regional dos Açores of the Tribunal de Contas audits
the previous year's regional account and publishes a Relatório e Parecer
(~180 pages, ~14 MB), usually in November or December. Each year has a page

  https://www.tcontas.pt/pt-pt/ProdutosTC/PareceresTribunalContas/
      pareceres-craa/Paginas/detalhe.aspx?dset=<ano>

whose HTML lists the PDFs (file names change from year to year). From FIRST
on, the pareceres share one layout, and this script reads from them:

  tdc.csv          the court's text, one row per item:
                     juízo         the verdict ("conformidade global, ...")
                     reserva       qualifications on the account
                     ênfase        matters of emphasis
                     recomendação  recommendations to the Government, with
                                   the status the next parecer gave them
                                   (Apêndice I) and the year first made
  tdc_valores.csv  figures:
                     Conta do sector público administrativo regional
                       (the consolidated account table, in euros: two
                       years per parecer, so it starts at FIRST - 1 when
                       that table is text; in 2023 it is an image)
                     Indicadores (million euros, from the verdict's text):
                       total debt, revenue and expenditure left off the
                       books, State transfers under the solidarity principle

PDF text comes from pypdf (pip install pypdf), imported only when a PDF is
read; parsing works on plain text so it can be tested without it. Both CSVs
are committed and refreshed weekly by .github/workflows/tdc.yml; main()
fails when the parecer expected by now is missing or cannot be read, so the
workflow fails and sends an email.
"""

import csv
import datetime as dt
import html
import io
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SITE = "https://www.tcontas.pt"
DETAIL = (
    SITE + "/pt-pt/ProdutosTC/PareceresTribunalContas/pareceres-craa/"
    "Paginas/detalhe.aspx?dset={}"
)
UA = "acores.net open data (github.com/fmesqg/a-ores.net-site)"
PAUSE = 1.0
FIRST = 2023  # first parecer in the current layout
CONTA = "Conta do sector público administrativo regional"
INDICADORES = "Indicadores"

COLS = [
    "conta",
    "tipo",
    "numero",
    "texto",
    "referencia",
    "situacao",
    "desde",
    "parecer",
    "sintese",
]
VCOLS = [
    "quadro",
    "ordem",
    "nivel",
    "rubrica",
    "caminho",
    "ano",
    "valor",
    "unidade",
    "parecer",
]

# The same row, worded differently from one parecer to the next.
ALIASES = {"Despesas com o pessoal": "Despesas com pessoal"}
# Top-level rows of the account table; the rows after one belong to it.
TOPO = {
    "Receita efetiva",
    "Receita não efetiva",
    "Receita total",
    "Despesa efetiva",
    "Despesa não efetiva",
    "Despesa total",
    "Despesa primária",
    "Saldo global ou efetivo",
    "Saldo primário",
}
EURO = r"\d{1,3}(?: \d{3})*,\d{2}"
MILHOES = r"(\d{1,3}(?: \d{3})*(?:,\d+)?) milhões"


class Blocked(Exception):
    pass


def get(url: str) -> bytes | None:
    """The body, or None on 404. Anything else fails loudly."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        why = e.headers.get("cf-mitigated") or e.reason
        raise Blocked(f"{e.code} ({why}) em {url}") from e


def documents(page: str) -> dict:
    """{'parecer': url, 'sintese': url} from a year's detail page."""
    out = {}
    links = re.findall(
        r"""href=['"]([^'"]*/pareceres-craa/Documents/[^'"]+\.pdf)['"]"""
        r"[^>]*>([^<]*)<",
        page,
        re.I,
    )
    for href, title in links:
        url = urllib.parse.urljoin(SITE, html.unescape(href))
        url = urllib.parse.quote(url, safe=":/%")
        title = html.unescape(title).strip()
        if re.search(r"duas páginas|síntese", title, re.I):
            out.setdefault("sintese", url)
        elif re.match(r"(Relatório e )?Parecer sobre", title, re.I):
            out.setdefault("parecer", url)
    return out


def pdf_pages(data: bytes) -> list[str]:
    from pypdf import PdfReader

    return [p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages]


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def flat(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def key(text: str) -> str:
    """Matches a recommendation across pareceres, even when the PDF text
    breaks words apart (Apêndice I): letters only, first 60, with "sector"
    and "setor" (both used, even in the same parecer) made the same."""
    return re.sub(r"[^a-z]", "", fold(text)).replace("sector", "setor")[:60]


def number(tok: str) -> float:
    return float(tok.replace(" ", "").replace(",", "."))


def drop_page_numbers(s: str) -> str:
    return re.sub(r"(?m)^\s*\d{1,3}\s*$\n?", "", s)


def section(text: str, start: str, end: str) -> str:
    """The last match of `start` and what follows it up to `end`."""
    starts = [m.end() for m in re.finditer(start, text, re.M)]
    if not starts:
        return ""
    a = starts[-1]
    m = re.compile(end, re.M).search(text, a)
    return text[a : m.start() if m else len(text)]


def bullets(s: str) -> list[str]:
    return [flat(b) for b in s.split("•")[1:] if flat(b)]


def parse_juizo(text: str) -> dict:
    s = section(
        text, r"^\s*Juízo sobre a Conta\s*$(?=\s*Compete)", r"^\s*Sumário\s*$"
    )
    s = re.sub(
        r"(?m)^\s*\d*\s*O parecer sobre a Conta é emitido[\s\S]*?LOPTC\)?"
        r"[^\n]*\n",
        "",
        s,
    )
    s = drop_page_numbers(s)
    m = re.search(
        r"Tribunal de Contas emite um juízo (.+?),? sobre (?:a )?Conta",
        flat(s),
    )
    juizo = "Juízo " + m.group(1) if m else ""
    res = re.search(r"^\s*Reservas\s*$([\s\S]*?)^\s*Ênfases\s*$", s, re.M)
    enf = re.search(r"^\s*Ênfases\s*$([\s\S]*)", s, re.M)
    return {
        "juizo": juizo,
        "reservas": bullets(res.group(1)) if res else [],
        "enfases": bullets(enf.group(1)) if enf else [],
    }


REF = (
    r"(?:Pontos?\s+\d[\d.]*(?:\s*(?:,|e)\s*\d[\d.]*)*\.?"
    r"|Capítulo\s+[IVX\d]+\.?)"
    r"(?:\s*,?\s*§§?\s*\d+(?:\s*(?:,|e|a)\s*\d+)*\.?)?"
)


def ordinal_fix(s: str) -> str:
    """'1\\n0\\n.ª' and '1\\n.\\nª' -> '10.ª', '1.ª'."""
    s = re.sub(r"(?m)^\s*(\d)\s*\n\s*(\d)\s*\n\s*\.\s*ª", r"\1\2.ª", s)
    return re.sub(r"(?m)^\s*(\d{1,2})\s*\n?\s*\.\s*\n?\s*ª", r"\1.ª", s)


def parse_recomendacoes(text: str) -> list[dict]:
    s = section(
        text,
        r"^\s*(?:\d+(?:\.\d+)*\.\s*)?Recomendações\s*$(?=[\s\S]{0,400}"
        r"pode formular recomendações)",
        r"^\s*Decisão\s*$",
    )
    m = re.search(r"entende reiterar[^:]*?(?::|plenitude\.)", s)
    if not m:
        return []
    s = ordinal_fix(s[m.end() :])
    s = re.sub(r"(?m)^\s*\d*\s*Artigo 41\.º[^\n]*LOPTC\.?\s*$", "", s)
    s = flat(drop_page_numbers(s))
    pieces = re.split(f"({REF})", s)
    out = []
    for body, ref in zip(pieces[0::2], pieces[1::2], strict=False):
        # "380 Face ao exposto ..., formula-se uma nova recomendação:"
        new = re.search(r"\bnovas? recomendaç", body)
        body = re.sub(r"\b\d{3} [^:]*recomendaç[^:]*:", "", body)
        body = re.sub(r"\b\d{1,2}\.ª", "", body)
        body = flat(body)
        if not body:
            continue
        out.append(
            {
                "numero": len(out) + 1,
                "texto": body,
                "referencia": flat(ref),
                "desde": "" if new is None else "new",
            }
        )
    return out


# Status in Apêndice I, matched with whitespace removed: the PDF text
# breaks words ("P\narcialmente").
SITUACAO = {
    "Parcialmenteimplementada": "Parcialmente implementada",
    "Nãoimplementada": "Não implementada",
    "Implementada": "Implementada",
    "Prejudicada": "Prejudicada",
}


def parse_acompanhamento(text: str) -> list[dict]:
    """Apêndice I: status of the recommendations of the previous parecer."""
    s = section(
        text,
        r"^\s*(?:I\s*[–-]\s*)?Acompanhamento de recomendações\s*$"
        r"(?=\s*Recomendações\s+anteriormente)",
        r"^\s*II\s*[–-]\s*Processo orçamental",
    )
    if not s:
        return []
    chunks = re.split(r"(?<![\d.])\d{1,2}\.ª", ordinal_fix(s))[1:]
    out = []
    for c in chunks:
        tight = re.sub(r"\s", "", c)
        sit = re.search("|".join(SITUACAO), tight)
        if not sit:
            continue
        desde = re.search(
            r"pelaprimeiravez,?noRelatórioeParecersobreaContade(\d{4})",
            tight,
        )
        out.append(
            {
                "chave": key(tight[: sit.start()]),
                "situacao": SITUACAO[sit.group(0)],
                "desde": desde.group(1) if desde else "",
            }
        )
    return out


def parse_conta(text: str) -> list[dict]:
    """The consolidated account table: [{rubrica, caminho, nivel, ordem,
    ano, valor}], two years. Empty when the table is an image."""
    starts = [
        m.end()
        for m in re.finditer(
            r"Quadro \d+ – Conta do se(?:c)?tor público administrativo "
            r"regional",
            text,
        )
    ]
    if not starts:
        return []
    a = starts[-1]
    b = text.find("Fonte", a)
    block = text[a : b if b > 0 else a + 6000]
    years = [int(y) for y in re.findall(r"(?m)^\s*(20\d\d)\s*$", block)[:2]]
    if len(years) != 2:
        return []
    lines = block.split("\n")
    rows, label, values, minus, top, started = [], [], [], False, "", False

    def flush():
        nonlocal label, values, top
        name = flat(" ".join(label))
        name = ALIASES.get(name, name)
        if name and len(values) >= 2:
            if name in TOPO:
                top, nivel, path = name, 0, name
            else:
                nivel, path = 1, f"{top} › {name}"
            for y, v in zip(years, values[:2], strict=True):
                rows.append(
                    {
                        "rubrica": name,
                        "caminho": path,
                        "nivel": nivel,
                        "ordem": len(rows) // 2 + 1,
                        "ano": y,
                        "valor": v,
                    }
                )
        label, values = [], []

    for line in lines:
        t = line.strip()
        if not started:
            if t == "Receita efetiva":
                started = True
            else:
                continue
        if t == "-" or t == "":
            minus = minus or t == "-"
            continue
        m = re.fullmatch(rf"(-?)\s*({EURO})(\s+-)?", t)
        if m:
            v = number(m.group(2))
            if minus or m.group(1):
                v = -v
            minus = False
            values.append(v)
            continue
        if re.fullmatch(r"-?[\d ]+(,\d+)?\s*%", t) or t == "-":
            continue
        if values:
            flush()
        label.append(t)
    flush()
    return rows


def indicadores(text: str, conta: int) -> list[dict]:
    s = flat(text)
    out = []

    def add(rubrica, valor):
        out.append(
            {
                "rubrica": rubrica,
                "caminho": rubrica,
                "nivel": 0,
                "ordem": len(out) + 1,
                "ano": conta,
                "valor": number(valor),
            }
        )

    debt = re.findall(
        r"dívida total do se(?:c)?tor público administrativo regional"
        r"[^.]{0,160}?" + MILHOES,
        s,
    )
    if debt:  # the most quoted figure: other years appear once or twice
        add("Dívida total", max(set(debt), key=debt.count))
    m = re.search(
        r"falta de registos contabilísticos\s+nos montantes de\s+"
        + MILHOES
        + r"(?: de euros)?\s+e de\s+"
        + MILHOES,
        s,
    )
    if m:
        add("Receita não registada na Conta", m.group(1))
        add("Despesa não registada na Conta", m.group(2))
    m = re.search(
        r"princípio da\s+solidariedade,? no montante de\s+" + MILHOES, s
    )
    if m:
        add(
            "Transferências do Estado (princípio da solidariedade)", m.group(1)
        )
    return out


def parecer_rows(
    pages: list[str], conta: int, docs: dict
) -> tuple[list[dict], list[dict], list[dict]]:
    """(text rows, value rows, acompanhamento) for one parecer."""
    text = "\n".join(pages)
    base = {
        "conta": conta,
        "parecer": docs.get("parecer", ""),
        "sintese": docs.get("sintese", ""),
        "referencia": "",
        "situacao": "",
        "desde": "",
    }
    j = parse_juizo(text)
    rows = []
    if j["juizo"]:
        rows.append(
            {**base, "tipo": "juízo", "numero": 1, "texto": j["juizo"]}
        )
    for tipo, items in (("reserva", j["reservas"]), ("ênfase", j["enfases"])):
        for i, t in enumerate(items, 1):
            rows.append({**base, "tipo": tipo, "numero": i, "texto": t})
    for r in parse_recomendacoes(text):
        r["desde"] = str(conta) if r["desde"] == "new" else ""
        rows.append({**base, "tipo": "recomendação", **r})
    values = []
    for quadro, unidade, items in (
        (CONTA, "€", parse_conta(text)),
        (INDICADORES, "milhões de €", indicadores(text, conta)),
    ):
        for r in items:
            values.append(
                {
                    **r,
                    "quadro": quadro,
                    "unidade": unidade,
                    "parecer": docs.get("parecer", ""),
                }
            )
    return rows, values, parse_acompanhamento(text)


def apply_status(rows: list[dict], conta: int, acomp: list[dict]) -> None:
    """Parecer `conta` judges the recommendations of parecer `conta - 1`."""
    by_key = {a["chave"]: a for a in acomp}
    for r in rows:
        if str(r["conta"]) != str(conta - 1) or r["tipo"] != "recomendação":
            continue
        k = key(r["texto"])
        hit = by_key.get(k) or next(
            (a for c, a in by_key.items() if c[:40] == k[:40]), None
        )
        if hit:
            r["situacao"] = f"{hit['situacao']} ({conta})"
            r["desde"] = hit["desde"]


def fill_desde(rows: list[dict]) -> None:
    """A recommendation's first year, known from any parecer's Apêndice I,
    holds for every year it was repeated."""
    first = {}
    for r in rows:
        if r["tipo"] == "recomendação" and r["desde"]:
            k = key(r["texto"])[:40]
            first[k] = min(first.get(k, r["desde"]), r["desde"])
    for r in rows:
        if r["tipo"] == "recomendação" and not r["desde"]:
            r["desde"] = first.get(key(r["texto"])[:40], "")


def merge_values(old: list[dict], new: list[dict]) -> list[dict]:
    """A later parecer's figure for a year replaces an earlier one's."""
    best = {}
    for r in old + new:
        k = (r["quadro"], r["caminho"], str(r["ano"]))
        prev = best.get(k)
        if prev is None or str(r["parecer"]) >= str(prev["parecer"]):
            best[k] = r
    out = list(best.values())
    out.sort(
        key=lambda r: (
            r["quadro"] != CONTA,
            int(r["ordem"]),
            int(r["ano"]),
        )
    )
    return out


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(path)


def expected(today: dt.date) -> int:
    """The latest account whose parecer should be out by now: it comes out
    in November or December of the following year, so by January of the
    year after that at the latest."""
    return today.year - 2


def main(out_dir: Path, everything: bool = False) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    path, vpath = out_dir / "tdc.csv", out_dir / "tdc_valores.csv"
    rows = [] if everything else read_csv(path)
    values = [] if everything else read_csv(vpath)
    have = {int(r["conta"]) for r in rows}
    today = dt.date.today()
    changed = everything
    for conta in range(FIRST, today.year):
        if conta in have:
            continue
        try:
            page = get(DETAIL.format(conta))
            time.sleep(PAUSE)
            docs = documents(page.decode("utf-8", "replace") if page else "")
            if "parecer" not in docs:
                print(f"{conta}: parecer ainda não publicado")
                continue
            data = get(docs["parecer"])
        except Blocked as e:
            print(f"{conta}: bloqueado: {e}")
            return 1
        if not data or not data.startswith(b"%PDF"):
            print(f"{conta}: o parecer não é um PDF: {docs['parecer']}")
            return 1
        new, vals, acomp = parecer_rows(pdf_pages(data), conta, docs)
        kinds = {r["tipo"] for r in new}
        if not {"juízo", "recomendação"} <= kinds:
            print(f"{conta}: não consegui ler o parecer {docs['parecer']}")
            return 1
        print(
            f"{conta}: {len(new)} textos, {len(vals)} valores, "
            f"{len(acomp)} recomendações acompanhadas"
        )
        rows += new
        apply_status(rows, conta, acomp)
        values = merge_values(values, vals)
        have.add(conta)
        changed = True
    if changed:
        fill_desde(rows)
        rows.sort(
            key=lambda r: (
                int(r["conta"]),
                ["juízo", "reserva", "ênfase", "recomendação"].index(
                    r["tipo"]
                ),
                int(r["numero"]),
            )
        )
        write_csv(path, rows, COLS)
        write_csv(vpath, values, VCOLS)
    if not have:
        print("nenhum parecer")
        return 1
    if max(have) < expected(today):
        print(
            f"o último parecer é sobre a Conta de {max(have)}; "
            f"o de {expected(today)} já devia ter saído "
            f"({DETAIL.format(expected(today))})"
        )
        return 1
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    target = Path(args[0]) if args else Path("data")
    sys.exit(main(target, everything="--tudo" in sys.argv))
