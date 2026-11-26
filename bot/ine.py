"""INE indicators for the Azores, by region, island, concelho and freguesia.

Usage:
  python3 bot/ine.py [data_dir]         fetch INDICATORS, write data_dir/ine.csv
  python3 bot/ine.py procurar TERMOS    search INE's catalogue for indicators
                                        with Azores-level geography

Stdlib only, like bot/datasets.py. The INE API is public and needs no key:
  data      https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=...
  metadata  https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp?varcd=...
  catalogue https://www.ine.pt/ine/xml_indic.jsp?opc=2 (all ~13 000 indicators)

Dim1=T asks for every period. Dim2=<*>20 asks for everything inside NUTS
code 20 (the Azores): the region, its 19 concelhos and, where the indicator
goes that deep, its 156 freguesias. Indicators keyed on the administrative
division (concelho 4203 = Ponta Delgada) reject that code, so they are
fetched whole and filtered to codes 41xx-49xx, then renamed to NUTS codes.

Other dimensions (sex, age group, type...) are reduced to their total
category when one exists ("HM", "Total"); a dimension without a total
(quintiles, for instance) is kept and described in the "categoria" column.

INE answers 429 to parallel requests, so requests go one at a time with a
pause. data/ine.csv is committed and refreshed weekly by
.github/workflows/ine.yml; bot/datasets.py copies it into docs/dados/ and
acores.db.
"""

import csv
import datetime as dt
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

API = "https://www.ine.pt/ine/json_indicador/"
CATALOGUE = "https://www.ine.pt/ine/xml_indic.jsp?opc=2&lang=PT"
UA = {"User-Agent": "acores.net open data (github.com/fmesqg/a-ores.net-site)"}
PAUSE = 1.0

# Indicators by theme: (varcd, note). The theme groups the indicator list on
# /dados/ine/. Prefer the "NUTS - 2024" version of a series when INE has
# both. Find more with: python3 bot/ine.py procurar <termos>
THEMES = {
    "Rendimento e IRS": [
        ("0012756", "rendimento após IRS por sujeito passivo"),
        ("0012757", "mediana do rendimento após IRS por sujeito passivo"),
        ("0012741", "mediana do rendimento após IRS por agregado fiscal"),
        ("0012749", "mediana do rendimento bruto por sujeito passivo"),
        ("0012670", "rendimento bruto declarado por habitante"),
        ("0014580", "poder de compra per capita"),
        ("0012760", "Gini do rendimento após IRS por sujeito passivo"),
        ("0012744", "Gini do rendimento após IRS por agregado fiscal"),
        ("0012761", "P80/P20 do rendimento após IRS, sujeitos passivos"),
        ("0012762", "P90/P10 do rendimento após IRS, sujeitos passivos"),
        ("0012759", "quintis do rendimento após IRS, sujeitos passivos"),
        ("0012750", "IRS liquidado por sujeito passivo"),
        ("0012747", "sujeitos passivos"),
        ("0013318", "agregados fiscais"),
    ],
    "Habitação e construção": [
        ("0014698", "mediana das rendas de novos contratos, anual"),
        ("0014696", "mediana das rendas de novos contratos, 12 meses"),
        ("0014697", "novos contratos de arrendamento, anual"),
        ("0014695", "novos contratos de arrendamento, 12 meses"),
        ("0012254", "mediana das vendas de alojamentos (€/m²), anual"),
        ("0014764", "vendas de alojamentos, 12 meses"),
        ("0000087", "fogos licenciados em construções novas"),
        ("0000076", "fogos concluídos em construções novas"),
        ("0000086", "edifícios licenciados"),
    ],
    "População": [
        ("0012918", "população residente"),
        ("0012909", "índice de envelhecimento"),
        ("0013178", "taxa de crescimento efetivo"),
        ("0012450", "nados-vivos"),
    ],
    "Trabalho e proteção social": [
        ("0012656", "ganho médio mensal (Quadros de Pessoal)"),
        ("0013417", "beneficiários do RSI"),
        ("0013420", "beneficiários do RSI por 1000 habitantes em idade ativa"),
        ("0014534", "pensionistas da segurança social"),
    ],
    "Turismo": [
        ("0013214", "dormidas em alojamento turístico, anual"),
        ("0013213", "hóspedes em alojamento turístico, anual"),
        ("0013210", "dormidas por 100 habitantes"),
        ("0013285", "proveitos totais do alojamento turístico"),
        ("0012088", "dormidas em alojamento turístico, mensal"),
    ],
    "Empresas": [
        ("0014061", "empresas"),
        ("0014643", "constituição de pessoas coletivas"),
    ],
    "Câmaras municipais": [
        ("0013908", "receitas das câmaras municipais"),
        ("0013909", "despesas das câmaras municipais"),
        ("0013899", "receitas não financeiras das câmaras por habitante"),
    ],
    "Ambiente, energia e segurança": [
        ("0014162", "consumo de eletricidade por habitante"),
        ("0012767", "resíduos urbanos recolhidos seletivamente por habitante"),
        ("0012261", "crimes registados"),
    ],
}
INDICATORS = [i for items in THEMES.values() for i in items]
TEMA = {v: t for t, items in THEMES.items() for v, _ in items}

