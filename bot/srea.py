"""SREA: Serviço Regional de Estatística dos Açores.

Usage:
  python3 bot/srea.py [data_dir]   update data_dir/srea.csv

srea.azores.gov.pt publishes its series as Excel files linked from one page
per area (/area/<slug>/). A new edition is uploaded under a new address
(wp-content/uploads/<ano>/<mês>/...), often with a slightly different name,
so each series is found by looking for a pattern among the links of its
area page (SERIES). The site's "relatório" pages open a Reporting Services
server that sits behind a Cloudflare challenge; the Excel files and the
WordPress API do not. Requests follow SREA's own limit in bot/gov.py.

Series kept, chosen for people who are not data experts:
  ipc        inflation in the Azores (IPC): year-on-year change, monthly,
             total and the 13 ECOICOP classes; and the 12-month average
  iae        Indicador de Atividade Económica, monthly (% change)
  icp        Indicador do Consumo Privado, monthly (% change)
  desemprego unemployment rate, quarterly (Inquérito ao Emprego). Each
             file has the last five quarters, so every file on the page is
             read and the history builds up in the CSV
  emprego    people in work (thousands), total and by sector of activity
             (CAE-Rev.4, from 2026), from the same Inquérito ao Emprego file
  dormidas   nights in hotels and in alojamento local by island, monthly
             (each file has this year and last year; history builds up)
  pib        GDP by island, annual, and pib_hab, GDP per resident using
  populacao  the SREA population estimates by island
  pagamentos card operations (SIBS), monthly since 2020: purchases in
             payment terminals (TPA), those with foreign cards, and cash
             withdrawals (CA); value in € by concelho, number for the Azores
  pde        saldo and dívida bruta of the Azores' public administration
             (Procedimento dos Défices Excessivos), yearly, read from the
             lead sentence of each notification post (POSTS): its tables
             are images. The WordPress site keeps posts only from 2025

Rows are kept by (serie, indicador, rubrica, local, periodo); a newer file
overwrites what an older one said, so revisions land. Excel is read with
openpyxl (.xlsx) and xlrd (.xls), imported only when a file is read; the
parsers work on lists of rows so they can be tested without them.
data/srea.csv is committed and refreshed weekly by
.github/workflows/srea.yml; bot/datasets.py copies it into docs/dados/.
main() returns 1, so the workflow fails and emails, when a series' file
can no longer be found or read: usually a renamed file (fix its pattern).
"""

import csv
import datetime as dt
import html
import io
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from bot import gov
except ImportError:  # run as a script: python3 bot/<name>.py
    import gov

SITE = "https://srea.azores.gov.pt"

COLS = [
    "serie",
    "indicador",
    "rubrica",
    "local",
    "periodo",
    "data",
    "valor",
    "unidade",
    "nota",
    "ficheiro",
    "pagina",
]
KEY = ("serie", "indicador", "rubrica", "local", "periodo")

MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()
ILHAS = [
    "Santa Maria",
    "São Miguel",
    "Terceira",
    "Graciosa",
    "São Jorge",
    "Pico",
    "Faial",
    "Flores",
    "Corvo",
]
NOTAS = {"§": "fiabilidade reduzida"}

Rows = list[list]


# --- reading -------------------------------------------------------------


HOST = urllib.parse.urlsplit(SITE).hostname
RETRY = {429, 500, 502, 503, 504}


def get(url: str, tries: int = 5) -> bytes:
    """GET within SREA's rate limit (bot/gov.py). On 429 or 5xx, wait
    longer each time (Retry-After when given) and try again; any other
    error, a 403 above all, is raised at once rather than repeated."""
    url = urllib.parse.quote(url, safe=":/%?=&#")  # names carry "–"
    req = urllib.request.Request(url, headers=gov.HEADERS)
    for n in range(tries):
        gov.wait(HOST)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in RETRY or n == tries - 1:
                raise
            after = e.headers.get("Retry-After", "")
            delay = int(after) if after.isdigit() else 10 * 2**n
            print(f"{e.code} on {url}; retrying in {delay} s", file=sys.stderr)
            gov._sleep(delay)
    raise AssertionError("unreachable")


