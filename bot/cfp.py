"""CFP: Sector Empresarial Regional dos Açores (SERAA), empresa a empresa.

Usage:
  python3 bot/cfp.py [data_dir]          add new CFP reports to data_dir/sper*.csv
  python3 bot/cfp.py [data_dir] --tudo   download and parse every report again

Once a year the Conselho das Finanças Públicas (CFP) publishes a report on
the regional public business sectors (Relatório n.º 13/2024 "Sector
Empresarial Regional 2022-2023"; n.º 9/2025 "Sector Empresarial do Estado e
Regional 2023-2024", ...). Each report page on

  https://www.cfp.pt/pt/publicacoes/sectores-das-administracoes-publicas

links two Excel files read here:

  fichas individuais  one sheet per company: workers, turnover, costs,
                      balance sheet, cash flows, GVA, EBITDA, net income and
                      ratios for the two years of the report, from each
                      company's annual accounts
  data series (-ds)   the report's tables; from it come the list of
                      companies (share held by the Region, shareholder, CAE,
                      whether it is counted inside general government
                      "EPR"), the weight of the sector in the regional
                      economy and the Region's net financial effort with
                      its companies

and three CSVs are written (all committed):

  sper.csv           one row per company, year and indicator (euros, people
                     or ratios); a later report wins for the same year
  sper_empresas.csv  the list of companies, as each report gives it
  sper_regiao.csv    weight in the economy and net financial effort, per
                     report: the CFP changed the method between reports
                     (from 9/2025 transfers to the three hospitals are
                     left out of the financial effort), so these are not
                     merged across reports

Only the Azores (SERAA) is kept: the companies listed between the "SERAA"
and "SERAM" headings of the list table. Cells are read by position because
the tables leave the Azores columns empty where only Madeira has a value.
.github/workflows/cfp.yml runs this weekly; main() fails when the report
expected by now is missing or cannot be read, so the workflow emails.
"""

import csv
import datetime as dt
import html
import io
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

SITE = "https://www.cfp.pt"
LISTA = SITE + "/pt/publicacoes/sectores-das-administracoes-publicas"
UA = "acores.net open data (github.com/fmesqg/a-ores.net-site)"
PAUSE = 1.0

REPORT_RE = re.compile(
    r'href="((?:https://www\.cfp\.pt)?/pt/publicacoes/'
    r"sectores-das-administracoes-publicas/"
    r'sector-empresarial-[a-z-]*regional-(\d{4})-(\d{4}))"'
)
NUMBER_RE = re.compile(r"rel[-_]0*(\d+)[-_](\d{4})", re.I)

COLS = [
    "relatorio",
    "ano",
    "sigla",
    "empresa",
    "ordem",
    "indicador",
    "valor",
    "unidade",
    "fonte",
    "url",
    "ficheiro",
]
ECOLS = [
    "relatorio",
    "ordem",
    "sigla",
    "empresa",
    "cae",
    "participacao",
    "acionista",
    "ap",
    "nota",
    "url",
]
RCOLS = [
    "relatorio",
    "quadro",
    "ordem",
    "grupo",
    "rubrica",
    "ano",
    "valor",
    "unidade",
    "nota",
    "url",
]
KEY = ("sigla", "ano", "indicador")

PESSOAS = {"Número de Trabalhadores"}
RACIOS = {
    "Desempenho Operacional",
    "Liquidez Geral",
    "Autonomia Financeira",
    "Solvabilidade",
    "Endividamento",
    "Rendibilidade das Vendas",
    "Rendibilidade do Ativo",
    "Rendibilidade dos Capitais Próprios",
    "Rotação do Ativo",
    "Rotação dos Capitais Próprios",
}
PESO = "Peso na economia"
ESFORCO = "Esforço financeiro líquido da Região"


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    time.sleep(PAUSE)
    return data


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def names(*texts: str, loose: bool = False) -> list[str]:
    """Keys a company can be matched by: the 2022-2023 fichas say
    "Atlânticoline, S.A." or "HDES, E.P.E.R." where the list says "Atlântico
    Line, S.A." or "HDES - Hospital Divino Espirito Santo, E.P.E.R.". The
    loose key (the part before " - ") is tried last, because "Sata - Gestão
    de Aeródromos" would otherwise take the key of "SATA" (Air Açores)."""
    out = []
    for t in texts:
        parts = [t.split(" - ")[0]] if loose else [t, t.split(",")[0]]
        for part in parts:
            part = re.sub(r"\s+(Lda|S\.A|E\.P\.E\.R)\.?$", "", part.strip())
            if fold(part) and fold(part) not in out:
                out.append(fold(part))
    return out


