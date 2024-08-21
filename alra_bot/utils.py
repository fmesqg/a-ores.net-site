import json
import os

from .constants import CATEGORIAS_REQUERIMENTOS, STATE_FILE


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
            for key in ["informacoes", "votos", "iniciativas"]
            if (delta := list(set(current[key]).difference(set(prev[key]))))
        }
    )
    return delta_dict
