from copy import deepcopy
from datetime import date

from bot.classes import FetchError, WebData
from bot.state import State


def test_state_init(state_dict):
    s = State(state_dict)
    assert s.last_joraa_update == date(2024, 8, 19)
    assert s.last_base_update == date(2024, 8, 18)
    assert isinstance(s.boletins, set)
    assert isinstance(s.sigica, set)
    assert "requerimentos" in s.alra_state
    assert "votos" in s.alra_state


def test_state_alra_keys(state_dict):
    s = State(state_dict)
    for key in State.alra:
        assert key in s.alra_state


def test_get_updated_state_success(state_dict):
    prev = State(state_dict)
    wd = WebData(
        joraa={},
        alra={},
        base={},
        portal={"boletins": {"http://new-beo"}, "sigica": {"http://new-sigica"}},
        alra_ids={"requerimentos": {}, "informacoes": [99]},
    )
    updated = State.get_updated_state(prev, wd)
    assert "http://new-beo" in updated.data["boletins"]
    assert "http://new-sigica" in updated.data["sigica"]
    assert updated.alra_state == {"requerimentos": {}, "informacoes": [99]}


def test_get_updated_state_joraa_error(state_dict):
    prev = State(state_dict)
    original_joraa_date = prev.last_joraa_update
    wd = WebData(
        joraa=FetchError("timeout"),
        alra={},
        base={},
        portal=FetchError("timeout"),
        alra_ids=FetchError("timeout"),
    )
    updated = State.get_updated_state(prev, wd)
    assert updated.last_joraa_update == original_joraa_date


def test_get_updated_state_base_error(state_dict):
    prev = State(state_dict)
    original_base_date = prev.last_base_update
    wd = WebData(
        joraa={},
        alra={},
        base=FetchError("timeout"),
        portal=FetchError("timeout"),
        alra_ids=FetchError("timeout"),
    )
    updated = State.get_updated_state(prev, wd)
    assert updated.last_base_update == original_base_date


def test_get_updated_state_portal_error(state_dict):
    prev = State(state_dict)
    original_boletins = deepcopy(prev.data["boletins"])
    wd = WebData(
        joraa={},
        alra={},
        base={},
        portal=FetchError("timeout"),
        alra_ids=FetchError("timeout"),
    )
    updated = State.get_updated_state(prev, wd)
    assert set(updated.data["boletins"]) == set(original_boletins)


def test_get_updated_state_alra_ids_error(state_dict):
    prev = State(state_dict)
    original_alra = deepcopy(prev.alra_state)
    wd = WebData(
        joraa={},
        alra={},
        base={},
        portal=FetchError("timeout"),
        alra_ids=FetchError("timeout"),
    )
    updated = State.get_updated_state(prev, wd)
    assert updated.alra_state == original_alra