def area_files(page_html: str) -> list[str]:
    """Excel links on an area page, oldest upload first."""
    urls = {
        html.unescape(u)
        for u in re.findall(r'href="([^"]+\.xlsx?)"', page_html, re.I)
    }

    def upload(u: str) -> tuple:
        m = re.search(r"/uploads/(\d{4})/(\d{2})/", u)
        return (m.groups() if m else ("0", "0"), u)

    return sorted(urls, key=upload)


def sheets(data: bytes, name: str) -> dict[str, Rows]:
    """Every sheet as a list of rows (empty cells are None)."""
    if name.lower().endswith(".xls"):
        import xlrd

        book = xlrd.open_workbook(file_contents=data)
        return {
            s.name: [
                [c if c != "" else None for c in s.row_values(i)]
                for i in range(s.nrows)
            ]
            for s in book.sheets()
        }
    import openpyxl

    book = openpyxl.load_workbook(
        io.BytesIO(data), data_only=True, read_only=True
    )
    return {
        ws.title: [list(r) for r in ws.iter_rows(values_only=True)]
        for ws in book.worksheets
    }


# --- helpers -------------------------------------------------------------


def text(v) -> str:
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""


def number(v) -> float | None:
    if isinstance(v, bool):
        return None
    if isinstance(v, int | float):
        return float(v)
    s = text(v).replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None  # "-", "x", "…": no value


def year_of(v) -> int | None:
    m = re.fullmatch(r"(\d{4})(?:\.0)?\*?", text(v))
    return int(m.group(1)) if m else None


def month_of(v) -> int | None:
    n = number(v)
    if n is not None and n == int(n) and 1 <= n <= 12:
        return int(n)
    s = text(v).lower()[:3]
    return MESES.index(s) + 1 if s in MESES else None


def place(v) -> str:
    """'41-Santa Maria' -> 'Santa Maria'; region totals -> 'Açores'."""
    s = re.sub(r"^\d+\s*-\s*", "", text(v))
    if s.upper() in ("TOTAL", "") or "Região Autónoma" in s:
        return "Açores"
    return s


def first_text(rows: Rows) -> str:
    for r in rows:
        for c in r:
            if text(c):
                return text(c)
    return ""


def row(
    serie, indicador, rubrica, local, periodo, data, valor, unidade, nota=""
):
    return {
        "serie": serie,
        "indicador": indicador,
        "rubrica": rubrica,
        "local": local,
        "periodo": periodo,
        "data": data,
        "valor": round(valor, 4),
        "unidade": unidade,
        "nota": nota,
    }


# --- parsers -------------------------------------------------------------


def parse_ipc(book: dict[str, Rows]) -> list[dict]:
    """IPC série longa: Q3-Q6, rows = classes or aggregates, cols = months.

    Q5 (classes) and Q6 (aggregates): taxa de variação homóloga; Q4: média
    dos últimos 12 meses (aggregates, only the total is kept)."""
    out = []
    wanted = {
        ("homóloga", "Consumo individual"): ("Variação homóloga", None),
        ("homóloga", "Agregados especiais"): ("Variação homóloga", "Total"),
        ("12 meses", "Agregados especiais"): (
            "Variação média dos últimos 12 meses",
            "Total",
        ),
    }
    for rows in book.values():
        title = first_text(rows)
        if "Mensal" not in title:
            continue
        hit = [v for (a, b), v in wanted.items() if a in title and b in title]
        if not hit:
            continue
        indicador, only = hit[0]
        head = next(
            (
                r
                for r in rows
                if sum(isinstance(c, dt.datetime | dt.date) for c in r) >= 2
            ),
            None,
        )
        if head is None:
            continue
        months = {j: c for j, c in enumerate(head) if isinstance(c, dt.date)}
        label_col = min(months) - 1
        for r in rows[rows.index(head) + 1 :]:
            label = text(r[label_col]) if label_col < len(r) else ""
            if not label or label.startswith(("(", "Fonte", "Nota")):
                continue
            if only and label != only:
                continue
            for j, d in months.items():
                v = number(r[j]) if j < len(r) else None
                if v is not None:
                    out.append(
                        row(
                            "ipc",
                            indicador,
                            label,
                            "Açores",
                            d.strftime("%Y-%m"),
                            d.strftime("%Y-%m-01"),
                            v,
                            "%",
                        )
                    )
    return out


