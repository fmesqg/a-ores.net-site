"""The Azores beside the EU's other outermost regions, Portugal, the EU and
other islands, from Eurostat's regional tables (NUTS 2).

Usage: python3 bot/eurostat.py [data_dir]   (stdlib only)

Writes data_dir/eurostat.csv, one row per indicator, region and year:

  indicador  key of the indicator (INDICADORES)
  tema, nome, unidade  for the page, in Portuguese
  geo        Eurostat's code (PT20 = Açores, PT30 = Madeira, ES70 =
             Canarias, FRY1-5 = the French overseas regions, PT, EU27_2020)
  regiao     its name; grupo: acores, rup (outermost region), pais, ue,
             ilha (other islands, for context)
  ano, valor, estado  Eurostat's flag: p provisional, e estimated, b break
             in series, u low reliability (small samples: the Labour Force
             Survey and SILC figures for the smaller regions), d definition
             differs
  tabela, atualizado  the Eurostat table and when Eurostat last updated it

The API (JSON-stat 2.0, ec.europa.eu/eurostat/api/dissemination) takes one
request per table with every region in it: about 20 requests. Eurostat
asks for no key and states no rate limit; the requests are sequential with
a pause anyway. A table that fails keeps its old rows, and main() returns
1 so .github/workflows/eurostat.yml fails and emails.

Some regions are missing from some tables: Iceland (IS00) is outside the
EU regional accounts, Mayotte (FRY5) has no SILC, Åland (FI20) and the
smaller outermost regions have suppressed LFS cells. The page shows what
there is.
"""

import csv
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
UA = "acores.net open data (github.com/fmesqg/a-ores.net-site)"
TRIES = 4
PAUSE = 1.0

# (code, name, group), in the order of the page's tables
REGIOES = [
    ("PT20", "Açores", "acores"),
    ("PT30", "Madeira", "rup"),
    ("ES70", "Canárias", "rup"),
    ("FRY1", "Guadalupe", "rup"),
    ("FRY2", "Martinica", "rup"),
    ("FRY3", "Guiana Francesa", "rup"),
    ("FRY4", "Reunião", "rup"),
    ("FRY5", "Maiote", "rup"),
    ("PT", "Portugal", "pais"),
    ("EU27_2020", "União Europeia", "ue"),
    ("ES53", "Baleares", "ilha"),
    ("FRM0", "Córsega", "ilha"),
    ("ITG2", "Sardenha", "ilha"),
    ("EL43", "Creta", "ilha"),
    ("MT00", "Malta", "ilha"),
    ("CY00", "Chipre", "ilha"),
    ("FI20", "Åland", "ilha"),
    ("IS00", "Islândia", "ilha"),
]

# key: (tema, nome, unidade, table, filters). Each filter fixes one
# dimension to one value, so the table gives one number per region and
# year.
INDICADORES = {
    "pib_ppc": (
        "Economia",
        "PIB por habitante em paridade de poder de compra",
        "UE = 100",
        "nama_10r_2gdp",
        {"unit": "PPS_HAB_EU27_2020"},
    ),
    "pib_hab": (
        "Economia",
        "PIB por habitante",
        "€",
        "nama_10r_2gdp",
        {"unit": "EUR_HAB"},
    ),
    "rendimento": (
        "Economia",
        "Rendimento disponível das famílias por habitante",
        "PPC",
        "nama_10r_2hhinc",
        {"unit": "PPS_EU27_2020_HAB", "na_item": "B6N", "direct": "BAL"},
    ),
    "id_pib": (
        "Economia",
        "Despesa em investigação e desenvolvimento",
        "% do PIB",
        "rd_e_gerdreg",
        {"sectperf": "TOTAL", "unit": "PC_GDP"},
    ),
    "dormidas": (
        "Economia",
        "Dormidas em alojamento turístico por mil habitantes",
        "por mil hab.",
        "tour_occ_nin2",
        {"c_resid": "TOTAL", "nace_r2": "I551-I553", "unit": "P_THAB"},
    ),
    "emprego": (
        "Trabalho",
        "Taxa de emprego (20-64 anos)",
        "%",
        "lfst_r_lfe2emprt",
        {"sex": "T", "age": "Y20-64", "unit": "PC"},
    ),
    "desemprego": (
        "Trabalho",
        "Taxa de desemprego (15-74 anos)",
        "%",
        "lfst_r_lfu3rt",
        {"sex": "T", "age": "Y15-74", "isced11": "TOTAL", "unit": "PC"},
    ),
    "desemprego_jovens": (
        "Trabalho",
        "Taxa de desemprego jovem (15-24 anos)",
        "%",
        "lfst_r_lfu3rt",
        {"sex": "T", "age": "Y15-24", "isced11": "TOTAL", "unit": "PC"},
    ),
    "desemprego_longa": (
        "Trabalho",
        "Desemprego de longa duração (12 meses ou mais)",
        "% da população ativa",
        "lfst_r_lfu2ltu",
        {"sex": "T", "age": "Y15-74", "isced11": "TOTAL", "unit": "PC_ACT"},
    ),
    "nem_nem": (
        "Educação",
        "Jovens que não trabalham nem estudam (15-29 anos)",
        "%",
        "edat_lfse_22",
        {
            "sex": "T",
            "age": "Y15-29",
            "training": "NO_FE_NO_NFE",
            "wstatus": "NEMP",
            "unit": "PC",
        },
    ),
    "abandono": (
        "Educação",
        "Abandono precoce da educação e formação (18-24 anos)",
        "%",
        "edat_lfse_16",
        {"sex": "T", "age": "Y18-24", "unit": "PC"},
    ),
    "superior": (
        "Educação",
        "População com ensino superior (25-64 anos)",
        "%",
        "edat_lfse_04",
        {"sex": "T", "age": "Y25-64", "isced11": "ED5-8", "unit": "PC"},
    ),
    "pobreza_exclusao": (
        "Pobreza",
        "Em risco de pobreza ou exclusão social",
        "% da população",
        "ilc_peps11n",
        {"unit": "PC"},
    ),
    "pobreza": (
        "Pobreza",
        "Taxa de risco de pobreza (após transferências sociais)",
        "% da população",
        "ilc_li41",
        {"unit": "PC"},
    ),
    "populacao": (
        "População e saúde",
        "População residente a 1 de janeiro",
        "pessoas",
        "demo_r_d2jan",
        {"sex": "T", "age": "TOTAL", "unit": "NR"},
    ),
    "idade_mediana": (
        "População e saúde",
        "Idade mediana da população",
        "anos",
        "demo_r_pjanind2",
        {"indic_de": "MEDAGEPOP", "unit": "YR"},
    ),
    "fecundidade": (
        "População e saúde",
        "Índice sintético de fecundidade",
        "filhos por mulher",
        "demo_r_find2",
        {"indic_de": "TOTFERRT", "unit": "NR"},
    ),
    "esperanca_vida": (
        "População e saúde",
        "Esperança de vida à nascença",
        "anos",
        "demo_r_mlifexp",
        {"sex": "T", "age": "Y_LT1", "unit": "YR"},
    ),
    "camas": (
        "População e saúde",
        "Camas de hospital por 100 mil habitantes",
        "por 100 mil hab.",
        "hlth_rs_bdsrg2",
        {"unit": "P_HTHAB"},
    ),
}

