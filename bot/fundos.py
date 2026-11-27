"""EU funds in the Azores: the PRR (Plano de Recuperação e Resiliência) and
the cohesion funds (PO Açores 2020, Açores 2030 and the national
programmes), project by project.

Usage:
  python3 bot/fundos.py [data_dir] [--cache DIR] [--so prr|kohesio]

Writes four files to data_dir:

  prr_projetos.csv   one row per PRR project with any part in the Azores
                     (NUTS II 20): amount approved and paid, the share of it
                     located in the Azores and the concelhos, investment
                     and component, dates
  prr_entidades.csv  the entities of those projects: NIF, name, role
                     (final or intermediate beneficiary, partner), head
                     office, CAE and the amount contracted and paid
  kohesio_projetos.csv  cohesion fund projects that Kohesio places in the
                     Azores: programme, period, fund, total cost, EU
                     support, dates, and a note when the location is
                     probably wrong
  kohesio_beneficiarios.csv  Kohesio's beneficiaries of those projects,
                     each with its number of projects and total amounts

PRR. The Estrutura de Missão Recuperar Portugal publishes the whole PRR on
dados.gov.pt as xlsx files, updated daily (DADOS: projects, locations,
entities, investments). The current file of each is found through the
dados.gov.pt API. The locations file gives, for every project, the
concelhos and the share of the approved amount in each; the Azorean
share is the sum over the Azores' concelhos, and applies to the amount
paid too (the file's paid shares add up to more than 100 % for some
projects).

Kohesio. The European Commission's Kohesio (kohesio.ec.europa.eu) has an
open JSON API behind its site. Kohesio is a work in progress, and so is
what is read from it:

- projects are listed by programme and fund (one request per programme
  and fund, pages of 1000), so each gets its programme and fund without
  a request per project;
- Kohesio geocodes some projects by place name, and gets some wrong:
  projects of the Norte and Madeira programmes land in Vila do Porto or
  Calheta (São Jorge), and so do many of the national programmes' (Porto
  -> Vila do Porto, Maia -> Maia, see HOMONIMOS). Those projects carry a
  note and are left out of the totals on the site;
- national projects with several locations, one of them in the Azores,
  come at their whole amount (the IEFP's, for example). Those, and the
  Interreg ones, carry a note and are left out of the totals too;
- the beneficiary of each project is not read yet (it takes one request
  per beneficiary); kohesio_beneficiarios.csv has Kohesio's totals per
  beneficiary for the region, which include those misplaced projects;
- Kohesio has no NIF, so it cannot be joined to BASE except by name.

.github/workflows/fundos.yml runs this weekly. main() fails, so the
workflow emails, when a source has no Azorean project; the other source is
still written.
"""

import csv
import datetime as dt
import json
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = "acores.net open data (github.com/fmesqg/a-ores.net-site)"
TRIES = 6
RETRY = {429, 500, 502, 503, 504}

DADOS = "https://dados.gov.pt/api/1/datasets/"
PRR = {
    "projetos": "dataset-estrutura-de-missao-prr-projetos-2",
    "localizacoes": "dataset-estrutura-de-missao-prr-localizacoes-1",
    "entidades": "dataset-estrutura-de-missao-prr-entidades-1",
    "investimentos": "dataset-estrutura-de-missao-prr-investimentos",
}
NUTS_ACORES = "20"

KOHESIO = "https://kohesio.ec.europa.eu/api"
ENTITY = "https://linkedopendata.eu/entity/"
PORTUGAL = ENTITY + "Q18"
ACORES = ENTITY + "Q204"
PAGE = 1000
# programmes of other regions: Kohesio's Azorean projects from these are
# geocoding errors (place names shared with the Azores)
OUTRAS_REGIOES = (
    "Madeira",
    "Norte",
    "Centro",
    "Lisboa",
    "Alentejo",
    "Algarve",
)
NOTA_FORA = "programa de outra região: localização provavelmente errada"
NOTA_INTERREG = "Interreg: valor do projeto inteiro, com parceiros de fora"
NOTA_VARIOS = "vários locais, também fora dos Açores: valor do projeto inteiro"
NOTA_HOMONIMO = (
    "programa nacional num ponto de um homónimo: localização provavelmente"
    " errada"
)
# Points where Kohesio puts projects of national programmes whose place
# shares a name with an Azorean one: Porto -> Vila do Porto, Maia (Porto)
# -> Maia (São Miguel), Calheta (Madeira) -> Calheta (São Jorge). Checked
# 27/11/2026: "Estágios Norte", "Maia PMPSE AMP2030", ETAR de Ponte de
# Moreira... Projects of the Azores' own programmes at these points stay.
HOMONIMOS = {
    "-25.0676137,37.0028353",
    "-25.385062536033,37.80411975017",
    "-28.0187906,38.6055151",
}
# longitude and latitude bounds of the islands
CAIXA_ACORES = ((-31.5, -24.5), (36.8, 39.9))