def parse_monthly(
    book: dict[str, Rows], serie: str, indicador: str
) -> list[dict]:
    """One monthly series in long form: Ano | Mês | valor (year blank
    after its first month), as in the IAE and ICP files."""
    rows = next(iter(book.values()))
    out, year = [], None
    for r in rows:
        cells = [c for c in r if c is not None and text(c) != ""]
        if len(cells) < 2:
            continue
        y = year_of(cells[0]) if len(cells) >= 3 else None
        if y and month_of(cells[1]):
            year, m, v = y, month_of(cells[1]), cells[2]
        elif year and month_of(cells[0]) and len(cells) == 2:
            m, v = month_of(cells[0]), cells[1]
        else:
            continue
        val = number(v)
        if val is not None:
            out.append(
                row(
                    serie,
                    indicador,
                    "Total",
                    "Açores",
                    f"{year}-{m:02d}",
                    f"{year}-{m:02d}-01",
                    val,
                    "%",
                )
            )
    return out


RUBRICAS_IE = {
    ("Taxa de desemprego", "HM"): "Total",
    ("Taxa de desemprego", "H"): "Homens",
    ("Taxa de desemprego", "M"): "Mulheres",
    ("Dos 16 aos 24 anos", "HM"): "Dos 16 aos 24 anos",
}


def _ie_table(
    book: dict[str, Rows],
    quadro: str,
    serie: str,
    indicador: str,
    unidade: str,
    rubrica_of,
) -> list[dict]:
    """One table of the Inquérito ao Emprego: a column per quarter (the
    last five, or fewer in a new table), a label in the first column of a
    block's first row and the sex (HM, H, M) in the second."""
    rows = next((v for k, v in book.items() if k.strip() == quadro), None)
    if rows is None:
        return []
    head = next(
        (r for r in rows if sum("trimestre" in text(c) for c in r) >= 3),
        None,
    )
    if head is None:
        return []
    quarters = {}
    for j, c in enumerate(head):
        m = re.match(r"(\d)\.º trimestre (\d{4})", text(c))
        if m:
            quarters[j] = (int(m.group(2)), int(m.group(1)))
        elif quarters and text(c):
            break  # the "Variação" columns and the long-series header
    out, label = [], ""
    for r in rows[rows.index(head) + 1 :]:
        if text(r[0]):
            label = text(r[0])
        rubrica = rubrica_of(label, text(r[1]) if len(r) > 1 else "")
        if not rubrica:
            continue
        for j, (y, q) in quarters.items():
            v = number(r[j]) if j < len(r) else None
            if v is None:
                continue
            flag = text(r[j + 1]) if j + 1 < len(r) else ""
            out.append(
                row(
                    serie,
                    indicador,
                    rubrica,
                    "Açores",
                    f"{y}-T{q}",
                    f"{y}-{3 * q - 2:02d}-01",
                    v,
                    unidade,
                    NOTAS.get(flag, ""),
                )
            )
    return out


def parse_desemprego(book: dict[str, Rows]) -> list[dict]:
    """Inquérito ao Emprego, Quadro 10: the last five quarters."""
    return _ie_table(
        book,
        "Quadro 10",
        "desemprego",
        "Taxa de desemprego",
        "%",
        lambda label, sexo: RUBRICAS_IE.get((label, sexo)),
    )


def parse_emprego(book: dict[str, Rows]) -> list[dict]:
    """Inquérito ao Emprego: people in work (thousands), the total from
    Quadro 4 and by sector of activity from Quadro 6.1 (CAE-Rev.4, in the
    files since 2026; the older Quadro 6 uses CAE-Rev.3, whose sections
    have other letters, and is not read). Both sexes only."""
    total = _ie_table(
        book,
        "Quadro 4",
        "emprego",
        "População empregada",
        "milhares",
        lambda label, sexo: (
            "Total" if label == "População empregada" and sexo == "HM" else ""
        ),
    )
    setores = _ie_table(
        book,
        "Quadro 6.1",
        "emprego",
        "População empregada por setor (CAE-Rev.4)",
        "milhares",
        lambda label, sexo: (
            label if sexo == "HM" and label != "População empregada" else ""
        ),
    )
    return total + setores


def parse_ie(book: dict[str, Rows]) -> list[dict]:
    """The quarterly Inquérito ao Emprego file: unemployment and jobs."""
    return parse_desemprego(book) + parse_emprego(book)


