import json
import os
import re

from .constants import CATEGORIAS_REQUERIMENTOS, STATE_FILE
from .export import Export
from .fetch import Blob, FetchError


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


def write_update(web_data: Blob, date=None):
    # portal = web_data.portal
    alra = (
        Export.markdown(web_data.alra)
        if not isinstance(web_data.alra, FetchError)
        else ""
    )
    joraa = (
        markdown_joraa(web_data.joraa)
        if not isinstance(web_data.joraa, FetchError)
        else ""
    )
    base = (
        markdown_base(web_data.base)
        if not isinstance(web_data.base, FetchError)
        else ""
    )
    portal = (
        markdown_portal(web_data.portal)
        if not isinstance(web_data.portal, FetchError)
        else ""
    )

    write_collection(date, alra, title="Atualização (ALRA)", folder="_alra_updates")

    write_collection(date, joraa, title="Atualização (JORAA)", folder="_joraa_updates")

    write_collection(date, base, title="Atualização (BASE)", folder="_base_updates")
    write_collection(
        date,
        portal,
        title="Atualização (portal.azores.gov.pt)",
        folder="_portal_updates",
    )

    write_post(date, joraa=joraa, alra=alra, contratos=base, portal=portal)


def write_collection(date, update, title, folder):
    page_font_matter = f"""---
date: {date}
title: {title}
---
"""
    if update:
        path = os.path.join(os.path.dirname(__file__), "..", folder, f"{date}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(page_font_matter + update + "\n")


def write_post(date, alra, joraa, contratos, portal):
    page_font_matter = f"""---
layout: default
date: {date}
categories: alra-scrapper
title: Atualização (ALRA + JORAA + Base)
---
"""
    if post_body := "\n\n".join([i for i in [alra, joraa, contratos, portal] if i]):
        path = os.path.join(
            os.path.dirname(__file__), "..", "_complete_updates", f"{date}.md"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(page_font_matter + post_body + "\n")


def markdown_joraa(entries):
    start = "## JORAA\n\n"
    url_entry_base = "https://jo.azores.gov.pt/#/ato/"

    def md(entry):
        entry_text = entry.text
        # entry_text = fetch_joraa_ato(entry["id"]).json()["considerandos"]
        sum_amounts = sum(
            parse_currency_to_number(amount) for amount in find_monies(entry_text)
        )
        entry = entry.json()  # TODO clean-up
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
    breakpoint()
    return start + "\n\n".join([text for pair in sorted_entries if (text := pair[2])])


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

    return start + "".join([md(entry) for entry in entries])


def markdown_portal(delta):
    portal = ""
    if delta:
        portal = "## Atualizações em portal.azores.gov.pt\n\n"
        if a := delta.get("boletins", None):
            for update in a:
                portal += f"* [{update}]({update})" + "\n"
        if a := delta.get("sigica", None):
            for update in a:
                portal += f"* [{update}]({update})" + "\n"
    return portal


def append_state(state: dict, timestamp):
    def f(i):
        if isinstance(i, FetchError):
            return "fetch_error"
        return i

    state = {k: f(v) for k, v in state.items()}
    state.update({"datetime": timestamp})
    path = os.path.join(os.path.dirname(__file__), STATE_FILE)
    with open(path, mode="a") as f:
        try:
            f.write("\n" + json.dumps(state))
        except Exception:
            pass


def get_prev_state():
    path = os.path.join(os.path.dirname(__file__), STATE_FILE)
    with open(path, mode="r") as f:
        last = ""
        for line in f.readlines():
            last = line
    return json.loads(last)


def compute_delta_ids(prev, current):
    # TODO: there should be a common logic for all except sigica and beo... one failure
    # should make them all fail.
    # TODO: iniciativas need extra handling too
    reqs = current["requerimentos"]
    if not isinstance(reqs, FetchError):
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
    else:
        delta_dict = {"requerimentos": FetchError()}

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
        "boletins",
        "sigica",
    ]:
        if not isinstance(current[key], FetchError):
            if delta := list(set(current[key]).difference(set(prev[key]))):
                deltas[key] = delta
        else:
            deltas[key] = current[key]  # propagate errors

    delta_dict.update(deltas)
    return delta_dict
