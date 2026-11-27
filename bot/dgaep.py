"""DGAEP: emprego público nos Açores (SIOE), trimestre a trimestre.

Usage:
  python3 bot/dgaep.py [data_dir]   rewrite data_dir/emprego_publico.csv

Every quarter the Direção-Geral da Administração e do Emprego Público
(DGAEP) publishes the Síntese Estatística do Emprego Público (SIEP), built
from the SIOE (Sistema de Informação da Organização do Estado), on

  https://www.dgaep.gov.pt/index.cfm?OBJID=ECA5D4CB-42B8-4692-A96C-8AAD63010A54

with an Excel file of tables that carry the whole series since 2011. Read
here, from the newest file:

  Q1.1   jobs in the Azores regional administration, by regional
         department (secretaria regional), with the Madeira regional
         administration and all of general government for comparison
  Q1.7   jobs in general government located in the Azores (State, Region
         and municipalities), by career (teachers, nurses, ...), and the
         national total
  Q1.9   mean monthly base pay and mean monthly earnings in the Azores
         regional administration, by department, against all of general
         government and Madeira (full-time workers)
  Q1.13  the same pay, for everybody working for general government in
         each NUTS I region (Total row only)

"Setor das administrações públicas" follows national accounts, so the
regional hospitals (EPE) and other companies the INE counts inside general
government are in; SATA, EDA and the other market companies are not (and,
says the DGAEP, the Region's companies do not report to the SIOE: see the
CFP data, bot/cfp.py). data/emprego_publico.csv is rewritten from the
newest file, which revises older quarters; .github/workflows/dgaep.yml runs
this weekly and main() fails, so the workflow emails, when the file cannot
be found or read or its newest quarter is too old.
"""

import csv
import datetime as dt
import html
import io
import re
import sys
import urllib.request
from pathlib import Path

PAGINA = (
    "https://www.dgaep.gov.pt/index.cfm?"
    "OBJID=ECA5D4CB-42B8-4692-A96C-8AAD63010A54"
)
UA = "acores.net open data (github.com/fmesqg/a-ores.net-site)"
XLSX_RE = re.compile(r'href="([^"]*siep_(\d{4})_t(\d)[^"]*\.xlsx)"', re.I)

COLS = [
    "quadro",
    "indicador",
    "ordem",
    "rubrica",
    "local",
    "data",
    "valor",
    "unidade",
    "provisorio",
    "ficheiro",
    "pagina",
]

MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()
NUTS = {
    "PORTUGAL": "Portugal",
    "CONTINENTE": "Continente",
    "R.A. DOS AÇORES": "Açores",
    "R.A. DA MADEIRA": "Madeira",
}
PAGA = {
    "REMUNERAÇÃO BASE MÉDIA MENSAL": "Remuneração base média mensal",
    "GANHO MÉDIO MENSAL": "Ganho médio mensal",
    "RBMM": "Remuneração base média mensal",
    "GMM": "Ganho médio mensal",
}

Rows = list[tuple]


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def latest_file(page: str) -> str:
    """The newest SIEP Excel linked from the page (by year and quarter)."""
    found = {
        (int(y), int(q)): html.unescape(u) for u, y, q in XLSX_RE.findall(page)
    }
    if not found:
        return ""
    url = found[max(found)]
    return url if url.startswith("http") else "https://www.dgaep.gov.pt/" + url


def load(data: bytes) -> dict[str, Rows]:
    import openpyxl

    wb = openpyxl.load_workbook(
        io.BytesIO(data), read_only=True, data_only=True
    )
    return {
        ws.title.strip(): [tuple(r) for r in ws.iter_rows(values_only=True)]
        for ws in wb.worksheets
    }


def text(v) -> str:
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""


def number(v) -> float | None:
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, int | float):
        return float(v)
    return None


def cell(r: tuple, j: int):
    return r[j] if j < len(r) else None


def when(label: str, year: int | None = None) -> tuple[str, bool]:
    """'31 dez 2023', '30 set 2026 (p)', '31 dez' (+ year), 'abril 2024',
    'julho (p)' (+ year) -> (ISO date, provisional). Pay is surveyed in a
    month: the first day stands for it."""
    s = text(label).lower()
    prov = "(p)" in s
    s = s.replace("(p)", " ").strip()
    m = re.match(r"(\d{1,2})\s*([a-zç]{3})[a-zç]*\.?\s*(\d{4})?$", s)
    if m and m.group(2) in MESES:
        y = int(m.group(3)) if m.group(3) else year
        if y:
            return (
                f"{y}-{MESES.index(m.group(2)) + 1:02d}-{int(m.group(1)):02d}",
                prov,
            )
    m = re.match(r"([a-zç]+)\s*(\d{4})?$", s)
    if m and m.group(1)[:3] in MESES:
        y = int(m.group(2)) if m.group(2) else year
        if y:
            return f"{y}-{MESES.index(m.group(1)[:3]) + 1:02d}-01", prov
    return "", prov