def parse_dormidas(book: dict[str, Rows], rubrica: str) -> list[dict]:
    """Nights by island: a block per island, a row per year, 12 months."""
    rows = next(iter(book.values()))
    head = next(
        r
        for r in rows
        if sum(month_of(c) is not None and isinstance(c, str) for c in r) >= 12
    )
    months = {j: month_of(c) for j, c in enumerate(head) if month_of(c)}
    out, local = [], ""
    for r in rows[rows.index(head) + 1 :]:
        first = text(r[0]) if r else ""
        if first.startswith("Nota"):
            break
        if first:
            local = "Açores" if first.startswith("Dormidas") else first
        y = next((year_of(c) for c in r[1 : min(months)] if year_of(c)), None)
        if not y or local not in ILHAS + ["Açores"]:
            continue
        for j, m in months.items():
            v = number(r[j]) if j < len(r) else None
            if v is not None:
                out.append(
                    row(
                        "dormidas",
                        "Dormidas",
                        rubrica,
                        local,
                        f"{y}-{m:02d}",
                        f"{y}-{m:02d}-01",
                        v,
                        "dormidas",
                    )
                )
    return out


def parse_pib(book: dict[str, Rows]) -> list[dict]:
    """PIB por ilha, current prices: islands in columns, a row per year."""
    rows = next(
        (v for k, v in book.items() if k.startswith("1 ")), None
    ) or next(iter(book.values()))
    head = next(r for r in rows if sum(text(c) in ILHAS for c in r) >= 9)
    cols = {
        j: place(c)
        for j, c in enumerate(head)
        if text(c) in ILHAS or text(c).upper() == "TOTAL"
    }
    out = []
    for r in rows[rows.index(head) + 1 :]:
        y = next((year_of(c) for c in r[: min(cols)] if year_of(c)), None)
        if not y:
            continue
        nota = "provisório" if any("*" in text(c) for c in r) else ""
        for j, local in cols.items():
            v = number(r[j]) if j < len(r) else None
            if v is not None:
                out.append(
                    row(
                        "pib",
                        "Produto interno bruto",
                        "Preços correntes",
                        local,
                        str(y),
                        f"{y}-01-01",
                        round(v * 1000),
                        "€",
                        nota,
                    )
                )
    return out


def parse_populacao(book: dict[str, Rows]) -> list[dict]:
    """Resident population by island (Q01, both sexes, all ages)."""
    rows = book.get("Q01") or next(iter(book.values()))
    out = []
    for r in rows:
        if len(r) < 4 or not year_of(r[0]) or text(r[2]):
            continue  # header, or a município row
        v = number(r[3])
        local = place(r[1])
        if v is not None and local in ILHAS + ["Açores"]:
            y = year_of(r[0])
            out.append(
                row(
                    "populacao",
                    "População residente",
                    "Total",
                    local,
                    str(y),
                    f"{y}-01-01",
                    v,
                    "pessoas",
                )
            )
    return out


PAGAMENTOS = {
    # rubrica: (canal starts with, tipo de operação, origem do cartão)
    "Compras em TPA": ("Terminais", "Compras", None),
    "Compras em TPA com cartões estrangeiros": (
        "Terminais",
        "Compras",
        "Outro país",
    ),
    "Levantamentos em CA": ("Caixas", "Levantamentos", None),
}


def parse_pagamentos(
    book: dict[str, Rows], indicador: str, unidade: str, concelhos: bool
) -> list[dict]:
    """SIBS card operations (TPA: payment terminals; CA: cash machines),
    monthly since 2020. The DADOS sheet has a row per year, month,
    concelho, channel, operation type and card origin; it is summed into
    the rubricas of PAGAMENTOS, for the Azores and, when ``concelhos``,
    for each concelho."""
    rows = next(v for k, v in book.items() if k.strip().startswith("DADOS"))
    head = next(r for r in rows if "Concelho" in [text(c) for c in r])
    col = {text(c): j for j, c in enumerate(head)}
    i_ano, i_mes, i_conc = col["Ano"], col["Mês"], col["Concelho"]
    i_canal, i_tipo = col["Canal"], col["Tipo de Operação"]
    i_orig, i_val = col["Origem do cartão"], len(col) - 1
    sums: dict[tuple, float] = {}
    for r in rows[rows.index(head) + 1 :]:
        if len(r) <= i_val:
            continue
        y, m, v = year_of(r[i_ano]), month_of(r[i_mes]), number(r[i_val])
        if not (y and m) or v is None:
            continue
        canal, tipo, orig = text(r[i_canal]), text(r[i_tipo]), text(r[i_orig])
        for rubrica, (c, t, o) in PAGAMENTOS.items():
            if canal.startswith(c) and tipo == t and o in (None, orig):
                places = ["Açores"] + ([text(r[i_conc])] if concelhos else [])
                for local in places:
                    k = (rubrica, local, y, m)
                    sums[k] = sums.get(k, 0) + v
    return [
        row(
            "pagamentos",
            indicador,
            rubrica,
            local,
            f"{y}-{m:02d}",
            f"{y}-{m:02d}-01",
            v,
            unidade,
        )
        for (rubrica, local, y, m), v in sums.items()
    ]


