import json
import os
import re

from .classes import FetchError, WebData
from .constants import (
    CATEGORIAS_REQUERIMENTOS,
    NOW_DATETIME,
    STATE_FILE,
    YESTERDAY_DATE,
)
from .export import Export
from .state import State


def find_monies(text: str):
    text = text.replace("&nbsp;", " ")  # great json we get from JORAA...
    pattern1 = r"(\b\d{1,3}(?:[\.\s]\d{3})*(?:,\d{2})?\s?€)"
    pattern2 = r"(€\s?\d{1,3}(?:[\.\s]\d{3})*(?:,\d{2})?)"
    return re.findall(pattern1, text) + re.findall(pattern2, text)


def parse_currency_to_number(currency_str):
    clean_str = currency_str.replace("€", "").strip()
    clean_str = clean_str.replace(".", "").replace(" ", "")
    clean_str = clean_str.replace(",", ".")
    return float(clean_str)


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


def write_collection(date: str, update, title, folder):
    page_font_matter = f"""---
date: {date}
title: {title}
layout: default
---
"""
    if update:
        path = os.path.join(os.path.dirname(__file__), "..","docs", folder, f"{date}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(page_font_matter + update + "\n")


def markdown_joraa(entries):
    start = "## JORAA\n\n"
    url_entry_base = "https://jo.azores.gov.pt/#/ato/"

    def md(entry: dict):
        entry_text = str(entry)
        sum_amounts = sum(
            parse_currency_to_number(amount) for amount in find_monies(entry_text)
        )
        header = f"* [{entry['sumario'].strip()}]({url_entry_base}{entry['id']})"
        human_id = f"  * {entry['humanId']}"
        sum_str = f"  * Soma dos montantes: {sum_amounts:,.2f} €"
        entidades = "\n".join([f"  * {ent['nome']}" for ent in entry["entidades"]])
        return (
            sum_amounts,
            entidades,
            header
            + "\n"
            + human_id
            + "\n"
            + sum_str
            + "\n"
            + entidades
            + "\n  * "
            + entry["descricaoPublicacao"],
        )

    sorted_entries = sorted(
        [md(entry) for entry in entries], key=lambda tup: (-tup[0], tup[1])
    )
    if body := "\n\n".join([text for pair in sorted_entries if (text := pair[2])]):
        return start + body


def markdown_base(entries):
    start = "## Contratos publicados ontem\n\n"
    url_entry_base = "https://www.base.gov.pt/Base4/pt/detalhe/?type=contratos&id="

    def md(entry):
        md = f"* [{entry['objectBriefDescription'].strip()}]({url_entry_base}{entry['id']})\n"  # noqa: 501
        md += f"  * Preço contratual: {entry['initialContractualPrice']}\n"
        md += f"  * Adjudicante: {entry['contracting']}\n"
        md += f"  * Adjudicatário: {entry['contracted']}\n"
        md += f"  * Tipo de procedimento: {entry['contractingProcedureType']}\n"
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


def append_state(state: State):
    state_json: dict = {
        "datetime": NOW_DATETIME.strftime("%Y-%m-%d %H:%M:%S"),
        "last_joraa_update": state.last_joraa_update.strftime("%Y-%m-%d"),
        "last_base_update": state.last_base_update.strftime("%Y-%m-%d"),
        "boletins": list(state.data["boletins"]),
        "sigica": list(state.data["sigica"]),
    }
    state_json.update(state.alra_state)
    path = os.path.join(os.path.dirname(__file__), STATE_FILE)
    with open(path, mode="a") as f:
        try:
            f.write("\n" + json.dumps(state_json))
        except Exception as exc:
            print(exc)
            f.write("\n" + json.dumps({"datetime": NOW_DATETIME, "error": str(exc)}))


def get_prev_state() -> State:
    path = os.path.join(os.path.dirname(__file__), STATE_FILE)
    with open(path, mode="r") as f:
        last = ""
        for line in f.readlines():
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
