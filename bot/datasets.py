"""Cumulative open datasets built from the daily update pages.

Usage: python3 bot/datasets.py [docs_dir]   (stdlib only, no poetry needed)

The bot writes one markdown page per source per day (docs/_base_updates/,
docs/_alra_updates/, docs/_joraa_updates/). This module re-reads all of them
and writes, under docs/dados/:

  base.csv   one row per BASE contract (deduplicated by id): what the bot
             saw since August 2024 plus, for every year since 2012, the
             IMPIC open data (data/base_impic/, from bot/base_impic.py);
             contratos.db carries more columns (NIFs, CPV, base and final
             price, bidders, place of execution)
  alra.csv   one row per ALRA record (requerimento, iniciativa, voto, ...),
             with the first/last day it appeared and its last known state
  joraa.csv  one row per JORAA act with an amount
  <tema>.db  every table below in SQLite, typed, indexed and (most) with
             an FTS5 index (<table>_fts), for SQL and Datasette Lite: one
             file per theme (BASES: contratos, parlamento, financas,
             estatisticas, empresas), so none is too big to open in a browser
  ine.csv    INE indicators for the Azores by region, concelho and
             freguesia: a copy of data/ine.csv, which bot/ine.py fetches
             weekly (it needs the network, so it is not rebuilt here)
  ine_meta.json  definitions of each INE indicator (concepts, formula,
             source, note): a copy of data/ine_meta.json, from bot/ine.py
  beo.csv    the regional government's monthly budget execution (Boletim
             de Execução Orçamental): a copy of data/beo.csv, which
             bot/beo.py parses from the PDFs weekly
  tdc.csv    the Tribunal de Contas' Parecer on the regional account:
             verdict, reservas, ênfases and recommendations (with the
             status the next parecer gave them), from data/tdc.csv
  tdc_valores.csv  figures from those pareceres (consolidated account,
             debt, revenue and expenditure left off the books)
  srea.csv   SREA series (inflation, economic activity, unemployment,
             tourism by island, GDP by island): a copy of data/srea.csv,
             which bot/srea.py fetches weekly
  srea.json  the same series, compact, for the charts on /dados/srea/
  sper.csv, sper_empresas.csv, sper_regiao.csv  the regional public
             companies (SERAA), company by company, from the Conselho das
             Finanças Públicas: copies of data/sper*.csv (bot/cfp.py)
  maiores.csv  the 200 largest companies with head office in the Azores in
             one year (Açoriano Oriental's "100 Maiores Empresas dos
             Açores"): a copy of data/maiores_<ano>.csv, entered by hand
  emprego_publico.csv  jobs and pay in general government in the Azores,
             quarterly since 2011 (DGAEP, SIOE): a copy of
             data/emprego_publico.csv (bot/dgaep.py)
  at_irs.csv IRS households, income and tax by tax bracket in the Azores,
             Madeira and the mainland, the additional solidarity rate and the general rates,
             yearly since 2016 (AT, Dossier Estatístico): a copy of
             data/at_irs.csv (bot/at_ir.py)
  at_irc.csv IRC at the regional rate, state surcharge (derrama estadual)
             by bracket and nominal rates, Azores / Madeira / mainland
             (AT, Dossier Estatístico IRC): data/at_irc.csv (bot/at_ir.py)
  at_distritos.csv  the "por distrito" chapters of the IRS (since 2015)
             and IRC (since 2011) dossiers: data/at_distritos.csv
  bportugal.csv  Banco de Portugal (BPstat) regional statistics: loans
             and overdue loans by region of the debtor (monthly since 2002
             and 2009), deposits by region of the branch (monthly since
             2018), foreign direct investment by region (yearly since 2017)
             and company indicators by region and sector (Central de
             Balanços, yearly since 2006): data/bportugal.csv
             (bot/bportugal.py)
  prr_projetos.csv, prr_entidades.csv  PRR projects with a part in the
             Azores and their entities (NIF, role, amounts), from the
             Recuperar Portugal open data: copies of data/prr_*.csv
             (bot/fundos.py)
  kohesio_projetos.csv, kohesio_beneficiarios.csv  cohesion fund projects
             that Kohesio places in the Azores, and its beneficiaries
             (work in progress, see bot/fundos.py): data/kohesio_*.csv
  meta.json  row counts, date coverage, build time

and, under docs/_data/ (read by Jekyll): ine_novidades.json, beo_ultimo.json,
resumo.json (the numbers on /introducao/ and /dados/srea/), fundos.json
(/financas/fundos-europeus/), sper.json
(/dados/sper/), credito.json (/dados/credito/), maiores.json (/dados/maiores-empresas/) and publico.json
(/economia/setor-publico/ and the public/private split on /economia/).

The CSVs are UTF-8 with BOM, so Excel opens accents correctly. The search
page (docs/dados.md) reads them directly. None of these files is committed:
.github/workflows/pages.yml generates them when it builds the site.
"""

import csv
import datetime as dt
import gzip
import json
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path

ITEM = re.compile(r"^\* \[(?P<title>.*)\]\((?P<url>[^)\s]+)\)\s*$")
SUB = re.compile(r"^\s{2,}\* (?P<text>.+)$")
LINK = re.compile(r"\[(?P<label>[^\]]*)\]\((?P<url>[^)\s]+)\)")
DMY = re.compile(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})")
STATE = re.compile(r"Alteração do estado:\s*(?P<old>.*?)\s*→\s*(?P<new>.+)")


def iso(text: str) -> str:
    """First dd/mm/yyyy or dd-mm-yyyy in text, as yyyy-mm-dd ('' if none)."""
    m = DMY.search(text or "")
    return f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}" if m else ""


def euros(text: str, decimal: str) -> float | None:
    """Parse '120.963,33 €' (decimal=',') or '993,164.40 €' (decimal='.')."""
    thousands = "." if decimal == "," else ","
    num = re.sub(r"[^\d" + re.escape(decimal) + "]", "", text)
    num = num.replace(thousands, "").replace(decimal, ".")
    try:
        return round(float(num), 2)
    except ValueError:
        return None


def parse_day(path: Path):
    """Yield (section, title, url, [sub-bullet lines]) for one daily page."""
    section, item = "", None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            if item:
                yield item
                item = None
            section = line.lstrip("#").strip()
        elif m := ITEM.match(line):
            if item:
                yield item
            item = (section, m["title"].strip(), m["url"], [])
        elif item and (m := SUB.match(line)):
            item[3].append(m["text"].strip())
    if item:
        yield item


def days(docs: Path, collection: str):
    for path in sorted((docs / collection).glob("????-??-??.md")):
        yield path.stem, path


def fields(subs: list[str]) -> dict[str, str]:
    """'Chave: valor' sub-bullets as a dict (plain text, links removed)."""
    out = {}
    for s in subs:
        plain = LINK.sub(r"\g<label>", s)
        if ":" in plain:
            key, val = plain.split(":", 1)
            out.setdefault(key.strip().lower(), val.strip())
    return out


def links(subs: list[str]) -> dict[str, str]:
    out = {}
    for s in subs:
        for m in LINK.finditer(s):
            out.setdefault(m["label"].strip().lower(), m["url"])
    return out


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
    "recolha",
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
DIARIO, IMPIC = "açores.net", "IMPIC"
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


def _extra(r: dict | None) -> list:
    if not r:
        return [""] * len(BASE_EXTRA)
    return [
        (
            _n(r[c], float if c.startswith("preco") else int)
            if c in ("preco_base", "preco_efetivo", "propostas")
            else r.get(c, "")
        )
        for c in BASE_EXTRA
    ]


def build_base(docs: Path, impic: dict | None = None) -> list[list]:
    """The contracts the bot saw day by day, completed and extended back to
    2012 with the IMPIC open data. When both have a contract, the bot's
    row wins (its 'publicado' is the day it appeared on base.gov.pt) and
    the IMPIC adds the columns the daily pages do not have."""
    if impic is None:
        impic = read_impic(docs.parent / "data")
    rows = {}
    for day, path in days(docs, "_base_updates"):
        for _, title, url, subs in parse_day(path):
            f = fields(subs)
            cid = re.search(r"id=(\d+)", url)
            key = int(cid[1]) if cid else url
            rows[key] = [
                key,
                day,
                iso(f.get("data da assinatura", "")),
                euros(f.get("preço contratual", ""), ","),
                f.get("adjudicante", ""),
                f.get("adjudicatário", ""),
                f.get("tipo de procedimento", ""),
                title,
                url,
            ]
    for key, r in rows.items():
        x = impic.get(key)
        r += [_n(x["concorrentes"], int) if x else "", DIARIO, *_extra(x)]
    for key, x in impic.items():
        if key in rows:
            continue
        rows[key] = [
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
            IMPIC,
            *_extra(x),
        ]
    return sorted(rows.values(), key=lambda r: (r[1], r[3] or 0), reverse=True)


ALRA_COLS = [
    "tipo",
    "titulo",
    "data",
    "autores",
    "estado",
    "primeiro_dia",
    "ultimo_dia",
    "documento",
    "resposta",
    "video",
    "url",
]
AUTHOR_KEYS = ("requerente(s)", "autor do texto inicial", "autores")
GRUPO = re.compile(
    r"^Nota [^-]*? d[ao] (?:Grupo Parlamentar|Representação(?: Parlamentar)?"
    r"|(Presidência)) d[ao] (.+?)\s+-\s"
)
DATE_KEYS = ("data", "dada de entrada", "data de entrada")


def build_alra(docs: Path) -> list[list]:
    """One row per record URL. base.alra.pt serves "ă" where it means "ã"
    (e.g. "Congratulaçăo"); Portuguese has no "ă", so it is fixed here."""
    rows: dict[str, list] = {}
    for day, path in days(docs, "_alra_updates"):
        for section, title, url, subs in parse_day(path):
            f, ln = fields(subs), links(subs)
            joined = " ".join(subs)
            estado = f.get("estado", "") or f.get("resultado", "")
            for s in subs:
                if m := STATE.search(s):
                    estado = m["new"].strip()
            if section == "Votos" and subs and ":" not in subs[0]:
                estado = " · ".join(x for x in (subs[0], estado) if x)
            data = next((iso(f[k]) for k in DATE_KEYS if k in f), "")
            if not data:  # "( data entrada: dd/mm/yyyy)" or a bare date
                data = iso(joined.split("resposta")[0])
            autores = next((f[k] for k in AUTHOR_KEYS if k in f), "")
            if not autores and (gp := GRUPO.search(title)):
                autores = "Presidência da ALRAA" if gp[1] else gp[2]
            if not autores and section == "Petições" and subs:
                autores = subs[0] if ":" not in subs[0] else ""
            doc = next(
                (
                    u
                    for k, u in ln.items()
                    if k != "video" and "resposta" not in k
                ),
                "",
            )
            resp = next((u for k, u in ln.items() if "resposta" in k), "")
            old = rows.get(url)
            if old:
                old[4] = estado or old[4]
                old[6] = day
                old[8] = resp or old[8]
                old[9] = ln.get("video", "") or old[9]
                continue
            rows[url] = [
                section,
                title,
                data,
                autores,
                estado,
                day,
                day,
                doc,
                resp,
                ln.get("video", ""),
                url,
            ]
    out = [
        [v.replace("ă", "ã") if isinstance(v, str) else v for v in r]
        for r in rows.values()
    ]
    return sorted(out, key=lambda r: (r[6], r[2]), reverse=True)


JORAA_COLS = [
    "publicado",
    "ato",
    "titulo",
    "montante",
    "montante_tipo",
    "entidade",
    "serie",
    "url",
]
# Until November 2026 the bot wrote "Soma dos montantes", the sum of every
# amount in the act (repeated amounts, costs and instalments included);
# since then "Montante: 1 234,56 € (what it is)", from utils.joraa_amount.
JORAA_SOMA_ANTIGA = "soma de todos os valores (método antigo)"


def joraa_montante(subs: list[str]) -> tuple[float | None, str]:
    for s in subs:
        if s.startswith("Soma"):
            return euros(s, "."), JORAA_SOMA_ANTIGA
        if s.startswith("Montante:"):
            valor, _, tipo = s.partition("€")
            return euros(valor, ","), tipo.strip(" ()")
    return None, ""


def build_joraa(docs: Path) -> list[list]:
    rows = {}
    for day, path in days(docs, "_joraa_updates"):
        for _, title, url, subs in parse_day(path):
            ato = subs[0] if subs else ""
            montante, tipo = joraa_montante(subs)
            serie = next((s for s in subs if s.startswith("Jornal")), "")
            entidade = next(
                (
                    s
                    for s in subs[1:]
                    if not s.startswith(("Soma", "Montante:", "Jornal"))
                ),
                "",
            )
            rows[url] = [day, ato, title, montante, tipo, entidade, serie, url]
    return sorted(rows.values(), key=lambda r: (r[0], r[3] or 0), reverse=True)


def write(out: Path, name: str, cols: list[str], rows: list[list]) -> dict:
    with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)
    return {"linhas": len(rows), "colunas": cols}


