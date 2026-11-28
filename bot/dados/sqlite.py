"""The SQLite files under docs/dados/ (one per theme): column types, indexes, full-text search."""

import sqlite3
from pathlib import Path

from .comum import MESES

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
    "dias": "INTEGER",
    "ano_lucro": "INTEGER",
    **{
        c: "REAL"
        for c in (
            "limite",
            "divida_total",
            "nao_orcamental",
            "fam",
            "divida",
            "pct_limite",
            "fef",
            "fsm",
            "irs",
            "irs_max",
            "irs_pct",
            "iva",
            "excedente",
            "receita_cobrada",
            "receita_liquidada",
            "despesa_comprometida",
            "taxa_geral",
            "taxa_reduzida",
        )
    },
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
    "dgal_contas": ["ano", "geocod", "mapa", "codigo"],
    "dgal_divida": ["ano", "geocod"],
    "dgal_pmp": ["data", "geocod"],
    "dgal_transferencias": ["ano", "geocod"],
    "anuario_execucao": ["ano", "geocod"],
    "derrama_municipal": ["ano_lucro", "geocod"],
}
DB_FTS = {
    "base": ["objeto", "adjudicante", "adjudicatario", "procedimento", "cpv"],
    "alra": ["titulo", "autores", "estado", "tipo"],
    "joraa": ["titulo", "ato", "entidade", "outros"],
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
    "dgal_contas": ["municipio", "descricao"],
    # dgal_divida, dgal_pmp: numbers per câmara; facets do the search
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
        "dgal_contas",
        "dgal_divida",
        "dgal_pmp",
        "dgal_transferencias",
        "anuario_execucao",
        "derrama_municipal",
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