COLS = [
    "varcd",
    "tema",
    "indicador",
    "periodo",
    "data",
    "nivel",
    "geocod",
    "local",
    "concelho",
    "ilha",
    "categoria",
    "valor",
    "unidade",
    "atualizado",
    "url",
]

ILHAS = {
    "1": "Santa Maria",
    "2": "São Miguel",
    "3": "Terceira",
    "4": "Graciosa",
    "5": "São Jorge",
    "6": "Pico",
    "7": "Faial",
    "8": "Flores",
    "9": "Corvo",
}
TOTALS = {"hm", "todos", "todas"}


def is_total(cat: str) -> bool:
    c = cat.strip().lower()
    return c in TOTALS or c.startswith("total")


MESES = {
    m: i + 1
    for i, m in enumerate(
        "janeiro fevereiro março abril maio junho julho agosto setembro "
        "outubro novembro dezembro".split()
    )
}
GEO_SUFFIX = re.compile(
    r"\s+por (?:Localização geográfica|Local de residência|Local de "
    r"localização|Local de registo|Localização)\b.*$",
    re.S,
)


def get_json(url: str, tries: int = 4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == tries - 1:
                raise
            time.sleep(10 * (i + 1))
        except (urllib.error.URLError, TimeoutError):
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))


def data_url(varcd: str, geo: str | None) -> str:
    q = {"op": "2", "varcd": varcd, "Dim1": "T", "lang": "PT"}
    if geo:
        q["Dim2"] = geo
    return API + "pindica.jsp?" + urllib.parse.urlencode(q, safe="<>*")


def period_date(periodo: str) -> str:
    """Sortable yyyy-mm-dd for an INE period label: '2024', 'Setembro de
    2026', '2.º Trimestre de 2026', '1.º Semestre de 2024', '2022 / 2023'
    (school year: last year), '2021 - 2025' (5 years: last year)."""
    years = re.findall(r"\b(\d{4})\b", periodo)
    if not years:
        return ""
    year, low, month = years[-1], periodo.lower(), 1
    if m := re.search(r"(\d)\.?\s*º?\s*trimestre", low):
        month = 3 * int(m[1]) - 2
    elif m := re.search(r"(\d)\.?\s*º?\s*semestre", low):
        month = 6 * int(m[1]) - 5
    else:
        month = next((n for name, n in MESES.items() if name in low), 1)
    return f"{year}-{month:02d}-01"


def nuts(geocod: str) -> str:
    """Administrative codes (4203, 420301) to NUTS 2024 ones (2004203,
    200420301); NUTS codes are returned unchanged."""
    if re.fullmatch(r"4[1-9]\d{2}(\d{2})?", geocod):
        return "2004" + geocod[1:]
    return geocod


def level(geocod: str) -> str:
    return {2: "Região", 3: "Região", 7: "Concelho", 9: "Freguesia"}.get(
        len(geocod), ""
    )


def short_name(nome: str) -> str:
    nome = nome.split(";")[0].split(" - INE,")[0].strip()
    return GEO_SUFFIX.sub("", nome).strip()