# SQLite column types (default TEXT), indexed columns and FTS columns.
DB_TYPES = {
    "id": "INTEGER",
    "preco": "REAL",
    "preco_base": "REAL",
    "preco_efetivo": "REAL",
    "concorrentes": "INTEGER",
    "propostas": "INTEGER",
    "escalao": "INTEGER",
    "montante": "REAL",
    "valor": "REAL",
    "ordem": "INTEGER",
    "ano": "INTEGER",
    "mes": "INTEGER",
    "conta": "INTEGER",
    "numero": "INTEGER",
    "posicao": "INTEGER",
    "trabalhadores": "INTEGER",
    "participacao": "REAL",
    "projetos": "INTEGER",
    **{
        c: "REAL"
        for c in (
            "aprovado",
            "pago",
            "aprovado_acores",
            "pago_acores",
            "perc_acores",
            "subvencoes",
            "emprestimos",
            "contratado",
            "custo_total",
            "apoio_ue",
        )
    },
    **{
        c: "REAL"
        for c in (
            "volume_negocios",
            "volume_negocios_2023",
            "cresc_vn_pct",
            "vab",
            "ativo",
            "capital_proprio",
            "passivo",
            "resultado_liquido",
            "resultado_liquido_2023",
            "cresc_rl_pct",
            "solvabilidade_pct",
            "rentab_cp_pct",
            "rentab_ativo_pct",
            "rentab_vn_pct",
            "rotacao_ativo_pct",
            "vab_trabalhador",
        )
    },
}
DB_INDEX = {
    "base": [
        "publicado",
        "data_assinatura",
        "adjudicante",
        "adjudicatario",
        "adjudicante_nif",
        "adjudicatario_nif",
    ],
    "alra": ["tipo", "data", "primeiro_dia", "autores"],
    "joraa": ["publicado", "entidade"],
    "ine": ["varcd", "data", "nivel", "local", "concelho"],
    "beo": ["quadro", "data", "caminho", "dimensao"],
    "tdc": ["conta", "tipo"],
    "tdc_valores": ["quadro", "ano", "caminho"],
    "srea": ["serie", "data", "local"],
    "sper": ["sigla", "ano", "indicador"],
    "sper_empresas": ["relatorio", "sigla"],
    "sper_regiao": ["relatorio", "quadro", "ano"],
    "maiores": ["ano", "posicao", "ilha", "setor"],
    "emprego_publico": ["quadro", "local", "data"],
    "censos2021_setores": ["ilha", "secao"],
    "at_irs": ["quadro", "medida", "ano", "regiao"],
    "at_irc": ["quadro", "ano", "regiao"],
    "at_distritos": ["imposto", "medida", "ano", "regiao"],
    "bportugal": ["indicador", "regiao", "data"],
    "prr_projetos": ["projeto", "investimento_codigo", "inicio"],
    "prr_entidades": ["projeto", "nif", "entidade", "papel"],
    "kohesio_projetos": ["programa", "periodo", "fundo", "inicio"],
    "kohesio_beneficiarios": ["beneficiario"],
}
DB_FTS = {
    "base": ["objeto", "adjudicante", "adjudicatario", "procedimento", "cpv"],
    "alra": ["titulo", "autores", "estado", "tipo"],
    "joraa": ["titulo", "ato", "entidade"],
    "ine": ["indicador", "tema", "local", "concelho", "ilha", "categoria"],
    "beo": ["quadro", "rubrica", "caminho", "dimensao"],
    "tdc": ["tipo", "texto", "referencia", "situacao"],
    "tdc_valores": ["quadro", "rubrica", "caminho"],
    "srea": ["indicador", "rubrica", "local"],
    "sper": ["empresa", "indicador"],
    "sper_empresas": ["empresa", "acionista", "nota"],
    "sper_regiao": ["quadro", "grupo", "rubrica"],
    "maiores": ["empresa", "ilha", "setor"],
    "emprego_publico": ["indicador", "rubrica", "local"],
    "censos2021_setores": ["concelho", "ilha"],
    "at_irs": ["quadro", "medida", "regiao", "taxa", "titularidade"],
    "at_irc": ["quadro", "medida", "regiao", "escalao"],
    "at_distritos": ["imposto", "medida", "distrito", "regiao"],
    # bportugal: numbers with a handful of labels; facets do the search
    "prr_projetos": ["designacao", "componente", "investimento", "concelhos"],
    "prr_entidades": ["entidade", "sede"],
    "kohesio_projetos": ["projeto", "programa"],
    "kohesio_beneficiarios": ["beneficiario"],
}


def tdc_latest(cols: list[str], rows: list[list]) -> dict:
    """The latest parecer: its year, verdict and PDF, for the home page."""
    c, t = cols.index("conta"), cols.index("tipo")
    juizos = [r for r in rows if r[t] == "juízo"]
    if not juizos:
        return {}
    r = max(juizos, key=lambda r: int(r[c]))
    return {
        "conta": r[c],
        "juizo": r[cols.index("texto")],
        "url": r[cols.index("parecer")],
    }


def beo_latest(cols: list[str], rows: list[list]) -> dict:
    """The latest boletim: its month and PDF, for the home page."""
    i, d, b = cols.index("quadro"), cols.index("data"), cols.index("boletim")
    own = [r for r in rows if r[i] == "Síntese global"]
    if not own:
        return {}
    last = max(own, key=lambda r: r[d])
    year, month = int(last[d][:4]), int(last[d][5:7])
    return {
        "data": last[d],
        "periodo": f"{MESES[month - 1]} de {year}",
        "url": last[b],
    }


MESES = [
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
]


def write_db(path: Path, tables: dict[str, tuple[list, list]]) -> None:
    """Write tables to a fresh SQLite file. Each table in DB_FTS gets an
    external content FTS5 index declared as content=[table], the form
    Datasette detects to show a search box."""
    tmp = path.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    con = sqlite3.connect(tmp)
    for name, (cols, rows) in tables.items():
        decl = ", ".join(f"[{c}] {DB_TYPES.get(c, 'TEXT')}" for c in cols)
        con.execute(
            f"CREATE TABLE [{name}] (rowid INTEGER PRIMARY KEY, {decl})"
        )
        marks = ", ".join("?" * len(cols))
        names = ", ".join(f"[{c}]" for c in cols)
        con.executemany(
            f"INSERT INTO [{name}] ({names}) VALUES ({marks})",
            ([None if v == "" else v for v in r] for r in rows),
        )
        for c in DB_INDEX[name]:
            con.execute(f"CREATE INDEX [idx_{name}_{c}] ON [{name}] ([{c}])")
        if name not in DB_FTS:
            continue
        fts = ", ".join(f"[{c}]" for c in DB_FTS[name])
        con.execute(
            f"CREATE VIRTUAL TABLE [{name}_fts] USING fts5({fts}, "
            f"content=[{name}], tokenize='unicode61 remove_diacritics 2')"
        )
        con.execute(
            f"INSERT INTO [{name}_fts]([{name}_fts]) VALUES('rebuild')"
        )
    con.commit()
    con.execute("VACUUM")
    con.close()
    tmp.replace(path)


# SQLite files under docs/dados/, one per theme, so that Datasette Lite (which
# downloads the whole file) opens only what a query needs. Every table goes
# in exactly one; a query can only join tables of the same file.
BASES = {
    "contratos": ["base"],
    "parlamento": ["alra", "joraa"],
    "financas": [
        "beo",
        "tdc",
        "tdc_valores",
        "at_irs",
        "at_irc",
        "at_distritos",
    ],
    "estatisticas": ["ine", "srea", "emprego_publico", "censos2021_setores"],
    "empresas": [
        "bportugal",
        "sper",
        "sper_empresas",
        "sper_regiao",
        "maiores",
    ],
    "fundos": [
        "prr_projetos",
        "prr_entidades",
        "kohesio_projetos",
        "kohesio_beneficiarios",
    ],
}


def write_dbs(out: Path, tables: dict[str, tuple[list, list]]) -> dict:
    """One SQLite file per entry of BASES; {name: {tabelas, bytes}}."""
    sem_base = set(tables) - {t for ts in BASES.values() for t in ts}
    if sem_base:
        raise ValueError(f"Tables in no database (BASES): {sorted(sem_base)}")
    (out / "acores.db").unlink(missing_ok=True)  # the old single file
    info = {}
    for name, names in BASES.items():
        got = {t: tables[t] for t in names if t in tables}
        if not got:
            continue
        path = out / f"{name}.db"
        write_db(path, got)
        info[name] = {"tabelas": list(got), "bytes": path.stat().st_size}
    return info


def ine_news(cols: list[str], rows: list[list], limit: int = 8) -> list[dict]:
    """Indicators most recently updated by INE, newest first, with the
    latest period they cover."""
    c = {k: i for i, k in enumerate(cols)}
    by: dict[str, dict] = {}
    for r in rows:
        x = by.setdefault(
            r[c["varcd"]],
            {
                "varcd": r[c["varcd"]],
                "indicador": r[c["indicador"]],
                "tema": r[c["tema"]],
                "atualizado": r[c["atualizado"]],
                "data": "",
                "periodo": "",
            },
        )
        if r[c["geocod"]] == "20" and r[c["data"]] > x["data"]:
            x["data"], x["periodo"] = r[c["data"]], r[c["periodo"]]
    news = sorted(
        by.values(), key=lambda x: (x["atualizado"], x["data"]), reverse=True
    )
    return news[:limit]


