import json
import os

from .constants import CATEGORIAS_REQUERIMENTOS, STATE_FILE


def markdown_joraa(entries):
    start = "# JORAA\n\n"
    url_entry_base = "https://jo.azores.gov.pt/#/ato/"

    def md(entry):
        header = f"* [{entry['sumario']}]({url_entry_base}{entry['id']})"
        entidades = "\n".join([f"  * {ent}" for ent in entry["entidades"]])
        return header + "\n" + entidades + "\n  * " + entry["descricaoPublicacao"]

    return start + "\n\n".join([md(entry) for entry in entries])


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
