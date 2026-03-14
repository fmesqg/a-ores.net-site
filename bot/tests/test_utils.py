import json
import os
from datetime import date, datetime
from unittest.mock import call, patch

from bot.classes import FetchError, WebData
from bot.state import State
from bot.utils import (
    append_state,
    compute_delta_ids,
    find_monies,
    get_prev_state,
    markdown_base,
    markdown_joraa,
    markdown_portal,
    parse_currency_to_number,
    write_collection,
    write_update,
)


# --- find_monies ---


def test_find_monies_euro_suffix():
    assert find_monies("valor de 1.500,00 €") == ["1.500,00 €"]


def test_find_monies_euro_prefix():
    # pattern2 matches €\s?\d{1,3} so only captures 3 digits after €
    assert find_monies("valor de € 200") == ["€ 200"]


def test_find_monies_nbsp():
    assert find_monies("1.500,00&nbsp;€") == ["1.500,00 €"]


def test_find_monies_multiple():
    result = find_monies("paga 100 € e recebe 200,50 €")
    assert len(result) == 2


def test_find_monies_thousands_space():
    assert find_monies("10 000,00 €") == ["10 000,00 €"]


def test_find_monies_no_match():
    assert find_monies("sem valores monetários") == []


# --- parse_currency_to_number ---


def test_parse_currency_simple():
    assert parse_currency_to_number("100 €") == 100.0


def test_parse_currency_thousands_dot():
    assert parse_currency_to_number("1.500,00 €") == 1500.0


def test_parse_currency_prefix():
    assert parse_currency_to_number("€ 2000") == 2000.0


def test_parse_currency_thousands_space():
    assert parse_currency_to_number("10 000,00 €") == 10000.0


# --- compute_delta_ids ---


def test_compute_delta_ids_new_ids(state_dict):
    prev = State(state_dict)
    current = {
        "requerimentos": {
            "RESPOSTA ATEMPADA": [8251, 8252],
            "NO PRAZO": [8300],
            "RESPOSTA TADIA": [],
            "FORA DE PRAZO": [],
            "JUSTIFICADO": [],
        },
        "informacoes": [20085, 20086, 20087],
        "diarios": [100, 101],
        "votos": [3525, 3526],
        "iniciativas": [3625],
        "intervencoes": [500],
        "peticoes": [200],
        "audi_gr": [50],
        "audi_ar": [60],
    }
    delta = compute_delta_ids(prev, current)
    assert "informacoes" in delta
    assert 20087 in delta["informacoes"]
    assert "votos" not in delta


def test_compute_delta_ids_category_change(state_dict):
    prev = State(state_dict)
    current = {
        "requerimentos": {
            "RESPOSTA ATEMPADA": [8251, 8252, 8300],
            "NO PRAZO": [],
            "RESPOSTA TADIA": [],
            "FORA DE PRAZO": [],
            "JUSTIFICADO": [],
        },
        "informacoes": [20085, 20086],
        "diarios": [100, 101],
        "votos": [3525, 3526],
        "iniciativas": [3625],
        "intervencoes": [500],
        "peticoes": [200],
        "audi_gr": [50],
        "audi_ar": [60],
    }
    delta = compute_delta_ids(prev, current)
    assert "requerimentos" in delta
    # 8300 moved from NO PRAZO to RESPOSTA ATEMPADA
    found = [t for t in delta["requerimentos"] if t[0] == 8300]
    assert len(found) == 1
    assert found[0][1] == "NO PRAZO"
    assert found[0][2] == "RESPOSTA ATEMPADA"


def test_compute_delta_ids_no_changes(state_dict):
    prev = State(state_dict)
    current = {
        "requerimentos": {
            "RESPOSTA ATEMPADA": [8251, 8252],
            "NO PRAZO": [8300],
            "RESPOSTA TADIA": [],
            "FORA DE PRAZO": [],
            "JUSTIFICADO": [],
        },
        "informacoes": [20085, 20086],
        "diarios": [100, 101],
        "votos": [3525, 3526],
        "iniciativas": [3625],
        "intervencoes": [500],
        "peticoes": [200],
        "audi_gr": [50],
        "audi_ar": [60],
    }
    delta = compute_delta_ids(prev, current)
    assert delta == {}


# --- write_collection ---


def test_write_collection(tmp_path):
    folder = "_test_updates"
    docs_dir = tmp_path / "docs" / folder
    docs_dir.mkdir(parents=True)
    # Patch write_collection to use tmp_path
    date_str = "2024-08-20"
    page = f"""---
date: {date_str}
title: Test
layout: default
---
"""
    content = "## Test content"
    path = docs_dir / f"{date_str}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(page + content + "\n")

    result = path.read_text()
    assert "date: 2024-08-20" in result
    assert "## Test content" in result


# --- markdown_joraa ---


def test_markdown_joraa():
    entries = [
        {
            "id": "abc",
            "sumario": "Resolução sobre 500 €",
            "humanId": "RES/001",
            "descricaoPublicacao": "Série I",
            "entidades": [{"nome": "Governo"}],
        },
        {
            "id": "def",
            "sumario": "Portaria sobre 1.000,00 €",
            "humanId": "PORT/002",
            "descricaoPublicacao": "Série I",
            "entidades": [{"nome": "Secretaria"}],
        },
    ]
    result = markdown_joraa(entries)
    assert "## JORAA" in result
    # 1000 > 500 so Portaria should come first
    port_pos = result.index("Portaria")
    res_pos = result.index("Resolução")
    assert port_pos < res_pos