def match(lista: list[dict], *texts: str) -> dict | None:
    """The list entry for a ficha: exact keys on both sides first."""
    ficha = (names(*texts), names(*texts, loose=True))
    for f, loose in ((0, False), (0, True), (1, False)):
        for e in lista:
            if set(ficha[f]) & set(
                names(e["empresa"], e["sigla"], loose=loose)
            ):
                return e
    return None


def clean(s) -> str:
    """Label without footnote marks: 'Dividendos*' -> 'Dividendos',
    'Açores(b)' -> 'Açores', 'Receitas provenientes do SER (1)' kept."""
    s = re.sub(r"\s+", " ", str(s)).strip()
    s = re.sub(r"\s*(\*+|\([a-z*]\))$", "", s)
    return s.rstrip(":").strip()


def year(v) -> int | None:
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    if isinstance(v, int) and 1990 < v < 2100:
        return v
    if isinstance(v, str) and re.fullmatch(r"\s*(19|20)\d\d\s*", v):
        return int(v)
    return None


def number(v) -> float | None:
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, int | float):
        return float(v)
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


def num_text(x: float) -> str:
    x = round(x, 6)
    return str(int(x)) if x.is_integer() else repr(x)


# --- the website --------------------------------------------------------


def reports(page: str) -> list[dict]:
    """Report pages on the CFP listing, oldest first."""
    out: dict[str, dict] = {}
    for m in REPORT_RE.finditer(page):
        url = m.group(1)
        if url.startswith("/"):
            url = SITE + url
        out[url] = {"url": url, "de": int(m.group(2)), "ate": int(m.group(3))}
    return sorted(out.values(), key=lambda r: r["ate"])


def files(page: str) -> dict:
    """The two Excel files and the report number on a report page."""
    hrefs = [html.unescape(h) for h in re.findall(r'href="([^"]+)"', page)]
    hrefs = [SITE + h if h.startswith("/") else h for h in hrefs]
    xlsx = [h for h in hrefs if h.lower().endswith(".xlsx")]
    out = {
        "fichas": next((h for h in xlsx if "ficha" in h.lower()), ""),
        "series": next(
            (h for h in xlsx if h.lower().endswith("-ds.xlsx")), ""
        ),
        "numero": "",
    }
    for h in hrefs:
        m = NUMBER_RE.search(h.rsplit("/", 1)[-1])
        if m and h.lower().endswith(".pdf"):
            out["numero"] = f"{int(m.group(1))}/{m.group(2)}"
            break
    return out


# --- the workbooks ------------------------------------------------------
# Parsers take a workbook as {sheet name: list of rows (tuples of cells)},
# so tests do not need openpyxl.


def load(data: bytes) -> dict[str, list[tuple]]:
    import openpyxl

    wb = openpyxl.load_workbook(
        io.BytesIO(data), read_only=True, data_only=True
    )
    return {ws.title: list(ws.iter_rows(values_only=True)) for ws in wb}


def find_sheet(book: dict, title: str) -> list[tuple]:
    """The sheet whose title cell (first rows) starts with `title`."""
    want = fold(title)
    for rows in book.values():
        for r in rows[:4]:
            for c in r:
                if isinstance(c, str) and fold(c).find(want) != -1:
                    return rows
    return []


def parse_lista(book: dict) -> list[dict]:
    """The SERAA part of the "Lista de empresas do SER" table, with the
    Portuguese footnotes (a), b), ...) attached to their companies."""
    rows = find_sheet(book, "Lista de empresas do SER")
    out, notas, inside, pt_notes = [], {}, False, False
    for r in rows:
        cells = [c for c in r if c is not None]
        if not cells:
            continue
        first = str(cells[0]).strip()
        if "(SERAA)" in first or first.endswith("SERAA"):
            inside = True
            continue
        if "SERAM" in first:
            inside = False
            continue
        if first.startswith("Notas"):
            pt_notes = True
        elif first.startswith("Notes"):
            pt_notes = False
        if pt_notes:
            m = re.match(r"([a-z])\)\s*(.+)", first)
            if m and m.group(1) not in notas:
                notas[m.group(1)] = m.group(2).strip()
            continue
        if not inside or not isinstance(cells[0], int | float):
            continue
        # by position: #, nome, sigla, participação, acionista, AP, CAE, obs
        r = list(r) + [None] * 10
        i = next(i for i, c in enumerate(r) if c is not None)
        nome, sigla, part, acion, ap, cae, obs = r[i + 1 : i + 8]
        out.append(
            {
                "ordem": int(cells[0]),
                "empresa": clean(nome),
                "sigla": clean(sigla),
                "participacao": number(part),
                "acionista": clean(acion or ""),
                "ap": "sim" if str(ap or "").strip().startswith("EPR") else "",
                "cae": clean(cae or ""),
                "obs": clean(obs or "").rstrip(")"),
            }
        )
    for e in out:
        e["nota"] = notas.get(e.pop("obs"), "")
    return out


