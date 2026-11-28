"""BASE contracts: the IMPIC open data (data/base_impic/) as one table, and the checks run before publishing it."""

import collections
import csv
import datetime as dt
import gzip
import re
from pathlib import Path

from .comum import write

BASE_COLS = [
    "id",
    "publicado",
    "data_assinatura",
    "preco",
    "adjudicante",
    "adjudicatario",
    "procedimento",
    "objeto",
    "url",
    "concorrentes",
]
# only in contratos.db: base.csv is read whole by the search page, keep it light
BASE_EXTRA = [
    "preco_base",
    "preco_efetivo",
    "adjudicante_nif",
    "adjudicatario_nif",
    "tipo_contrato",
    "cpv",
    "propostas",
    "local",
    "fundamentacao",
    "acordo_quadro",
]
BASE_ALL = BASE_COLS + BASE_EXTRA
BASE_URL = "https://www.base.gov.pt/Base4/pt/detalhe/?type=contratos&id="


def read_impic(data: Path) -> dict:
    """{id: row dict} from data/base_impic/<ano>.csv.gz (bot/base_impic.py)."""
    out = {}
    for path in sorted((data / "base_impic").glob("*.csv.gz")):
        with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                out[int(r["id"])] = r
    return out


def _n(x: str, kind=float):
    try:
        return kind(x) if x not in (None, "") else ""
    except ValueError:
        return ""


def nif(x: str) -> str:
    """The IMPIC writes "-" for a party with no Portuguese NIF (foreign
    companies, people): 5 517 contracts, 2 724 different names, that a
    query by NIF would take for one supplier. Kept empty instead."""
    return " | ".join("" if p == "-" else p for p in (x or "").split(" | "))


def _extra(r: dict | None) -> list:
    if not r:
        return [""] * len(BASE_EXTRA)
    return [
        (
            _n(r[c], float if c.startswith("preco") else int)
            if c in ("preco_base", "preco_efetivo", "propostas")
            else nif(r.get(c, "")) if c.endswith("_nif") else r.get(c, "")
        )
        for c in BASE_EXTRA
    ]


def build_base(docs: Path, impic: dict | None = None) -> list[list]:
    """Every BASE contract since 2012, from the IMPIC open data
    (bot/base_impic.py). The daily pages (docs/_base_updates/) keep only
    five fields per contract and miss what the BASE search misses, so they
    are not read here: they are the daily feed, not the dataset."""
    if impic is None:
        impic = read_impic(docs.parent / "data")
    rows = [
        [
            key,
            x["publicado"],
            x["data_assinatura"],
            None if _n(x["preco"]) == "" else _n(x["preco"]),
            x["adjudicante"],
            x["adjudicatario"],
            x["procedimento"],
            x["objeto"],
            BASE_URL + str(key),
            _n(x["concorrentes"], int),
            *_extra(x),
        ]
        for key, x in impic.items()
    ]
    return sorted(rows, key=lambda r: (r[1], r[3] or 0), reverse=True)


NIF_PART = re.compile(r"\d{9}|")
QUEDA, MAX_DIAS_BASE = 0.25, 30  # see check_base()


def check_base(rows: list[list], hoje: dt.date | None = None) -> dict:
    """Checks on the contracts before they are published. "erros" stop the
    deploy (python3 bot/datasets.py exits 1): a NIF that is not 9 digits
    (the IMPIC's "-" once made 2 724 suppliers look like one). "avisos" are
    only printed (and kept in meta.json): no contract in the last
    MAX_DIAS_BASE days, or an entity that signed 10+ contracts a year in
    the three years before and fewer than QUEDA of that in the last
    twelve months, which is how Vila do Porto's contracts went missing."""
    hoje = hoje or dt.date.today()
    col = {c: i for i, c in enumerate(BASE_ALL)}
    erros, avisos = [], []
    maus = collections.Counter()
    for r in rows:
        for c in ("adjudicante_nif", "adjudicatario_nif"):
            for part in str(r[col[c]] or "").split(" | "):
                if not NIF_PART.fullmatch(part):
                    maus[(c, part)] += 1
    for (c, v), n in maus.most_common(5):
        erros.append(f"{c} {v!r} em {n} contratos (NIF de 9 dígitos ou vazio)")
    datas = [r[col["publicado"]] for r in rows if r[col["publicado"]]]
    if not datas:
        return {"erros": erros + ["nenhum contrato"], "avisos": avisos}
    ultimo = dt.date.fromisoformat(max(datas))
    if (hoje - ultimo).days > MAX_DIAS_BASE:
        avisos.append(f"o contrato mais recente é de {ultimo}")
    um_ano = (ultimo - dt.timedelta(days=365)).isoformat()
    antes = (ultimo - dt.timedelta(days=4 * 365)).isoformat()
    recente, passado = collections.Counter(), collections.Counter()
    nomes = {}
    for r in rows:
        nif, d = r[col["adjudicante_nif"]], r[col["publicado"]]
        if not nif or not d or d <= antes:
            continue
        nomes[nif] = r[col["adjudicante"]]
        (recente if d > um_ano else passado)[nif] += 1
    for nif, n in passado.most_common():
        media = n / 3
        if media < 10:
            break
        if recente[nif] < QUEDA * media:
            avisos.append(
                f"{nomes[nif]} ({nif}): {recente[nif]} contratos nos últimos"
                f" 12 meses, {media:.0f} por ano nos três anteriores"
            )
    return {"erros": erros, "avisos": avisos}


def write_base_anos(out: Path, rows: list[list]) -> dict[str, int]:
    """docs/dados/base/<ano>.csv: base.csv split by year of publication, so
    the search page on /dados/ loads only the years it needs (base.csv is
    16 MB). Returns {year: rows}, newest first."""
    folder = out / "base"
    folder.mkdir(exist_ok=True)
    for old in folder.glob("*.csv"):
        old.unlink()
    por_ano: dict[str, list] = {}
    for r in rows:
        por_ano.setdefault(str(r[1])[:4] or "sem_data", []).append(
            r[: len(BASE_COLS)]
        )
    for ano, rs in por_ano.items():
        write(folder, ano, BASE_COLS, rs)
    return {a: len(rs) for a, rs in sorted(por_ano.items(), reverse=True)}
