"""ALRA records and JORAA acts, re-read from the daily update pages; the JORAA backfill note."""

import datetime as dt
import json
import re
from pathlib import Path

from .comum import STATE, days, euros, fields, iso, links, parse_day

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