def parse_ficha(rows: list[tuple]) -> dict | None:
    """One company sheet: {'empresa', 'fonte', 'valores': [(ano,
    indicador, valor), ...]} or None if the sheet is not a ficha."""
    if not rows or not any(
        isinstance(c, str) and "Ficha" in c for r in rows[:2] for c in r
    ):
        return None
    empresa, years, fonte, valores, ordem = "", {}, "", [], 0
    for r in rows[1:]:
        cells = [(j, c) for j, c in enumerate(r) if c is not None]
        if not cells:
            continue
        ys = {j: year(c) for j, c in cells if year(c)}
        if len(ys) >= 2 and not years:
            years = ys
            continue
        label = cells[0][1]
        if not isinstance(label, str) or "Ficha" in label:
            continue
        if not empresa:
            empresa = clean(label)
            continue
        if label.startswith("Fonte"):
            fonte = clean(label)
            continue
        if not years:
            continue
        ind = clean(label)
        got = False
        for j, y in years.items():
            v = number(r[j]) if j < len(r) else None
            if v is not None:
                valores.append((y, ordem, ind, v))
                got = True
        ordem += got
    if not empresa or not valores:
        return None
    return {"empresa": empresa, "fonte": fonte, "valores": valores}


def unidade(ind: str) -> str:
    if ind in PESSOAS:
        return "pessoas"
    if ind in RACIOS:
        return "rácio"
    return "€"


def table_years(rows: list[tuple], start: int) -> tuple[int, dict]:
    """First row from `start` with at least two years: (row index,
    {column: year}) for the first two year columns (the Azores ones)."""
    for i in range(start, len(rows)):
        ys = [(j, year(c)) for j, c in enumerate(rows[i]) if year(c)]
        if len(ys) >= 2:
            return i, dict(ys[:2])
    return -1, {}


def note(rows: list[tuple]) -> str:
    """The Portuguese source + notes line under a table."""
    for r in rows:
        for c in r:
            if isinstance(c, str) and c.startswith("Fonte"):
                return re.sub(r"\s+", " ", c.split("Sources:")[0]).strip()
    return ""


def parse_esforco(book: dict) -> list[dict]:
    rows = find_sheet(book, "Esforço financeiro líquido das R")
    hdr, years = table_years(rows, 0)
    if hdr < 0:
        return []
    out, ordem = [], 0
    for r in rows[hdr + 1 :]:
        label = next((c for c in r if isinstance(c, str)), None)
        if label is None or label.startswith(("Fonte", "Source")):
            if label:
                break
            continue
        if label.strip() in ("M€", "%"):
            continue
        rub = clean(label)
        pct = "PIB" in rub
        for j, y in years.items():
            v = number(r[j]) if j < len(r) else None
            if v is None:
                continue
            out.append(
                {
                    "quadro": ESFORCO,
                    "ordem": ordem,
                    "grupo": "",
                    "rubrica": rub,
                    "ano": y,
                    "valor": v * 100 if pct else v,
                    "unidade": "% do PIB" if pct else "M€",
                }
            )
        ordem += 1
    if out:
        out[0]["nota"] = note(rows)
    return out


AZORES = re.compile(r"\bSERAA\b|\bRAA\b|^Açores", re.I)


def parse_peso(book: dict) -> list[dict]:
    """Azores rows of the "Peso do SEE/SER na economia" table."""
    rows = find_sheet(book, "Peso do SE")
    hdr, years = table_years(rows, 0)
    if hdr < 0:
        return []
    out, ordem, grupo = [], 0, ""
    for r in rows[hdr + 1 :]:
        label = next((c for c in r if isinstance(c, str)), None)
        if label is None:
            continue
        if label.startswith(("Fonte", "Source")):
            break
        vals = {y: number(r[j]) for j, y in years.items() if j < len(r)}
        vals = {y: v for y, v in vals.items() if v is not None}
        if not vals:
            grupo = clean(label)
            continue
        rub = clean(label)
        if not AZORES.search(rub) or "SERAM" in rub:
            continue
        ind = grupo.startswith("Indicadores")
        unid = (
            "%" if ind else "milhares" if "milhares" in grupo.lower() else "M€"
        )
        for y, v in vals.items():
            out.append(
                {
                    "quadro": PESO,
                    "ordem": ordem,
                    "grupo": grupo,
                    "rubrica": rub,
                    "ano": y,
                    "valor": v * 100 if ind else v,
                    "unidade": unid,
                }
            )
        ordem += 1
    if out:
        out[0]["nota"] = note(rows)
    return out