def find_row(rows: Rows, test) -> int:
    return next((i for i, r in enumerate(rows) if test(r)), -1)


def is_change(v) -> bool:
    """The variation columns that follow the levels."""
    return bool(re.match(r"(VT|VH|Varia)", text(v), re.I))


def clean(label) -> str:
    """Without the footnote marks: 'Entid. Reclassif. (ii)', 'Total:'."""
    s = re.sub(r"\s*\((?:[ivx]+|[a-f]|\*)\)\s*$", "", text(label))
    return s.rstrip(":").strip()


def out_row(
    quadro, indicador, ordem, rubrica, local, data, valor, unidade, prov
):
    return {
        "quadro": quadro,
        "indicador": indicador,
        "ordem": ordem,
        "rubrica": rubrica,
        "local": local,
        "data": data,
        "valor": int(valor) if valor == int(valor) else round(valor, 2),
        "unidade": unidade,
        "provisorio": "p" if prov else "",
    }


def azores_block(rows: Rows, start: int) -> list[int]:
    """Row indices from the "...REGIONAL DOS AÇORES" heading to the row
    before the Madeira one."""
    out = []
    for i in range(start, len(rows)):
        lab = text(cell(rows[i], 1)).upper()
        if i > start and (
            "MADEIRA" in lab or lab.startswith("ADMINISTRAÇÃO LOCAL")
        ):
            break
        out.append(i)
    return out


def parse_q11(book: dict[str, Rows]) -> list[dict]:
    """Q1.1: jobs by subsector and department, at the end of each quarter."""
    rows = book.get("Q1.1")
    if not rows:
        return []
    top = find_row(rows, lambda r: any(text(c) == "EMPREGO" for c in r))
    if top < 0:
        return []
    first = next(j for j, c in enumerate(rows[top]) if text(c) == "EMPREGO")
    last = next(
        (j for j in range(first + 1, len(rows[top])) if text(rows[top][j])),
        len(rows[top]),
    )
    years, days = rows[top + 1], rows[top + 2]
    cols, year = {}, None
    for j in range(first, last):
        if re.match(r"\d{4}$", text(cell(years, j))):
            year = int(text(cell(years, j)))
        d, prov = when(cell(days, j), year)
        if d:
            cols[j] = (d, prov)
    keep = []
    az = find_row(
        rows,
        lambda r: text(cell(r, 1)).upper()
        == "ADMINISTRAÇÃO REGIONAL DOS AÇORES",
    )
    if az >= 0:
        keep += [(i, "Açores") for i in azores_block(rows, az)]
    for i, r in enumerate(rows):
        lab = text(cell(r, 1))
        if lab.upper() == "ADMINISTRAÇÕES PÚBLICAS":
            keep.append((i, "Portugal"))
        elif lab.upper() == "ADMINISTRAÇÃO REGIONAL DA MADEIRA":
            keep.append((i, "Madeira"))
        elif "Segurança Social da Adm. Regional dos Açores" in lab:
            keep.append((i, "Açores"))
    out = []
    for i, local in keep:
        r = rows[i]
        for j, (d, prov) in cols.items():
            v = number(cell(r, j))
            if v is not None:
                out.append(
                    out_row(
                        "Q1.1",
                        "Postos de trabalho",
                        i,
                        clean(cell(r, 1)),
                        local,
                        d,
                        v,
                        "postos de trabalho",
                        prov,
                    )
                )
    return out


def parse_q17(book: dict[str, Rows]) -> list[dict]:
    """Q1.7: jobs by career in each NUTS I region; the Azores column for
    every career and Portugal for the total."""
    rows = book.get("Q1.7")
    if not rows:
        return []
    nuts = find_row(
        rows, lambda r: any(text(c) == "R.A. DOS AÇORES" for c in r)
    )
    if nuts < 0:
        return []
    dates = rows[nuts - 1]
    cols, cur = {}, ("", False)
    for j, c in enumerate(rows[nuts]):
        if text(cell(dates, j)):
            if is_change(cell(dates, j)):
                break
            cur = when(cell(dates, j))
        local = NUTS.get(text(c))
        if cur[0] and local in ("Açores", "Portugal"):
            cols[j] = (local, *cur)
    out = []
    for i in range(nuts + 1, len(rows)):
        r = rows[i]
        lab = clean(cell(r, 1))
        if not lab or lab.startswith(("Fonte", "Nota")):
            if lab:
                break
            continue
        for j, (local, d, prov) in cols.items():
            if local == "Portugal" and lab != "Total":
                continue
            v = number(cell(r, j))
            if v is not None:
                out.append(
                    out_row(
                        "Q1.7",
                        "Postos de trabalho nas administrações públicas, por carreira",
                        i,
                        lab,
                        local,
                        d,
                        v,
                        "postos de trabalho",
                        prov,
                    )
                )
    return out


