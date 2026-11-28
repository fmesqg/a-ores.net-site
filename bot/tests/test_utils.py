import json
from datetime import date, datetime
from unittest.mock import patch

from bot.classes import FetchError, WebData
from bot.state import State
from bot.utils import (
    append_state,
    compute_delta_ids,
    euros_pt,
    get_prev_state,
    item_line,
    joraa_amount,
    markdown_base,
    markdown_joraa,
    markdown_portal,
    safe_markdown,
    write_update,
)

# --- joraa_amount ---


def clauses(*texts):
    return [{"normativo": t} for t in texts]


def test_amount_grant_not_added_to_project_cost():
    act = {
        "sumario": "Aquisição de mobiliário.",
        "considerandos": "<p>Entre a Região e a Junta de Freguesia...</p>",
        "normativos": clauses(
            "1 – O custo total do investimento apoiado é de 9.688,32 € "
            "(nove mil, seiscentos e oitenta e oito euros).\n2 – A PRIMEIRA "
            "OUTORGANTE assegura a comparticipação, a fundo perdido, no valor "
            "de 9.470,33 € (nove mil, quatrocentos e setenta euros).",
            "O processamento é feito em duas prestações, a primeira no "
            "montante de 5.000,00 €.",
        ),
    }
    assert joraa_amount(act) == (9470.33, "valor")


def test_amount_amendment_reads_the_new_clauses_only():
    act = {
        "sumario": "Aditamento ao Protocolo de Cooperação",
        "considerandos": "foi concedido um apoio no montante de "
        "16.297,49€, deixando de ser preciso o apoio de 5.199,07€",
        "normativos": clauses(
            "cujo investimento estimado é de 10.598,42€ (dez mil...), a "
            "primeira outorgante obriga-se a conceder uma comparticipação "
            "no valor de 11.098,42€ que inclui o encargo com o registo do "
            "ónus, no montante total de 250,00€"
        ),
    }
    assert joraa_amount(act) == (11098.42, "valor")


def test_amount_list_of_grants_adds_up_repeated_values():
    act = {
        "sumario": "Apoio financeiro.",
        "considerandos": "<p>se concedam os seguintes apoios:</p>"
        "<p>Nome: A, Lda</p><p>Montante Euros: 1 525,00 €</p>"
        "<p>Nome: B, Lda</p><p>Montante Euros: 25&nbsp;000,00 €</p>"
        "<p>Nome: C, Lda</p><p>Montante Euros: 25 000,00 €</p>",
        "normativos": [],
    }
    assert joraa_amount(act) == (51525.0, "soma de 3 valores")


def test_amount_repeated_value_counts_once():
    act = {
        "sumario": "Autoriza a despesa de 3 175 000,00 €",
        "textoIntegral": "É autorizada a despesa de 3 175 000,00 € "
        "(três milhões...), com o limite de 3.175.000 euros.",
    }
    assert joraa_amount(act) == (3175000.0, "valor")


def test_amount_procurement_notice_base_price():
    act = {
        "sumario": "Empreitada de arruamentos.",
        "considerandos": "Valor do preço base do procedimento (EUR): (*) "
        "Valor total estimado (EUR): (*) 199523 Preço Base s/IVA (€): (*) "
        "199.523,28 Lotes: N.º: (*) LOT-0001 Preço base s/IVA (€): (*) "
        "72.259,00",
        "normativos": [],
    }
    assert joraa_amount(act) == (199523.28, "preço base")


def test_amount_ignores_numbers_glued_to_a_reference():
    act = {
        "sumario": "Apoio",
        "considerandos": "moradia sita no Caminho n.º 17 250,00 € de apoio",
    }
    assert joraa_amount(act) == (250.0, "valor")


def test_amount_none_without_euros():
    act = {"sumario": "Recomenda", "considerandos": "artigo 44.º, n.º 3"}
    assert joraa_amount(act) is None


def test_euros_pt():
    assert euros_pt(1234567.8) == "1 234 567,80 €"


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


# --- safe_markdown ---