PRR_PROJETOS = [
    "projeto",
    "designacao",
    "componente",
    "investimento",
    "investimento_codigo",
    "concelhos",
    "perc_acores",
    "aprovado",
    "pago",
    "aprovado_acores",
    "pago_acores",
    "subvencoes",
    "emprestimos",
    "inicio",
    "conclusao_prevista",
    "conclusao",
    "referencia",
]
PRR_ENTIDADES = [
    "projeto",
    "nif",
    "entidade",
    "papel",
    "sede",
    "cae",
    "contratado",
    "pago",
]
KOHESIO_PROJETOS = [
    "id",
    "projeto",
    "programa",
    "periodo",
    "fundo",
    "inicio",
    "fim",
    "custo_total",
    "apoio_ue",
    "objetivo",
    "nota",
    "ligacao",
]
KOHESIO_BENEFICIARIOS = [
    "id",
    "beneficiario",
    "projetos",
    "custo_total",
    "apoio_ue",
    "cofinanciamento",
    "ligacao",
]


def get(url: str, tries: int = TRIES, sleep=time.sleep) -> bytes:
    """GET with exponential backoff on 429, 5xx and network errors."""
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in RETRY or attempt == tries - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == tries - 1:
                raise
        sleep(2**attempt)
    raise AssertionError("unreachable")


def get_json(url: str, fetch=get):
    return json.loads(fetch(url))


def num(v) -> float:
    """Kohesio's '167500851,17', the xlsx's numbers or '' as a float."""
    if v is None or v == "":
        return 0.0
    if isinstance(v, int | float):
        return float(v)
    return float(str(v).replace(" ", "").replace(",", "."))


def money(x: float) -> str:
    return f"{x:.2f}".rstrip("0").rstrip(".") if x else "0"


def day(v) -> str:
    if isinstance(v, dt.datetime):
        return v.date().isoformat()
    return str(v or "")[:10]


# PRR -------------------------------------------------------------------


def prr_url(slug: str, fetch=get) -> str:
    """URL of the dataset's newest xlsx file."""
    res = get_json(DADOS + slug + "/", fetch)["resources"]
    xlsx = [r for r in res if r["url"].lower().endswith(".xlsx")] or res
    return max(xlsx, key=lambda r: r.get("last_modified") or "")["url"]


def xlsx_rows(path: Path):
    """Each row of the first sheet as a dict keyed by the header row."""
    import openpyxl  # only the PRR needs it

    wb = openpyxl.load_workbook(path, read_only=True)
    try:
        it = wb.worksheets[0].iter_rows(values_only=True)
        head = [str(h).strip() if h is not None else "" for h in next(it)]
        for r in it:
            yield dict(zip(head, r, strict=False))
    finally:
        wb.close()


def prr_locations(rows) -> dict[str, dict]:
    """{project: {aprovado, concelhos}} for the projects with a location
    in the Azores: the Azorean share (%) of the approved amount, and the
    concelhos. The file's perc_valor_pago is not used: for some projects
    it gives 100 % to each of several regions."""
    out: dict[str, dict] = {}
    for r in rows:
        if str(r.get("cd_nutsii") or "").strip() != NUTS_ACORES:
            continue
        p = out.setdefault(r["cd_projeto"], {"aprovado": 0.0, "concelhos": []})
        p["aprovado"] += num(r.get("perc_valor_aprovado"))
        conc = (r.get("ds_concelho") or "").strip()
        if conc and conc not in p["concelhos"]:
            p["concelhos"].append(conc)
    return out


def _inv_key(code: str) -> str:
    """'RE-C01-i01' (investments file) and 'C01-i01' (projects) alike."""
    code = (code or "").strip()
    head, _, rest = code.partition("-")
    return rest if len(head) == 2 and head.isalpha() and rest else code


def prr_investments(rows) -> dict[str, tuple[str, str]]:
    """{investment code: (component, investment name)}."""
    out = {}
    for r in rows:
        code = r.get("Código do Investimento")
        if not code:
            continue
        comp = (r.get("Designação da Componente") or "").strip()
        cc = (r.get("Código da Componente") or "").strip()
        nome = (r.get("Designação do Investimento") or "").strip()
        out[_inv_key(code)] = (f"{cc} {comp}".strip(), nome)
    return out


def _investment(code: str, inv: dict) -> tuple[str, str]:
    """Look a project's investment code up, falling back to shorter forms
    ('C14-i03-RAA' -> 'C14-i03', 'C06-i03.02' -> 'C06-i03')."""
    k = _inv_key(code)
    base = "-".join(k.split("-")[:2])
    for cand in (k, k.split(".")[0], base, base.split(".")[0]):
        if cand in inv:
            return inv[cand]
    return "", ""


