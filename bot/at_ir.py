"""AT: IRS and IRC statistics for the Azores, Madeira and the mainland.

Usage:
  python3 bot/at_ir.py [data_dir] [--cache DIR]
      rewrite data_dir/at_irs.csv, at_irc.csv and at_distritos.csv

Every spring (late March to mid April) the Autoridade Tributária publishes
a "Dossier Estatístico" of the IRS returns (Modelo 3) and one of the IRC
returns (Modelo 22), each covering the last three years, one Excel file per
edition, on

  https://info.portaldasfinancas.gov.pt/pt/dgci/divulgacao/estatisticas/estatisticas_ir/Pages/estatisticas_irs.aspx
  https://info.portaldasfinancas.gov.pt/pt/dgci/divulgacao/estatisticas/estatisticas_ir/Pages/estatisticas_irc.aspx

Tables are found by their content, not their number (the "Mapa" numbers
change between editions):

  at_irs.csv
    Taxas de Tributação por Circunscrições Administrativas: households,
        income taxed at the general rates (Rendimento Englobado) and tax
        assessed (IRS Liquidado), by the tax rate actually applied, for
        the mainland (C), the Azores (A) and Madeira (M), split into
        married / not married / total.
    Taxa Adicional de Solidariedade: households and tax at the additional
        solidarity rate (80 to 250 thousand euros, above 250 thousand).
    Taxas Gerais de IRS: the general rates of each year in each region,
        with the upper limit of each bracket in "valor".
  at_irc.csv
    Cálculo do imposto: returns and tax at the regional IRC rate
        ("Imposto à taxa da Reg. Aut. dos Açores / da Madeira").
    Derrama estadual: returns and state surcharge by bracket of taxable
        profit, mainland / Azores / Madeira (since 2017).
    Taxas nominais: the nominal IRC rates, mainland / Azores / Madeira.
  at_distritos.csv
    the "por distrito" chapters of both dossiers: IRS households, income,
    tax and effective rate (since 2015); IRC returns, profit, losses,
    taxable income, tax and effective rate (since 2011). The column
    "distrito" is the AT's label. Until about 2020 the Azores appear as
    the three old districts (Angra do Heroísmo, Horta, Ponta Delgada) and
    Madeira as Funchal, later as "R. A. Açores" / "R. A. Madeira";
    "regiao" puts each label in Açores, Madeira, Continente or Total.
    Some IRS editions print both the old districts and the regional
    total: add the old districts only when the regional total is missing.

Every edition back to the first .xlsx is read; a year that appears in two
editions keeps the newest one, since the AT revises the older years.
Amounts are in millions of euros in the files and are written in euros;
rates are written in percent. Read the Notas Prévias before using the
numbers: IRS households count where the taxpayer lives; IRC returns count
where the company has its head office (a mainland company with branches in
the Azores counts in the mainland).

.github/workflows/at_ir.yml runs this weekly in March to May, and monthly
otherwise. main() fails, so the workflow emails, when no edition can be
read or the newest year is more than ~2.5 years old.
"""

import csv
import datetime as dt
import io
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

SITE = "https://info.portaldasfinancas.gov.pt"
PAGINAS = {
    imposto: SITE + "/pt/dgci/divulgacao/estatisticas/estatisticas_ir/"
    f"Pages/estatisticas_{imposto.lower()}.aspx"
    for imposto in ("IRS", "IRC")
}
UA = "acores.net open data (github.com/fmesqg/a-ores.net-site)"
XLSX_RE = re.compile(r'href="([^"]*\.xlsx)"', re.I)
EDICAO_RE = re.compile(r"(20\d\d)\D{1,3}(20\d\d)")
REGIAO_RE = re.compile(r"^[A-Z]\s*-\s*(CONTINENTE|AÇORES|MADEIRA)\s*$", re.I)
REGIOES = {
    "CONTINENTE": "Continente",
    "AÇORES": "Açores",
    "MADEIRA": "Madeira",
}
FOLDED = {"CONTINENTE": "Continente", "ACORES": "Açores", "MADEIRA": "Madeira"}
AZORES_OLD = {"ANGRA DO HEROISMO", "HORTA", "PONTA DELGADA"}
MAX_IDADE = 2  # years between the newest year in the files and today