def write_ine_news(docs: Path, cols: list[str], rows: list[list]) -> None:
    """docs/_data/ine_novidades.json, for the home page (Jekyll reads _data
    at build time; pages.yml runs this script before Jekyll)."""
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "ine_novidades.json").write_text(
        json.dumps(ine_news(cols, rows), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )


# Indicators shown on /introducao/ (Açores vs Madeira vs país, latest year).
RESUMO_INE = (
    "0012918",  # população residente
    "0012909",  # índice de envelhecimento
    "0012757",  # rendimento mediano após IRS por sujeito passivo
    "0012656",  # ganho médio mensal
    "0013420",  # RSI por 1000 habitantes
    "0014698",  # renda mediana, novos contratos (€/m²)
    "0013210",  # dormidas por 100 habitantes
    "0014103",  # PIB por habitante
    "0014663",  # inflação (IPC, variação homóloga)
    "0012136",  # taxa de desemprego, trimestral
    "0012749",  # rendimento bruto mediano por sujeito passivo
)
PIB_HAB, MEDIANA_BRUTO, GANHO = "0014103", "0012749", "0012656"


def salario_pib(cols: list[str], rows: list[list]) -> dict:
    """Gross pay against GDP per head, Açores/Madeira/país, for the latest
    year with the three series: the median gross income declared per
    taxpayer (IRS, annual) and the mean monthly earnings (Quadros de
    Pessoal) times 14, an açores.net estimate of a year's pay."""
    c = {k: i for i, k in enumerate(cols)}
    val: dict[tuple, float] = {}
    url = {}
    for r in rows:
        v, g = r[c["varcd"]], r[c["geocod"]]
        if v in (PIB_HAB, MEDIANA_BRUTO, GANHO) and g in ("20", "30", "PT"):
            if not r[c["categoria"]] and (x := _num(r[c["valor"]])):
                val[(v, g, r[c["periodo"]])] = x
                url[v] = r[c["url"]]
    anos = [
        a
        for a in {k[2] for k in val}
        if all(
            (v, g, a) in val
            for v in (PIB_HAB, MEDIANA_BRUTO, GANHO)
            for g in ("20", "30", "PT")
        )
    ]
    if not anos:
        return {}
    ano = max(anos)
    locais = []
    for g, nome in (("20", "Açores"), ("30", "Madeira"), ("PT", "Portugal")):
        pib = val[(PIB_HAB, g, ano)]
        med = val[(MEDIANA_BRUTO, g, ano)]
        ganho = val[(GANHO, g, ano)]
        locais.append(
            {
                "local": nome,
                "pib": pib,
                "mediana": med,
                "mediana_pct": round(100 * med / pib),
                "ganho": ganho,
                "ganho_ano": round(ganho * 14),
                "ganho_pct": round(100 * ganho * 14 / pib),
            }
        )
    return {
        "ano": ano,
        "locais": locais,
        "url_pib": url[PIB_HAB],
        "url_mediana": url[MEDIANA_BRUTO],
        "url_ganho": url[GANHO],
    }


def _num(v: str) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def resumo_ine(cols: list[str], rows: list[list]) -> dict:
    """Latest Região/país values of RESUMO_INE, plus population by island."""
    c = {k: i for i, k in enumerate(cols)}
    out: dict = {}
    for v in RESUMO_INE:
        own = [r for r in rows if r[c["varcd"]] == v and not r[c["categoria"]]]
        top = [r for r in own if r[c["geocod"]] in ("20", "30", "PT")]
        if not top:
            continue
        last = max(r[c["data"]] for r in top)
        x = {"periodo": "", "url": "", "unidade": ""}
        for r in top:
            if r[c["data"]] != last:
                continue
            key = {"20": "acores", "30": "madeira", "PT": "pt"}[r[c["geocod"]]]
            x[key] = _num(r[c["valor"]])
            x["periodo"], x["url"] = r[c["periodo"]], r[c["url"]]
            x["unidade"] = r[c["unidade"]]
        if v == "0012918":
            ilhas: dict[str, float] = {}
            for r in own:
                if r[c["data"]] == last and r[c["nivel"]] == "Concelho":
                    n = _num(r[c["valor"]]) or 0
                    ilhas[r[c["ilha"]]] = ilhas.get(r[c["ilha"]], 0) + n
            x["ilhas"] = [
                {"ilha": k, "valor": round(n)}
                for k, n in sorted(ilhas.items(), key=lambda t: -t[1])
            ]
        out[v] = x
    return out


def resumo_beo(cols: list[str], rows: list[list]) -> dict:
    """The last complete year of the budget execution bulletins, consolidated:
    where the money came from, what it paid and the balance (millions of €)."""
    c = {k: i for i, k in enumerate(cols)}
    euro = [r for r in rows if r[c["medida"]] == "Montante (€)"]
    sint = [
        r
        for r in euro
        if r[c["quadro"]] == "Síntese global"
        and r[c["dimensao"]] == "Consolidado"
    ]
    anos = sorted({r[c["ano"]] for r in sint if r[c["mes"]] == "12"})
    if not anos:
        return {}
    ano = anos[-1]
    dez = [r for r in sint if r[c["ano"]] == ano and r[c["mes"]] == "12"]
    by = {r[c["caminho"]]: _num(r[c["valor"]]) or 0.0 for r in dez}

    def m(*paths: str) -> float:
        return round(sum(by.get(p, 0.0) for p in paths) / 1e6, 1)

    rc, rk = "Receita corrente › ", "Receita de capital › "
    receita = m("Receita efetiva")
    impostos = m(rc + "Impostos diretos", rc + "Impostos indiretos")
    estado = m(
        rc + "Transferências correntes › Administração central - Estado",
        rk + "Transferências de capital › Administração central - Estado",
    )
    exterior = m(
        rc + "Transferências correntes › Resto do mundo",
        rk + "Transferências de capital › Resto do mundo",
    )
    dc = "Despesa corrente › "
    despesa = m("Despesa efetiva")
    pessoal = m(dc + "Despesas com pessoal")
    bens = m(dc + "Aquisição de bens e serviços correntes")
    juros = m(dc + "Juros e outros encargos")
    capital = m("Despesa de capital")
    func = [
        r
        for r in euro
        if r[c["quadro"]] == "Despesa do GRA por função"
        and r[c["ano"]] == ano
        and r[c["mes"]] == "12"
        and r[c["nivel"]] == "1"
    ]
    funcoes = sorted(
        (
            {
                "nome": r[c["rubrica"]].removesuffix(" n.e."),
                "valor": round((_num(r[c["valor"]]) or 0) / 1e6, 1),
            }
            for r in func
        ),
        key=lambda x: -x["valor"],
    )
    total_f = round(sum(x["valor"] for x in funcoes), 1)
    if len(funcoes) > 5:
        resto = round(total_f - sum(x["valor"] for x in funcoes[:5]), 1)
        funcoes = funcoes[:5] + [{"nome": "Todas as outras", "valor": resto}]
    return {
        "ano": ano,
        "boletim": dez[0][c["boletim"]] if dez else "",
        "receita": receita,
        "receitas": [
            {"nome": "Impostos cobrados nos Açores", "valor": impostos},
            {"nome": "Transferências do Estado", "valor": estado},
            {
                "nome": "Do exterior (sobretudo fundos europeus)",
                "valor": exterior,
            },
            {
                "nome": "Outras receitas",
                "valor": round(receita - impostos - estado - exterior, 1),
            },
        ],
        "despesa": despesa,
        "despesas": [
            {"nome": "Salários e outros custos com pessoal", "valor": pessoal},
            {"nome": "Compras de bens e serviços", "valor": bens},
            {
                "nome": "Investimento e apoios ao investimento",
                "valor": capital,
            },
            {"nome": "Juros da dívida", "valor": juros},
            {
                "nome": "Outras despesas",
                "valor": round(despesa - pessoal - bens - capital - juros, 1),
            },
        ],
        "saldo": m("Saldo global"),
        "saldo_abs": abs(m("Saldo global")),
        "funcoes": funcoes,
        "funcoes_total": total_f,
    }


def srea_json(cols: list[str], rows: list[list]) -> list[dict]:
    """data/srea.csv grouped by series, for the charts on /dados/srea/:
    one entry per (serie, indicador, rubrica, local) with its points."""
    c = {k: i for i, k in enumerate(cols)}
    by: dict[tuple, dict] = {}
    for r in sorted(rows, key=lambda r: r[c["data"]]):
        k = tuple(r[c[x]] for x in ("serie", "indicador", "rubrica", "local"))
        s = by.setdefault(
            k,
            {
                "serie": k[0],
                "indicador": k[1],
                "rubrica": k[2],
                "local": k[3],
                "unidade": r[c["unidade"]],
                "pagina": r[c["pagina"]],
                "p": [],
            },
        )
        s["ficheiro"] = r[c["ficheiro"]]
        p = [r[c["periodo"]], _num(r[c["valor"]])]
        if r[c["nota"]]:
            p.append(r[c["nota"]])
        s["p"].append(p)
    return list(by.values())


def _mes(data: str) -> str:
    return f"{MESES[int(data[5:7]) - 1]} de {data[:4]}"


def resumo_srea(cols: list[str], rows: list[list]) -> dict:
    """Latest SREA figures for /introducao/ and /dados/srea/."""
    c = {k: i for i, k in enumerate(cols)}

    def pts(serie, indicador, rubrica="Total", local="Açores") -> list:
        return sorted(
            (
                r
                for r in rows
                if r[c["serie"]] == serie
                and r[c["indicador"]] == indicador
                and r[c["rubrica"]] == rubrica
                and r[c["local"]] == local
            ),
            key=lambda r: r[c["data"]],
        )

    def v(r) -> float:
        return _num(r[c["valor"]]) or 0.0

    out: dict = {}
    vh = pts("ipc", "Variação homóloga")
    if vh:
        last = vh[-1]
        m12 = {
            r[c["data"]]: v(r)
            for r in pts("ipc", "Variação média dos últimos 12 meses")
        }
        classes = sorted(
            (
                {"nome": r[c["rubrica"]], "valor": v(r)}
                for r in rows
                if r[c["serie"]] == "ipc"
                and r[c["indicador"]] == "Variação homóloga"
                and r[c["rubrica"]] != "Total"
                and r[c["data"]] == last[c["data"]]
            ),
            key=lambda x: -x["valor"],
        )
        out["ipc"] = {
            "valor": v(last),
            "cem": round(100 + v(last), 2),
            "media12": m12.get(last[c["data"]]),
            "periodo": _mes(last[c["data"]]),
            "antes": _mes(
                f"{int(last[c['data']][:4]) - 1}{last[c['data']][4:]}"
            ),
            "mais": classes[:3],
            "menos": classes[-2:][::-1],
            "url": last[c["pagina"]],
        }
    for serie, ind in (
        ("iae", "Indicador de atividade económica"),
        ("icp", "Indicador do consumo privado"),
    ):
        s = pts(serie, ind)
        if s:
            out[serie] = {
                "valor": round(v(s[-1]), 1),
                "periodo": _mes(s[-1][c["data"]]),
                "url": s[-1][c["pagina"]],
            }
    d = pts("desemprego", "Taxa de desemprego")
    if d:
        last = d[-1]
        y, q = last[c["periodo"]].split("-T")
        prev = {r[c["periodo"]]: v(r) for r in d}.get(f"{int(y) - 1}-T{q}")
        out["desemprego"] = {
            "valor": v(last),
            "antes": prev,
            "periodo": f"{q}.º trimestre de {y}",
            "periodo_antes": f"{q}.º trimestre de {int(y) - 1}",
            "nota": last[c["nota"]],
            "url": last[c["pagina"]],
        }
    dorm = [r for r in rows if r[c["serie"]] == "dormidas"]
    if dorm:
        # the last month both kinds of accommodation have published
        last = min(
            max(r[c["data"]] for r in dorm if r[c["rubrica"]] == k)
            for k in {r[c["rubrica"]] for r in dorm}
        )
        y, m = int(last[:4]), int(last[5:7])

        def ytd(local, year):
            return sum(
                v(r)
                for r in dorm
                if r[c["local"]] == local
                and r[c["data"]][:4] == str(year)
                and int(r[c["data"]][5:7]) <= m
            )

        ilhas = []
        for local in sorted({r[c["local"]] for r in dorm} - {"Açores"}):
            a, b = ytd(local, y), ytd(local, y - 1)
            ilhas.append(
                {
                    "ilha": local,
                    "valor": round(a),
                    "var": round(100 * (a - b) / b, 1) if b else None,
                }
            )
        ilhas.sort(key=lambda x: -x["valor"])
        a, b = ytd("Açores", y), ytd("Açores", y - 1)
        out["dormidas"] = {
            "valor": round(a),
            "antes": round(b),
            "var": round(100 * (a - b) / b, 1) if b else None,
            "periodo": (
                f"janeiro a {MESES[m - 1]} de {y}"
                if m > 1
                else f"janeiro de {y}"
            ),
            "ilhas": ilhas,
            "url": dorm[0][c["pagina"]],
        }
    ph = [r for r in rows if r[c["serie"]] == "pib_hab"]
    if ph:
        ano = max(r[c["periodo"]] for r in ph)
        last = [r for r in ph if r[c["periodo"]] == ano]
        top = max(v(r) for r in last if r[c["local"]] != "Açores")
        reg = next((r for r in last if r[c["local"]] == "Açores"), None)
        total = next(
            (
                v(r)
                for r in rows
                if r[c["serie"]] == "pib"
                and r[c["local"]] == "Açores"
                and r[c["periodo"]] == ano
            ),
            None,
        )
        out["pib_hab"] = {
            "ano": ano,
            "provisorio": any(r[c["nota"]] for r in last),
            "acores": v(reg) if reg else None,
            "total_mm": round(total / 1e9, 1) if total else None,
            "por_ilha": [
                {
                    "ilha": r[c["local"]],
                    "valor": v(r),
                    "pct": round(100 * v(r) / top),
                }
                for r in sorted(last, key=lambda r: -v(r))
                if r[c["local"]] != "Açores"
            ],
            "url": last[0][c["pagina"]],
        }
    return out


def resumo_tdc(tdc: tuple[list, list], valores: tuple[list, list]) -> dict:
    """Latest Tribunal de Contas parecer for /financas/: debt, deficit,
    money left out of the Conta, reservations and what happened to the
    recommendations of the previous parecer."""
    cols, rows = tdc
    t = [dict(zip(cols, r, strict=False)) for r in rows]
    if not t:
        return {}
    conta = max(r["conta"] for r in t)
    last = [r for r in t if r["conta"] == conta]
    out: dict = {
        "conta": conta,
        "url": last[0]["parecer"],
        "juizo": next((r["texto"] for r in last if r["tipo"] == "juízo"), ""),
        "reservas": sum(r["tipo"] == "reserva" for r in last),
        "recomendacoes": sum(r["tipo"] == "recomendação" for r in last),
    }
    # Recommendations of the previous parecer, as assessed in this one.
    prev = [
        r
        for r in t
        if r["tipo"] == "recomendação" and r["situacao"].endswith(f"({conta})")
    ]
    if prev:
        estados: dict[str, int] = {}
        for r in prev:
            k = r["situacao"].rsplit(" (", 1)[0]
            estados[k] = estados.get(k, 0) + 1
        out["avaliadas"] = len(prev)
        out["estados"] = [{"nome": k, "n": n} for k, n in estados.items()]
        desde = [int(r["desde"]) for r in prev if r["desde"].isdigit()]
        if desde:
            out["desde"] = min(desde)
    vcols, vrows = valores
    v = [dict(zip(vcols, r, strict=False)) for r in vrows]

    def val(rubrica: str, ano: str, quadro: str) -> float | None:
        for r in v:
            if (r["rubrica"], r["ano"], r["quadro"]) == (rubrica, ano, quadro):
                return _num(r["valor"])
        return None

    ind, conta_q = (
        "Indicadores",
        "Conta do sector público administrativo regional",
    )
    anterior = str(int(conta) - 1)
    divida = val("Dívida total", conta, ind)
    divida_ant = val("Dívida total", anterior, ind)
    if divida is not None:
        out["divida"] = divida
        if divida_ant:
            out["divida_var"] = round(100 * (divida / divida_ant - 1), 1)
    saldo = val("Saldo global ou efetivo", conta, conta_q)
    if saldo is not None:
        out["saldo"] = round(saldo / 1e6, 1)
        out["saldo_abs"] = abs(out["saldo"])
    for k, rub in (
        ("receita_fora", "Receita não registada na Conta"),
        ("despesa_fora", "Despesa não registada na Conta"),
    ):
        x = val(rub, conta, ind)
        if x is not None:
            out[k] = x
    return out


def _dicts(table: tuple[list, list]) -> list[dict]:
    cols, rows = table
    return [dict(zip(cols, r, strict=False)) for r in rows]


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _rel_key(rel: str) -> tuple[int, int]:
    n, y = rel.split("/")
    return int(y), int(n)


# CAE Rev. 3 sections, as the CFP list gives them (one letter).
CAE = {
    "A": "Agricultura e pesca",
    "C": "Indústria",
    "D": "Eletricidade e gás",
    "E": "Água e resíduos",
    "F": "Construção",
    "G": "Comércio",
    "H": "Transportes",
    "I": "Alojamento e restauração",
    "J": "Informação e comunicação",
    "L": "Imobiliário",
    "M": "Atividades técnicas",
    "N": "Serviços administrativos",
    "O": "Administração pública",
    "Q": "Saúde",
    "R": "Cultura e espetáculos",
}
SPER_IND = {
    "trabalhadores": "Número de Trabalhadores",
    "vn": "Volume de Negócios",
    "vab": "Valor Acrescentado Bruto (VAB)",
    "ebitda": "EBITDA",
    "rl": "Resultado Líquido",
    "cp": "Capital Próprio",
    "passivo": "Total do Passivo",
    "ativo": "Total do Ativo",
    "pessoal": "Gastos com Pessoal",
}
ESFORCO = "Esforço financeiro líquido da Região"
ESFORCO_TOTAL = "Esforço financeiro líquido (2)-(1)"


def sper_data(
    sper: tuple[list, list],
    empresas: tuple[list, list] | None = None,
    regiao: tuple[list, list] | None = None,
) -> dict:
    """data/sper*.csv (bot/cfp.py) for /dados/sper/ and /economia/: sector
    totals by year, one entry per company for the latest year, the
    Region's net financial effort and the sector's weight."""
    v = _dicts(sper)
    if not v:
        return {}
    by = {
        (r["sigla"], int(r["ano"]), r["indicador"]): _num(r["valor"])
        for r in v
    }
    anos = sorted({int(r["ano"]) for r in v})
    ano = anos[-1]
    rel = max({r["relatorio"] for r in v}, key=_rel_key)
    last = next(r for r in v if r["relatorio"] == rel)
    siglas = sorted({r["sigla"] for r in v})

    def amount(k: str, x: float, dec: int = 2) -> float:
        """People as integers, money in million euros (+ 0.0 drops -0.0)."""
        return int(x) if k == "trabalhadores" else round(x / 1e6, dec) + 0.0

    totais = []
    for a in anos:
        t: dict = {"ano": a}
        for k, ind in SPER_IND.items():
            xs = [
                by[s, a, ind]
                for s in siglas
                if by.get((s, a, ind)) is not None
            ]
            if xs:
                t[k] = amount(k, sum(xs), 1)
        t["prejuizo"] = sum(
            1 for s in siglas if (by.get((s, a, SPER_IND["rl"])) or 0) < 0
        )
        totais.append(t)
    out: dict = {
        "relatorio": rel,
        "url": last["url"],
        "ficheiro": last.get("ficheiro", ""),
        "ano": ano,
        "anos": [{"ano": a} for a in anos],
        "totais": totais,
        "total": totais[-1],
    }
    lista = (
        [e for e in _dicts(empresas) if e["relatorio"] == rel]
        if empresas
        else []
    )
    emp = []
    for e in lista or [{"sigla": s, "empresa": s} for s in siglas]:
        s = e["sigla"]
        part = _num(e.get("participacao", ""))
        d: dict = {
            "sigla": s,
            "nome": _curto(e["empresa"], s),
            "empresa": e["empresa"],
            "setor": CAE.get(e.get("cae", ""), e.get("cae", "")),
            "acionista": e.get("acionista", ""),
            "ap": e.get("ap") == "sim",
            "nota": e.get("nota", ""),
        }
        if part is not None:
            d["participacao"] = round(100 * part, 1)
        for k, ind in SPER_IND.items():
            x = by.get((s, ano, ind))
            if x is not None:
                d[k] = amount(k, x)
        d["rl_anos"] = [
            (
                {"ano": a, "v": amount("rl", by[s, a, SPER_IND["rl"]])}
                if by.get((s, a, SPER_IND["rl"])) is not None
                else {"ano": a}
            )
            for a in anos
        ]
        emp.append(d)
    emp.sort(key=lambda d: -d.get("vn", -1e9))
    out["empresas"] = emp
    out["n"] = len(emp)
    out["sem_ficha"] = [d["nome"] for d in emp if "vn" not in d]
    out["cp_negativo"] = [d["nome"] for d in emp if d.get("cp", 0) < 0]
    if regiao:
        out.update(_sper_regiao(_dicts(regiao), rel))
    return out


def _sper_regiao(rows: list[dict], rel: str) -> dict:
    out: dict = {}
    mine = [r for r in rows if r["relatorio"] == rel]
    esf = [r for r in mine if r["quadro"] == ESFORCO]
    if esf:
        anos = sorted({int(r["ano"]) for r in esf})
        linhas: dict[str, dict] = {}
        for r in esf:
            ln = linhas.setdefault(
                r["rubrica"],
                {"rubrica": r["rubrica"], "unidade": r["unidade"], "v": {}},
            )
            ln["v"][int(r["ano"])] = _num(r["valor"])
        out["esforco"] = {
            "relatorio": rel,
            "url": esf[0]["url"],
            "nota": next((r["nota"] for r in esf if r["nota"]), ""),
            "anos": [{"ano": a} for a in anos],
            "linhas": [
                {
                    "rubrica": ln["rubrica"],
                    "unidade": ln["unidade"],
                    "total": ln["rubrica"].startswith("Esforço"),
                    "valores": [
                        {"v": ln["v"][a]} if a in ln["v"] else {} for a in anos
                    ],
                }
                for ln in linhas.values()
            ],
        }
        tot = {
            int(r["ano"]): _num(r["valor"])
            for r in esf
            if r["rubrica"] == ESFORCO_TOTAL
        }
        if tot:
            a = max(tot)
            out["esforco"].update(ano=a, total=tot[a])
            # The same year in an older report, when the method differed.
            for r in rows:
                if (
                    r["relatorio"] != rel
                    and r["quadro"] == ESFORCO
                    and r["rubrica"] == ESFORCO_TOTAL
                    and int(r["ano"]) in tot
                    and abs(_num(r["valor"]) - tot[int(r["ano"])]) > 1
                ):
                    out["esforco"]["antes"] = {
                        "relatorio": r["relatorio"],
                        "url": r["url"],
                        "ano": int(r["ano"]),
                        "valor": _num(r["valor"]),
                        "agora": tot[int(r["ano"])],
                    }
    peso = [r for r in mine if r["quadro"] == "Peso na economia"]
    for k, start in (
        ("vab_pib", "Peso do SERAA"),
        ("emprego", "Proporção do SERAA"),
    ):
        xs = [r for r in peso if r["rubrica"].startswith(start)]
        if xs:
            r = max(xs, key=lambda r: int(r["ano"]))
            out[k] = round(_num(r["valor"]), 1)
            out["peso_ano"] = int(r["ano"])
    return out


def _curto(empresa: str, sigla: str) -> str:
    """Readable short name: 'Sata Air Açores, S.A.' -> 'SATA Air Açores',
    'HDES - Hospital Divino Espirito Santo, E.P.E.R.' -> 'HDES'."""
    nome = empresa.split(",")[0].strip()
    if " - " in nome or len(nome) > 22:
        return sigla
    return re.sub(r"^Sata\b", "SATA", nome)


def _company_keys(name: str, loose: bool) -> set[str]:
    out = {_fold(name.split(",")[0])}
    if loose:
        out.add(_fold(name.split(" - ")[0]))
    return out


def maiores_data(
    maiores: tuple[list, list], sper_lista: list[dict] | None = None
) -> dict:
    """The largest companies (data/maiores_<ano>.csv, in thousands of euros)
    for /dados/maiores-empresas/ and /economia/, with the regional public
    companies among them marked."""
    m = _dicts(maiores)
    if not m:
        return {}
    # Full CFP names only: a sigla such as "SATA" would also match a private
    # "SATA - ..." company by its loose key.
    publicas = {}
    for e in sper_lista or []:
        for k in _company_keys(e["empresa"], False):
            publicas[k] = e["sigla"]

    def num(x: str) -> float:
        return _num(x) or 0.0

    emp = []
    for r in m:
        sigla = next(
            (
                publicas[k]
                for k in _company_keys(r["empresa"], True)
                if k in publicas
            ),
            "",
        )
        d = {
            "posicao": int(r["posicao"]),
            "empresa": r["empresa"],
            "ilha": r["ilha"],
            "setor": r["setor"],
            "trabalhadores": int(num(r["trabalhadores"])),
            "vn": round(num(r["volume_negocios"]) / 1e3, 1),
            "rl": round(num(r["resultado_liquido"]) / 1e3, 1),
            "publica": sigla,
        }
        if r["cresc_vn_pct"]:
            d["cresc_vn"] = num(r["cresc_vn_pct"])
        emp.append(d)
    emp.sort(key=lambda d: d["posicao"])
    vn = sum(d["vn"] for d in emp)

    def groups(key: str) -> list[dict]:
        g: dict[str, dict] = {}
        for d in emp:
            x = g.setdefault(
                d[key], {"nome": d[key], "n": 0, "vn": 0.0, "trabalhadores": 0}
            )
            x["n"] += 1
            x["vn"] += d["vn"]
            x["trabalhadores"] += d["trabalhadores"]
        out = sorted(g.values(), key=lambda x: -x["vn"])
        for x in out:
            x["vn"] = round(x["vn"], 1)
            x["pct"] = round(100 * x["vn"] / vn) if vn else 0
        return out

    pub = [d for d in emp if d["publica"]]
    return {
        "ano": int(m[0]["ano"]),
        "fonte": m[0]["fonte"],
        "url": m[0]["url"],
        "n": len(emp),
        "vn": round(vn, 1),
        "trabalhadores": sum(d["trabalhadores"] for d in emp),
        "top10_pct": (
            round(100 * sum(d["vn"] for d in emp[:10]) / vn) if vn else 0
        ),
        "prejuizo": sum(1 for d in emp if d["rl"] < 0),
        "publicas": len(pub),
        "publicas_pct": (
            round(100 * sum(d["vn"] for d in pub) / vn) if vn else 0
        ),
        "privadas": len(emp) - len(pub),
        "privadas_vn": round(vn - sum(d["vn"] for d in pub), 1),
        "privadas_trabalhadores": sum(
            d["trabalhadores"] for d in emp if not d["publica"]
        ),
        "setores": groups("setor"),
        "ilhas": groups("ilha"),
        "empresas": emp,
    }


AR_ACORES = "ADMINISTRAÇÃO REGIONAL DOS AÇORES"
AR_SER = "dos quais: SER - Entid. Reclassif."
AR_FORA = {
    AR_ACORES,
    "Órgãos do Governo Regional dos Açores",
    "Serviços e Fundos Autónomos da AR dos Açores",
}
CARREIRAS = {
    "Educ.infância e doc. ens. básico/secund.": (
        "Educadores de infância e professores do básico e secundário"
    ),
    "Assist. operacional/operário/auxiliar": (
        "Assistentes operacionais, operários e auxiliares"
    ),
    "Assistente técnico/administrativo": (
        "Assistentes técnicos e administrativos"
    ),
    "Técnico superior": "Técnicos superiores",
    "Enfermeiro": "Enfermeiros",
    "Médico": "Médicos",
    "Técnico diagnóstico e terapêutica": (
        "Técnicos de diagnóstico e terapêutica"
    ),
    "Técnico superior de saúde": "Técnicos superiores de saúde",
    "Docente ensino universitário": "Professores universitários",
    "Representantes do poder legislativo": (
        "Eleitos e membros de órgãos executivos"
    ),
    "Dirigente intermédio": "Dirigentes intermédios",
    "Dirigente superior": "Dirigentes superiores",
    "Informático": "Informáticos",
    "Magistrado": "Magistrados",
    "Oficial de justiça": "Oficiais de justiça",
    "Pessoal de inspeção": "Inspetores",
    "Polícia municipal": "Polícia municipal",
}
# the sub-rows of a group in Q1.7 ("Dirigente superior de 1.º grau",
# "Forças Armadas - Oficial", ...)
SUBCARREIRA = re.compile(r" de \d\.º| - ")
MESES_DGAEP = {
    "01": "janeiro",
    "04": "abril",
    "07": "julho",
    "10": "outubro",
}


def _dia(data: str) -> str:
    """'2026-09-30' -> '30 de setembro de 2026'."""
    return f"{int(data[8:10])} de {_mes(data)}"


def publico_data(
    emprego: tuple[list, list],
    srea: tuple[list, list] | None = None,
    sper: dict | None = None,
    ine: tuple[list, list] | None = None,
    censos: tuple[list, list] | None = None,
) -> dict:
    """data/emprego_publico.csv (bot/dgaep.py) for /economia/setor-publico/:
    jobs in general government in the Azores by career, the regional
    administration by department, the yearly series and pay; with the SREA
    employment survey and the CFP's market companies, the public and
    private shares of the jobs in the Azores (an estimate, see the page)."""
    rows = _dicts(emprego)
    if not rows:
        return {}

    def serie(quadro, rubrica, local="Açores", indicador=None) -> dict:
        return {
            r["data"]: _num(r["valor"])
            for r in rows
            if r["quadro"] == quadro
            and r["rubrica"] == rubrica
            and r["local"] == local
            and (indicador is None or r["indicador"] == indicador)
        }

    ar = serie("Q1.1", AR_ACORES)
    ap = serie("Q1.7", "Total")
    pt = serie("Q1.7", "Total", "Portugal")
    if not ar or not ap:
        return {}
    last = max(ar)
    antes = f"{int(last[:4]) - 1}{last[4:]}"
    q11 = [r for r in rows if r["quadro"] == "Q1.1" and r["local"] == "Açores"]
    fss = serie(
        "Q1.1",
        next(
            (r["rubrica"] for r in q11 if r["rubrica"].startswith("Fundos")),
            "",
        ),
    )
    out: dict = {
        "data": last,
        "periodo": _dia(last),
        "provisorio": any(r["provisorio"] for r in rows if r["data"] == last),
        "ficheiro": rows[0]["ficheiro"],
        "pagina": rows[0]["pagina"],
        "ap": int(ap[last]),
        "ap_var": int(ap[last] - ap[antes]) if antes in ap else None,
        "ap_pct_pais": (
            round(100 * ap[last] / pt[last], 1) if pt.get(last) else None
        ),
        "ar": int(ar[last]),
        "ar_var": int(ar[last] - ar[antes]) if antes in ar else None,
        "ar_inicio": int(ar[min(ar)]),
        "ano_inicio": int(min(ar)[:4]),
        "fss": int(fss.get(last) or 0),
    }
    # the rest of general government in the Azores: the State's services
    # (courts, university, ...) and the municipalities and parishes
    out["outros"] = out["ap"] - out["ar"] - out["fss"]

    # regional administration by department; the reclassified companies
    # (the hospitals EPE) are counted apart from the departments, and the
    # two add up to the total
    deps = []
    for _ordem, rub in sorted({(int(r["ordem"]), r["rubrica"]) for r in q11}):
        if rub in AR_FORA or rub.startswith("Fundos"):
            continue
        x = serie("Q1.1", rub)
        if last not in x:
            continue
        nome = rub
        if rub == AR_SER:
            nome = "Hospitais EPE e outras empresas públicas contadas como administração"
        elif rub == "Órgãos de Soberania e Entidades Independentes":
            nome = "Assembleia Legislativa e outros órgãos independentes"
        deps.append(
            {
                "nome": nome,
                "valor": int(x[last]),
                "var": int(x[last] - x[antes]) if antes in x else None,
                "pct": round(100 * x[last] / ar[last], 1),
                "ser": rub == AR_SER,
            }
        )
    deps.sort(key=lambda d: (d["ser"], -d["valor"]))
    out["secretarias"] = deps
    out["secretarias_soma_ok"] = sum(d["valor"] for d in deps) == out["ar"]

    # by career, everybody in general government in the Azores
    q17 = {
        r["rubrica"]
        for r in rows
        if r["quadro"] == "Q1.7" and r["local"] == "Açores"
    }
    car = []
    for rub in q17 - {"Total"}:
        if SUBCARREIRA.search(rub):
            continue
        x = serie("Q1.7", rub)
        if not x.get(last):
            continue
        car.append(
            {
                "nome": CARREIRAS.get(rub, rub),
                "valor": int(x[last]),
                "var": int(x[last] - x[antes]) if antes in x else None,
                "pct": round(100 * x[last] / ap[last], 1),
            }
        )
    car.sort(key=lambda d: -d["valor"])
    resto = out["ap"] - sum(d["valor"] for d in car[:10])
    out["carreiras"] = car[:10]
    out["carreiras_resto"] = resto
    out["carreiras_resto_pct"] = round(100 * resto / ap[last], 1)

    # one point a year (31 December) and the latest quarter
    anos = sorted({d[:4] for d in ar})
    evol = []
    for a in anos:
        d = (
            f"{a}-12-31"
            if f"{a}-12-31" in ar
            else (last if a == last[:4] else "")
        )
        if not d:
            continue
        evol.append(
            {
                "ano": int(a),
                "quando": "31 dez" if d.endswith("12-31") else _dia(d)[:-8],
                "ar": int(ar[d]),
                "ap": int(ap[d]) if d in ap else None,
            }
        )
    out["evolucao"] = evol
    out["evolucao_max"] = max((e["ap"] or e["ar"]) for e in evol)

    # pay: general government in each region (Q1.13) and the regional
    # administration (Q1.9), in the latest month surveyed
    pay = {}
    for quadro, rub, local, chave in (
        ("Q1.13", "Total", "Açores", "acores"),
        ("Q1.13", "Total", "Portugal", "pais"),
        ("Q1.9", AR_ACORES, "Açores", "ar"),
        ("Q1.9", "ADMINISTRAÇÃO REGIONAL DA MADEIRA", "Madeira", "madeira"),
    ):
        for ind, k in (
            ("Remuneração base média mensal", "base"),
            ("Ganho médio mensal", "ganho"),
        ):
            x = serie(quadro, rub, local, ind)
            if x:
                m = max(x)
                pay.setdefault(chave, {})[k] = round(x[m])
                pay["mes"] = f"{MESES_DGAEP.get(m[5:7], m[5:7])} de {m[:4]}"
    out["salarios"] = pay

    # public and private shares of the jobs in the Azores
    if srea:
        sr = _dicts(srea)
        emp = sorted(
            (
                r
                for r in sr
                if r["serie"] == "emprego"
                and r["indicador"] == "População empregada"
                and r["rubrica"] == "Total"
            ),
            key=lambda r: r["data"],
        )
        if emp:
            e = emp[-1]
            y, q = e["periodo"].split("-T")
            fim = f"{y}-{3 * int(q):02d}"
            ap_q = next((v for d, v in ap.items() if d[:7] == fim), None)
            total = _num(e["valor"]) * 1000
            setor_p = next(
                (
                    _num(r["valor"])
                    for r in sr
                    if r["serie"] == "emprego"
                    and r["periodo"] == e["periodo"]
                    and r["rubrica"].startswith("P:")
                ),
                None,
            )
            mercado = 0
            if sper:
                mercado = sum(
                    d.get("trabalhadores", 0)
                    for d in sper.get("empresas", [])
                    if not d.get("ap")
                )
            if ap_q:
                pub = ap_q + mercado
                out["peso"] = {
                    "periodo": f"{q}.º trimestre de {y}",
                    "emprego_mil": _num(e["valor"]),
                    "ap": int(ap_q),
                    "ap_pct": round(100 * ap_q / total, 1),
                    "mercado": mercado,
                    "mercado_ano": sper.get("ano") if sper else None,
                    "publico": int(pub),
                    "publico_pct": round(100 * pub / total),
                    "um_em": round(total / pub),
                    "privado": int(total - pub),
                    "privado_pct": 100 - round(100 * pub / total),
                    "setor_p_mil": setor_p,
                    "url": e["pagina"],
                }
    if ine:
        out["comparacao"] = _comparacao(rows, ine)
    if censos:
        out["ilhas"] = _ilhas_censos(censos)
    return out


ORDEM_ILHAS = [
    "Santa Maria",
    "São Miguel",
    "Terceira",
    "Graciosa",
    "São Jorge",
    "Pico",
    "Faial",
    "Flores",
    "Corvo",
]


def _ilhas_censos(censos: tuple[list, list]) -> dict:
    """Employed residents of each island in CAE sections O (public
    administration, defence, social security), P (education) and Q (health
    and social work), 2021 census (data/censos2021_setores.csv)."""
    soma: dict = {}
    conc: dict = {}
    ilha_de: dict = {}
    for r in _dicts(censos):
        for k, tab in ((r["ilha"], soma), (r["concelho"], conc)):
            d = tab.setdefault(k, {"O": 0, "P": 0, "Q": 0, "Total": 0})
            d[r["secao"]] += int(r["valor"])
        ilha_de[r["concelho"]] = r["ilha"]
    if not soma:
        return {}
    soma["Açores"] = {
        k: sum(d[k] for d in soma.values()) for k in ("O", "P", "Q", "Total")
    }

    def linha(nome: str, tab: dict | None = None) -> dict:
        d = (tab or soma)[nome]
        t = d["Total"]
        return {
            "ilha": ilha_de.get(nome, nome) if tab else nome,
            "nome": nome,
            "empregados": t,
            "o": d["O"],
            "o_pct": round(100 * d["O"] / t, 1),
            "p_pct": round(100 * d["P"] / t, 1),
            "q_pct": round(100 * d["Q"] / t, 1),
            "opq_pct": round(100 * (d["O"] + d["P"] + d["Q"]) / t, 1),
        }

    ilhas = [linha(n) for n in ORDEM_ILHAS if n in soma]
    concelhos = sorted(
        (linha(n, conc) for n in conc), key=lambda x: -x["o_pct"]
    )
    return {
        "lista": ilhas,
        "concelhos": concelhos,
        "max_pct_concelho": max(x["opq_pct"] for x in concelhos),
        "acores": linha("Açores"),
        "max_pct": max(x["opq_pct"] for x in ilhas),
        "url": _dicts(censos)[0]["url"],
    }


EMPREGADOS = "0012118"  # INE, Inquérito ao Emprego, quarterly, NUTS II
AR_LOCAL = {
    "Açores": "ADMINISTRAÇÃO REGIONAL DOS AÇORES",
    "Madeira": "ADMINISTRAÇÃO REGIONAL DA MADEIRA",
}


def _comparacao(rows: list[dict], ine: tuple[list, list]) -> dict:
    """General government jobs (DGAEP Q1.7, by NUTS) as a share of the
    employed population (INE) in the Azores, Madeira and Portugal, for the
    latest quarter both have."""
    ap = {
        (r["local"], r["data"]): _num(r["valor"])
        for r in rows
        if r["quadro"] == "Q1.7" and r["rubrica"] == "Total"
    }
    ar = {
        (r["local"], r["data"]): _num(r["valor"])
        for r in rows
        if r["quadro"] == "Q1.1" and AR_LOCAL.get(r["local"]) == r["rubrica"]
    }
    nomes = {"20": "Açores", "30": "Madeira", "PT": "Portugal"}
    emp = {}
    for r in _dicts(ine):
        if r["varcd"] == EMPREGADOS and not r["categoria"] and r["valor"]:
            if r["geocod"] in nomes:
                emp[(nomes[r["geocod"]], r["data"])] = (
                    _num(r["valor"]),
                    r["periodo"],
                )

    def inicio(d: str) -> str:  # 2026-09-30 -> 2026-07-01
        return f"{d[:4]}-{int(d[5:7]) - 2:02d}-01"

    datas = sorted({d for (_, d) in ap}, reverse=True)  # quarter ends
    for d in datas:
        if all((n, d) in ap and (n, inicio(d)) in emp for n in nomes.values()):
            break
    else:
        return {}
    locais = []
    for n in nomes.values():
        e, periodo = emp[(n, inicio(d))]
        x = {
            "local": n,
            "ap": int(ap[(n, d)]),
            "empregados": int(e),
            "ap_pct": round(100 * ap[(n, d)] / e, 1),
        }
        if (n, d) in ar:
            x["ar"] = int(ar[(n, d)])
            x["ar_pct"] = round(100 * ar[(n, d)] / e, 1)
        locais.append(x)
    return {
        "data": d,
        "periodo": periodo,
        "provisorio": any(
            r["provisorio"]
            for r in rows
            if r["quadro"] == "Q1.7" and r["data"] == d
        ),
        "locais": locais,
        "max_pct": max(x["ap_pct"] for x in locais),
        "url_ine": f"https://www.ine.pt/xurl/indx/{EMPREGADOS}",
    }


# /financas/camaras/: the 19 câmaras municipais per inhabitant, next to other
# sources for the same concelho.
CAMARAS_IND = {
    "pop": "0012918",
    "receita": "0013908",
    "despesa": "0013909",
    "rnf_hab": "0013899",
    "rendimento": "0012757",
    "dormidas": "0013210",
    "rsi": "0013420",
}
REFS = {"20": "Açores", "30": "Madeira", "PT": "Portugal"}
NAO_CAMARA = re.compile(
    r"associacao|servicos municipalizados|smas|operacoes municipais|"
    r"empresa municipal|\bei ?m\b|comunidade|comercio"
)
# the same name exists in mainland Portugal or Madeira
AMBIGUO = {"calheta": r"jorge|acores|raa", "lagoa": r"acores|raa"}


def _words(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def municipio(adjudicante: str, concelhos: list[str]) -> str:
    """The concelho whose câmara is the BASE adjudicante, or "" (also for
    SMAS, municipal companies and associations of municipalities). BASE has
    several spellings: "Município de Lagoa (Açores)", "Câmara Municipal de
    Nordeste", "MUNICÍPIO DA RIBEIRA GRANDE", "Municipio da  Ribeira Grande".
    """
    n = _words(adjudicante)
    if not re.search(r"\b(municipio|camara municipal)\b", n):
        return ""
    if NAO_CAMARA.search(n):
        return ""
    keys = []
    for c in concelhos:
        k = _words(re.sub(r"\(R\.A\.A\.\)", "", c))
        keys.append((k.removeprefix("vila da "), c))
    for k, c in sorted(keys, key=lambda kc: -len(kc[0])):
        if re.search(rf"\b{k}\b", n):
            if k in AMBIGUO and not re.search(AMBIGUO[k], n):
                return ""
            return c
    return ""


def camaras_data(
    ine: tuple[list, list], base: tuple[list, list] | None = None
) -> dict:
    """Receitas and despesas of each câmara municipal per inhabitant (INE),
    with income, tourism and RSI for the same concelho and the contracts the
    câmara signed in BASE."""
    rows = [r for r in _dicts(ine) if r["varcd"] in CAMARAS_IND.values()]
    if not rows:
        return {}
    by: dict = {}
    for r in rows:
        if r["categoria"] or not r["valor"]:
            continue
        geo = r["geocod"]
        if r["nivel"] != "Concelho" and geo not in REFS:
            continue
        by.setdefault((r["varcd"], geo), {})[r["periodo"]] = float(r["valor"])

    def serie(k: str, geo: str) -> dict:
        return by.get((CAMARAS_IND[k], geo), {})

    anos = sorted(
        {
            a
            for (v, _), d in by.items()
            if v == CAMARAS_IND["despesa"]
            for a in d
        }
    )
    if not anos:
        return {}
    ano, inicio = anos[-1], anos[0]

    def ultimo(k: str) -> str:
        return max(
            (a for (v, _), d in by.items() if v == CAMARAS_IND[k] for a in d),
            default="",
        )

    anos_de = {k: ultimo(k) for k in ("rendimento", "dormidas", "rsi")}
    nomes = {}
    for r in rows:
        if r["nivel"] == "Concelho":
            nomes[r["geocod"]] = (r["local"], r["ilha"])
    contratos: dict = {}
    base_de = base_ate = ""
    if base:
        cols = base[0]
        b = [dict(zip(cols, r, strict=False)) for r in base[1]]
        datas = sorted(r["publicado"] for r in b if r["publicado"])
        base_de, base_ate = (datas[0], datas[-1]) if datas else ("", "")
        concelhos = [n for n, _ in nomes.values()]
        for r in b:
            c = municipio(r["adjudicante"], concelhos)
            if c:
                d = contratos.setdefault(c, {"n": 0, "valor": 0.0})
                d["n"] += 1
                d["valor"] += float(r["preco"] or 0)

    def linha(geo: str, nome: str, ilha: str = "") -> dict | None:
        pop = serie("pop", geo).get(ano)
        desp = serie("despesa", geo).get(ano)
        if not pop or desp is None:
            return None
        rec = serie("receita", geo).get(ano, 0)
        pop0 = serie("pop", geo).get(inicio)
        desp0 = serie("despesa", geo).get(inicio)
        d = {
            "nome": nome,
            "ilha": ilha,
            "pop": int(pop),
            "despesa_m": round(desp / 1e6, 1),
            "receita_m": round(rec / 1e6, 1),
            "despesa_hab": round(desp / pop),
            "receita_hab": round(rec / pop),
            "rnf_hab": round(serie("rnf_hab", geo).get(ano, 0)),
        }
        if pop0 and desp0:
            d["despesa_hab_inicio"] = round(desp0 / pop0)
            d["var_pct"] = round(100 * (d["despesa_hab"] / (desp0 / pop0) - 1))
        for k, a in anos_de.items():
            v = serie(k, geo).get(a)
            if v is not None:
                d[k] = round(v, 1) if k == "rsi" else round(v)
        if nome in contratos:
            c = contratos[nome]
            d["contratos_n"] = c["n"]
            d["contratos_m"] = round(c["valor"] / 1e6, 1)
            d["contratos_hab"] = round(c["valor"] / pop)
        return d

    lista = [
        x for g, (n, i) in nomes.items() if (x := linha(g, n, i)) is not None
    ]
    lista.sort(key=lambda d: -d["despesa_hab"])
    refs = [x for g, n in REFS.items() if (x := linha(g, n)) is not None]
    out = {
        "ano": ano,
        "inicio": inicio,
        "anos_de": anos_de,
        "concelhos": lista,
        "refs": refs,
        "max_hab": max(d["despesa_hab"] for d in lista) if lista else 0,
        "base_de": base_de,
        "base_ate": base_ate,
        "sem_contratos": [d["nome"] for d in lista if "contratos_n" not in d],
        "url": {
            k: f"https://www.ine.pt/xurl/indx/{v}"
            for k, v in CAMARAS_IND.items()
        },
    }
    out["grafico"] = _dispersao(lista)
    return out


def _ponto(x: float, y: float, nome: str, rotulos: dict) -> dict:
    p = {"x": x, "y": y, "nome": nome, "rotulo": nome in rotulos}
    if nome in rotulos:
        dx, dy, ancora = rotulos[nome]
        p.update(lx=round(x + dx, 1), ly=round(y + dy, 1), ancora=ancora)
    return p


def _dispersao(lista: list[dict]) -> dict:
    """Positions for the scatter of population (log scale) against spending
    per inhabitant, in a 600 x 300 viewBox."""
    import math

    if not lista:
        return {}
    w, h, esq, dir_, top, fundo = 600, 300, 56, 16, 12, 34
    xs = [500, 1000, 5000, 10000, 50000]
    lo, hi = math.log10(300), math.log10(100000)
    ymax = 1000 * math.ceil(max(d["despesa_hab"] for d in lista) / 1000)

    def x(v):
        return round(
            esq + (math.log10(v) - lo) / (hi - lo) * (w - esq - dir_), 1
        )

    def y(v):
        return round(top + (1 - v / ymax) * (h - top - fundo), 1)

    # label the extremes only; on the right edge the label goes to the left
    rotulos = {
        "Corvo": (8, 4, "start"),
        "Lajes das Flores": (8, 4, "start"),
        "Angra do Heroísmo": (-8, -8, "end"),
        "Ponta Delgada": (-8, 18, "end"),
    }
    return {
        "w": w,
        "h": h,
        "esq": esq,
        "dir": w - dir_,
        "base": h - fundo,
        "top": top,
        "pontos": [
            _ponto(x(d["pop"]), y(d["despesa_hab"]), d["nome"], rotulos)
            for d in lista
        ],
        "xt": [{"x": x(v), "v": v} for v in xs],
        "yt": [{"y": y(v), "v": v} for v in range(0, ymax + 1, 2000)],
    }


def write_economia(docs: Path, tables: dict) -> None:
    """docs/_data/sper.json, maiores.json and publico.json for the Economia
    section."""
    (docs / "_data").mkdir(exist_ok=True)
    sper: dict = {}
    if "sper" in tables:
        sper = sper_data(
            tables["sper"],
            tables.get("sper_empresas"),
            tables.get("sper_regiao"),
        )
    maiores: dict = {}
    if "maiores" in tables:
        lista = (
            [
                e
                for e in _dicts(tables["sper_empresas"])
                if e["relatorio"] == sper.get("relatorio")
            ]
            if "sper_empresas" in tables
            else []
        )
        maiores = maiores_data(tables["maiores"], lista)
        posicao = {
            d["publica"]: d["posicao"]
            for d in maiores["empresas"]
            if d["publica"]
        }
        for d in sper.get("empresas", []):
            if d["sigla"] in posicao:
                d["posicao"] = posicao[d["sigla"]]
        if sper:
            sper["maiores_ano"] = maiores["ano"]
    publico: dict = {}
    if "emprego_publico" in tables:
        publico = publico_data(
            tables["emprego_publico"],
            tables.get("srea"),
            sper,
            tables.get("ine"),
            tables.get("censos2021_setores"),
        )
    for name, data in (
        ("sper", sper),
        ("maiores", maiores),
        ("publico", publico),
    ):
        (docs / "_data" / f"{name}.json").write_text(
            json.dumps(_texts(data), ensure_ascii=False, indent=1),
            encoding="utf-8",
        )


def pt_num(x: float) -> str:
    """245328 -> '245 328', 39.38 -> '39,4', 5.94 -> '5,94' (pt-PT, the
    thousands separator is a no-break space)."""
    dec = 0 if abs(x) >= 100 else 1 if abs(x) >= 10 else 2
    s = f"{x:,.{dec}f}".replace(",", "\u00a0").replace(".", ",")
    if "," in s:
        s = s.rstrip("0").rstrip(",")
    return s


def _texts(node, total: float | None = None):
    """Add 'k_t' (formatted) next to every number 'k', and 'pct' (share of
    total) to items of the lists, so the Liquid page needs no arithmetic."""
    if isinstance(node, dict):
        for k, v in list(node.items()):
            if isinstance(v, int | float) and not isinstance(v, bool):
                node[k + "_t"] = pt_num(v)
            elif isinstance(v, list):
                tot = {
                    "ilhas": node.get("acores"),
                    "receitas": node.get("receita"),
                    "despesas": node.get("despesa"),
                    "funcoes": node.get("funcoes_total"),
                }.get(k)
                for item in v:
                    if tot and isinstance(item, dict) and "valor" in item:
                        item["pct"] = round(100 * item["valor"] / tot)
                    _texts(item)
            else:
                _texts(v)
    return node


def irs_data(at: tuple[list, list]) -> dict:
    """docs/_data/irs.json for /dados/irs/: IRS by tax bracket in the
    Azores in the latest year (AT), the top bracket year by year against
    Madeira, and the additional solidarity rate."""
    rows = [
        r
        for r in _dicts(at)
        if r["titularidade"] == "Total"
        and r["quadro"] == "Taxas de tributação"
    ]
    if not rows:
        return {}
    by: dict = {}
    for r in rows:
        by.setdefault((r["medida"], r["regiao"], int(r["ano"])), {})[
            int(r["escalao"])
        ] = (float(r["taxa"]), float(r["valor"]))
    anos = sorted({k[2] for k in by})
    ano = anos[-1]

    def pct(x: float | None) -> str:
        # rates keep every decimal (11,55 %, not 11,6 %)
        return "" if x is None else f"{x:g} %".replace(".", ",")

    def tab(medida: str, regiao: str, a: int) -> dict:
        return by.get((medida, regiao, a), {})

    agr = tab("Agregados", "Açores", ano)
    ren = tab("Rendimento englobado", "Açores", ano)
    irs = tab("IRS liquidado", "Açores", ano)
    cont = tab("Agregados", "Continente", ano)
    tot_a = sum(v for _, v in agr.values())
    tot_r = sum(v for _, v in ren.values())
    tot_i = sum(v for _, v in irs.values())
    escaloes = []
    for o in sorted(agr):
        n = agr[o][1]
        i = irs.get(o, (0, 0))[1]
        escaloes.append(
            {
                "ordem": o,
                "taxa_s": pct(agr[o][0]),
                "taxa_continente_s": pct(cont.get(o, (None, None))[0]),
                "agregados": int(n),
                "agregados_pct": round(100 * n / tot_a, 1),
                "rendimento_m": round(ren.get(o, (0, 0))[1] / 1e6, 1),
                "irs_m": round(i / 1e6, 1),
                "irs_pct": round(100 * i / tot_i, 1),
                "irs_medio": round(i / n) if n else 0,
            }
        )
    serie = []
    for a in anos:
        linha: dict = {"ano": a}
        for regiao, k in (("Açores", "acores"), ("Madeira", "madeira")):
            g = tab("Agregados", regiao, a)
            t = tab("IRS liquidado", regiao, a)
            if not g:
                continue
            topo = max(g)
            total = sum(v for _, v in g.values())
            linha[k] = int(g[topo][1])
            linha[k + "_taxa_s"] = pct(g[topo][0])
            linha[k + "_por_mil"] = round(1000 * g[topo][1] / total, 1)
            if t:
                linha[k + "_irs_pct"] = round(
                    100 * t[topo][1] / sum(v for _, v in t.values()), 1
                )
        serie.append(linha)
    adicional = {}
    for r in _dicts(at):
        if r["quadro"] != "Taxa adicional de solidariedade":
            continue
        if r["regiao"] != "Açores":
            continue
        d = adicional.setdefault(int(r["ano"]), {"ano": int(r["ano"])})
        k = "agregados" if r["medida"] == "Agregados" else "irs"
        d[k] = d.get(k, 0) + float(r["valor"])
    adic = []
    for a in sorted(adicional):
        d = adicional[a]
        adic.append(
            {
                "ano": a,
                "agregados": int(d.get("agregados", 0)),
                "irs_m": round(d.get("irs", 0) / 1e6, 2),
            }
        )
    fonte = next(
        r
        for r in _dicts(at)
        if int(r["ano"]) == ano and r["regiao"] == "Açores"
    )
    topo = escaloes[-1] if escaloes else {}
    return {
        "ano": ano,
        "primeiro": anos[0],
        "agregados": int(tot_a),
        "rendimento_m": round(tot_r / 1e6, 1),
        "irs_m": round(tot_i / 1e6, 1),
        "taxa_media": round(100 * tot_i / tot_r, 1) if tot_r else 0,
        "escaloes": escaloes,
        "topo": topo,
        "serie": serie,
        "adicional": adic,
        "dossie": fonte["dossie"],
        "url": fonte["url"],
    }


def at_regioes(
    dist: tuple[list, list], imposto: str, medida: str, unidade: str
) -> dict[str, dict[int, float]]:
    """{regiao: {ano: valor}} from at_distritos. The AT's regional total
    when it prints one ("R. A. Açores", "RA MADEIRA", "TOTAL"); else, for
    the years it only prints the old districts, their sum (Angra, Horta
    and Ponta Delgada; Funchal is all of Madeira). Rates of the three
    Azorean districts cannot be added, so those years stay empty."""
    tot: dict[str, dict[int, float]] = {}
    parts: dict[str, dict[int, list]] = {}
    for r in _dicts(dist):
        if (r["imposto"], r["medida"], r["unidade"]) != (
            imposto,
            medida,
            unidade,
        ):
            continue
        reg, ano, v = r["regiao"], int(r["ano"]), float(r["valor"])
        lab = _fold(r["distrito"])
        if reg == "Total" or "acores" in lab or "madeira" in lab:
            tot.setdefault(reg, {})[ano] = v
        elif reg in ("Açores", "Madeira"):
            parts.setdefault(reg, {}).setdefault(ano, []).append(v)
    for reg, anos in parts.items():
        for ano, vs in anos.items():
            if ano in tot.get(reg, {}):
                continue
            if unidade != "%" or len(vs) == 1:
                tot.setdefault(reg, {})[ano] = sum(vs)
    return tot


def _pct_s(x: float | None) -> str:
    # rates keep every decimal (11,55 %, not 11,6 %)
    return "" if x is None else f"{x:g} %".replace(".", ",")


def _share(a: float | None, b: float | None) -> float | str:
    return round(100 * a / b, 1) if a and b else ""


def irs_pais(dist: tuple[list, list]) -> list[dict]:
    """IRS by region, year by year, from the 'por distrito' maps:
    households, tax, tax per household and the shares of the country."""
    g = {
        k: at_regioes(dist, "IRS", m, u)
        for k, m, u in (
            ("agr", "Agregados", "agregados"),
            ("irs", "IRS liquidado", "€"),
        )
    }
    out = []
    for a in sorted(g["irs"].get("Açores", {})):
        linha: dict = {"ano": a}
        for reg, k in (
            ("Açores", "acores"),
            ("Madeira", "madeira"),
            ("Total", "pais"),
        ):
            n = g["agr"].get(reg, {}).get(a)
            v = g["irs"].get(reg, {}).get(a)
            if not (n and v):
                continue
            linha[k + "_agregados"] = int(n)
            linha[k + "_irs_m"] = round(v / 1e6, 1)
            linha[k + "_por_agregado"] = round(v / n)
        tot_n = g["agr"].get("Total", {}).get(a)
        tot_v = g["irs"].get("Total", {}).get(a)
        linha["acores_agregados_pct"] = _share(
            g["agr"].get("Açores", {}).get(a), tot_n
        )
        linha["acores_irs_pct"] = _share(
            g["irs"].get("Açores", {}).get(a), tot_v
        )
        out.append(linha)
    return out


def irs_gerais(at: tuple[list, list]) -> dict:
    """The general IRS rates of the latest year, a row per bracket."""
    rows = [r for r in _dicts(at) if r["quadro"] == "Taxas gerais"]
    if not rows:
        return {}
    ano = max(int(r["ano"]) for r in rows)
    by: dict[int, dict] = {}
    for r in rows:
        if int(r["ano"]) != ano:
            continue
        o = int(r["escalao"])
        d = by.setdefault(o, {"ordem": o})
        d[
            {
                "Continente": "continente",
                "Açores": "acores",
                "Madeira": "madeira",
            }[r["regiao"]]
            + "_s"
        ] = _pct_s(float(r["taxa"]))
        d["limite"] = r["valor"]
    escaloes = []
    anterior = None
    for o in sorted(by):
        d = by[o]
        lim = float(d.pop("limite")) if d.get("limite") else None
        de = f"{pt_num(anterior)} €" if anterior else ""
        ate = f"{pt_num(lim)} €" if lim else ""
        d["escalao"] = (
            f"até {ate}"
            if not de
            else f"de {de} a {ate}" if ate else f"acima de {de}"
        )
        anterior = lim
        escaloes.append(d)
    return {"ano": ano, "escaloes": escaloes}


def write_irs(docs: Path, tables: dict) -> None:
    data = irs_data(tables["at_irs"]) if "at_irs" in tables else {}
    if data:
        if "at_distritos" in tables:
            data["pais"] = irs_pais(tables["at_distritos"])
        data["gerais"] = irs_gerais(tables["at_irs"])
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "irs.json").write_text(
        json.dumps(_texts(data), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )


def _primeiro_num(s: str) -> float:
    """'Mais de 1.500.000 a 7.500.000' -> 1500000."""
    m = re.search(r"\d[\d.]*", s)
    return float(m[0].replace(".", "")) if m else 0.0


def irc_data(dist: tuple[list, list], irc: tuple[list, list]) -> dict:
    """docs/_data/irc.json for /dados/irc/: IRC in the Azores year by year
    (AT, Dossier Estatístico IRC), against Madeira and the country."""
    g = {
        k: at_regioes(dist, "IRC", m, u)
        for k, m, u in (
            ("decl", "Declarações", "declarações"),
            ("lucro", "Lucro tributável", "€"),
            ("prej", "Prejuízo fiscal", "€"),
            ("mc", "Matéria coletável", "€"),
            ("liq", "IRC liquidado", "€"),
            ("taxa", "Taxa média efetiva", "%"),
        )
    }
    anos = sorted(g["liq"].get("Açores", {}))
    if not anos:
        return {}
    linhas = _dicts(irc)

    def quadro(q: str, reg: str, unidade: str, escalao: str | None = None):
        return {
            int(r["ano"]): float(r["valor"])
            for r in linhas
            if r["quadro"] == q
            and r["regiao"] == reg
            and r["unidade"] == unidade
            and (escalao is None or r["escalao"] == escalao)
        }

    regional = quadro("Cálculo do imposto", "Açores", "€")
    regional_n = quadro("Cálculo do imposto", "Açores", "declarações")
    derrama = quadro("Derrama estadual", "Açores", "€", "Total")
    derrama_n = quadro("Derrama estadual", "Açores", "declarações", "Total")

    def v(k: str, a: int, reg: str = "Açores"):
        return g[k].get(reg, {}).get(a)

    def m(x: float | None) -> float | str:
        return "" if x is None else round(x / 1e6, 1)

    serie = []
    for a in anos:
        serie.append(
            {
                "ano": a,
                "declaracoes": int(v("decl", a) or 0),
                "lucro_m": m(v("lucro", a)),
                "prejuizo_m": m(v("prej", a)),
                "irc_m": m(v("liq", a)),
                "regional_m": m(regional.get(a)),
                "decl_pct": _share(v("decl", a), v("decl", a, "Total")),
                "irc_pct": _share(v("liq", a), v("liq", a, "Total")),
                "taxa_s": _pct_s(v("taxa", a)),
                "taxa_madeira_s": _pct_s(v("taxa", a, "Madeira")),
                "taxa_pais_s": _pct_s(v("taxa", a, "Total")),
                "derrama_m": m(derrama.get(a)) if a in derrama else "",
                "derrama_n": int(derrama_n[a]) if a in derrama_n else "",
            }
        )
    ano = anos[-1]
    ultimo = serie[-1]
    escaloes = [
        {
            "escalao": r["escalao"],
            "declaracoes": int(
                next(
                    (
                        float(x["valor"])
                        for x in linhas
                        if x["quadro"] == "Derrama estadual"
                        and x["regiao"] == "Açores"
                        and x["unidade"] == "declarações"
                        and x["ano"] == r["ano"]
                        and x["escalao"] == r["escalao"]
                    ),
                    0,
                )
            ),
            "valor_m": round(float(r["valor"]) / 1e6, 2),
        }
        for r in linhas
        if r["quadro"] == "Derrama estadual"
        and r["regiao"] == "Açores"
        and r["unidade"] == "€"
        and int(r["ano"]) == ano
        and r["escalao"] != "Total"
    ]
    escaloes.sort(key=lambda e: _primeiro_num(e["escalao"]))
    nominais: dict[str, dict] = {}
    for r in linhas:
        if r["quadro"] != "Taxas nominais" or int(r["ano"]) != ano:
            continue
        d = nominais.setdefault(r["escalao"], {"designacao": r["escalao"]})
        key = {
            "Continente": "continente",
            "Açores": "acores",
            "Madeira": "madeira",
        }
        d[key[r["regiao"]] + "_s"] = _pct_s(float(r["valor"]))
    fonte = next(
        r
        for r in _dicts(dist)
        if r["imposto"] == "IRC" and int(r["ano"]) == ano
    )
    # the general rate first, then the reduced and the normal rate
    ordem = sorted(
        nominais, key=lambda k: (not k.startswith("Taxa geral"), "<=" not in k)
    )
    return {
        "ano": ano,
        "primeiro": anos[0],
        "ultimo": ultimo,
        "lucro_cresc": _share(v("lucro", ano), v("lucro", anos[0])),
        "regional_n": int(regional_n.get(ano, 0)),
        "serie": serie,
        "derrama_escaloes": escaloes,
        "nominais": [nominais[k] for k in ordem],
        "dossie": fonte["dossie"],
        "url": fonte["url"],
    }


def write_irc(docs: Path, tables: dict) -> None:
    data = {}
    if "at_distritos" in tables and "at_irc" in tables:
        data = irc_data(tables["at_distritos"], tables["at_irc"])
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "irc.json").write_text(
        json.dumps(_texts(data), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )


BPSTAT_SERIE = "https://bpstat.bportugal.pt/serie/"
MESES = (
    "janeiro fevereiro março abril maio junho julho agosto setembro "
    "outubro novembro dezembro"
).split()
M_EUR = "Milhões de euros"
PCT = "Percentagem"
MIL_DEV = "Milhares de devedores"
TODAS_CAE = (
    "Todas as atividades de sociedades não financeiras exceto "
    "atividades das sedes sociais"
)
# BdP's aggregates of other sectors, left out of the sector table
CAE_AGREGADOS = {
    TODAS_CAE,
    "Comércio, transportes, alojamento e restauração",
    "Indústrias, eletricidade, gás e água",
    "Atividades das sedes sociais",
    # "Outras atividades" overlaps the sectors listed on their own: those
    # ten add up to the total (7 728 companies in the Azores in 2025)
    "Outras atividades",
}
EMPRESAS_IND = [
    ("Número de empresas", "Número de empresas"),
    ("Número de pessoas ao serviço", "Número de pessoas"),
    ("Vendas e serviços prestados", "Milhares de euros"),
    ("Autonomia financeira", PCT),
    ("Financiamentos obtidos em percentagem do ativo", PCT),
    ("Custo dos financiamentos obtidos", PCT),
    ("Cobertura dos gastos de financiamento", "Número"),
    ("Rendibilidade do ativo", PCT),
    ("Rendibilidade dos capitais próprios", PCT),
    ("Empresas com resultado líquido negativo", "% das empresas"),
    ("Empresas com capital próprio negativo", "% das empresas"),
    ("Prazo médio de recebimentos", "Número de dias"),
    ("Prazo médio de pagamentos", "Número de dias"),
]
REG_K = {"Açores": "acores", "Madeira": "madeira", "Portugal": "pais"}


def _mes_ano(data: str) -> str:
    """'2026-10-31' -> 'outubro de 2026'."""
    return f"{MESES[int(data[5:7]) - 1]} de {data[:4]}"


def _populacao(ine: tuple[list, list] | None) -> dict[str, dict[int, float]]:
    """{regiao: {ano: residentes}} for the Azores, Madeira and Portugal
    (INE, 0012918)."""
    nomes = {"20": "Açores", "30": "Madeira", "PT": "Portugal"}
    out: dict[str, dict[int, float]] = {}
    for r in _dicts(ine) if ine else []:
        if r["varcd"] == "0012918" and r["geocod"] in nomes and r["valor"]:
            reg = nomes[r["geocod"]]
            out.setdefault(reg, {})[int(r["periodo"])] = float(r["valor"])
    return out


def _pop(pop: dict, regiao: str, data: str) -> tuple[float | None, int | None]:
    """Residents in the year of ``data``, or the latest year before it."""
    anos = [a for a in pop.get(regiao, {}) if a <= int(data[:4])]
    return (pop[regiao][max(anos)], max(anos)) if anos else (None, None)


def bp_series(bp: tuple[list, list]) -> dict[tuple, dict[str, dict]]:
    """{(conjunto, indicador, setor, detalhe, unidade): {regiao: {data:
    (valor, serie)}}}. Where the BdP gives no national total (loans and
    deposits), 'Portugal' is the sum of the regions (and of the deposits
    not tied to a branch): amounts and counts only, never percentages."""
    out: dict[tuple, dict[str, dict]] = {}
    for r in _dicts(bp):
        k = (
            r["conjunto"],
            r["indicador"],
            r["setor"],
            r["detalhe"],
            r["unidade"],
        )
        out.setdefault(k, {}).setdefault(r["regiao"], {})[r["data"]] = (
            float(r["valor"]),
            r["serie"],
        )
    for k, regs in out.items():
        if "Portugal" in regs or k[4] == PCT or k[0] == "empresas":
            continue
        soma: dict[str, float] = {}
        for datas in regs.values():
            for d, (v, _) in datas.items():
                soma[d] = soma.get(d, 0.0) + v
        regs["Portugal"] = {d: (round(v, 1), "") for d, v in soma.items()}
    return out


def _bp_fmt(unidade: str, v: float | None) -> str:
    if v is None:
        return ""
    if unidade == "Milhares de euros":
        return pt_num(round(v / 1000)) + " M€"
    if unidade in (PCT, "% das empresas"):
        return _pct_s(round(v, 1))
    if unidade == "Número de dias":
        return pt_num(v) + " dias"
    return pt_num(v)


def _vencidos(s: dict, setor: str, det: str, reg: str, d: str) -> dict:
    """Overdue ratio and share of debtors with overdue loans. The BdP's
    own figures for a region; for Portugal, worked out from the regional
    amounts and debtors (açores.net)."""

    def val(k, r=reg):
        got = s.get(k, {}).get(r, {}).get(d)
        return got[0] if got else None

    rk = ("emprestimos", "Rácio de empréstimos vencidos", setor, det, PCT)
    dk = ("emprestimos", "Devedores com empréstimos vencidos", setor, det, PCT)
    if reg != "Portugal":
        return {"racio": val(rk), "devedores": val(dk)}
    venc = val(("emprestimos", "Empréstimos vencidos", setor, det, M_EUR))
    tot = val(("emprestimos", "Empréstimos", setor, det, M_EUR))
    n = c = 0.0
    for r in s.get(dk, {}):
        pct = val(dk, r)
        num = val(("emprestimos", "Devedores", setor, det, MIL_DEV), r)
        if pct is not None and num:
            n += pct * num
            c += num
    return {
        "racio": (
            round(100 * venc / tot, 1) if venc is not None and tot else None
        ),
        "devedores": round(n / c, 1) if c else None,
    }


def _empresas_bp(s: dict, serie) -> dict:
    """Company indicators (Central de Balanços): the latest year for the
    Azores, Madeira and Portugal, the Azores by sector, and the Azores
    year by year."""

    def val(ind: str, unid: str, cae: str, reg: str, d: str):
        got = (
            s.get(("empresas", ind, "Empresas", cae, unid), {})
            .get(reg, {})
            .get(d)
        )
        return got[0] if got else None

    anos = sorted(
        s.get(
            (
                "empresas",
                "Número de empresas",
                "Empresas",
                TODAS_CAE,
                "Número de empresas",
            ),
            {},
        ).get("Açores", {})
    )
    if not anos:
        return {}
    d = anos[-1]
    comparar = []
    for ind, unid in EMPRESAS_IND:
        k = ("empresas", ind, "Empresas", TODAS_CAE, unid)
        linha = {"nome": ind, "url": serie(k)}
        for reg, rk in REG_K.items():
            linha[rk + "_s"] = _bp_fmt(unid, val(ind, unid, TODAS_CAE, reg, d))
        comparar.append(linha)
    setores = []
    caes = {k[3] for k in s if k[0] == "empresas"} - CAE_AGREGADOS
    for cae in caes:
        n = val("Número de empresas", "Número de empresas", cae, "Açores", d)
        if not n:
            continue

        def f(ind, unid, cae=cae):
            return _bp_fmt(unid, val(ind, unid, cae, "Açores", d))

        setores.append(
            {
                "nome": cae,
                "empresas": round(n),
                "pessoas_s": f(
                    "Número de pessoas ao serviço", "Número de pessoas"
                ),
                "vendas_s": f(
                    "Vendas e serviços prestados", "Milhares de euros"
                ),
                "autonomia_s": f("Autonomia financeira", PCT),
                "rendibilidade_s": f("Rendibilidade do ativo", PCT),
                "negativo_s": f(
                    "Empresas com resultado líquido negativo", "% das empresas"
                ),
                "pagamentos_s": f(
                    "Prazo médio de pagamentos", "Número de dias"
                ),
            }
        )
    setores.sort(key=lambda x: -x["empresas"])
    unidades = dict(EMPRESAS_IND)
    evolucao = []
    for a in reversed(anos):
        linha = {"ano": a[:4]}
        for ind, nome in (
            ("Número de empresas", "empresas"),
            ("Número de pessoas ao serviço", "pessoas"),
            ("Vendas e serviços prestados", "vendas"),
            ("Autonomia financeira", "autonomia"),
            ("Rendibilidade do ativo", "rendibilidade"),
            ("Empresas com resultado líquido negativo", "negativo"),
        ):
            u = unidades[ind]
            linha[nome + "_s"] = _bp_fmt(
                u, val(ind, u, TODAS_CAE, "Açores", a)
            )
        evolucao.append(linha)
    return {
        "ano": d[:4],
        "comparar": comparar,
        "setores": setores,
        "evolucao": evolucao,
    }


def credito_data(bp: tuple[list, list], ine: tuple[list, list] | None) -> dict:
    """docs/_data/credito.json for /dados/credito/: loans, deposits, FDI
    and company indicators of the Banco de Portugal, with figures per
    resident from the INE population."""
    s = bp_series(bp)
    pop = _populacao(ine)
    E = "emprestimos"
    hab = (E, "Empréstimos", "Particulares", "Habitação", M_EUR)
    con = (E, "Empréstimos", "Particulares", "Consumo e outros fins", M_EUR)
    par = (E, "Empréstimos", "Particulares", "", M_EUR)
    emp = (E, "Empréstimos", "Empresas", "", M_EUR)
    dep = {
        st: ("depositos", "Depósitos", st, "", M_EUR)
        for st in ("Particulares", "Empresas", "Emigrantes")
    }
    if not s.get(par, {}).get("Açores"):
        return {}

    def val(k: tuple, reg: str, d: str) -> float | None:
        got = s.get(k, {}).get(reg, {}).get(d)
        return got[0] if got else None

    def serie(k: tuple, reg: str = "Açores") -> str:
        sid = next((x for _, x in s.get(k, {}).get(reg, {}).values() if x), "")
        return BPSTAT_SERIE + sid if sid else ""

    ultimo = max(s[par]["Açores"])
    dep_ult = max(s.get(dep["Particulares"], {}).get("Açores", {}) or [ultimo])

    por_hab = []
    pop_ano = None
    for nome, k, d in (
        ("Crédito à habitação", hab, ultimo),
        ("Crédito ao consumo e outros fins", con, ultimo),
        ("Empréstimos a empresas", emp, ultimo),
        ("Depósitos de particulares", dep["Particulares"], dep_ult),
        ("Depósitos de empresas", dep["Empresas"], dep_ult),
    ):
        linha: dict = {"nome": nome, "url": serie(k)}
        for reg, rk in REG_K.items():
            v, (p, pop_ano) = val(k, reg, d), _pop(pop, reg, d)
            linha[rk] = round(v * 1e6 / p) if v and p else ""
        por_hab.append(linha)
    rel: dict = {}
    for reg, rk in REG_K.items():
        e = val(par, reg, dep_ult)
        dp = val(dep["Particulares"], reg, dep_ult)
        rel[rk] = round(100 * e / dp) if e and dp else ""

    incumprimento = []
    for nome, setor, det in (
        ("Crédito à habitação", "Particulares", "Habitação"),
        ("Consumo e outros fins", "Particulares", "Consumo e outros fins"),
        ("Empresas", "Empresas", ""),
    ):
        linha = {
            "nome": nome,
            "url": serie(
                (E, "Rácio de empréstimos vencidos", setor, det, PCT)
            ),
        }
        for reg, rk in REG_K.items():
            got = _vencidos(s, setor, det, reg, ultimo)
            linha[rk + "_racio_s"] = _pct_s(got["racio"])
            linha[rk + "_devedores_s"] = _pct_s(got["devedores"])
        incumprimento.append(linha)

    datas = [
        d for d in s[par]["Açores"] if d.endswith("-12-31") or d == ultimo
    ]
    serie_anual = []
    for d in sorted(datas, reverse=True):
        linha = {"periodo": d[:4] if d.endswith("-12-31") else _mes_ano(d)}
        for k, nome in (
            (hab, "habitacao"),
            (con, "consumo"),
            (emp, "empresas"),
            (dep["Particulares"], "dep_particulares"),
            (dep["Empresas"], "dep_empresas"),
            (dep["Emigrantes"], "dep_emigrantes"),
        ):
            v = val(k, "Açores", d)
            linha[nome] = round(v) if v is not None else ""
        for setor in ("Particulares", "Empresas"):
            linha[f"vencidos_{setor.lower()}_s"] = _pct_s(
                val(
                    (E, "Rácio de empréstimos vencidos", setor, "", PCT),
                    "Açores",
                    d,
                )
            )
        serie_anual.append(linha)

    um_ano = f"{int(ultimo[:4]) - 1}{ultimo[4:]}"
    h, h0 = val(hab, "Açores", ultimo), val(hab, "Açores", um_ano)
    cards = {
        "habitacao_m": round(h) if h is not None else "",
        "habitacao_cresc_s": (
            _pct_s(round(100 * (h / h0 - 1), 1))
            if h is not None and h0
            else ""
        ),
        "devedores_habitacao_mil": val(
            (E, "Devedores", "Particulares", "Habitação", MIL_DEV),
            "Açores",
            ultimo,
        ),
        "empresas_m": round(val(emp, "Açores", ultimo) or 0),
        "dep_particulares_m": round(
            val(dep["Particulares"], "Açores", dep_ult) or 0
        ),
        "dep_emigrantes_m": round(
            val(dep["Emigrantes"], "Açores", dep_ult) or 0
        ),
    }

    ide = []
    k_ide = {
        det: ("ide", "Investimento direto do exterior", "", det, M_EUR)
        for det in ("Sedes", "Estabelecimentos")
    }
    for d in sorted(s.get(k_ide["Sedes"], {}).get("Açores", {}), reverse=True):
        linha = {"ano": d[:4]}
        for det, nome in (("Sedes", "sedes"), ("Estabelecimentos", "estab")):
            a = val(k_ide[det], "Açores", d)
            linha[nome] = round(a) if a is not None else ""
            linha[nome + "_pct"] = _share(a, val(k_ide[det], "Portugal", d))
        ide.append(linha)

    return {
        "ultimo": ultimo,
        "ultimo_mes": _mes_ano(ultimo),
        "depositos_mes": _mes_ano(dep_ult),
        "populacao_ano": pop_ano or "",
        "cards": cards,
        "por_habitante": por_hab,
        "credito_depositos": rel,
        "incumprimento": incumprimento,
        "serie": serie_anual,
        "ide": ide,
        "ide_url": serie(k_ide["Sedes"]),
        "empresas": _empresas_bp(s, serie),
    }


def write_credito(docs: Path, tables: dict) -> None:
    data = {}
    if "bportugal" in tables:
        data = credito_data(tables["bportugal"], tables.get("ine"))
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "credito.json").write_text(
        json.dumps(_texts(data), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )


def _m(x: float) -> float:
    return round(x / 1e6, 1)


def _f(x: str) -> float:
    try:
        return float(x) if x else 0.0
    except ValueError:
        return 0.0


def fundos_data(tables: dict) -> dict:
    """PRR and Kohesio totals for /financas/fundos-europeus/. PRR amounts
    are the Azorean share (aprovado_acores, pago_acores); a final
    beneficiary's amount is what it contracted, times the Azorean share of
    each project. Kohesio's projects with a note (another region's
    programme, Interreg) are left out of its totals."""
    out: dict = {}
    if "prr_projetos" in tables:
        proj = _dicts(tables["prr_projetos"])
        share = {p["projeto"]: _f(p["perc_acores"]) / 100 for p in proj}
        aprov = sum(_f(p["aprovado_acores"]) for p in proj)
        pago = sum(_f(p["pago_acores"]) for p in proj)
        conc: dict[str, list] = {}
        comp: dict[str, list] = {}
        for p in proj:
            cs = p["concelhos"].split("; ") if p["concelhos"] else []
            k = cs[0] if len(cs) == 1 else "Vários concelhos"
            for d, key in ((conc, k), (comp, p["componente"] or "?")):
                d.setdefault(key, [0, 0.0, 0.0])
                d[key][0] += 1
                d[key][1] += _f(p["aprovado_acores"])
                d[key][2] += _f(p["pago_acores"])

        def lista(d: dict) -> list[dict]:
            return [
                {
                    "nome": k,
                    "projetos": v[0],
                    "aprovado": _m(v[1]),
                    "pago": _m(v[2]),
                    "pct_pago": round(100 * v[2] / v[1]) if v[1] else 0,
                }
                for k, v in sorted(d.items(), key=lambda kv: -kv[1][1])
            ]

        ben: dict[str, list] = {}
        for e in _dicts(tables.get("prr_entidades", ([], []))):
            if e["papel"] != "Beneficiário Final":
                continue
            b = ben.setdefault(
                e["nif"] or e["entidade"], [e["entidade"], 0, 0.0]
            )
            b[1] += 1
            b[2] += _f(e["contratado"]) * share.get(e["projeto"], 1)
        datas = sorted(p["referencia"] for p in proj if p["referencia"])
        out["prr"] = {
            "projetos": len(proj),
            "aprovado": _m(aprov),
            "pago": _m(pago),
            "pct_pago": round(100 * pago / aprov) if aprov else 0,
            "beneficiarios": len(ben),
            "referencia": datas[-1] if datas else "",
            "concelhos": lista(conc),
            "componentes": lista(comp),
            "maiores": [
                {"nif": k, "nome": v[0], "projetos": v[1], "valor": _m(v[2])}
                for k, v in sorted(ben.items(), key=lambda kv: -kv[1][2])[:25]
            ],
        }
    if "kohesio_projetos" in tables:
        proj = _dicts(tables["kohesio_projetos"])
        boas = [p for p in proj if not p["nota"]]
        prog: dict[str, list] = {}
        for p in proj:
            g = prog.setdefault(
                p["programa"] or "?", [p["periodo"], p["nota"], 0, 0.0, 0.0]
            )
            g[2] += 1
            g[3] += _f(p["custo_total"])
            g[4] += _f(p["apoio_ue"])
        periodos = {}
        for p in boas:
            g = periodos.setdefault(p["periodo"] or "?", [0, 0.0])
            g[0] += 1
            g[1] += _f(p["apoio_ue"])
        ben = _dicts(tables.get("kohesio_beneficiarios", ([], [])))
        out["kohesio"] = {
            "projetos": len(boas),
            "apoio_ue": _m(sum(_f(p["apoio_ue"]) for p in boas)),
            "custo_total": _m(sum(_f(p["custo_total"]) for p in boas)),
            "excluidos": len(proj) - len(boas),
            "excluidos_ue": _m(
                sum(_f(p["apoio_ue"]) for p in proj if p["nota"])
            ),
            "periodos": [
                {"nome": k, "projetos": v[0], "apoio_ue": _m(v[1])}
                for k, v in sorted(periodos.items())
            ],
            "programas": [
                {
                    "nome": k,
                    "periodo": v[0],
                    "nota": v[1],
                    "projetos": v[2],
                    "custo_total": _m(v[3]),
                    "apoio_ue": _m(v[4]),
                }
                for k, v in sorted(prog.items(), key=lambda kv: -kv[1][4])
            ],
            "beneficiarios": len(ben),
            "maiores": [
                {
                    "nome": b["beneficiario"],
                    "projetos": int(b["projetos"] or 0),
                    "apoio_ue": _m(_f(b["apoio_ue"])),
                    "ligacao": b["ligacao"],
                }
                for b in ben[:25]
            ],
        }
    return out


def write_fundos(docs: Path, tables: dict) -> None:
    """docs/_data/fundos.json for /financas/fundos-europeus/."""
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "fundos.json").write_text(
        json.dumps(_texts(fundos_data(tables)), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )


def write_camaras(docs: Path, tables: dict) -> None:
    """docs/_data/camaras.json for /financas/camaras/."""
    base = tables.get("base")
    if base and "recolha" in base[0]:
        # the per-capita contract totals cover what the bot saw day by day
        # (since August 2024), not the IMPIC years before
        i = base[0].index("recolha")
        base = (base[0], [r for r in base[1] if r[i] == DIARIO])
    data = camaras_data(tables["ine"], base) if "ine" in tables else {}
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "camaras.json").write_text(
        json.dumps(_texts(data), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )


def joraa_estado(line: dict) -> dict:
    """The JORAA days still missing, from the bot's last state line: the
    backfill range, or, before the bot has planned one, the days after the
    last one fetched (more than the few recent days a night run takes)."""
    hoje = dt.date.fromisoformat(line["datetime"][:10])
    last = dt.date.fromisoformat(line["last_joraa_update"])
    de = ate = None
    if line.get("joraa_backfill"):
        de, ate = (dt.date.fromisoformat(d) for d in line["joraa_backfill"])
    elif (hoje - last).days > 3:
        de, ate = last + dt.timedelta(days=1), hoje - dt.timedelta(days=1)
    if not de:
        return {}
    return {
        "atraso_de": de.strftime("%d/%m/%Y"),
        "atraso_ate": ate.strftime("%d/%m/%Y"),
        "dias": (ate - de).days + 1,
    }


def write_joraa_estado(docs: Path) -> None:
    """docs/_data/joraa_estado.json for the note on the JORAA backfill
    (_includes/joraa-atraso.html)."""
    state = docs.parent / "bot" / "state.jsonl"
    out: dict = {}
    if state.exists():
        lines = state.read_text(encoding="utf-8").strip().splitlines()
        if lines:
            out = joraa_estado(json.loads(lines[-1]))
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "joraa_estado.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8"
    )


def write_resumo(docs: Path, tables: dict) -> None:
    """docs/_data/resumo.json: the few numbers /introducao/ and /financas/ show, computed
    here so that page does not download the full CSVs."""
    out: dict = {}
    if "ine" in tables:
        out["ine"] = resumo_ine(*tables["ine"])
        out["salario_pib"] = salario_pib(*tables["ine"])
    if "beo" in tables:
        out["beo"] = resumo_beo(*tables["beo"])
        pop = out.get("ine", {}).get("0012918", {}).get("acores")
        if out["beo"] and pop:
            out["beo"]["despesa_hab"] = round(
                out["beo"]["despesa"] * 1e6 / pop
            )
    if "srea" in tables:
        out["srea"] = resumo_srea(*tables["srea"])
    if "tdc" in tables and "tdc_valores" in tables:
        out["tdc"] = resumo_tdc(tables["tdc"], tables["tdc_valores"])
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "resumo.json").write_text(
        json.dumps(_texts(out), ensure_ascii=False, indent=1), encoding="utf-8"
    )


