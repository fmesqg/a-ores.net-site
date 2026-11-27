"""BASE contracts in the Azores since 2012, from the IMPIC open data.

Usage:
  python3 bot/base_impic.py [data_dir] [--cache DIR] [--anos 2012-2026]

The daily bot (bot/fetch.py) has seen every new contract on base.gov.pt
since August 2024. For the years before, the IMPIC (Instituto dos Mercados
Públicos, do Imobiliário e da Construção), which runs the BASE portal,
publishes every contract on dados.gov.pt, one file per year, in the public
domain:

  https://dados.gov.pt/datasets/contratos-publicos-portal-base-impic-contratos-de-2012-a-2026

Each contratos<ano>.zip holds one JSON array (0.2-0.5 GB unzipped, about
200 000 contracts a year for the whole country), read here as a stream with
ijson. A contract is kept when one of its places of execution
(localExecucao) is in the Azores: the same rule as the BASE search the daily
bot uses (distrito 20), which picks the same contracts (checked on 2025).
The IMPIC id is the base.gov.pt id, so bot/datasets.py joins both sources
by id.

The yearly files are not split by publication date (a file can hold
contracts published the year before or after), so all of them are read and
a contract that appears twice keeps the newest file's version.

data/base_impic/<ano>.csv.gz (one file per year of publication, so a
monthly run only changes the recent years) is rewritten from scratch;
.github/workflows/base_impic.yml runs this monthly. main() fails, so the workflow emails, when
a year cannot be read, a year has no Azores contracts, or the newest
contract is more than ~90 days old.
"""

import csv
import datetime as dt
import gzip
import html
import io
import json
import re
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

DATASET = (
    "https://dados.gov.pt/api/1/datasets/"
    "contratos-publicos-portal-base-impic-contratos-de-2012-a-2026/"
)
UA = "acores.net open data (github.com/fmesqg/a-ores.net-site)"
ZIP_RE = re.compile(r"contratos(\d{4})\.zip$", re.I)
OUT = "base_impic"  # one <ano>.csv.gz per year of publication
MAX_IDADE = 90  # days

COLS = [
    "id",
    "publicado",
    "data_assinatura",
    "preco",
    "preco_base",
    "preco_efetivo",
    "adjudicante",
    "adjudicante_nif",
    "adjudicatario",
    "adjudicatario_nif",
    "procedimento",
    "tipo_contrato",
    "objeto",
    "cpv",
    "concorrentes",
    "propostas",
    "local",
    "fundamentacao",
    "acordo_quadro",
]
LOCAL_PREFIX = re.compile(r"^Portugal,\s*Região Autónoma dos Açores,?\s*")


def retry(fn, tries: int = 4):
    """dados.gov.pt sometimes does not answer at all: try again."""
    for i in range(tries):
        try:
            return fn()
        except OSError as e:  # URLError and timeouts are OSErrors
            if i == tries - 1:
                raise
            print(f"  {e}; a tentar de novo", file=sys.stderr)
            time.sleep(30 * (i + 1))


def get(url: str) -> bytes:
    def once():
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read()

    return retry(once)