COLS = [
    "quadro",
    "medida",
    "ano",
    "regiao",
    "escalao",
    "taxa",
    "titularidade",
    "valor",
    "unidade",
    "dossie",
    "url",
]
IRC_COLS = [
    "quadro",
    "medida",
    "ano",
    "regiao",
    "escalao",
    "valor",
    "unidade",
    "dossie",
    "url",
]
DIST_COLS = [
    "imposto",
    "medida",
    "unidade",
    "ano",
    "distrito",
    "regiao",
    "valor",
    "dossie",
    "url",
]
TAXAS = "Taxas de tributação"
ADICIONAL = "Taxa adicional de solidariedade"
GERAIS = "Taxas gerais"
CALCULO = "Cálculo do imposto"
DERRAMA = "Derrama estadual"
NOMINAIS = "Taxas nominais"


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def dossies(page: str, imposto: str = "IRS") -> dict[str, str]:
    """{edition "2022-2024": url} of one tax. Editions are told apart by
    their years: the 2022-2024 IRS file is called Notas_Previas_..., the
    2016-2018 one has its years only in its folder, and the 2017-2019 IRC
    file is called ..._IRS_2017_2019.xlsx (in an IRC_2017_2019 folder)."""
    out = {}
    for href in XLSX_RE.findall(page):
        path = urllib.parse.unquote(href).upper()
        if imposto == "IRC" and "IRC" not in path:
            continue
        if imposto == "IRS" and ("IRS" not in path or "IRC" in path):
            continue
        name = path.rsplit("/", 1)[-1]
        m = EDICAO_RE.search(name) or EDICAO_RE.search(path)
        if not m or int(m[2]) - int(m[1]) != 2:
            continue
        out[f"{m[1]}-{m[2]}"] = urllib.parse.urljoin(SITE, href)
    return out