COLS = [
    "indicador",
    "tema",
    "nome",
    "unidade",
    "geo",
    "regiao",
    "grupo",
    "ano",
    "valor",
    "estado",
    "tabela",
    "atualizado",
]


def get(table: str, filters: dict) -> dict:
    query = [("lang", "EN"), ("format", "JSON")]
    query += [("geo", g) for g, _, _ in REGIOES]
    query += sorted(filters.items())
    url = API + table + "?" + urllib.parse.urlencode(query)
    for attempt in range(TRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except (urllib.error.URLError, TimeoutError) as e:
            code = getattr(e, "code", None)
            if code and code not in (429, 500, 502, 503, 504):
                raise
            if attempt == TRIES - 1:
                raise
            time.sleep(10 * (attempt + 1))
    raise RuntimeError("unreachable")


def rows_of(key: str, data: dict) -> list[list]:
    """One row per region and year with a value. Every dimension but geo
    and time has a single category (fixed by the filters), so the flat
    index is geo_index * n_time + time_index."""
    tema, nome, unidade, table, filters = INDICADORES[key]
    dims = data["id"]
    sizes = data["size"]
    extra = [d for d, n in zip(dims, sizes, strict=True) if n > 1]
    if set(extra) - {"geo", "time"}:
        raise ValueError(f"{table}: dimensions not fixed: {extra}")
    geo = data["dimension"]["geo"]["category"]["index"]
    tim = data["dimension"]["time"]["category"]["index"]
    # strides of the row-major flat index
    stride, strides = 1, {}
    for d, n in reversed(list(zip(dims, sizes, strict=True))):
        strides[d] = stride
        stride *= n
    names = {g: (n, grp) for g, n, grp in REGIOES}
    values = data.get("value", {})
    status = data.get("status", {})
    updated = data.get("updated", "")[:10]
    out = []
    for g, gi in geo.items():
        for t, ti in sorted(tim.items()):
            i = str(gi * strides["geo"] + ti * strides["time"])
            v = values.get(i)
            if v is None:
                continue
            nome_r, grupo = names.get(g, (g, ""))
            out.append(
                [
                    key,
                    tema,
                    nome,
                    unidade,
                    g,
                    nome_r,
                    grupo,
                    t,
                    v,
                    status.get(i, ""),
                    table,
                    updated,
                ]
            )
    return out


def read(path: Path) -> dict[str, list[list]]:
    """The existing CSV, by indicator (kept for a table that fails)."""
    if not path.exists():
        return {}
    out: dict[str, list[list]] = {}
    with path.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            out.setdefault(r["indicador"], []).append([r[c] for c in COLS])
    return out


def main(data_dir: Path) -> int:
    path = data_dir / "eurostat.csv"
    old = read(path)
    new: dict[str, list[list]] = {}
    failed = []
    for key, (_, _, _, table, filters) in INDICADORES.items():
        try:
            new[key] = rows_of(key, get(table, filters))
            if not any(r[4] == "PT20" for r in new[key]):
                raise ValueError("no value for the Azores")
            print(key, table, len(new[key]), "rows")
        except Exception as e:  # noqa: BLE001 - keep going, report below
            print(f"::error::{key} ({table}): {e}")
            failed.append(key)
            if key in old:
                new[key] = old[key]
        time.sleep(PAUSE)
    if len(failed) > len(INDICADORES) // 2:
        print("more than half the tables failed: CSV not written")
        return 1
    order = {g: i for i, (g, _, _) in enumerate(REGIOES)}
    rows = [
        r
        for key in INDICADORES
        for r in sorted(
            new.get(key, []), key=lambda r: (order.get(r[4], 99), r[7])
        )
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLS)
        w.writerows(rows)
    print(path, len(rows), "rows")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "data")))
