"""Banco de Portugal (BPstat): loans, deposits, foreign direct investment
and company indicators for the Azores.

Usage:
  python3 bot/bportugal.py [data_dir] [--cache DIR]   rewrite data_dir/bportugal.csv

BPstat has an open API (no key) that returns JSON-stat:

  https://bpstat.bportugal.pt/data/v1/domains/<domain>/datasets/<dataset>/?lang=PT

Its "Estatísticas regionais" domain has four parts read here (DATASETS):

  emprestimos  loans by the resident financial sector to private
               individuals (housing; consumption and other purposes) and to
               non-financial companies, by NUTS II region of the debtor, at
               the end of each month: amount, overdue amount, overdue ratio,
               number of debtors and share of debtors with overdue loans.
               Companies since December 2002, private individuals since
               January 2009.
  depositos    deposits of private individuals, companies and emigrants by
               region of the bank branch, monthly since December 2018
               (deposits not tied to a branch are "Concelho não alocado").
  ide          foreign direct investment in Portugal by region, yearly since
               2017, split into head offices (sedes) and establishments.
  empresas     the Central de Balanços indicators of non-financial companies
               by region and sector of activity (number of companies, people
               employed, sales, financial autonomy, returns, payment
               periods...), yearly since 2006, from the IES.

The API sends a dataset in pages of at most 100 series, each page a JSON-stat
cube with its own values. Every page is read and every value is written: for
loans, deposits and FDI the nine NUTS II regions (so a national total can be
summed and checked; BPstat gives none for these), for companies the Azores,
Madeira and Portugal. The NUTS III rows are dropped: for the two autonomous
regions they repeat the NUTS II ones.

Requests are made one at a time; a 429, a 5xx or a network error is retried
with exponential backoff (1, 2, 4, ... 64 s). A run is about 80 requests.

.github/workflows/bportugal.yml runs this weekly. main() fails, so the
workflow emails, when a dataset has no Azores row or the newest month of
loans is more than ~4 months old.
"""

import csv
import datetime as dt
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://bpstat.bportugal.pt/data/v1"
UA = "acores.net open data (github.com/fmesqg/a-ores.net-site)"
PAGE_SIZE = 100  # the API refuses more
TRIES = 8
MAX_IDADE = 130  # days between the newest month of loans and today

# (conjunto, domain, dataset, which regions to keep)
DATASETS = [
    ("emprestimos", 188, "961306c1ed49daf795a53dc5fea4a04b", "nuts2"),
    ("emprestimos", 188, "d5bf6198a39f1e77b0d14dda97103de0", "nuts2"),
    ("depositos", 206, "d5bf6198a39f1e77b0d14dda97103de0", "nuts2"),
    ("ide", 189, "226fdb00077f154289f54e87da9e68dc", "nuts2"),
    ("empresas", 178, "14ed8f5141827c03e802bdcb99bf1ad8", "ilhas"),
    ("empresas", 178, "8f81a135c26dd5e58fd92232e266e951", "ilhas"),
]

COLS = [
    "conjunto",
    "indicador",
    "setor",
    "detalhe",
    "regiao",
    "data",
    "valor",
    "unidade",
    "serie",
]
REGIOES = {
    "Região Autónoma dos Açores": "Açores",
    "Região Autónoma da Madeira": "Madeira",
}
SETORES = {
    "Famílias e instituições sem fim lucrativo ao serviço das famílias": (
        "Particulares"
    ),
    "Sociedades não financeiras": "Empresas",
    "Emigrantes": "Emigrantes",
}
# (Rubrica, Métrica) of the loans datasets -> indicator
EMPRESTIMOS = {
    ("Empréstimos", "Valor em fim do período"): "Empréstimos",
    ("Empréstimos", "Contagem"): "Devedores",
    (
        "Empréstimos vencidos",
        "Valor em fim do período",
    ): "Empréstimos vencidos",
    ("Empréstimos vencidos", "Rácio de empréstimos vencidos"): (
        "Rácio de empréstimos vencidos"
    ),
    ("Empréstimos vencidos", "% de devedores"): (
        "Devedores com empréstimos vencidos"
    ),
}


def get(url: str, tries: int = TRIES, sleep=time.sleep) -> dict:
    """GET JSON; retry 429, 5xx and network errors with exponential
    backoff. Other HTTP errors (400, 404) are not retried."""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500 or i == tries - 1:
                raise
            wait = int(e.headers.get("Retry-After") or 0) or 2**i
        except (OSError, ValueError) as e:  # URLError, timeouts, bad JSON
            if i == tries - 1:
                raise
            wait = 2**i
            print(f"  {e}; a tentar de novo", file=sys.stderr)
        sleep(min(wait, 120))
    raise RuntimeError(url)  # not reached


def pages(domain: int, dataset: str, fetch=get):
    """Every page of a dataset, following extension.next_page."""
    url = (
        f"{API}/domains/{domain}/datasets/{dataset}/"
        f"?lang=PT&page_size={PAGE_SIZE}"
    )
    while url:
        page = fetch(url)
        yield page
        url = page.get("extension", {}).get("next_page")