PDE_LEAD = re.compile(
    r"Em (\d{4})\s*(?:\(([^)]*)\))?,?\s*a (necessidade|capacidade) de "
    r"financiamento da Administração Pública da Região Autónoma dos Açores "
    r"foi de ([\d.]+(?:,\d+)?) milhões de euros.*?dívida bruta "
    r"\(consolidada\) atingido os ([\d.]+(?:,\d+)?) M€",
    re.S,
)


def pt_number(s: str) -> float:
    """'3.797,8' -> 3797.8"""
    return float(s.replace(".", "").replace(",", "."))


def parse_pde(posts: list[dict]) -> list[dict]:
    """Saldo and dívida of the Azores' public administration (Procedimento
    dos Défices Excessivos), from the lead sentence of each notification
    post: the tables are only images. Posts oldest first, so a later
    notification revises an earlier one for the same year."""
    out = []
    for p in sorted(posts, key=lambda p: p["date"]):
        body = html.unescape(re.sub(r"<[^>]+>", " ", p["content"]))
        m = PDE_LEAD.search(re.sub(r"\s+", " ", body))
        if not m:
            continue
        y, quali, sinal, saldo, divida = m.groups()
        nota = "provisório" if quali and "provis" in quali else ""
        saldo_v = pt_number(saldo) * (-1 if sinal == "necessidade" else 1)
        for indicador, v in (
            ("Saldo das administrações públicas regionais", saldo_v),
            ("Dívida bruta consolidada", pt_number(divida)),
        ):
            r = row(
                "pde", indicador, "Total", "Açores", y, f"{y}-01-01", v, "M€"
            )
            r.update(nota=nota, ficheiro=p["link"], pagina=p["link"])
            out.append(r)
    return out


def pib_hab(rows: list[dict]) -> list[dict]:
    """GDP per resident by island, where both are known for the year."""
    pop = {
        (r["local"], r["periodo"]): r
        for r in rows
        if r["serie"] == "populacao"
    }
    out = []
    for r in rows:
        p = pop.get((r["local"], r["periodo"]))
        if r["serie"] == "pib" and p and float(p["valor"]):
            out.append(
                {
                    **r,
                    "serie": "pib_hab",
                    "indicador": "PIB por habitante",
                    "valor": round(float(r["valor"]) / float(p["valor"])),
                    "unidade": "€ por habitante",
                }
            )
    return out


# Each series: area page, file-name pattern, parser, and whether every
# matching file is read (oldest first, so the newest wins) or only the
# newest.
SERIES = [
    ("ipc", "precos", r"IPC.*S[eé]rie.?Longa", parse_ipc, False),
    (
        "iae",
        "conjuntura",
        r"IAE",
        lambda b: parse_monthly(b, "iae", "Indicador de atividade económica"),
        False,
    ),
    (
        "icp",
        "conjuntura",
        r"ICP.*Serie.?Longa",
        lambda b: parse_monthly(b, "icp", "Indicador do consumo privado"),
        False,
    ),
    (
        "desemprego",
        "mercado-de-trabalho",
        r"Quadros_Publicacao_IE|Estatisticas-\d\.o-Trim",
        parse_ie,
        True,
    ),
    (
        "dormidas-ht",
        "turismo",
        r"/HT-Dormidas-Ilha",
        lambda b: parse_dormidas(b, "Hotelaria"),
        False,
    ),
    (
        "dormidas-al",
        "turismo",
        r"/AL-Dormidas-Ilha",
        lambda b: parse_dormidas(b, "Alojamento local"),
        False,
    ),
    ("pib", "contas-regionais", r"PIB-por-Ilha", parse_pib, False),
    (
        "populacao",
        "populacao",
        r"Estimativas_Popula",
        parse_populacao,
        False,
    ),
    (
        "pagamentos-valor",
        "atividade-financeira",
        r"/Operacoes-em-TPA-e-CA-valor",
        lambda b: parse_pagamentos(b, "Valor", "€", concelhos=True),
        False,
    ),
    (
        "pagamentos-numero",
        "atividade-financeira",
        r"/Operacoes-em-TPA-e-CA-numero",
        lambda b: parse_pagamentos(b, "Número", "operações", concelhos=False),
        False,
    ),
]

