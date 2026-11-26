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
  meta.json  row counts, date coverage, build time

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
DB_TYPES = {"id": "INTEGER", "preco": "REAL", "montante": "REAL"}
DB_INDEX = {
    "base": ["publicado", "data_assinatura", "adjudicante", "adjudicatario"],
    "alra": ["tipo", "data", "primeiro_dia", "autores"],
    "joraa": ["publicado", "entidade"],
}
DB_FTS = {
    "base": ["objeto", "adjudicante", "adjudicatario", "procedimento"],
    "alra": ["titulo", "autores", "estado", "tipo"],
    "joraa": ["titulo", "ato", "entidade"],
}


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
        info["de"], info["ate"] = all_days[0], all_days[-1]
        meta[name] = info
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