def test_safe_markdown_neutralises_html_liquid_and_links():
    md = (
        "* [<img src=x onerror=alert(1)>](https://alra.pt/a?b=1&c=2)\n"
        "  * {{ site.x }} {% include y %} {: onclick=z}\n"
        "* [x](javascript:alert(1)) [y]( JavaScript:z) [ok](/ao/1/)"
    )
    out = safe_markdown(md)
    assert "<" not in out and "{" not in out and "}" not in out
    assert (
        "[&lt;img src=x onerror=alert(1)>](https://alra.pt/a?b=1&c=2)" in out
    )
    assert "&#123;&#123; site.x &#125;&#125;" in out
    assert "[x](#) [y](#) [ok](/ao/1/)" in out
    assert safe_markdown("* [a](https://jo.azores.gov.pt/#/ato/1)") == (
        "* [a](https://jo.azores.gov.pt/#/ato/1)"
    )


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
    # the amount leads the item line
    assert "* 1 000 € · [Portaria sobre 1.000,00 €](" in result


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
    assert "* 1 000 € · [Serviço X](" in result
    assert "Câmara" in result


def test_markdown_base_sorted_by_price():
    def c(i, price):
        return {
            "id": i,
            "objectBriefDescription": f"C{i}",
            "initialContractualPrice": price,
            "contracting": "A",
            "contracted": "B",
            "contractingProcedureType": "Ajuste Direto",
            "signingDate": "01-01-2026",
        }

    result = markdown_base([c(1, "999,99 €"), c(2, "1.234.567,80 €")])
    assert "* 1 234 568 € · [C2]" in result
    assert result.index("[C2]") < result.index("[C1]")


def test_item_line_parsed_by_datasets():
    from bot.dados.comum import ITEM

    m = ITEM.match(item_line("Título [x] · y", "https://e.pt/1", 12.5))
    assert (
        m and m["title"] == "Título [x] · y" and m["url"] == "https://e.pt/1"
    )
    assert ITEM.match("* [Sem montante](https://e.pt/2)")["title"] == (
        "Sem montante"
    )


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


def _bot_dir(monkeypatch, tmp_path):
    monkeypatch.setattr("bot.utils.os.path.dirname", lambda _: str(tmp_path))


def test_get_prev_state(tmp_path, state_dict, monkeypatch):
    _bot_dir(monkeypatch, tmp_path)
    (tmp_path / "state.json").write_text(json.dumps(state_dict))
    s = get_prev_state()
    assert s.last_joraa_update.year == 2024


def test_get_prev_state_falls_back_to_old_ledger(
    tmp_path, state_dict, monkeypatch
):
    _bot_dir(monkeypatch, tmp_path)
    (tmp_path / "state.jsonl").write_text(
        json.dumps({"dummy": "first"}) + "\n" + json.dumps(state_dict) + "\n"
    )
    s = get_prev_state()
    assert s.last_joraa_update.year == 2024


# --- append_state ---


def test_append_state(tmp_path, state_dict, monkeypatch):
    _bot_dir(monkeypatch, tmp_path)
    (tmp_path / "state.jsonl").write_text(json.dumps({"seed": True}))
    (tmp_path / "state.json").write_text(json.dumps({"old": True}))
    fixed_dt = datetime(2024, 8, 20, 12, 0, 0)
    monkeypatch.setattr("bot.utils.NOW_DATETIME", fixed_dt)

    append_state(State(state_dict))

    written = json.loads((tmp_path / "state.json").read_text())
    assert written["datetime"] == "2024-08-20 12:00:00"
    assert written["last_joraa_update"] == "2024-08-19"
    assert written["last_base_update"] == "2024-08-18"
    assert "boletins" in written and "sigica" in written
    assert "requerimentos" in written and "votos" in written
    assert "old" not in written  # replaced, not appended
    assert not (tmp_path / "state.jsonl").exists()  # migrated
    assert not (tmp_path / "state.json.tmp").exists()
    # the state reads back the same
    assert (
        get_prev_state().last_joraa_update
        == State(state_dict).last_joraa_update
    )


def test_append_state_is_stable(tmp_path, state_dict, monkeypatch):
    _bot_dir(monkeypatch, tmp_path)
    monkeypatch.setattr("bot.utils.NOW_DATETIME", datetime(2024, 8, 20))
    append_state(State(state_dict))
    first = (tmp_path / "state.json").read_text()
    append_state(get_prev_state())
    assert (tmp_path / "state.json").read_text() == first


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