# Series read from the text of SREA's posts (WordPress API) rather than from
# an Excel file: name, search terms, slug prefix of the posts, parser.
POSTS = [
    ("pde", "defices excessivos", "pde-", parse_pde),
]


def posts(search: str, slug: str) -> list[dict]:
    """Every post matching ``search`` whose slug starts with ``slug``."""
    q = urllib.parse.urlencode(
        {
            "search": search,
            "per_page": 100,
            "_fields": "date,link,slug,content",
        }
    )
    got = json.loads(get(f"{SITE}/wp-json/wp/v2/posts?{q}"))
    return [
        {
            "date": p["date"],
            "link": p["link"],
            "content": p["content"]["rendered"],
        }
        for p in got
        if p["slug"].startswith(slug)
    ]


# --- CSV -----------------------------------------------------------------


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def merge(old: list[dict], new: list[dict]) -> list[dict]:
    """New rows replace old ones with the same key."""
    keep = {tuple(r[k] for k in KEY): r for r in old}
    for r in new:
        keep[tuple(str(r[k]) for k in KEY)] = r
    names = [s[0] for s in SERIES] + [p[0] for p in POSTS]
    order = {}
    for i, name in enumerate(names):
        order.setdefault(name.split("-")[0], i)
    order["pib_hab"] = order["pib"]
    return sorted(
        keep.values(),
        key=lambda r: (
            order.get(r["serie"], 99),
            r["indicador"],
            r["rubrica"],
            r["local"],
            r["data"],
        ),
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, COLS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            v = float(r["valor"])
            w.writerow({**r, "valor": int(v) if v == int(v) else v})


def excel_series(name, area, pattern, parse, every, pages) -> list[dict]:
    """One series from the Excel files on its area page (``pages`` caches
    the area pages already read)."""
    page = f"{SITE}/area/{area}/"
    if area not in pages:
        pages[area] = get(page).decode("utf-8", "replace")
    files = [u for u in area_files(pages[area]) if re.search(pattern, u)]
    if not files:
        raise ValueError(f"no file matches {pattern!r}")
    got = []
    for url in files if every else files[-1:]:
        fname = urllib.parse.unquote(url.rsplit("/", 1)[-1])
        rows = parse(sheets(get(url), fname))
        for r in rows:
            r["ficheiro"], r["pagina"] = url, page
        got += rows
    print(f"{name}: {len(got)} values from {len(files)} file(s)")
    return got


def main(out_dir: Path) -> int:
    pages: dict[str, str] = {}
    jobs = [(s[0], lambda s=s: excel_series(*s, pages)) for s in SERIES] + [
        (
            name,
            lambda search=search, slug=slug, parse=parse: parse(
                posts(search, slug)
            ),
        )
        for name, search, slug, parse in POSTS
    ]
    new: list[dict] = []
    failed = []
    for name, job in jobs:
        try:
            got = job()
            if not got:
                raise ValueError("nothing parsed")
            new += got
        except Exception as e:  # keep going; report at the end
            failed.append(name)
            print(f"{name}: FAILED {e}", file=sys.stderr)
            if isinstance(e, urllib.error.HTTPError) and e.code == 403:
                print("SREA refused the bot (403): stopping.", file=sys.stderr)
                break
    path = out_dir / "srea.csv"
    rows = merge(read_csv(path), new)
    rows = merge(rows, pib_hab(rows))
    write_csv(path, rows)
    print(f"{path}: {len(rows)} rows")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "data")))