def prr_projects(rows, loc: dict, inv: dict) -> list[list]:
    out = []
    for r in rows:
        p = loc.get(r.get("cd_projeto"))
        if not p:
            continue
        aprovado, pago = num(r.get("valor_aprovado")), num(r.get("valor_pago"))
        pa = min(p["aprovado"], 100)
        comp, nome = _investment(r.get("cd_investimento"), inv)
        out.append(
            [
                r["cd_projeto"],
                (r.get("ds_projeto") or "").strip(),
                comp,
                nome,
                r.get("cd_investimento") or "",
                "; ".join(sorted(p["concelhos"])),
                money(round(pa, 2)),
                money(aprovado),
                money(pago),
                money(round(aprovado * pa / 100, 2)),
                money(round(pago * pa / 100, 2)),
                money(num(r.get("subvencoes"))),
                money(num(r.get("emprestimos"))),
                day(r.get("dt_inicio")),
                day(r.get("dt_prevista_conclusao")),
                day(r.get("dt_efetiva_conclusao")),
                day(r.get("dt_referencia")),
            ]
        )
    out.sort(key=lambda x: (-float(x[9]), x[0]))
    return out


def prr_entities(rows, projetos: set[str]) -> list[list]:
    out = []
    for r in rows:
        if r.get("cd_projeto") not in projetos:
            continue
        nif = r.get("nif_entidade") or r.get("cd_entidade") or ""
        out.append(
            [
                r["cd_projeto"],
                str(nif).strip(),
                (r.get("ds_entidade") or "").strip(),
                (r.get("papel_entidade") or "").strip(),
                (r.get("localizacao_sede") or "").strip(),
                str(r.get("atividade_economica") or "").strip(),
                money(num(r.get("valor_contratado"))),
                money(num(r.get("valor_pago"))),
            ]
        )
    out.sort(key=lambda x: (x[0], x[3], x[2]))
    return out


def read_prr(tmp: Path, fetch=get, rows=xlsx_rows) -> tuple[list, list]:
    paths = {}
    for name, slug in PRR.items():
        path = tmp / f"prr_{name}.xlsx"
        if not path.exists():  # --cache keeps them between runs
            path.write_bytes(fetch(prr_url(slug, fetch)))
        paths[name] = path
    loc = prr_locations(rows(paths["localizacoes"]))
    inv = prr_investments(rows(paths["investimentos"]))
    projetos = prr_projects(rows(paths["projetos"]), loc, inv)
    entidades = prr_entities(
        rows(paths["entidades"]), {p[0] for p in projetos}
    )
    return projetos, entidades


# Kohesio ---------------------------------------------------------------


def k_url(path: str, **params) -> str:
    q = {"language": "pt", **params}
    return f"{KOHESIO}{path}?{urllib.parse.urlencode(q)}"


def periodo(programa: str) -> str:
    cci = programa[:4]
    return {"2014": "2014-2020", "2021": "2021-2027"}.get(cci, "")


def nos_acores(coord: str) -> bool:
    """Kohesio's 'longitude,latitude' falls within the islands."""
    try:
        lon, lat = (float(c) for c in coord.split(","))
    except ValueError:
        return True  # no usable point: not evidence of another place
    (x0, x1), (y0, y1) = CAIXA_ACORES
    return x0 <= lon <= x1 and y0 <= lat <= y1


def nota(programa: str, coords: list[str] | None = None) -> str:
    """Why a project's amount should not count as the Azores' (or '')."""
    nome = programa.split(" - ", 1)[-1]
    if "Interreg" in nome:
        return NOTA_INTERREG
    if "Açores" not in nome and any(r in nome for r in OUTRAS_REGIOES):
        return NOTA_FORA
    if "Açores" not in nome and coords and set(coords) <= HOMONIMOS:
        return NOTA_HOMONIMO
    if not all(nos_acores(c) for c in coords or []):
        return NOTA_VARIOS
    return ""


def k_project(x: dict, programa: str, fundo: str) -> list:
    first = lambda k: (x.get(k) or [""])[0]  # noqa: E731
    return [
        x["item"],
        first("labels"),
        programa,
        periodo(programa),
        fundo,
        first("startTimes"),
        first("endTimes"),
        money(num(first("totalBudgets"))),
        money(num(first("euBudgets"))),
        ",".join(x.get("objectiveIds") or []),
        nota(programa, x.get("coordinates")),
        f"https://kohesio.ec.europa.eu/pt/projects/{x['item']}",
    ]


def k_pages(fetch=get, **filters):
    """Every project matching filters in the Azores, page by page."""
    offset = 0
    while True:
        url = k_url(
            "/projects",
            country=PORTUGAL,
            region=ACORES,
            offset=offset,
            limit=PAGE,
            **filters,
        )
        page = get_json(url, fetch)
        got = page.get("list") or []
        yield from got
        offset += len(got)
        if not got or offset >= page.get("numberResults", 0):
            return