def report_rows(
    rel: str, url: str, fichas: dict, series: dict, ficheiro: str = ""
) -> tuple[list, list, list]:
    lista = parse_lista(series)
    if not lista:
        raise ValueError(f"{rel}: no SERAA list of companies")
    empresas = [{**e, "relatorio": rel, "url": url} for e in lista]
    for e in empresas:
        if e["participacao"] is not None:
            e["participacao"] = num_text(e["participacao"])
    rows = []
    for title, sheet in fichas.items():
        f = parse_ficha(sheet)
        if not f:
            continue
        e = match(lista, f["empresa"], title)
        if not e:
            continue
        for ano, ordem, ind, v in f["valores"]:
            rows.append(
                {
                    "relatorio": rel,
                    "ano": ano,
                    "sigla": e["sigla"],
                    "empresa": e["empresa"],
                    "ordem": ordem,
                    "indicador": ind,
                    "valor": num_text(v),
                    "unidade": unidade(ind),
                    "fonte": f["fonte"],
                    "url": url,
                    "ficheiro": ficheiro,
                }
            )
    if len({r["sigla"] for r in rows}) < len(lista) // 2:
        raise ValueError(f"{rel}: only {len(rows)} SERAA values found")
    regiao = []
    for r in parse_peso(series) + parse_esforco(series):
        r["valor"] = num_text(r["valor"])
        regiao.append({"nota": "", **r, "relatorio": rel, "url": url})
    return rows, empresas, regiao


# --- files --------------------------------------------------------------


def rel_key(rel: str) -> tuple[int, int]:
    n, y = rel.split("/")
    return int(y), int(n)


def merge(old: list[dict], new: list[dict]) -> list[dict]:
    """Company values: the latest report wins for the same company, year
    and indicator."""
    out: dict[tuple, dict] = {}
    for r in sorted(old + new, key=lambda r: rel_key(r["relatorio"])):
        out[tuple(str(r[k]) for k in KEY)] = r
    return sorted(
        out.values(),
        key=lambda r: (r["sigla"], int(r["ano"]), int(r["ordem"])),
    )


def replace(old: list[dict], new: list[dict]) -> list[dict]:
    """Per-report tables: a report's rows replace its old ones."""
    rels = {r["relatorio"] for r in new}
    rows = [r for r in old if r["relatorio"] not in rels] + new
    return sorted(
        rows,
        key=lambda r: (rel_key(r["relatorio"]), r.get("quadro", ""))
        + (int(r["ordem"]),),
    )


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def expected(today: dt.date) -> int:
    """Last year the newest report should cover: the CFP published the
    2023-2024 report in 2025, so by the end of year Y the report ending in
    Y - 1 should be out; allow until January."""
    return today.year - 2 if today.month > 1 else today.year - 3


def main(out_dir: Path, everything: bool = False) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        n: out_dir / f"{n}.csv"
        for n in ("sper", "sper_empresas", "sper_regiao")
    }
    old = {n: read_csv(p) for n, p in paths.items()}
    done = set() if everything else {r["url"] for r in old["sper"]}
    found = reports(get(LISTA).decode("utf-8", "replace"))
    if not found:
        print("no report links on", LISTA, file=sys.stderr)
        return 1
    new: dict[str, list] = {n: [] for n in paths}
    for rep in found:
        if rep["url"] in done:
            continue
        page = get(rep["url"]).decode("utf-8", "replace")
        f = files(page)
        if not (f["fichas"] and f["series"] and f["numero"]):
            print("missing files on", rep["url"], f, file=sys.stderr)
            return 1
        rows, empresas, regiao = report_rows(
            f["numero"],
            rep["url"],
            load(get(f["fichas"])),
            load(get(f["series"])),
            f["fichas"],
        )
        print(
            f"{f['numero']} ({rep['de']}-{rep['ate']}): "
            f"{len({r['sigla'] for r in rows})} empresas, {len(rows)} valores"
        )
        new["sper"] += rows
        new["sper_empresas"] += empresas
        new["sper_regiao"] += regiao
    if any(new.values()):
        base = {n: ([] if everything else old[n]) for n in paths}
        write_csv(paths["sper"], merge(base["sper"], new["sper"]), COLS)
        write_csv(
            paths["sper_empresas"],
            replace(base["sper_empresas"], new["sper_empresas"]),
            ECOLS,
        )
        write_csv(
            paths["sper_regiao"],
            replace(base["sper_regiao"], new["sper_regiao"]),
            RCOLS,
        )
    latest = max(r["ate"] for r in found)
    if latest < expected(dt.date.today()):
        print(f"newest CFP report ends in {latest}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.exit(main(Path(args[0] if args else "data"), "--tudo" in sys.argv))