def download(url: str, dest: Path) -> None:
    part = dest.with_suffix(".part")

    def once():
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            with open(part, "wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
        part.replace(dest)

    retry(once)


def zips(dataset: dict) -> dict[int, str]:
    """{year: url} of the contratos<ano>.zip resources."""
    out = {}
    for res in dataset.get("resources", []):
        m = ZIP_RE.search(res.get("url", "")) or ZIP_RE.search(
            res.get("title", "")
        )
        if m:
            out[int(m[1])] = res["url"]
    return out


def text(s) -> str:
    return re.sub(r"\s+", " ", html.unescape(str(s or ""))).strip()


def money(x) -> float | str:
    if x in (None, ""):
        return ""
    try:
        return round(float(x), 2)
    except (TypeError, ValueError):
        return ""


def entities(lst) -> tuple[str, str]:
    lst = lst or []
    names = " | ".join(text(e.get("descEntContrato")) for e in lst)
    nifs = " | ".join(text(e.get("nifEntContrato")) for e in lst)
    return names, nifs


def in_azores(r: dict) -> bool:
    return any("Açores" in (loc or "") for loc in r.get("localExecucao") or [])


def row(r: dict) -> list:
    adj, adj_nif = entities(r.get("adjudicante"))
    con, con_nif = entities(r.get("adjudicatarios"))
    cpv = r.get("CPV") or []
    principal = next(
        (c for c in cpv if c.get("CPVObjeto") == "Principal"),
        cpv[0] if cpv else {},
    )
    lotes = r.get("Lotes") or []
    props = [lt["NumPropostas"] for lt in lotes if lt.get("NumPropostas")]
    locais = []
    for loc in r.get("localExecucao") or []:
        loc = LOCAL_PREFIX.sub("", text(loc)) or "Açores"
        if loc not in locais:
            locais.append(loc)
    return [
        int(r["idcontrato"]),
        r.get("dataPublicacao") or "",
        r.get("dataCelebracaoContrato") or "",
        money(r.get("precoContratual")),
        money(r.get("precoBaseProcedimento")),
        money(r.get("PrecoTotalEfetivo")),
        adj,
        adj_nif,
        con,
        con_nif,
        text(r.get("tipoprocedimento")),
        " | ".join(text(t) for t in r.get("tipoContrato") or []),
        text(r.get("objectoContrato") or r.get("descContrato")),
        (
            f"{principal.get('cpvID', '')} {text(principal.get('cpvdescricao'))}"
        ).strip(),
        len(r.get("concorrentes") or []) or "",
        max(props) if props else "",
        "; ".join(locais),
        text(r.get("fundamentacao")),
        text(r.get("DescrAcordoQuadro") or r.get("numAcordoQuadro")),
    ]


def read_zip(path: Path) -> list[list]:
    import ijson  # only this script needs it (pip install ijson)

    with zipfile.ZipFile(path) as z:
        (name,) = [n for n in z.namelist() if n.lower().endswith(".json")]
        with z.open(name) as f:
            return [
                row(r)
                for r in ijson.items(f, "item", use_float=True)
                if in_azores(r) and r.get("idcontrato")
            ]


def anos(spec: str) -> range:
    a, _, b = spec.partition("-")
    return range(int(a), int(b or a) + 1)


def main(
    data_dir: Path,
    cache: Path | None = None,
    years: range | None = None,
    today: dt.date | None = None,
) -> int:
    today = today or dt.date.today()
    urls = zips(json.loads(get(DATASET)))
    if years:
        urls = {y: u for y, u in urls.items() if y in years}
    if not urls:
        print("No contratos<ano>.zip on dados.gov.pt", file=sys.stderr)
        return 1
    rows: dict[int, list] = {}
    with tempfile.TemporaryDirectory() as tmp:
        for year in sorted(urls):
            path = (cache or Path(tmp)) / f"contratos{year}.zip"
            if not path.exists():
                download(urls[year], path)
            got = read_zip(path)
            print(f"{year}: {len(got)} contratos nos Açores")
            if not got:
                print(f"{year}: nenhum contrato dos Açores", file=sys.stderr)
                return 1
            for r in got:
                rows[r[0]] = r
            if not cache:
                path.unlink()
    out = sorted(rows.values(), key=lambda r: (r[1], r[0]), reverse=True)
    newest = max((r[1] for r in out if r[1]), default="")
    if not years and (
        not newest or (today - dt.date.fromisoformat(newest)).days > MAX_IDADE
    ):
        print(f"Newest contract is too old: {newest!r}", file=sys.stderr)
        return 1
    folder = data_dir / OUT
    folder.mkdir(parents=True, exist_ok=True)
    by_year: dict[str, list] = {}
    for r in out:
        by_year.setdefault(r[1][:4] or "sem_data", []).append(r)
    for old in folder.glob("*.csv.gz"):
        if old.name.split(".")[0] not in by_year:
            old.unlink()
    for year, rs in by_year.items():
        # mtime=0: the same rows give the same bytes, so git sees no change
        with (
            open(folder / f"{year}.csv.gz", "wb") as raw,
            gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz,
            io.TextIOWrapper(gz, encoding="utf-8", newline="") as f,
        ):
            w = csv.writer(f, lineterminator="\n")
            w.writerow(COLS)
            w.writerows(rs)
    print(f"{len(out)} contratos, até {newest} -> {data_dir / OUT}")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    cache = years = None
    if "--cache" in args:
        i = args.index("--cache")
        cache = Path(args[i + 1])
        cache.mkdir(parents=True, exist_ok=True)
        del args[i : i + 2]
    if "--anos" in args:
        i = args.index("--anos")
        years = anos(args[i + 1])
        del args[i : i + 2]
    sys.exit(main(Path(args[0] if args else "data"), cache, years))