def test_markdown_joraa_empty():
    assert markdown_joraa([]) is None


# --- markdown_base ---


def test_markdown_base():
    entries = [
        {
            "id": 1,
            "objectBriefDescription": "Serviço X",
            "initialContractualPrice": "1000 €",
            "contracting": "Câmara",
            "contracted": "Empresa",
            "contractingProcedureType": "Ajuste Direto",
            "signingDate": "2024-01-01",
        }
    ]
    result = markdown_base(entries)
    assert "## Contratos publicados ontem" in result
    assert "Serviço X" in result
    assert "Câmara" in result


def test_markdown_base_empty():
    assert markdown_base([]) is None


# --- markdown_portal ---


def test_markdown_portal_with_delta():
    delta = {
        "boletins": {"http://beo1"},
        "sigica": {"http://sigica1"},
    }
    result = markdown_portal(delta)
    assert "portal.azores.gov.pt" in result
    assert "http://beo1" in result
    assert "http://sigica1" in result


def test_markdown_portal_empty():
    delta = {"boletins": set(), "sigica": set()}
    assert markdown_portal(delta) == ""


# --- get_prev_state ---


def test_get_prev_state(tmp_path, state_dict, monkeypatch):
    state_file = tmp_path / "state.jsonl"
    state_file.write_text(
        json.dumps({"dummy": "first"})
        + "\n"
        + json.dumps(state_dict)
    )
    monkeypatch.setattr(
        "bot.utils.os.path.join",
        lambda *args: str(state_file)
        if args[-1] == "state.jsonl"
        else os.path.join(*args),
    )
    s = get_prev_state()
    assert s.last_joraa_update.year == 2024


# --- append_state ---


def test_append_state(tmp_path, state_dict, monkeypatch):
    state_file = tmp_path / "state.jsonl"
    state_file.write_text("")
    monkeypatch.setattr(
        "bot.utils.os.path.join",
        lambda *args: str(state_file)
        if args[-1] == "state.jsonl"
        else os.path.join(*args),
    )
    fixed_dt = datetime(2024, 8, 20, 12, 0, 0)
    monkeypatch.setattr("bot.utils.NOW_DATETIME", fixed_dt)

    state = State(state_dict)
    append_state(state)

    lines = [l for l in state_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 1
    written = json.loads(lines[0])
    assert written["datetime"] == "2024-08-20 12:00:00"
    assert written["last_joraa_update"] == "2024-08-19"
    assert written["last_base_update"] == "2024-08-18"
    assert "boletins" in written
    assert "sigica" in written
    # alra keys should be present
    assert "requerimentos" in written
    assert "votos" in written


def test_append_state_appends_not_overwrites(
    tmp_path, state_dict, monkeypatch
):
    state_file = tmp_path / "state.jsonl"
    seed = json.dumps({"seed": True})
    state_file.write_text(seed)
    monkeypatch.setattr(
        "bot.utils.os.path.join",
        lambda *args: str(state_file)
        if args[-1] == "state.jsonl"
        else os.path.join(*args),
    )
    fixed_dt = datetime(2024, 8, 20, 12, 0, 0)
    monkeypatch.setattr("bot.utils.NOW_DATETIME", fixed_dt)

    state = State(state_dict)
    append_state(state)

    lines = [l for l in state_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"seed": True}


# --- write_update ---


def test_write_update_all_success():
    joraa_data = {
        date(2024, 8, 20): [
            {
                "id": "abc",
                "sumario": "Test 500 €",
                "humanId": "RES/001",
                "descricaoPublicacao": "Série I",
                "entidades": [{"nome": "Governo"}],
            }
        ]
    }
    base_data = {
        date(2024, 8, 20): [
            {
                "id": 1,
                "objectBriefDescription": "Serviço",
                "initialContractualPrice": "1000 €",
                "contracting": "Câmara",
                "contracted": "Empresa",
                "contractingProcedureType": "Ajuste Direto",
                "signingDate": "2024-01-01",
            }
        ]
    }
    web_data = WebData(
        alra={},
        joraa=joraa_data,
        base=base_data,
        portal={"boletins": set(), "sigica": set()},
    )
    with patch("bot.utils.write_collection") as mock_wc:
        write_update(web_data)

    folders = [c.kwargs["folder"] for c in mock_wc.call_args_list]
    assert "_alra_updates" in folders
    assert "_joraa_updates" in folders
    assert "_base_updates" in folders
    assert "_portal_updates" in folders
    assert mock_wc.call_count == 4


def test_write_update_alra_error():
    web_data = WebData(
        alra=FetchError("alra down"),
        joraa={},
        base={},
        portal={"boletins": set(), "sigica": set()},
    )
    with patch("bot.utils.write_collection") as mock_wc:
        write_update(web_data)

    alra_call = [
        c
        for c in mock_wc.call_args_list
        if c.kwargs.get("folder") == "_alra_updates"
    ]
    assert len(alra_call) == 1
    assert "Erro" in alra_call[0].args[1]


def test_write_update_joraa_error():
    web_data = WebData(
        alra={},
        joraa=FetchError("joraa down"),
        base={},
        portal={"boletins": set(), "sigica": set()},
    )
    with patch("bot.utils.write_collection") as mock_wc:
        write_update(web_data)

    joraa_call = [
        c
        for c in mock_wc.call_args_list
        if c.kwargs.get("folder") == "_joraa_updates"
    ]
    assert len(joraa_call) == 1
    assert "Erro" in joraa_call[0].args[1]
