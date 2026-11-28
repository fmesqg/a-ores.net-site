"""CAP payments (FEAGA, FEADER, POSEI) to beneficiaries in the Azores, from
the IFAP's yearly publication of beneficiaries.

Usage: python3 bot/ifap.py [data_dir]   (stdlib only)

EU law (Reg. 2021/2116, art. 98; Reg. 2022/128, ch. VI) makes the IFAP
publish every beneficiary of the agricultural funds each year: name,
district and concelho, postcode, and the amount per measure. The IFAP's
search page (apj13.ifap.pt/idigital.consultarFundos) offers the whole
financial year as one zip ("Lista Completa"):
pub/FEAGA_FEADER_<ano>.zip, ~12 MB, a Latin-1 CSV with ";" and one row per
beneficiary and measure plus a "Total" row per beneficiary (left out
here). A financial year runs from 16 October to 15 October (2025 =
16/10/2024 to 15/10/2025). The Azores are districts 41 (Santa Maria) to
49 (Corvo), one per island, so a place is "200" + district + concelho in
INE's codes ("42" "03" = 2004203, Ponta Delgada). Some years write the
concelho without a leading zero and without its name: the name comes from
CONCELHOS.

The law keeps each year online for two years, and the IFAP removes it
after that (in November 2026 it has 2024 and 2025; 2023 is a 404). This
script follows the same rule for names: data_dir/ifap_pagamentos.csv,
which has the beneficiaries, is rewritten with only the years the IFAP
still publishes. data_dir/ifap_resumo.csv keeps, for every year ever
read, the totals per concelho and measure (number of beneficiaries and
amounts, no names); a newer read wins for a year.

Amounts: FEAGA (100 % EU: direct payments, markets, POSEI), FEADER (EU
share of rural development) and the national/regional co-financing of the
FEADER measures; montante = FEAGA + FEADER + co-financing. Recoveries are
negative. POSEI (measure VII.1) here is only what is paid to
beneficiaries with an Azorean address: POSEI aid paid to operators
registered elsewhere (part of the supply arrangement, REA) is not in
these files as Azorean.

.github/workflows/ifap.yml runs this weekly (the file changes once a year,
around May). main() returns 1 when no year can be read or a year's Azores
total looks wrong (MIN_TOTAL).
"""

import csv
import datetime as dt
import io
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

URL = "https://apj13.ifap.pt/idigital.consultarFundos/pub/FEAGA_FEADER_{}.zip"
SEARCH = "https://apj13.ifap.pt/idigital.consultarFundos/"
UA = "acores.net open data (github.com/fmesqg/a-ores.net-site)"
# a year's Azores total below this means a broken file (2024: 122 M€)
MIN_TOTAL = 50e6

# district (island) -> name; (district, concelho) -> (INE geocode, name)
ILHAS = {
    "41": "Santa Maria",
    "42": "São Miguel",
    "43": "Terceira",
    "44": "Graciosa",
    "45": "São Jorge",
    "46": "Pico",
    "47": "Faial",
    "48": "Flores",
    "49": "Corvo",
}
CONCELHOS = {
    ("41", "01"): "Vila do Porto",
    ("42", "01"): "Lagoa",
    ("42", "02"): "Nordeste",
    ("42", "03"): "Ponta Delgada",
    ("42", "04"): "Povoação",
    ("42", "05"): "Ribeira Grande",
    ("42", "06"): "Vila Franca do Campo",
    ("43", "01"): "Angra do Heroísmo",
    ("43", "02"): "Praia da Vitória",
    ("44", "01"): "Santa Cruz da Graciosa",
    ("45", "01"): "Calheta",
    ("45", "02"): "Velas",
    ("46", "01"): "Lajes do Pico",
    ("46", "02"): "Madalena",
    ("46", "03"): "São Roque do Pico",
    ("47", "01"): "Horta",
    ("48", "01"): "Lajes das Flores",
    ("48", "02"): "Santa Cruz das Flores",
    ("49", "01"): "Corvo",
}

# The IFAP's own names (its search page), for the codes paid in the
# Azores. VI.23 is what the EU list calls the Croatian payments; the IFAP
# uses the code in the Azores, so its name is kept as published.
MEDIDAS = {
    "I.1": "Apoio ao rendimento de base para garantir a sustentabilidade",
    "I.2": "Apoio redistributivo complementar ao rendimento",
    "I.3": "Apoio complementar ao rendimento para jovens agricultores",
    "I.4": "Regimes no domínio climático e ambiental",
    "I.5": "Pagamento aos pequenos agricultores",
    "I.6": "Apoio associado ao rendimento",
    "II.12": "Recuperações (condicionalidade, fraude ou irregularidades)",
    "III.2": "Setor da apicultura",
    "III.3": "Setor vitivinícola",
    "IV.3": "Regime de frutos, produtos hortícolas e leite nas escolas",
    "IV.5": "Medidas excecionais",
    "IV.7": "Apoio ao setor vitivinícola",
    "V.1": "Compromissos ambientais, climáticos e outros de gestão",
    "V.2": "Condicionantes naturais ou outras condicionantes específicas",
    "V.4": "Investimentos, incluindo em irrigação",
    "V.5": "Instalação de jovens agricultores e novos agricultores",
    "V.6": "Instrumentos de gestão de riscos",
    "V.7": "Cooperação",
    "VI.1": "Transferência de conhecimentos e informação",
    "VI.2": "Aconselhamento",
    "VI.3": "Regimes de qualidade",
    "VI.4": "Investimentos em ativos físicos",
    "VI.6": "Desenvolvimento das explorações agrícolas e das empresas",
    "VI.8": "Investimentos em zonas florestais",
    "VI.14": "Agrupamentos e organizações de produtores",
    "VI.15": "Agroambiente e clima",
    "VI.16": "Agricultura biológica",
    "VI.17": "Natura 2000 e Diretiva-Quadro da Água",
    "VI.18": "Zonas sujeitas a condicionantes naturais (PRORURAL+)",
    "VI.19": "Bem-estar animal",
    "VI.20": "Serviços silvoambientais e conservação das florestas",
    "VI.21": "Cooperação",
    "VI.22": "Gestão de riscos",
    "VI.23": "Artigo 40.º do Reg. 1305/2013 (código do IFAP)",
    "VI.24": "LEADER (desenvolvimento local de base comunitária)",
    "VI.25": "Assistência técnica",
    "VI.27": "Reforma antecipada",
    "VII.1": "POSEI (Reg. UE 228/2013)",
    "X.1": "Reembolsos de dotações transitadas",
    "X.2": "Desenvolvimento rural: períodos de programação anteriores",
}


