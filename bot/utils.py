import json
import os
import re
from datetime import datetime, timedelta

from .constants import CATEGORIAS_REQUERIMENTOS, STATE_FILE
from .export import Export
from .fetch import fetch_day_joraa, fetch_contratos_RAA, fetch_joraa_ato


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


def write_post(delta: dict[str, object], date=None):
    if not date:
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    markdown = Export.markdown(delta) if delta else ""
    markdown_jo = (
        markdown_joraa(joraa_entries)
        if (joraa_entries := fetch_day_joraa(date))
        else ""
    )
    markdown_contratos = (
        markdown_base(base_entries)
        if (base_entries := fetch_contratos_RAA(from_pub_date=date, to_pub_date=date))
        else ""
    )

    page_font_matter = f"""---
layout: default
date: {date}
categories: alra-scrapper
title: Update (ALRA + JORAA) - {date}
---
"""
    if post_body := "\n\n".join(
        [i for i in [markdown, markdown_jo, markdown_contratos] if i]
    ):
        path = os.path.join(
            os.path.dirname(__file__), "..", "_posts", f"{date}-alra.md"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(page_font_matter + post_body + "\n")


def markdown_joraa(entries):
    start = "## JORAA\n\n"
    url_entry_base = "https://jo.azores.gov.pt/#/ato/"

    def md(entry):
        entry_text = fetch_joraa_ato(entry["id"]).json()["considerandos"]
        sum_amounts = sum(
            parse_currency_to_number(amount) for amount in find_monies(entry_text)
        )
        header = f"* [{entry['sumario'].strip()}]({url_entry_base}{entry['id']})"
        human_id = f"  * {entry['humanId']}"
        sum_str = f"  * Soma dos montantes: {sum_amounts:,.2f} €"
        entidades = "\n".join([f"  * {ent}" for ent in entry["entidades"]])
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
    return start + "\n\n".join([text for pair in sorted_entries if (text := pair[2])])


def markdown_base(entries):
    start = "## Contratos publicados ontem\n\n"
    url_entry_base = "https://www.base.gov.pt/Base4/pt/detalhe/?type=contratos&id="

    def md(entry):
        md = f"* [{entry['objectBriefDescription']}]({url_entry_base}{entry['id']})\n"
        md += f"  * Preço contratual: {entry['initialContractualPrice']}\n"
        md += f"  * Adjudicante: {entry['contracting']}\n"
        md += f"  * Adjudicatário: {entry['contracted']}\n"
        md += f"  * Tipo de procedimento: {entry['contractingProcedureType']}\n"
        md += f"  * Data da assinatura: {entry['signingDate']}\n"

        return md

    return start + "".join([md(entry) for entry in entries])


def append_state(state: dict):
    path = os.path.join(os.path.dirname(__file__), STATE_FILE)
    with open(path, mode="a") as f:
        f.write("\n" + json.dumps(state))


def get_prev_state():
    path = os.path.join(os.path.dirname(__file__), STATE_FILE)
    with open(path, mode="r") as f:
        last = ""
        for line in f.readlines():
            last = line
    return json.loads(last)


def compute_delta_ids(prev, current):
    # TODO: iniciativas need extra handling too
    today_dict = {
        req_id: cat
        for cat in CATEGORIAS_REQUERIMENTOS
        for req_id in current["requerimentos"][cat]
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

    delta_dict.update(
        {
            key: delta
            for key in [
                "informacoes",
                "votos",
                "iniciativas",
                "diarios",
                "intervencoes",
                "peticoes",
                "audi_ar",
                "audi_gr",
            ]
            if (delta := list(set(current[key]).difference(set(prev[key]))))
        }
    )
    return delta_dict