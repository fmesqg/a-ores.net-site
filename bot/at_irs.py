"""AT: IRS by tax bracket in the Azores, Madeira and the mainland.

Usage:
  python3 bot/at_irs.py [data_dir] [--cache DIR]   rewrite data_dir/at_irs.csv

Every spring (late March to mid April) the Autoridade Tributária publishes
the "Dossier Estatístico" of the IRS returns (Modelo 3) for the last three
years, one Excel file per edition, on

  https://info.portaldasfinancas.gov.pt/pt/dgci/divulgacao/estatisticas/estatisticas_ir/Pages/estatisticas_irs.aspx

Two kinds of table are read, found by their content and not by their
number (the "Mapa" numbers change between editions):

  Taxas de Tributação por Circunscrições Administrativas
      one table per year (the two newest years of each edition) and per
      measure: households (Número de Agregados), income taxed at the
      general rates (Rendimento Englobado) and tax assessed (IRS
      Liquidado), by bracket, for the mainland (C), the Azores (A) and
      Madeira (M), split into married / not married / total. The bracket
      is the tax rate actually applied, so the Azores rows carry the
      regional rates (30% below the mainland's since 2021).
  Taxa Adicional de Solidariedade
      households and tax assessed at the additional solidarity rate (80 to
      250 thousand euros, above 250 thousand), by region, three years per
      edition.

Every edition back to 2015-2017 (.xlsx) is read; a year that appears in two
editions keeps the newest one, since the AT revises the older years. The
amounts are in millions of euros in the files and are written in euros.
Read the Notas Prévias before using the numbers: households are counted
where the taxpayer lives, and the "Rendimento Englobado" leaves out income
taxed at special rates.

.github/workflows/at_irs.yml runs this weekly in April and May, and monthly
otherwise. main() fails, so the workflow emails, when no edition can be
read or the newest year is more than ~2.5 years old.
"""

import csv
import datetime as dt
import io
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

SITE = "https://info.portaldasfinancas.gov.pt"
PAGINA = (
    SITE + "/pt/dgci/divulgacao/estatisticas/estatisticas_ir/Pages/"
    "estatisticas_irs.aspx"
)
UA = "acores.net open data (github.com/fmesqg/a-ores.net-site)"
XLSX_RE = re.compile(r'href="([^"]*IRS[^"]*\.xlsx)"', re.I)
EDICAO_RE = re.compile(r"(20\d\d)\D{1,3}(20\d\d)")
REGIAO_RE = re.compile(r"^[A-Z]\s*-\s*(CONTINENTE|AÇORES|MADEIRA)\s*$", re.I)
REGIOES = {
    "CONTINENTE": "Continente",
    "AÇORES": "Açores",
    "MADEIRA": "Madeira",
}
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
TAXAS = "Taxas de tributação"
ADICIONAL = "Taxa adicional de solidariedade"


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def dossies(page: str) -> dict[str, str]:
    """{edition "2022-2024": url}. The 2022-2024 file is called
    Notas_Previas_..., so editions are told apart by their years."""
    out = {}
    for href in XLSX_RE.findall(page):
        name = urllib.parse.unquote(href.rsplit("/", 1)[-1])
        # the 2016-2018 file has no years in its name, only in its folder
        m = EDICAO_RE.search(name) or EDICAO_RE.search(
            urllib.parse.unquote(href)
        )
        if not m or int(m[2]) - int(m[1]) != 2:
            continue
        out[f"{m[1]}-{m[2]}"] = urllib.parse.urljoin(SITE, href)
    return out


def _cells(row) -> list:
    return [c for c in row if c not in (None, "")]


def _medida(text: str) -> str:
    t = text.lower()
    if "agregados" in t:
        return "Agregados"
    if "liquidado" in t:
        return "IRS liquidado"
    if "rendimento" in t:
        return "Rendimento englobado"
    return ""