def fold(s) -> str:
    """'R. A. Açores' -> 'R. A. ACORES' (upper case, no accents)."""
    s = unicodedata.normalize("NFKD", str(s).replace("​", ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().upper()


def regiao(label: str) -> str:
    n = fold(label)
    if "ACORES" in n or n in AZORES_OLD:
        return "Açores"
    if "MADEIRA" in n or n == "FUNCHAL":
        return "Madeira"
    if n.startswith("TOTAL"):
        return "Total"
    return "Continente"


def num(x) -> float | None:
    """A number from a cell: 0.133, 7881, '13,1%' (-> 0.131), '1 234,5'."""
    if isinstance(x, bool):
        return None
    if isinstance(x, int | float):
        return float(x)
    if not isinstance(x, str):
        return None
    s = re.sub(r"[\s​ ]", "", x)
    pct = s.endswith("%")
    s = s.rstrip("%")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        v = float(s)
    except ValueError:
        return None
    return v / 100 if pct else v


def _cells(row) -> list:
    return [c for c in row if c not in (None, "")]


def _head(rows: list[list], n: int = 6) -> str:
    return " / ".join(str(c) for r in rows[:n] for c in _cells(r))


def _year(c) -> int | None:
    if isinstance(c, int) and not isinstance(c, bool):
        y = c
    elif isinstance(c, str) and re.fullmatch(r"\s*20\d\d\s*", c):
        y = int(c)
    else:
        return None
    return y if 2000 <= y <= 2100 else None


def year_cols(row: list) -> dict[int, int] | None:
    """{year: column} when the row is a table header (consecutive years
    next to '%', 'Var.', 'Cód.', 'Designação' or 'Escalões'), else None."""
    cols: dict[int, int] = {}
    for i, c in enumerate(row):
        y = _year(c)
        if y and y not in cols:
            cols[y] = i
    if len(cols) < 2:
        return None
    ys = sorted(cols)
    if ys != list(range(ys[0], ys[0] + len(ys))):
        return None
    marks = [fold(c) for c in row if isinstance(c, str) and not _year(c)]
    if not any(
        m == "%" or m.startswith(("VAR", "COD", "DESIGNA", "ESCALOES"))
        for m in marks
    ):
        return None
    return cols


def _label(row: list) -> str:
    """The row's label: its first text cell that is not a district code."""
    for c in row:
        if isinstance(c, str) and c.strip() and not c.strip().isdigit():
            return re.sub(r"\s+", " ", c.replace("​", "")).strip()
    return ""


def _escala(text: str) -> float:
    t = text.lower()
    if "milhões" in t or "milhoes" in t:
        return 1e6
    if "milhares" in t:
        return 1e3
    return 1.0


def _unidade(head: str) -> str:
    """'declarações' for a count table, '€' for an amount table. A title
    can carry both words ("CAP.II - VALORES DECLARADOS - MAPA 13 / ... /
    NÚMERO DE DECLARAÇÕES"), so the count wins."""
    h = fold(head)
    if "NUMERO DE DECLARACOES" in h:
        return "declarações"
    return "€" if "VALORES" in h else "declarações"


def _valor(v: float, unidade: str, escala: float):
    if unidade == "€":
        return round(v * escala, 2)
    if unidade == "%":
        return round(v * 100, 2)
    return int(round(v))


def by_columns(rows: list[list]):
    """(label, year, value) of a table with the years as columns. A new
    header row (a regional block, say) resets the columns."""
    cols = None
    for r in rows:
        yc = year_cols(r)
        if yc:
            cols = yc
            continue
        if not cols:
            continue
        label = _label(r)
        if not label or fold(label).startswith(("FONTE", "DATA", "NOTA")):
            continue
        for y, i in cols.items():
            v = num(r[i]) if i < len(r) else None
            if v is not None:
                yield label, y, v


def parse_distritos(
    rows: list[list], imposto: str, medida: str, unidade: str, escala: float
) -> list[list]:
    """A 'por distrito' table: one row per district and year."""
    return [
        [
            imposto,
            medida,
            unidade,
            y,
            label,
            regiao(label),
            _valor(v, unidade, escala),
        ]
        for label, y, v in by_columns(rows)
    ]


# IRS ----------------------------------------------------------------------


def _medida(text: str) -> str:
    t = text.lower()
    if "agregados" in t:
        return "Agregados"
    if "liquidado" in t:
        return "IRS liquidado"
    if "rendimento" in t:
        return "Rendimento englobado"
    return ""


def parse_taxas(rows: list[list], dossie: str, url: str) -> list[list]:
    """One 'Taxas de Tributação' sheet: year, then a block per region."""
    medida, ano, reg, escala, ordem, out = "", None, "", 1.0, 0, []
    for r in rows:
        if not r:
            continue
        first = r[0]
        if isinstance(first, str):
            if not medida and _medida(first) and len(r) == 1:
                medida = _medida(first)
            if "valores em" in first.lower():
                escala = _escala(first)
            m = REGIAO_RE.match(first.strip())
            if m:
                reg, ordem = REGIOES[m[1].upper()], 0
                escala = 1.0 if medida == "Agregados" else 1e6
            continue
        if isinstance(first, int) and 2000 <= first <= 2100 and len(r) == 1:
            ano = first
            continue
        nums = [x for x in r if isinstance(x, int | float)]
        if not (reg and ano and medida) or len(nums) < 4:
            continue
        ordem += 1
        taxa, casados, nao_casados, total = nums[:4]
        unidade = "agregados" if medida == "Agregados" else "€"
        for tit, v in (
            ("Casados", casados),
            ("Não casados", nao_casados),
            ("Total", total),
        ):
            valor = round(v * escala, 2) if unidade == "€" else int(v)
            out.append(
                [
                    TAXAS,
                    medida,
                    ano,
                    reg,
                    ordem,
                    round(taxa, 2),
                    tit,
                    valor,
                    unidade,
                    dossie,
                    url,
                ]
            )
    return out


def parse_adicional(rows: list[list], dossie: str, url: str) -> list[list]:
    """One 'Taxa Adicional de Solidariedade' sheet: a block per region,
    with the years as columns."""
    medida, reg, anos, escala, ordem, out = "", "", [], 1.0, 0, []
    for r in rows:
        if not r:
            continue
        first = r[0]
        if not isinstance(first, str):
            continue
        low = first.strip().lower()
        if not medida and len(r) == 1 and _medida(first):
            medida = _medida(first)
            continue
        if "valores em" in low:
            escala = _escala(first)
            continue
        if len(r) == 1 and low in ("continente", "açores", "madeira"):
            reg, anos, ordem = first.strip().capitalize(), [], 0
            escala = 1.0 if medida == "Agregados" else 1e6
            continue
        years = [x for x in r[1:] if isinstance(x, int) and 2000 <= x <= 2100]
        if years:
            anos = years
            continue
        if not (reg and anos and medida) or low.startswith("total"):
            continue
        vals = r[1 : 1 + len(anos)]
        if len(vals) < len(anos) or not all(
            isinstance(v, int | float) for v in vals
        ):
            continue
        ordem += 1
        label = re.sub(r"\s+", " ", first).strip()
        unidade = "agregados" if medida == "Agregados" else "€"
        for ano, v in zip(anos, vals, strict=True):
            valor = round(v * escala, 2) if unidade == "€" else int(v)
            out.append(
                [
                    ADICIONAL,
                    medida,
                    ano,
                    reg,
                    ordem,
                    label,
                    "Total",
                    valor,
                    unidade,
                    dossie,
                    url,
                ]
            )
    return out


def _limite(label: str) -> float | str:
    """'De mais de 7703 até 11623' -> 11623; 'Superior a 80000' -> ''."""
    m = re.search(r"at[ée]\s*([\d.\s]+)", label, re.I)
    if not m:
        return ""
    return float(re.sub(r"[.\s]", "", m[1]))


def parse_gerais(rows: list[list], dossie: str, url: str) -> list[list]:
    """'Taxas Gerais de IRS': per year, a bracket per row and a column per
    region."""
    ano, cols, ordem, out = None, {}, 0, []
    for r in rows:
        cells = _cells(r)
        if not cells:
            continue
        first = cells[0]
        if isinstance(first, str):
            m = re.match(r"\s*Ano\s+(20\d\d)", first)
            if m:
                ano, cols, ordem = int(m[1]), {}, 0
                continue
        names = {
            FOLDED[fold(c)]: i
            for i, c in enumerate(r)
            if isinstance(c, str) and fold(c) in FOLDED
        }
        if len(names) >= 2:
            cols = names
            continue
        if not (ano and cols) or not isinstance(first, str):
            continue
        vals = {k: num(r[i]) if i < len(r) else None for k, i in cols.items()}
        if any(v is None for v in vals.values()):
            continue
        ordem += 1
        for reg, v in vals.items():
            out.append(
                [
                    GERAIS,
                    "Taxa",
                    ano,
                    reg,
                    ordem,
                    round(v, 2),
                    "",
                    _limite(first),
                    "€ (limite superior do escalão)",
                    dossie,
                    url,
                ]
            )
    return out


# (keys all in the title, medida, unidade) of an IRS "por distrito" sheet
# (the editions up to 2017-2019 have "Rendimento Bruto", a "Taxa Efetiva
# de Tributação Bruta" and the "Sobretaxa"; they are kept apart)
IRS_DISTRITO = [
    (("SOBRETAXA", "NUMERO DE AGREGADOS"), "Sobretaxa", "agregados"),
    (("SOBRETAXA",), "Sobretaxa", "€"),
    (("TAXA EFETIVA", "BRUTA"), "Taxa efetiva bruta", "%"),
    (("TAXA EFETIVA",), "Taxa efetiva", "%"),
    (("IRS LIQUIDADO", "NUMERO DE AGREGADOS"), "IRS liquidado", "agregados"),
    (("IRS LIQUIDADO",), "IRS liquidado", "€"),
    (("RENDIMENTO BRUTO", "NUMERO DE AGREGADOS"), "Agregados", "agregados"),
    (("RENDIMENTO BRUTO",), "Rendimento bruto", "€"),
    (("RENDIMENTO ENGLOBADO",), "Rendimento englobado", "€"),
    (("NUMERO DE AGREGADOS",), "Agregados", "agregados"),
]


def _irs_medida(head: str) -> tuple[str, str]:
    h = fold(head)
    for keys, medida, unidade in IRS_DISTRITO:
        if all(k in h for k in keys):
            return medida, unidade
    return "", ""


def parse_irs(sheets: dict[str, list[list]], dossie: str, url: str):
    """(at_irs rows, at_distritos rows) of one IRS edition."""
    irs, dist = [], []
    for raw in sheets.values():
        rows = [_cells(r) for r in raw]
        head = " ".join(str(c) for r in rows[:3] for c in r)
        if "Taxa Adicional" in head:
            irs += parse_adicional(rows, dossie, url)
        elif "Taxas de Tributação" in head and any(
            r and isinstance(r[0], str) and REGIAO_RE.match(r[0].strip())
            for r in rows
        ):
            irs += parse_taxas(rows, dossie, url)
        elif "Taxas Gerais" in head:
            irs += parse_gerais(raw, dossie, url)
        elif "DISTRITO" in fold(head):
            medida, unidade = _irs_medida(_head(raw, 4))
            if medida:
                escala = _escala(_head(raw))
                dist += [
                    r + [dossie, url]
                    for r in parse_distritos(
                        raw, "IRS", medida, unidade, escala
                    )
                ]
    return irs, dist


def parse_book(sheets: dict[str, list[list]], dossie: str, url: str):
    return parse_irs(sheets, dossie, url)[0]


# IRC ----------------------------------------------------------------------

# (key in the title, medida); the longer keys first ("MATÉRIA COLETÁVEL"
# contains "COLETA")
IRC_MEDIDAS = [
    ("TAXAS MEDIAS EFETIVAS", "Taxa média efetiva"),
    ("IRC LIQUIDADO", "IRC liquidado"),
    ("REG. SIMPLIFICADO", "Matéria coletável, regime simplificado"),
    ("MATERIA COLETAVEL", "Matéria coletável"),
    ("COLETA", "Coleta"),
    ("COLECTA", "Coleta"),
    ("LUCRO TRIBUTAVEL", "Lucro tributável"),
    ("PREJUIZO FISCAL", "Prejuízo fiscal"),
    ("NEGATIVO", "Resultado líquido negativo"),
    ("POSITIVO", "Resultado líquido positivo"),
]


def _irc_medida(head: str) -> tuple[str, str]:
    """(medida, unidade) of an IRC 'por distrito' sheet."""
    h = fold(head)
    if "QUADRO RESUMO" in h or "POR DISTRITO" not in h:
        return "", ""
    for key, medida in IRC_MEDIDAS:
        if key in h:
            if medida.startswith("Taxa"):
                return medida, "%"
            return medida, _unidade(head)
    if "NUMERO DE DECLARACOES" in h:
        return "Declarações", "declarações"
    return "", ""


def parse_calculo(rows: list[list], dossie: str, url: str) -> list[list]:
    """'Cálculo do imposto': the rows of the tax at a regional rate."""
    head = _head(rows, 10)
    unidade = _unidade(head)
    escala = _escala(head)
    out = []
    for label, y, v in by_columns(rows):
        n = fold(label)
        if "REG. AUT" not in n and "REGIAO AUTONOMA" not in n:
            continue
        out.append(
            [
                CALCULO,
                "Imposto à taxa regional",
                y,
                regiao(label),
                label,
                _valor(v, unidade, escala),
                unidade,
                dossie,
                url,
            ]
        )
    return out


def parse_derrama(rows: list[list], dossie: str, url: str) -> list[list]:
    """'Derrama estadual por escalões': a block per region."""
    unidade = _unidade(_head(rows, 10))
    out, reg, cols, escala = [], "", None, 1.0
    for r in rows:
        cells = _cells(r)
        if not cells:
            continue
        if len(cells) == 1 and isinstance(cells[0], str):
            n = fold(cells[0])
            if n in FOLDED:
                reg, cols = FOLDED[n], None
            elif "VALORES EM" in n:
                escala = _escala(cells[0])
            continue
        yc = year_cols(r)
        if yc:
            cols = yc
            continue
        if not (reg and cols):
            continue
        label = _label(r)
        if not label or fold(label).startswith(("FONTE", "DATA", "NOTA")):
            continue
        for y, i in cols.items():
            v = num(r[i]) if i < len(r) else None
            if v is None:
                continue
            out.append(
                [
                    DERRAMA,
                    "Derrama estadual",
                    y,
                    reg,
                    "Total" if fold(label).startswith("TOTAL") else label,
                    _valor(v, unidade, escala),
                    unidade,
                    dossie,
                    url,
                ]
            )
    return out


def parse_nominais(rows: list[list], dossie: str, url: str) -> list[list]:
    """'Evolução das taxas nominais em IRC': mainland rates first, then a
    block per autonomous region; the exceptional rates are left out."""
    out, reg, cols = [], "Continente", None
    for r in rows:
        cells = _cells(r)
        if not cells:
            continue
        yc = year_cols(r)
        if yc:
            cols = yc
            continue
        label = _label(r)
        n = fold(label)
        if "EXCECIONAIS" in n or "EXCEPCIONAIS" in n:
            break
        if len(cells) == 1:
            if "ACORES" in n or "MADEIRA" in n:
                reg = regiao(label)
            continue
        if not cols:
            continue
        for y, i in cols.items():
            v = num(r[i]) if i < len(r) else None
            if v is None:
                continue
            out.append(
                [
                    NOMINAIS,
                    "Taxa",
                    y,
                    reg,
                    label,
                    _valor(v, "%", 1),
                    "%",
                    dossie,
                    url,
                ]
            )
    return out


def parse_irc(sheets: dict[str, list[list]], dossie: str, url: str):
    """(at_irc rows, at_distritos rows) of one IRC edition."""
    irc, dist = [], []
    for raw in sheets.values():
        head = _head(raw, 10)  # older editions spread the title over rows
        h = fold(head)
        if "DERRAMA ESTADUAL" in h:
            irc += parse_derrama(raw, dossie, url)
        elif "TAXAS NOMINAIS" in h:
            irc += parse_nominais(raw, dossie, url)
        elif "CALCULO DO IMPOSTO" in h:
            irc += parse_calculo(raw, dossie, url)
        else:
            medida, unidade = _irc_medida(head)
            if medida:
                dist += [
                    r + [dossie, url]
                    for r in parse_distritos(
                        raw, "IRC", medida, unidade, _escala(head)
                    )
                ]
    return irc, dist


# -------------------------------------------------------------------------


def load(data: bytes) -> dict[str, list[list]]:
    """The sheets of a workbook, cells in place (None where empty)."""
    import openpyxl  # only this script needs it (pip install openpyxl)

    wb = openpyxl.load_workbook(
        io.BytesIO(data), read_only=True, data_only=True
    )
    out = {}
    for ws in wb.worksheets:
        rows = []
        for r in ws.iter_rows(values_only=True):
            r = list(r)
            while r and r[-1] in (None, ""):
                r.pop()
            rows.append(r)
        out[ws.title] = rows
    return out


def merge(editions: list[list[list]], key, cover) -> list[list]:
    """Newest edition wins: an edition replaces every value of the
    (table, year)s it covers. editions are oldest first."""
    best: dict[tuple, list] = {}
    for rows in editions:
        covered = {cover(r) for r in rows}
        best = {k: v for k, v in best.items() if cover(v) not in covered}
        for r in rows:
            best[key(r)] = r
    return list(best.values())


def write_csv(path: Path, cols: list[str], rows: list[list]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        w.writerows(rows)


def read_editions(imposto: str, cache: Path | None):
    page = get(PAGINAS[imposto]).decode("utf-8", "replace")
    urls = dossies(page, imposto)
    for dossie in sorted(urls):  # oldest first
        path = cache / f"{imposto.lower()}_{dossie}.xlsx" if cache else None
        if path and path.exists():
            data = path.read_bytes()
        else:
            time.sleep(2)  # one request at a time, gently
            data = get(urls[dossie])
            if path:
                path.write_bytes(data)
        yield dossie, urls[dossie], load(data)


def main(
    data_dir: Path, cache: Path | None = None, today: dt.date | None = None
) -> int:
    today = today or dt.date.today()
    eds: dict[str, list] = {"IRS": [], "IRC": []}
    dist_eds: dict[str, list] = {"IRS": [], "IRC": []}
    for imposto, parse in (("IRS", parse_irs), ("IRC", parse_irc)):
        for dossie, url, sheets in read_editions(imposto, cache):
            own, dist = parse(sheets, dossie, url)
            print(f"{imposto} {dossie}: {len(own)} + {len(dist)} por distrito")
            if not own or not dist:
                print(f"{imposto} {dossie}: tables not found", file=sys.stderr)
                return 1
            eds[imposto].append(own)
            dist_eds[imposto].append(dist)
        if not eds[imposto]:
            print(f"No {imposto} dossier on the AT page", file=sys.stderr)
            return 1
    irs = merge(
        eds["IRS"],
        key=lambda r: (r[0], r[1], r[2], r[3], r[4], r[6]),
        cover=lambda r: (r[0], r[1], r[2]),
    )
    irc = merge(
        eds["IRC"],
        key=lambda r: (r[0], r[1], r[2], r[3], r[4], r[6]),
        cover=lambda r: (r[0], r[2], r[6]),
    )
    dist = []
    for imposto in ("IRS", "IRC"):
        dist += merge(
            dist_eds[imposto],
            key=lambda r: (r[0], r[1], r[2], r[3], r[4]),
            cover=lambda r: (r[0], r[1], r[2], r[3]),
        )
    newest = min(max(r[2] for r in irs), max(r[2] for r in irc))
    if today.year - newest > MAX_IDADE:
        print(f"Newest year is too old: {newest}", file=sys.stderr)
        return 1
    data_dir.mkdir(parents=True, exist_ok=True)
    irs.sort(key=lambda r: (r[0], r[1], r[2], r[3], r[4]))
    irc.sort(key=lambda r: (r[0], r[6], r[2], r[3], str(r[4])))
    dist.sort(key=lambda r: (r[0], r[1], r[2], r[3], r[5], r[4]))
    write_csv(data_dir / "at_irs.csv", COLS, irs)
    write_csv(data_dir / "at_irc.csv", IRC_COLS, irc)
    write_csv(data_dir / "at_distritos.csv", DIST_COLS, dist)
    print(
        f"{len(irs)} IRS, {len(irc)} IRC, {len(dist)} por distrito, "
        f"até {newest} -> {data_dir}"
    )
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    cache = None
    if "--cache" in args:
        i = args.index("--cache")
        cache = Path(args[i + 1])
        cache.mkdir(parents=True, exist_ok=True)
        del args[i : i + 2]
    sys.exit(main(Path(args[0] if args else "data"), cache))
