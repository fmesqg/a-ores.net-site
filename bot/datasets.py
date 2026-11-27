"""Cumulative open datasets built from the daily update pages.

Usage: python3 bot/datasets.py [docs_dir]   (stdlib only, no poetry needed)

The bot writes one markdown page per source per day (docs/_base_updates/,
docs/_alra_updates/, docs/_joraa_updates/). This module re-reads all of them
and writes, under docs/dados/:

  base.csv   one row per BASE contract (deduplicated by id)
  alra.csv   one row per ALRA record (requerimento, iniciativa, voto, ...),
             with the first/last day it appeared and its last known state
  joraa.csv  one row per JORAA act with an amount
  acores.db  the same three tables in SQLite, typed, indexed and with an
             FTS5 index per table (<table>_fts), for SQL and Datasette Lite
  ine.csv    INE indicators for the Azores by region, concelho and
             freguesia: a copy of data/ine.csv, which bot/ine.py fetches
             weekly (it needs the network, so it is not rebuilt here)
  ine_meta.json  definitions of each INE indicator (concepts, formula,
             source, note): a copy of data/ine_meta.json, from bot/ine.py
  beo.csv    the regional government's monthly budget execution (Boletim
             de Execução Orçamental): a copy of data/beo.csv, which
             bot/beo.py parses from the PDFs weekly
  srea.csv   SREA series (inflation, economic activity, unemployment,
             tourism by island, GDP by island): a copy of data/srea.csv,
             which bot/srea.py fetches weekly
  srea.json  the same series, compact, for the charts on /dados/srea/
  meta.json  row counts, date coverage, build time

and, under docs/_data/ (read by Jekyll): ine_novidades.json, beo_ultimo.json
and resumo.json (the numbers on /acores-101/ and /dados/srea/).

The CSVs are UTF-8 with BOM, so Excel opens accents correctly. The search
page (docs/dados.md) reads them directly. None of these files is committed:
.github/workflows/pages.yml generates them when it builds the site.
"""

import csv
import datetime as dt
import json
import re
import sqlite3
import sys
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
]


def build_base(docs: Path) -> list[list]:
    rows = {}
    for day, path in days(docs, "_base_updates"):
        for _, title, url, subs in parse_day(path):
            f = fields(subs)
            cid = re.search(r"id=(\d+)", url)
            key = cid[1] if cid else url
            rows[key] = [
                int(key) if key.isdigit() else key,
                day,
                iso(f.get("data da assinatura", "")),
                euros(f.get("preço contratual", ""), ","),
                f.get("adjudicante", ""),
                f.get("adjudicatário", ""),
                f.get("tipo de procedimento", ""),
                title,
                url,
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
    "entidade",
    "serie",
    "url",
]


def build_joraa(docs: Path) -> list[list]:
    rows = {}
    for day, path in days(docs, "_joraa_updates"):
        for _, title, url, subs in parse_day(path):
            ato = subs[0] if subs else ""
            montante = next(
                (euros(s, ".") for s in subs if s.startswith("Soma")), None
            )
            serie = next((s for s in subs if s.startswith("Jornal")), "")
            entidade = next(
                (s for s in subs[1:] if not s.startswith(("Soma", "Jornal"))),
                "",
            )
            rows[url] = [day, ato, title, montante, entidade, serie, url]
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
    "montante": "REAL",
    "valor": "REAL",
    "ordem": "INTEGER",
    "ano": "INTEGER",
    "mes": "INTEGER",
}
DB_INDEX = {
    "base": ["publicado", "data_assinatura", "adjudicante", "adjudicatario"],
    "alra": ["tipo", "data", "primeiro_dia", "autores"],
    "joraa": ["publicado", "entidade"],
    "ine": ["varcd", "data", "nivel", "local", "concelho"],
    "beo": ["quadro", "data", "caminho", "dimensao"],
    "srea": ["serie", "data", "local"],
}
DB_FTS = {
    "base": ["objeto", "adjudicante", "adjudicatario", "procedimento"],
    "alra": ["titulo", "autores", "estado", "tipo"],
    "joraa": ["titulo", "ato", "entidade"],
    "ine": ["indicador", "tema", "local", "concelho", "ilha", "categoria"],
    "beo": ["quadro", "rubrica", "caminho", "dimensao"],
    "srea": ["indicador", "rubrica", "local"],
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
    """Write tables to a fresh SQLite file. Each table gets an external
    content FTS5 index declared as content=[table], the form Datasette
    detects to show a search box."""
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


# Indicators shown on /acores-101/ (Açores vs Madeira vs país, latest year).
RESUMO_INE = (
    "0012918",  # população residente
    "0012909",  # índice de envelhecimento
    "0012757",  # rendimento mediano após IRS por sujeito passivo
    "0012656",  # ganho médio mensal
    "0013420",  # RSI por 1000 habitantes
    "0014698",  # renda mediana, novos contratos (€/m²)
    "0013210",  # dormidas por 100 habitantes
)


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
    """Latest SREA figures for /acores-101/ and /dados/srea/."""
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


def write_resumo(docs: Path, tables: dict) -> None:
    """docs/_data/resumo.json: the few numbers /acores-101/ shows, computed
    here so that page does not download the full CSVs."""
    out: dict = {}
    if "ine" in tables:
        out["ine"] = resumo_ine(*tables["ine"])
    if "beo" in tables:
        out["beo"] = resumo_beo(*tables["beo"])
        pop = out.get("ine", {}).get("0012918", {}).get("acores")
        if out["beo"] and pop:
            out["beo"]["despesa_hab"] = round(
                out["beo"]["despesa"] * 1e6 / pop
            )
    if "srea" in tables:
        out["srea"] = resumo_srea(*tables["srea"])
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "resumo.json").write_text(
        json.dumps(_texts(out), ensure_ascii=False, indent=1), encoding="utf-8"
    )


def main(docs: Path) -> dict:
    out = docs / "dados"
    out.mkdir(exist_ok=True)
    meta = {"gerado": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%MZ")}
    tables: dict[str, tuple[list, list]] = {}
    for name, cols, build, coll in (
        ("base", BASE_COLS, build_base, "_base_updates"),
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
    for name in ("ine", "beo", "srea"):  # fetched weekly by their bots
        src = docs.parent / "data" / f"{name}.csv"
        if not src.exists():
            continue
        with open(src, encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            cols, rows = next(reader), list(reader)
        tables[name] = (cols, rows)
        info = write(out, name, cols, rows)
        dates = sorted(
            r[cols.index("data")] for r in rows if r[cols.index("data")]
        )
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
        else:
            info["ultimo"] = beo_latest(cols, rows)
            (docs / "_data").mkdir(exist_ok=True)
            (docs / "_data" / "beo_ultimo.json").write_text(
                json.dumps(info["ultimo"], ensure_ascii=False),
                encoding="utf-8",
            )
        meta[name] = info
    write_resumo(docs, tables)
    write_db(out / "acores.db", tables)
    meta["acores.db"] = (out / "acores.db").stat().st_size
    (out / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return meta


if __name__ == "__main__":
    docs_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "docs")
    for k, v in main(docs_dir).items():
        print(
            k,
            v if not isinstance(v, dict) else (v["linhas"], v["de"], v["ate"]),
        )
