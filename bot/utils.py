import json
import logging
import os
import re

from .classes import FetchError, WebData
from .constants import (
    CATEGORIAS_REQUERIMENTOS,
    NOW_DATETIME,
    OLD_STATE_FILE,
    STATE_FILE,
    YESTERDAY_DATE,
)
from .export import Export
from .state import State

logger = logging.getLogger(__name__)


# The amount shown for a JORAA act (markdown_joraa). Since 2026 the API gives
# the text in "considerandos" (the preamble, or all of a short act) and
# "normativos" (articles or clauses); older answers had "textoIntegral".
# "anexos" are separate files and are not read, so an act whose amounts are
# only in an annex (the portarias with the grants to each freguesia) shows
# none. Adding up every amount in the text, as the bot did until November
# 2026, counted a repeated amount twice and added the cost of a project to
# its grant, or the old values of an amended agreement to the new ones.
_AMOUNT = re.compile(
    r"(?<![\d.,])(?<!n\.º )"
    r"(\d{1,3}(?:\.\d{3})+|\d{1,3}(?:[ \xa0]\d{3}){1,2}|\d+)(,\d{2})?"
    r"(?=[ \xa0]?(?:€|euros\b|EUR\b))",
    re.I,
)
# procurement notices: the price of the whole procedure, before the lots
_BASE_PRICE = (
    re.compile(
        r"preço base do procedimento \(EUR\): \(\*\)\s*([\d. ]+,\d{2})", re.I
    ),
    re.compile(r"preço base s/IVA \(€\): \(\*\)\s*([\d. ]+,\d{2})", re.I),
)
# words just before an amount that make it a part or the cost of the
# project, not the amount granted or authorised
_PART = re.compile(
    r"prestaç|tranche|parcela|inclu[ií]|custo|investimento|orçamento"
    r"|despesa elegível|deixando de",
    re.I,
)
# an act that lists several grants: their amounts add up
_LIST = re.compile(
    r"\bseguintes:?\s+(?:apoios|comparticipaç|verbas|montantes|subsídios"
    r"|incentivos|transferências|valores|importâncias)",
    re.I,
)


def _plain(html_text) -> str:
    text = re.sub(r"<[^>]+>", " ", str(html_text or ""))
    return text.replace("&nbsp;", " ").replace("\xa0", " ")


def _amounts(text: str) -> list[tuple[float, str]]:
    """Each amount in euros in ``text`` with the words just before it."""
    out, prev = [], 0
    for m in _AMOUNT.finditer(text):
        value = float(
            re.sub(r"[ .\xa0]", "", m[1]) + (m[2] or "").replace(",", ".")
        )
        out.append((value, text[max(prev, m.start() - 100) : m.start()]))
        prev = m.end()
    return out


def joraa_amount(entry: dict) -> tuple[float, str] | None:
    """The act's amount and what it is: the base price of a procurement
    notice; the sum of the grants an act lists; otherwise the largest amount
    of the operative text (clauses, or the whole text when there are none),
    leaving out instalments and the cost of the project. None when the text
    has no amount in euros."""
    preamble = _plain(entry.get("considerandos") or entry.get("textoIntegral"))
    clauses = " ".join(
        _plain(n.get("normativo")) if isinstance(n, dict) else _plain(n)
        for n in entry.get("normativos") or []
    )
    text = f"{entry.get('sumario', '')} {preamble} {clauses}"
    for pattern in _BASE_PRICE:
        if m := pattern.search(text):
            return float(re.sub(r"[ .]", "", m[1]).replace(",", ".")), (
                "preço base"
            )
    found = _amounts(clauses) or _amounts(text)
    if not found:
        return None
    kept = [v for v, before in found if not _PART.search(before)]
    if _LIST.search(text) and len(kept) > 1:
        return sum(kept), f"soma de {len(kept)} valores"
    values = kept or [v for v, _ in found]
    return max(values), "valor" if len(set(values)) == 1 else "maior valor"


def euros_pt(value: float) -> str:
    """1234567.8 -> '1 234 567,80 €'."""
    return f"{value:,.2f} €".replace(",", " ").replace(".", ",")