def parse_q19(book: dict[str, Rows]) -> list[dict]:
    """Q1.9: mean base pay and mean earnings by subsector and department."""
    rows = book.get("Q1.9")
    if not rows:
        return []
    top = find_row(rows, lambda r: any(text(c) in PAGA for c in r))
    if top < 0:
        return []
    years, months = rows[top + 1], rows[top + 2]
    cols, ind, year = {}, "", None
    for j in range(len(rows[top])):
        if text(cell(rows[top], j)) in PAGA:
            ind = PAGA[text(cell(rows[top], j))]
        if is_change(cell(years, j)):
            continue  # each block ends with its variation columns
        if re.match(r"\d{4}$", text(cell(years, j))):
            year = int(text(cell(years, j)))
        d, prov = when(cell(months, j), year)
        if ind and d:
            cols[j] = (ind, d, prov)
    keep = []
    az = find_row(
        rows,
        lambda r: text(cell(r, 1)).upper()
        == "ADMINISTRAÇÃO REGIONAL DOS AÇORES",
    )
    if az >= 0:
        keep += [(i, "Açores") for i in azores_block(rows, az)]
    for i, r in enumerate(rows):
        lab = text(cell(r, 1)).upper()
        if lab == "ADMINISTRAÇÕES PÚBLICAS":
            keep.append((i, "Portugal"))
        elif lab == "ADMINISTRAÇÃO REGIONAL DA MADEIRA":
            keep.append((i, "Madeira"))
    out = []
    for i, local in keep:
        r = rows[i]
        for j, (ind, d, prov) in cols.items():
            v = number(cell(r, j))
            if v is not None:
                out.append(
                    out_row(
                        "Q1.9",
                        ind,
                        i,
                        clean(cell(r, 1)),
                        local,
                        d,
                        v,
                        "€",
                        prov,
                    )
                )
    return out


def parse_q113(book: dict[str, Rows]) -> list[dict]:
    """Q1.13: mean base pay and earnings of everybody working for general
    government in each NUTS I region (the Total row)."""
    rows = book.get("Q1.13")
    if not rows:
        return []
    nuts = find_row(
        rows, lambda r: any(text(c) == "R.A. DOS AÇORES" for c in r)
    )
    if nuts < 0:
        return []
    dates, kinds = rows[nuts - 1], rows[nuts + 1]
    cols, cur, local = {}, ("", False), None
    for j in range(len(rows[nuts])):
        if text(cell(dates, j)):
            if is_change(cell(dates, j)):
                break
            cur = when(cell(dates, j))
        if text(cell(rows[nuts], j)):
            local = NUTS.get(text(cell(rows[nuts], j)))
        ind = PAGA.get(text(cell(kinds, j)))
        if cur[0] and local and ind:
            cols[j] = (local, ind, *cur)
    i = find_row(rows, lambda r: clean(cell(r, 1)) == "Total")
    if i < 0:
        return []
    out = []
    for j, (local, ind, d, prov) in cols.items():
        v = number(cell(rows[i], j))
        if v is not None:
            out.append(
                out_row("Q1.13", ind, i, "Total", local, d, v, "€", prov)
            )
    return out


def parse(book: dict[str, Rows]) -> list[dict]:
    return (
        parse_q11(book) + parse_q17(book) + parse_q19(book) + parse_q113(book)
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    rows = sorted(
        rows,
        key=lambda r: (
            r["quadro"],
            r["indicador"],
            r["local"],
            r["ordem"],
            r["data"],
        ),
    )
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main(out_dir: Path, today: dt.date | None = None) -> int:
    today = today or dt.date.today()
    url = latest_file(get(PAGINA).decode("utf-8", "replace"))
    if not url:
        print("no SIEP Excel linked from", PAGINA, file=sys.stderr)
        return 1
    rows = parse(load(get(url)))
    quadros = {r["quadro"] for r in rows}
    if quadros != {"Q1.1", "Q1.7", "Q1.9", "Q1.13"}:
        print(f"{url}: only {sorted(quadros)} could be read", file=sys.stderr)
        return 1
    newest = max(r["data"] for r in rows if r["quadro"] == "Q1.1")
    # one edition a quarter, about 45 days after it ends
    if dt.date.fromisoformat(newest) < today - dt.timedelta(days=200):
        print(f"{url}: newest quarter is {newest}", file=sys.stderr)
        return 1
    for r in rows:
        r["ficheiro"], r["pagina"] = url, PAGINA
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "emprego_publico.csv", rows)
    print(f"{url}: {len(rows)} valores, último trimestre {newest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "data")))
