import json
import os

import pytest

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def alra_ids_html():
    with open(os.path.join(FIXTURES_DIR, "alra_ids_page.html")) as f:
        return f.read()


@pytest.fixture
def alra_record_html():
    with open(os.path.join(FIXTURES_DIR, "alra_record_page.html")) as f:
        return f.read()


@pytest.fixture
def joraa_search_json():
    with open(os.path.join(FIXTURES_DIR, "joraa_search.json")) as f:
        return json.load(f)


@pytest.fixture
def joraa_search_empty_json():
    with open(os.path.join(FIXTURES_DIR, "joraa_search_empty.json")) as f:
        return json.load(f)


@pytest.fixture
def base_contratos_json():
    with open(os.path.join(FIXTURES_DIR, "base_contratos.json")) as f:
        return json.load(f)


@pytest.fixture
def portal_beo_html():
    with open(os.path.join(FIXTURES_DIR, "portal_beo.html")) as f:
        return f.read()


@pytest.fixture
def portal_sigica_html():
    with open(os.path.join(FIXTURES_DIR, "portal_sigica.html")) as f:
        return f.read()


@pytest.fixture
def joraa_ato_json():
    with open(os.path.join(FIXTURES_DIR, "joraa_ato.json")) as f:
        return json.load(f)


@pytest.fixture
def state_dict():
    with open(os.path.join(FIXTURES_DIR, "state_line.json")) as f:
        return json.load(f)