def write_update(web_data: WebData):
    if not isinstance(web_data.alra, FetchError):
        write_collection(
            YESTERDAY_DATE,
            Export.markdown(web_data.alra),
            title="Atualização (ALRA)",
            folder="_alra_updates",
        )
    else:
        write_collection(
            YESTERDAY_DATE,
            f"Erro: Problema a conectar a alra.pt\n{web_data.alra.info}\n.",
            title="Atualização (ALRA)",
            folder="_alra_updates",
        )
    if not isinstance(web_data.joraa, FetchError):
        for day, data in web_data.joraa.items():
            day_joraa_string = markdown_joraa(data)
            write_collection(
                day.strftime("%Y-%m-%d"),
                day_joraa_string,
                title="Atualização (JORAA)",
                folder="_joraa_updates",
            )
    else:
        write_collection(
            YESTERDAY_DATE,
            f"Erro: Sem conexão ao site JORAA {web_data.joraa.info}",
            title="Atualização (JORAA)",
            folder="_joraa_updates",
        )

    if not isinstance(web_data.base, FetchError):
        for day, data in web_data.base.items():
            day_base_string = markdown_base(data)
            write_collection(
                day.strftime("%Y-%m-%d"),
                day_base_string,
                title="Atualização (BASE)",
                folder="_base_updates",
            )
    else:
        write_collection(
            YESTERDAY_DATE,
            "Erro: Problema a conectar a base.gov.pt",
            title="Atualização (BASE)",
            folder="_base_updates",
        )
    if not isinstance(web_data.portal, FetchError):
        write_collection(
            YESTERDAY_DATE,
            markdown_portal(web_data.portal),
            title="Atualização (portal.azores.gov.pt)",
            folder="_portal_updates",
        )
    else:
        write_collection(
            YESTERDAY_DATE,
            "Erro: Problema a conectar a portal.azores.gov.pt",
            title="Atualização (portal.azores.gov.pt)",
            folder="_portal_updates",
        )


# Scraped text (ALRA petitions and votes, JORAA, BASE, error messages) goes
# into these pages as-is. kramdown passes raw HTML through, and Jekyll runs
# Liquid on the page, so "<" would let a title inject HTML or script, "{{" or
# "{%" would run Liquid (or break the build), and "{:" would add attributes.
# Links other than http(s) or site-relative (e.g. "javascript:") are dropped.
_UNSAFE_CHARS = {"<": "&lt;", "{": "&#123;", "}": "&#125;"}
_UNSAFE_LINK = re.compile(
    r"\]\((?!\s*(?:https?://|/|#))(?:[^()]|\([^()]*\))*\)", re.I
)


def safe_markdown(text: str) -> str:
    """Neutralise HTML, Liquid and unsafe links in generated markdown."""
    text = re.sub("[<{}]", lambda m: _UNSAFE_CHARS[m.group()], text)
    return _UNSAFE_LINK.sub("](#)", text)