def k_count(fetch=get, **filters) -> int:
    url = k_url(
        "/projects", country=PORTUGAL, region=ACORES, limit=1, **filters
    )
    return get_json(url, fetch).get("numberResults", 0)


def read_kohesio(fetch=get) -> tuple[list, list]:
    funds = {
        f["instance"]: f["instanceLabel"]
        for f in get_json(k_url("/queries/funds"), fetch)
    }
    progs = get_json(k_url("/queries/programs", country=PORTUGAL), fetch)
    total = k_count(fetch)
    seen: dict[str, list] = {}
    for p in progs:
        n = k_count(fetch, program=p["instance"])
        if not n:
            continue
        label, got = p["instanceLabel"], 0
        for f in p.get("funds") or []:
            fundo = funds.get(f, "").split(" - ")[0]
            for x in k_pages(fetch, program=p["instance"], fund=f):
                seen.setdefault(x["item"], k_project(x, label, fundo))
                got += 1
        if got < n:  # projects with no fund, or one not listed
            for x in k_pages(fetch, program=p["instance"]):
                seen.setdefault(x["item"], k_project(x, label, ""))
    if len(seen) < total:  # programmes not listed for Portugal (Interreg)
        for x in k_pages(fetch):
            seen.setdefault(x["item"], k_project(x, "", ""))
    projetos = sorted(seen.values(), key=lambda r: (-float(r[8]), r[0]))

    ben, offset = [], 0
    while True:
        url = k_url(
            "/beneficiaries",
            country=PORTUGAL,
            region=ACORES,
            offset=offset,
            limit=5000,
        )
        page = get_json(url, fetch)
        got = page.get("list") or []
        for b in got:
            q = b["id"].rsplit("/", 1)[-1]
            ben.append(
                [
                    q,
                    (b.get("label") or "").strip(),
                    b.get("numberProjects") or 0,
                    money(num(b.get("budget"))),
                    money(num(b.get("euBudget"))),
                    b.get("cofinancingRate") or "",
                    f"https://kohesio.ec.europa.eu/pt/beneficiaries/{q}",
                ]
            )
        offset += len(got)
        if not got or offset >= page.get("numberResults", 0):
            break
    ben.sort(key=lambda r: (-float(r[4]), r[0]))
    return projetos, ben


# -----------------------------------------------------------------------


def write_csv(path: Path, cols: list[str], rows: list[list]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        w.writerows(rows)


def main(
    data_dir: Path,
    cache: Path | None = None,
    so: str | None = None,
    fetch=get,
) -> int:
    data_dir.mkdir(parents=True, exist_ok=True)
    falhou = False
    if so in (None, "prr"):
        with tempfile.TemporaryDirectory() as t:
            try:
                projetos, entidades = read_prr(cache or Path(t), fetch)
            except Exception as e:  # noqa: BLE001 - report, try Kohesio
                print(f"PRR: {e!r}", file=sys.stderr)
                projetos, entidades = [], []
        if projetos:
            write_csv(data_dir / "prr_projetos.csv", PRR_PROJETOS, projetos)
            write_csv(data_dir / "prr_entidades.csv", PRR_ENTIDADES, entidades)
            aprov = sum(float(p[9]) for p in projetos) / 1e6
            print(
                f"PRR: {len(projetos)} projetos, {len(entidades)} entidades,"
                f" {aprov:.1f} M€ aprovados nos Açores"
            )
        else:
            print("PRR: no Azorean project", file=sys.stderr)
            falhou = True
    if so in (None, "kohesio"):
        try:
            projetos, ben = read_kohesio(fetch)
        except Exception as e:  # noqa: BLE001
            print(f"Kohesio: {e!r}", file=sys.stderr)
            projetos, ben = [], []
        if projetos:
            write_csv(
                data_dir / "kohesio_projetos.csv", KOHESIO_PROJETOS, projetos
            )
            write_csv(
                data_dir / "kohesio_beneficiarios.csv",
                KOHESIO_BENEFICIARIOS,
                ben,
            )
            fora = sum(1 for p in projetos if p[10])
            print(
                f"Kohesio: {len(projetos)} projetos ({fora} com nota),"
                f" {len(ben)} beneficiários"
            )
        else:
            print("Kohesio: no Azorean project", file=sys.stderr)
            falhou = True
    return 1 if falhou else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    cache = so = None
    if "--cache" in args:
        i = args.index("--cache")
        cache = Path(args[i + 1])
        cache.mkdir(parents=True, exist_ok=True)
        del args[i : i + 2]
    if "--so" in args:
        i = args.index("--so")
        so = args[i + 1]
        del args[i : i + 2]
    sys.exit(main(Path(args[0] if args else "data"), cache, so))