def _escala(text: str) -> float:
    t = text.lower()
    if "milhões" in t or "milhoes" in t:
        return 1e6
    if "milhares" in t:
        return 1e3
    return 1.0


def parse_taxas(rows: list[list], dossie: str, url: str) -> list[list]:
    """One 'Taxas de Tributação' sheet: year, then a block per region."""
    medida, ano, regiao, escala, ordem, out = "", None, "", 1.0, 0, []
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
                regiao, ordem = REGIOES[m[1].upper()], 0
                escala = 1.0 if medida == "Agregados" else 1e6
            continue
        if isinstance(first, int) and 2000 <= first <= 2100 and len(r) == 1:
            ano = first
            continue
        nums = [x for x in r if isinstance(x, int | float)]
        if not (regiao and ano and medida) or len(nums) < 4:
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
                    regiao,
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
    medida, regiao, anos, escala, ordem, out = "", "", [], 1.0, 0, []
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
            regiao, anos, ordem = first.strip().capitalize(), [], 0
            escala = 1.0 if medida == "Agregados" else 1e6
            continue
        years = [x for x in r[1:] if isinstance(x, int) and 2000 <= x <= 2100]
        if years:
            anos = years
            continue
        if not (regiao and anos and medida) or low.startswith("total"):
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
                    regiao,
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


def parse_book(sheets: dict[str, list[list]], dossie: str, url: str):
    out = []
    for rows in sheets.values():
        head = " ".join(str(c) for r in rows[:3] for c in r)
        if "Taxa Adicional" in head:
            out += parse_adicional(rows, dossie, url)
        elif "Taxas de Tributação" in head and any(
            r and isinstance(r[0], str) and REGIAO_RE.match(r[0].strip())
            for r in rows
        ):
            out += parse_taxas(rows, dossie, url)
    return out


def load(data: bytes) -> dict[str, list[list]]:
    import openpyxl  # only this script needs it (pip install openpyxl)

    wb = openpyxl.load_workbook(
        io.BytesIO(data), read_only=True, data_only=True
    )
    return {
        ws.title: [_cells(r) for r in ws.iter_rows(values_only=True)]
        for ws in wb.worksheets
        if ws.title.lower().startswith("mapa")
    }


def main(
    data_dir: Path, cache: Path | None = None, today: dt.date | None = None
) -> int:
    today = today or dt.date.today()
    urls = dossies(get(PAGINA).decode("utf-8", "replace"))
    if not urls:
        print("No IRS dossier on the AT page", file=sys.stderr)
        return 1
    best: dict[tuple, list] = {}
    for dossie in sorted(urls):  # oldest first: newer editions overwrite
        path = cache / f"irs_{dossie}.xlsx" if cache else None
        if path and path.exists():
            data = path.read_bytes()
        else:
            time.sleep(2)  # one request at a time, gently
            data = get(urls[dossie])
            if path:
                path.write_bytes(data)
        rows = parse_book(load(data), dossie, urls[dossie])
        print(f"{dossie}: {len(rows)} valores")
        if not rows:
            print(f"{dossie}: nothing read", file=sys.stderr)
            return 1
        # a newer edition replaces every value of the years it covers
        covered = {(r[0], r[1], r[2]) for r in rows}
        best = {k: v for k, v in best.items() if k[:3] not in covered}
        for r in rows:
            best[(r[0], r[1], r[2], r[3], r[4], r[6])] = r
    out = sorted(best.values(), key=lambda r: (r[0], r[1], r[2], r[3], r[4]))
    newest = max(r[2] for r in out)
    if today.year - newest > MAX_IDADE:
        print(f"Newest year is too old: {newest}", file=sys.stderr)
        return 1
    data_dir.mkdir(parents=True, exist_ok=True)
    with open(data_dir / "at_irs.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLS)
        w.writerows(out)
    print(f"{len(out)} valores, até {newest} -> {data_dir / 'at_irs.csv'}")
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