def programa(code: str) -> str:
    """Group of a measure code, for the page."""
    roman = code.split(".")[0]
    if roman == "VII":
        return "POSEI"
    if roman in ("I", "II"):
        return "Pagamentos diretos"
    if roman in ("III", "IV", "IX"):
        return "Mercados agrícolas"
    if roman in ("V", "VI") or code == "X.2":
        return "Desenvolvimento rural"
    return "Outros"


PAG_COLS = [
    "exercicio",
    "beneficiario",
    "grupo",
    "nif_grupo",
    "ilha",
    "concelho",
    "geocod",
    "codigo_postal",
    "medida",
    "medida_nome",
    "programa",
    "feaga",
    "feader",
    "cofinanciado",
    "montante",
]
RES_COLS = [
    "exercicio",
    "ilha",
    "concelho",
    "geocod",
    "medida",
    "medida_nome",
    "programa",
    "beneficiarios",
    "feaga",
    "feader",
    "cofinanciado",
    "montante",
]


def download(year: int, dest: Path) -> bool:
    """The year's zip into dest; False when the IFAP has no such year."""
    req = urllib.request.Request(URL.format(year), headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                if "zip" not in r.headers.get("Content-Type", ""):
                    return False
                dest.write_bytes(r.read())
                return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            if attempt == 3:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise
        time.sleep(20 * (attempt + 1))
    return False


def num(text: str) -> float:
    return round(float(text or 0), 2)


def azores_rows(path: Path) -> list[list]:
    """The year's rows with an Azorean address, without the Total rows."""
    out = []
    with zipfile.ZipFile(path) as z:
        name = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        with z.open(name) as raw:
            f = io.TextIOWrapper(raw, encoding="latin-1", newline="")
            for r in csv.DictReader(f, delimiter=";"):
                d = r["DISTRITO"].strip()
                if d not in ILHAS or r["MEDIDA"] == "Total":
                    continue
                c = r["CONCELHO"].strip().zfill(2)
                code = r["MEDIDA"].strip()
                out.append(
                    [
                        r["EXERCICIO"],
                        " ".join(r["DENOMINACAO"].split()),
                        " ".join(r["NOME_GRUPO_EMPRESAS"].split()),
                        r["NIF_GRUPO_EMPRESAS"].strip(),
                        ILHAS[d],
                        CONCELHOS.get((d, c), r["DESCRICAO_CONCELHO"]),
                        f"200{d}{c}",
                        r["CODIGO_POSTAL"].strip(),
                        code,
                        MEDIDAS.get(code, code),
                        programa(code),
                        num(r["MONTANTE_FEAGA"]),
                        num(r["MONTANTE_FEADER"]),
                        num(r["MONTANTE_COFINANCIADO"]),
                        num(r["MONTANTE"]),
                    ]
                )
    return out


def resumo(rows: list[list]) -> list[list]:
    """Totals per year, concelho and measure."""
    agg: dict[tuple, list] = {}
    for r in rows:
        k = (r[0], r[4], r[5], r[6], r[8], r[9], r[10])
        a = agg.setdefault(k, [set(), 0.0, 0.0, 0.0, 0.0])
        a[0].add(r[1])
        for i, v in enumerate(r[11:15]):
            a[i + 1] += v
    return [
        [*k, len(a[0]), *(round(v, 2) for v in a[1:])]
        for k, a in sorted(agg.items())
    ]


def read(path: Path) -> list[list]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.reader(f))[1:]


def write(path: Path, cols: list[str], rows: list[list]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        w.writerows(rows)
    print(path, len(rows), "rows")


def main(data_dir: Path) -> int:
    this = dt.date.today().year
    rows: list[list] = []
    years = []
    errors = 0
    with tempfile.TemporaryDirectory() as tmp:
        for year in range(this + 1, this - 4, -1):
            z = Path(tmp) / f"{year}.zip"
            if not download(year, z):
                continue
            got = azores_rows(z)
            total = sum(r[14] for r in got)
            print(year, len(got), "rows", round(total / 1e6, 1), "M€")
            if total < MIN_TOTAL:
                print(f"::error::IFAP {year}: Azores total {total:.0f} €")
                errors += 1
                continue
            rows += got
            years.append(str(year))
    if not years:
        print("::error::no IFAP year could be read")
        return 1
    rows.sort(key=lambda r: (r[0], r[1].casefold(), r[8]))
    write(data_dir / "ifap_pagamentos.csv", PAG_COLS, rows)
    old = [r for r in read(data_dir / "ifap_resumo.csv") if r[0] not in years]
    write(
        data_dir / "ifap_resumo.csv",
        RES_COLS,
        sorted(old + resumo(rows), key=lambda r: (r[0], r[3], r[4])),
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "data")))