def rows_from(varcd: str, data: dict, meta: dict) -> list[list]:
    """Rows for one indicator from its pindica (data) and pindicaMeta
    (meta) JSON. Keeps Azores geographies only, collapses dimensions that
    have a total, and drops observations without a value."""
    nome = short_name(
        meta.get("IndicadorNome") or data.get("IndicadorDsg", "")
    )
    periodicidade = (meta.get("Periodic") or "").strip().lower()
    if periodicidade and periodicidade != "anual":
        nome += f" – {periodicidade}"  # annual and monthly series share names
    unidade = meta.get("UnidadeMedida", "")
    atualizado = meta.get("DataUltimaAtualizacao", "")
    url = f"https://www.ine.pt/xurl/indx/{varcd}"
    obs = []
    for periodo, items in (data.get("Dados") or {}).items():
        for o in items:
            g = nuts(o.get("geocod", ""))
            if g.startswith("200") or g == "20":
                obs.append((periodo, g, o))
    # Which extra dimensions have a total category?
    dims: dict[str, set] = {}
    for _, _, o in obs:
        for k, v in o.items():
            if re.fullmatch(r"dim_\d+_t", k):
                dims.setdefault(k, set()).add(v)
    total = {
        k: next(v for v in sorted(vals) if is_total(v))
        for k, vals in dims.items()
        if any(is_total(v) for v in vals)
    }
    names = {g: o.get("geodsg", "") for _, g, o in obs}
    has_region = "20" in names
    out = []
    for periodo, g, o in obs:
        if g == "200" and has_region:
            continue  # NUTS III = NUTS II for the Azores
        if any(o.get(k) != v for k, v in total.items()):
            continue
        valor = o.get("valor")
        if valor in (None, ""):
            continue
        try:
            valor = float(valor)
        except ValueError:
            continue
        cat = " · ".join(
            o[k]
            for k in sorted(dims, key=lambda k: int(k.split("_")[1]))
            if k not in total and o.get(k)
        )
        nivel = level(g)
        out.append(
            [
                varcd,
                TEMA.get(varcd, ""),
                nome,
                periodo,
                period_date(periodo),
                nivel,
                g,
                o.get("geodsg", "").strip(),
                names.get(g[:7], "").strip() if nivel == "Freguesia" else "",
                ILHAS.get(g[4], "") if len(g) >= 7 else "",
                cat,
                int(valor) if valor.is_integer() else valor,
                unidade,
                atualizado,
                url,
            ]
        )
    return out


def fetch(varcd: str) -> list[list]:
    meta = get_json(API + f"pindicaMeta.jsp?varcd={varcd}&lang=PT")[0]
    time.sleep(PAUSE)
    data = get_json(data_url(varcd, "<*>20"))[0]
    if not data.get("Dados"):  # administrative division: fetch all, filter
        time.sleep(PAUSE)
        data = get_json(data_url(varcd, None))[0]
    return rows_from(varcd, data, meta)


def main(out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows, failed = [], []
    for varcd, note in INDICATORS:
        try:
            got = fetch(varcd)
        except Exception as e:  # keep going; report at the end
            failed.append(f"{varcd} ({note}): {e}")
            got = []
        if not got and not any(varcd in f for f in failed):
            failed.append(f"{varcd} ({note}): sem dados dos Açores")
        print(f"{varcd} {len(got):6d}  {note}", flush=True)
        rows += got
        time.sleep(PAUSE)
    if failed and len(failed) > len(INDICATORS) // 2:
        # Probably INE is down: keep the previous file rather than shrink it.
        print("Too many failures, ine.csv left unchanged:", *failed, sep="\n")
        return 1
    order = {v: i for i, (v, _) in enumerate(INDICATORS)}
    rows.sort(key=lambda r: (order[r[0]], r[4], r[6], r[10]))
    tmp = out_dir / "ine.csv.tmp"
    with open(tmp, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        w.writerows(rows)
    tmp.replace(out_dir / "ine.csv")
    print(f"{len(rows)} rows, {len(INDICATORS) - len(failed)} indicators")
    for f in failed:
        print("FAILED", f)
    return 0


def search(terms: list[str]) -> None:
    """Print catalogue indicators below NUTS II whose title or description
    matches all terms (accent-insensitive)."""

    def fold(s: str) -> str:
        import unicodedata

        s = unicodedata.normalize("NFD", s or "")
        return "".join(c for c in s if not unicodedata.combining(c)).lower()

    req = urllib.request.Request(CATALOGUE, headers=UA)
    with urllib.request.urlopen(req, timeout=600) as r:
        root = ET.parse(r).getroot()
    want = [fold(t) for t in terms]
    deep = {"NUTS II", "NUTS III", "Município", "Freguesia", "Região autónoma"}
    have = {v for v, _ in INDICATORS}
    for i in root.iter("indicator"):
        geo = (i.findtext("geo_lastlevel") or "").strip()
        text = fold(
            (i.findtext("title") or "")
            + " "
            + (i.findtext("description") or "")
        )
        if geo in deep and all(t in text for t in want):
            upd = (i.findtext("dates/last_update") or "").strip()
            v = (i.findtext("varcd") or "").strip()
            print(
                "*" if v in have else " ",
                v,
                f"{geo:10.10}",
                upd,
                (i.findtext("description") or "").strip()[:140],
            )


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "procurar":
        search(args[1:])
    else:
        target = Path(args[0]) if args else Path("data")
        started = dt.datetime.now()
        code = main(target)
        print(f"took {(dt.datetime.now() - started).seconds}s")
        sys.exit(code)