def observations(page: dict):
    """(series id, {dimension label: category label}, date, value) for
    every value of one JSON-stat page."""
    ids, size, dims = page["id"], page["size"], page["dimension"]
    cats = []  # per dimension: position -> category id
    for k in ids:
        idx = dims[k]["category"]["index"]
        if isinstance(idx, dict):
            idx = sorted(idx, key=idx.get)
        cats.append(idx)
    # a series is the set of its categories, one per dimension but time
    by_cats = {}
    for s in page.get("extension", {}).get("series", []):
        key = frozenset(
            (str(c["dimension_id"]), str(c["category_id"]))
            for c in s["dimension_category"]
        )
        by_cats[key] = s["id"]
    values = page["value"]
    items = values.items() if isinstance(values, dict) else enumerate(values)
    for flat, v in items:
        if v is None:
            continue
        flat, coord = int(flat), []
        for n in reversed(size):
            coord.append(flat % n)
            flat //= n
        coord.reverse()
        labels, key, date = {}, set(), ""
        for k, i in zip(ids, coord, strict=True):
            c = cats[ids.index(k)][i]
            if k == "reference_date":
                date = c
                continue
            key.add((k, str(c)))
            labels[dims[k]["label"]] = (
                dims[k]["category"].get("label", {}).get(c, c)
            )
        yield by_cats.get(frozenset(key), ""), labels, date, v


def regiao(labels: dict) -> tuple[str, str]:
    """('Açores', 'NUTS II') from the territory dimension that varies:
    'Território de contraparte' for loans, 'de referência' otherwise."""
    for dim in ("Território de contraparte", "Território de referência"):
        t = labels.get(dim, "")
        if t in ("", "Portugal", "Todos os Países") and dim.endswith(
            "contraparte"
        ):
            continue
        if t.endswith(")"):
            name, _, nivel = t[:-1].rpartition(" (")
            return REGIOES.get(name, name), nivel
        return t, ""
    return "", ""


def _cae(text: str) -> str:
    return text.removesuffix(" (rev 4)")


def row(conjunto: str, serie, labels: dict, date: str, v) -> list | None:
    reg, nivel = regiao(labels)
    unidade = labels.get("Unidade de medida", "")
    setor = SETORES.get(
        labels.get("Setor institucional de contraparte", ""), ""
    )
    detalhe = ""
    if conjunto == "emprestimos":
        indicador = EMPRESTIMOS.get(
            (labels.get("Rubrica"), labels.get("Métrica"))
        )
        if not indicador:
            return None
        detalhe = labels.get("Finalidade", "")
        if detalhe:
            setor = "Particulares"
    elif conjunto == "depositos":
        indicador = "Depósitos"
    elif conjunto == "ide":
        indicador = "Investimento direto do exterior"
        detalhe = labels.get("Setorização adicional", "")
    else:
        indicador = labels.get("Indicadores") or labels.get("Rubrica", "")
        if labels.get("Métrica") == "% do número de empresas":
            unidade = "% das empresas"
        detalhe = _cae(
            labels.get("Atividade económica de referência (CAE)", "")
        )
        setor = "Empresas"
    return [
        conjunto,
        indicador,
        setor,
        detalhe,
        reg,
        date,
        v,
        unidade,
        serie,
    ], nivel


def keep(reg: str, nivel: str, regioes: str) -> bool:
    if regioes == "ilhas":
        return reg == "Portugal" or (
            reg in ("Açores", "Madeira") and nivel == "NUTS II"
        )
    return nivel == "NUTS II" or reg in ("Portugal", "Concelho não alocado")


def read(conjunto: str, domain: int, dataset: str, regioes: str, fetch=get):
    out = {}
    for page in pages(domain, dataset, fetch):
        for serie, labels, date, v in observations(page):
            got = row(conjunto, serie, labels, date, v)
            if not got:
                continue
            r, nivel = got
            if not keep(r[4], nivel, regioes):
                continue
            # pages can repeat a series: the key drops the duplicate
            out[tuple(r[:6]) + (r[7],)] = r
    return list(out.values())


def main(
    data_dir: Path,
    cache: Path | None = None,
    today: dt.date | None = None,
    fetch=get,
) -> int:
    today = today or dt.date.today()

    def cached(url: str) -> dict:
        if not cache:
            return fetch(url)
        name = url.split("/domains/")[1].replace("/", "_").replace("?", "_")
        path = cache / (name.replace("&", "_").replace("=", "") + ".json")
        if path.exists():
            return json.loads(path.read_text())
        data = fetch(url)
        path.write_text(json.dumps(data))
        return data

    rows = []
    for conjunto, domain, dataset, regioes in DATASETS:
        got = read(conjunto, domain, dataset, regioes, cached)
        az = [r for r in got if r[4] == "Açores"]
        print(f"{conjunto} {domain}/{dataset[:6]}: {len(got)} valores")
        if not az:
            print(f"{conjunto}: nothing for the Azores", file=sys.stderr)
            return 1
        rows += got
    newest = max(r[5] for r in rows if r[0] == "emprestimos")
    if (today - dt.date.fromisoformat(newest)).days > MAX_IDADE:
        print(f"Newest month of loans is too old: {newest}", file=sys.stderr)
        return 1
    order = {"Açores": 0, "Madeira": 1, "Portugal": 2}
    rows.sort(
        key=lambda r: (
            r[0],
            r[1],
            r[2],
            r[3],
            order.get(r[4], 3),
            r[4],
            r[5],
            r[7],
        )
    )
    data_dir.mkdir(parents=True, exist_ok=True)
    with open(
        data_dir / "bportugal.csv", "w", encoding="utf-8", newline=""
    ) as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLS)
        w.writerows(rows)
    print(f"{len(rows)} valores, empréstimos até {newest}")
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
