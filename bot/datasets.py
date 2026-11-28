"""Cumulative open datasets built from the daily update pages.

Usage: python3 bot/datasets.py [docs_dir]   (stdlib only, no poetry needed)

The bot writes one markdown page per source per day (docs/_base_updates/,
docs/_alra_updates/, docs/_joraa_updates/); bot/arquivo.py folds the ALRA
and JORAA pages into data/alra.csv.gz and data/joraa.csv.gz and drops pages
older than 90 days. This module reads those archives plus the pages left
and writes, under docs/dados/:

  base.csv   one row per BASE contract since 2012, from the IMPIC open data
             (data/base_impic/, from bot/base_impic.py; not from the daily
             pages, which keep only five fields per contract); contratos.db carries more columns (NIFs, CPV, base and final
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

The code is split by source under bot/dados/ (base, parlamento, sqlite,
resumo, empresas, publico, camaras, impostos, credito, fundos, comum);
this file only runs them in order.
"""

import csv
import datetime as dt
import gzip
import json
import sys
from pathlib import Path

try:  # imported as bot.datasets (tests)
    from .dados.base import (
        BASE_ALL,
        BASE_COLS,
        build_base,
        check_base,
        write_base_anos,
    )
    from .dados.camaras import write_camaras
    from .dados.comum import write
    from .dados.credito import write_credito
    from .dados.empresas import write_economia
    from .dados.fundos import write_fundos
    from .dados.impostos import write_irc, write_irs
    from .dados.parlamento import (
        ALRA_COLS,
        JORAA_COLS,
        build_alra,
        build_joraa,
        read_archive,
        write_joraa_estado,
    )
    from .dados.resumo import srea_json, write_ine_news, write_resumo
    from .dados.sqlite import beo_latest, tdc_latest, write_dbs
except ImportError:  # run as python3 bot/datasets.py
    from dados.base import (
        BASE_ALL,
        BASE_COLS,
        build_base,
        check_base,
        write_base_anos,
    )
    from dados.camaras import write_camaras
    from dados.comum import write
    from dados.credito import write_credito
    from dados.empresas import write_economia
    from dados.fundos import write_fundos
    from dados.impostos import write_irc, write_irs
    from dados.parlamento import (
        ALRA_COLS,
        JORAA_COLS,
        build_alra,
        build_joraa,
        read_archive,
        write_joraa_estado,
    )
    from dados.resumo import srea_json, write_ine_news, write_resumo
    from dados.sqlite import beo_latest, tdc_latest, write_dbs


def main(docs: Path) -> dict:
    out = docs / "dados"
    out.mkdir(exist_ok=True)
    meta = {"gerado": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%MZ")}
    tables: dict[str, tuple[list, list]] = {}
    base = build_base(docs)
    tables["base"] = (BASE_ALL, base)
    meta["verificacao"] = check_base(base)
    info = write(out, "base", BASE_COLS, [r[: len(BASE_COLS)] for r in base])
    datas = sorted(r[1] for r in base if r[1])
    info["de"], info["ate"] = (datas[0], datas[-1]) if datas else ("", "")
    info["anos"] = write_base_anos(out, base)
    meta["base"] = info
    # the archive in data/ (bot/arquivo.py) plus the pages not yet in it
    for name, cols, build, primeiro, ultimo in (
        ("alra", ALRA_COLS, build_alra, "primeiro_dia", "ultimo_dia"),
        ("joraa", JORAA_COLS, build_joraa, "publicado", "publicado"),
    ):
        arquivo = docs.parent / "data" / f"{name}.csv.gz"
        rows = build(docs, read_archive(arquivo, cols))
        tables[name] = (cols, rows)
        info = write(out, name, cols, rows)
        de = [r[cols.index(primeiro)] for r in rows if r[cols.index(primeiro)]]
        ate = [r[cols.index(ultimo)] for r in rows if r[cols.index(ultimo)]]
        info["de"], info["ate"] = (min(de), max(ate)) if rows else ("", "")
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
        "dgal_contas",
        "dgal_divida",
        "dgal_pmp",
        "dgal_transferencias",
        "anuario_execucao",
        "derrama_municipal",
    ):
        src = docs.parent / "data" / f"{name}.csv"
        if name == "maiores" and maiores:
            src = maiores[-1]  # the latest year entered
        if not src.exists() and src.with_suffix(".csv.gz").exists():
            src = src.with_suffix(".csv.gz")
        if not src.exists():
            continue
        opener = gzip.open if src.suffix == ".gz" else open
        with opener(src, "rt", encoding="utf-8-sig", newline="") as f:
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
    meta = main(docs_dir)
    for k, v in meta.items():
        if k == "verificacao":
            for x in v["avisos"]:
                print(f"::warning::{x}")
            for x in v["erros"]:
                print(f"::error::{x}")
        elif k == "bases":
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
    if meta["verificacao"]["erros"]:
        sys.exit(1)