def main(docs: Path) -> dict:
    out = docs / "dados"
    out.mkdir(exist_ok=True)
    meta = {"gerado": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%MZ")}
    tables: dict[str, tuple[list, list]] = {}
    base = build_base(docs)
    tables["base"] = (BASE_ALL, base)
    info = write(out, "base", BASE_COLS, [r[: len(BASE_COLS)] for r in base])
    datas = sorted(r[1] for r in base if r[1])
    info["de"], info["ate"] = (datas[0], datas[-1]) if datas else ("", "")
    diario = [d for d, _ in days(docs, "_base_updates")]
    info["diario_de"] = diario[0] if diario else ""
    meta["base"] = info
    for name, cols, build, coll in (
        ("alra", ALRA_COLS, build_alra, "_alra_updates"),
        ("joraa", JORAA_COLS, build_joraa, "_joraa_updates"),
    ):
        rows = build(docs)
        tables[name] = (cols, rows)
        info = write(out, name, cols, rows)
        all_days = [d for d, _ in days(docs, coll)]
        info["de"], info["ate"] = (
            (all_days[0], all_days[-1]) if all_days else ("", "")
        )
        meta[name] = info
    # fetched weekly into data/ by their bots
    maiores = sorted((docs.parent / "data").glob("maiores_*.csv"))
    for name in (
        "ine",
        "beo",
        "srea",
        "tdc",
        "tdc_valores",
        "sper",
        "sper_empresas",
        "sper_regiao",
        "maiores",
        "emprego_publico",
        "censos2021_setores",
        "at_irs",
        "at_irc",
        "at_distritos",
        "bportugal",
        "prr_projetos",
        "prr_entidades",
        "kohesio_projetos",
        "kohesio_beneficiarios",
    ):
        src = docs.parent / "data" / f"{name}.csv"
        if name == "maiores" and maiores:
            src = maiores[-1]  # the latest year entered
        if not src.exists():
            continue
        with open(src, encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            cols, rows = next(reader), list(reader)
        tables[name] = (cols, rows)
        info = write(out, name, cols, rows)
        when = next(
            (
                cols.index(c)
                for c in ("data", "conta", "ano", "inicio")
                if c in cols
            ),
            None,
        )
        dates = sorted(r[when] for r in rows if when is not None and r[when])
        info["de"], info["ate"] = (dates[0], dates[-1]) if dates else ("", "")
        if name == "ine":
            info["indicadores"] = len({r[0] for r in rows})
            write_ine_news(docs, cols, rows)
            defs = docs.parent / "data" / "ine_meta.json"
            if defs.exists():
                (out / "ine_meta.json").write_bytes(defs.read_bytes())
        elif name == "srea":
            (out / "srea.json").write_text(
                json.dumps(srea_json(cols, rows), ensure_ascii=False),
                encoding="utf-8",
            )
        elif name in ("beo", "tdc"):
            latest = beo_latest if name == "beo" else tdc_latest
            info["ultimo"] = latest(cols, rows)
            (docs / "_data").mkdir(exist_ok=True)
            (docs / "_data" / f"{name}_ultimo.json").write_text(
                json.dumps(info["ultimo"], ensure_ascii=False),
                encoding="utf-8",
            )
        meta[name] = info
    write_resumo(docs, tables)
    write_joraa_estado(docs)
    write_economia(docs, tables)
    write_camaras(docs, tables)
    write_irs(docs, tables)
    write_irc(docs, tables)
    write_credito(docs, tables)
    write_fundos(docs, tables)
    meta["bases"] = write_dbs(out, tables)
    (out / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return meta


if __name__ == "__main__":
    docs_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "docs")
    for k, v in main(docs_dir).items():
        if k == "bases":
            for name, b in v.items():
                print(
                    f"{name}.db",
                    round(b["bytes"] / 1e6, 1),
                    "MB",
                    b["tabelas"],
                )
        elif isinstance(v, dict):
            print(k, (v["linhas"], v["de"], v["ate"]))
        else:
            print(k, v)