def write_collection(date: str, update, title, folder):
    page_font_matter = f"""---
date: {date}
title: {title}
layout: default
---
"""
    if update:
        path = os.path.join(
            os.path.dirname(__file__), "..", "docs", folder, f"{date}.md"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(page_font_matter + safe_markdown(update) + "\n")


def markdown_joraa(entries):
    start = "## JORAA\n\n"
    url_entry_base = "https://jo.azores.gov.pt/#/ato/"

    def md(entry: dict):
        amount = joraa_amount(entry)
        lines = [
            f"* [{entry['sumario'].strip()}]({url_entry_base}{entry['id']})",
            f"  * {entry['humanId']}",
        ]
        if amount:
            lines.append(f"  * Montante: {euros_pt(amount[0])} ({amount[1]})")
        entidades = "\n".join(
            [f"  * {ent['nome']}" for ent in entry["entidades"]]
        )
        lines += [entidades, f"  * {entry['descricaoPublicacao']}"]
        return amount[0] if amount else 0, entidades, "\n".join(lines)

    sorted_entries = sorted(
        [md(entry) for entry in entries], key=lambda tup: (-tup[0], tup[1])
    )
    if body := "\n\n".join(
        [text for pair in sorted_entries if (text := pair[2])]
    ):
        return start + body


def markdown_base(entries):
    start = "## Contratos publicados ontem\n\n"
    url_entry_base = (
        "https://www.base.gov.pt/Base4/pt/detalhe/?type=contratos&id="
    )

    def md(entry):
        md = f"* [{entry['objectBriefDescription'].strip()}]({url_entry_base}{entry['id']})\n"  # noqa: E501
        md += f"  * Preço contratual: {entry['initialContractualPrice']}\n"
        md += f"  * Adjudicante: {entry['contracting']}\n"
        md += f"  * Adjudicatário: {entry['contracted']}\n"
        md += (
            f"  * Tipo de procedimento: {entry['contractingProcedureType']}\n"
        )
        md += f"  * Data da assinatura: {entry['signingDate']}\n"

        return md

    if body := "".join([md(entry) for entry in entries]):
        return start + body


def markdown_portal(delta):
    if not sum(len(v) for v in delta.values()):
        return ""
    if delta:
        portal = "## Atualizações em portal.azores.gov.pt\n\n"
        if a := delta.get("boletins", None):
            for update in a:
                portal += f"* [{update}]({update})" + "\n"
        if a := delta.get("sigica", None):
            for update in a:
                portal += f"* [{update}]({update})" + "\n"
    return portal


def _sorted(v):
    """Lists in a stable order, so the daily diff of state.json shows only
    what changed."""
    if isinstance(v, dict):
        return {k: _sorted(x) for k, x in v.items()}
    if isinstance(v, list | set | tuple):
        return sorted(v, key=lambda x: (type(x).__name__, x))
    return v


def append_state(state: State):
    """Write the run's state to bot/state.json, replacing the previous one
    (git keeps the history), and remove the old state.jsonl ledger. If the
    state cannot be serialised the file is left as it was and the error is
    raised, so the run fails instead of losing the state."""
    state_json: dict = {
        "datetime": NOW_DATETIME.strftime("%Y-%m-%d %H:%M:%S"),
        "last_joraa_update": state.last_joraa_update.strftime("%Y-%m-%d"),
        "joraa_backfill": (
            [d.strftime("%Y-%m-%d") for d in state.joraa_backfill]
            if state.joraa_backfill
            else None
        ),
        "last_base_update": state.last_base_update.strftime("%Y-%m-%d"),
        "boletins": _sorted(state.data["boletins"]),
        "sigica": _sorted(state.data["sigica"]),
    }
    state_json.update(_sorted(state.alra_state))
    folder = os.path.dirname(__file__)
    path = os.path.join(folder, STATE_FILE)
    try:
        text = json.dumps(state_json, ensure_ascii=False, indent=1) + "\n"
    except (TypeError, ValueError) as exc:
        logger.error("State write failed: %s", exc)
        raise
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)
    old = os.path.join(folder, OLD_STATE_FILE)
    if os.path.exists(old):
        os.remove(old)


def get_prev_state() -> State:
    """The last run's state: bot/state.json, or, before the first run that
    wrote it, the last line of the old bot/state.jsonl."""
    folder = os.path.dirname(__file__)
    path = os.path.join(folder, STATE_FILE)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return State(json.load(f))
    with open(os.path.join(folder, OLD_STATE_FILE), encoding="utf-8") as f:
        last = ""
        for line in f:
            if line.strip():
                last = line
    return State(json.loads(last))


def compute_delta_ids(prev: State, current_ids: dict) -> dict:
    """Return a delta of the ids not present in the prev State."""
    prev = prev.data

    reqs = current_ids["requerimentos"]
    today_dict = {
        req_id: cat for cat in CATEGORIAS_REQUERIMENTOS for req_id in reqs[cat]
    }
    prev_dict = {
        req_id: cat
        for cat in CATEGORIAS_REQUERIMENTOS
        for req_id in prev["requerimentos"][cat]
    }
    delta_reqs = [
        (id, last_cat, cat)
        for id, cat in today_dict.items()
        if (last_cat := prev_dict.get(id, None)) != cat
    ]
    delta_dict = {"requerimentos": delta_reqs} if delta_reqs else {}

    deltas = {}
    for key in [
        "informacoes",
        "votos",
        "iniciativas",
        "diarios",
        "intervencoes",
        "peticoes",
        "audi_ar",
        "audi_gr",
    ]:
        if delta := list(set(current_ids[key]).difference(set(prev[key]))):
            deltas[key] = delta

    delta_dict.update(deltas)
    return delta_dict
