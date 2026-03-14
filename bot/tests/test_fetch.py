import asyncio
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import requests

from bot.classes import FetchError, WebData
from bot.fetch import (
    _fetch_data_dict_by_id,
    fetch_alra,
    fetch_alra_ids,
    fetch_beo_all,
    fetch_contratos_RAA,
    fetch_day_joraa,
    fetch_joraa_ato,
    fetch_portal,
    fetch_record,
    fetch_requerimentos,
    fetch_sigica_all,
    fetch_web_data,
    pre_fetch_alra,
)
from bot.record import (
    AudiARep,
    AudiGRep,
    Diario,
    Info,
    Iniciativa,
    Interven,
    Peti,
    Requerimento,
    Voto,
)
from bot.state import State


# --- Mocked unit tests ---


class TestFetchAlraIds:
    def test_parse_ids(self, alra_ids_html):
        mock_resp = MagicMock()
        mock_resp.content = alra_ids_html.encode()
        with patch("bot.fetch.requests.get", return_value=mock_resp):
            result = fetch_alra_ids(Voto)
        assert result == [3525, 3526, 3527]

    def test_network_error(self):
        with patch(
            "bot.fetch.requests.get",
            side_effect=requests.exceptions.ConnectionError("fail"),
        ):
            result = fetch_alra_ids(Voto)
        assert isinstance(result, FetchError)


class TestFetchDayJoraa:
    def test_returns_list(self, joraa_search_json):
        mock_resp = MagicMock()
        mock_resp.json.return_value = joraa_search_json
        with patch("bot.fetch.requests.get", return_value=mock_resp):
            result = fetch_day_joraa("2024-08-20")
        assert len(result) == 2
        assert result[0]["id"] == "abc123"

    def test_empty_results(self, joraa_search_empty_json):
        mock_resp = MagicMock()
        mock_resp.json.return_value = joraa_search_empty_json
        with patch("bot.fetch.requests.get", return_value=mock_resp):
            result = fetch_day_joraa("2024-08-20")
        assert result == []


class TestFetchBeoAll:
    def test_returns_beo_urls(self, portal_beo_html):
        mock_resp = MagicMock()
        mock_resp.content = portal_beo_html.encode()
        with patch("bot.fetch.requests.get", return_value=mock_resp):
            result = fetch_beo_all()
        assert isinstance(result, set)
        assert len(result) == 2
        assert all("/BEO" in url for url in result)

    def test_network_error(self):
        with patch(
            "bot.fetch.requests.get",
            side_effect=requests.exceptions.Timeout("timeout"),
        ):
            result = fetch_beo_all()
        assert isinstance(result, FetchError)


class TestFetchSigicaAll:
    def test_returns_sigica_urls(self, portal_sigica_html):
        mock_resp = MagicMock()
        mock_resp.content = portal_sigica_html.encode()
        with patch("bot.fetch.requests.get", return_value=mock_resp):
            result = fetch_sigica_all()
        assert isinstance(result, set)
        assert len(result) == 2
        assert all("sigica" in url for url in result)


class TestFetchRequerimentos:
    def test_all_categories(self, alra_ids_html):
        mock_resp = MagicMock()
        mock_resp.content = alra_ids_html.encode()
        with patch("bot.fetch.requests.get", return_value=mock_resp):
            result = fetch_requerimentos()
        assert isinstance(result, dict)
        assert "RESPOSTA ATEMPADA" in result
        assert "NO PRAZO" in result

    def test_one_category_fails(self):
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise requests.exceptions.ConnectionError("fail")
            mock = MagicMock()
            # Return HTML that has requerimento IDs (internal_db_int=4)
            mock.content = b'<html><a href="/w_pesquisa_registo/4/100">x</a></html>'
            return mock

        with patch("bot.fetch.requests.get", side_effect=side_effect):
            result = fetch_requerimentos()
        assert isinstance(result, FetchError)


class TestPreFetchAlra:
    def test_all_succeed(self, alra_ids_html):
        mock_resp = MagicMock()
        mock_resp.content = alra_ids_html.encode()
        with patch("bot.fetch.requests.get", return_value=mock_resp):
            result = pre_fetch_alra()
        assert isinstance(result, dict)
        assert "votos" in result

    def test_one_fails(self):
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise requests.exceptions.ConnectionError("fail")
            mock = MagicMock()
            mock.content = b"<html></html>"
            return mock

        with patch("bot.fetch.requests.get", side_effect=side_effect):
            result = pre_fetch_alra()
        assert isinstance(result, FetchError)


class TestFetchDataDictById:
    def test_parses_record(self, alra_record_html):
        mock_resp = MagicMock()
        mock_resp.content = alra_record_html.encode()
        with patch("bot.fetch.requests.get", return_value=mock_resp):
            result = _fetch_data_dict_by_id(Voto, 3525)
        assert result["Legislatura"] == "XIII"
        assert result["Assunto"] == "Pela subida à Primeira Liga"
        assert result["Resultado"] == "Aprovado por unanimidade"
        assert result["id"] == 3525


class TestFetchRecord:
    def test_returns_record(self, alra_record_html):
        mock_resp = MagicMock()
        mock_resp.content = alra_record_html.encode()
        with patch("bot.fetch.requests.get", return_value=mock_resp):
            result = fetch_record(Voto, 3525)
        assert isinstance(result, Voto)
        assert result._data["Assunto"] == "Pela subida à Primeira Liga"


class TestFetchContratosRAA:
    def test_returns_items(self, base_contratos_json):
        mock_resp = MagicMock()
        mock_resp.json.return_value = base_contratos_json
        with patch("bot.fetch.requests.post", return_value=mock_resp):
            result = fetch_contratos_RAA("2024-08-01", "2024-08-01")
        assert len(result) == 2
        assert result[0]["id"] == 12345

    def test_type_error_raises_fetch_error(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = None
        with patch("bot.fetch.requests.post", return_value=mock_resp):
            with pytest.raises(FetchError):
                fetch_contratos_RAA("2024-08-01")


class TestFetchAlra:
    def test_simple_types(self, alra_record_html):
        mock_resp = MagicMock()
        mock_resp.content = alra_record_html.encode()
        delta = {"votos": [3525], "informacoes": [20085]}
        with patch("bot.fetch.requests.get", return_value=mock_resp):
            result = fetch_alra(delta)
        assert isinstance(result, dict)
        assert Voto in result
        assert Info in result

    def test_with_requerimentos(self, alra_record_html):
        mock_resp = MagicMock()
        mock_resp.content = alra_record_html.encode()
        delta = {"requerimentos": [(100, None, "NO PRAZO")]}
        with patch("bot.fetch.requests.get", return_value=mock_resp):
            result = fetch_alra(delta)
        assert Requerimento in result
        assert len(result[Requerimento]) == 1
        req, prev, now = result[Requerimento][0]
        assert isinstance(req, Requerimento)
        assert prev is None
        assert now == "NO PRAZO"

    def test_fetch_error_in_delta(self):
        delta = {"votos": FetchError("fail")}
        result = fetch_alra(delta)
        assert isinstance(result, FetchError)

    def test_fetch_error_from_record(self):
        delta = {"votos": [3525]}
        with patch(
            "bot.fetch.requests.get",
            side_effect=requests.exceptions.ConnectionError("fail"),
        ):
            result = fetch_alra(delta)
        assert isinstance(result, FetchError)


class TestFetchPortal:
    def test_returns_delta(self, portal_beo_html, portal_sigica_html, state_dict):
        prev = State(state_dict)

        def mock_get(url, **kwargs):
            mock = MagicMock()
            if "beo" in url:
                mock.content = portal_beo_html.encode()
            else:
                mock.content = portal_sigica_html.encode()
            return mock

        with patch("bot.fetch.requests.get", side_effect=mock_get):
            result = fetch_portal(prev)
        assert isinstance(result, dict)
        assert "boletins" in result
        assert "sigica" in result

    def test_fetch_error(self, state_dict):
        prev = State(state_dict)
        with patch(
            "bot.fetch.requests.get",
            side_effect=requests.exceptions.Timeout("timeout"),
        ):
            result = fetch_portal(prev)
        assert isinstance(result, FetchError)


def _make_async_session(mock_resp):
    """Build a mock aiohttp session with proper async context manager."""
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=mock_resp)
    ctx.__aexit__ = AsyncMock(return_value=False)
    session = MagicMock()
    session.get.return_value = ctx
    return session


class TestFetchJoraaAto:
    def test_success(self, joraa_ato_json):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=joraa_ato_json)

        session = _make_async_session(mock_resp)
        result = asyncio.run(fetch_joraa_ato(session, "abc123"))
        assert result == joraa_ato_json

    def test_error_status(self):
        mock_resp = MagicMock()
        mock_resp.status = 500

        session = _make_async_session(mock_resp)
        with pytest.raises(FetchError):
            asyncio.run(fetch_joraa_ato(session, "bad_id"))


class TestFetchWebData:
    def test_all_success(self, state_dict):
        prev = State(state_dict)
        # Set dates to "yesterday" so date ranges produce 0 days
        now = datetime(2024, 8, 20, 12, 0, 0)

        alra_ids = {
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

        with (
            patch("bot.fetch.pre_fetch_alra", return_value=alra_ids),
            patch("bot.fetch.compute_delta_ids", return_value={}),
            patch("bot.fetch.fetch_alra", return_value={}),
            patch("bot.fetch.fetch_day_joraa", return_value=[]),
            patch("bot.fetch.fetch_contratos_RAA", return_value=[]),
            patch(
                "bot.fetch.fetch_portal",
                return_value={"boletins": set(), "sigica": set()},
            ),
            patch("bot.fetch.datetime") as mock_dt,
        ):
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = fetch_web_data(prev)

        assert isinstance(result, WebData)
        assert not isinstance(result.alra, FetchError)
        assert result.alra_ids == alra_ids

    def test_alra_prefetch_error(self, state_dict):
        prev = State(state_dict)
        now = datetime(2024, 8, 20, 12, 0, 0)
        err = FetchError("alra down")

        with (
            patch("bot.fetch.pre_fetch_alra", return_value=err),
            patch("bot.fetch.fetch_day_joraa", return_value=[]),
            patch("bot.fetch.fetch_contratos_RAA", return_value=[]),
            patch(
                "bot.fetch.fetch_portal",
                return_value={"boletins": set(), "sigica": set()},
            ),
            patch("bot.fetch.datetime") as mock_dt,
        ):
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = fetch_web_data(prev)

        assert isinstance(result.alra, FetchError)
        assert isinstance(result.alra_ids, FetchError)


# --- Network integration tests (existing) ---


@pytest.mark.network
def test_fetch_voto():
    expected = {
        "id": 3525,
        "url": "http://base.alra.pt:82/4DACTION/w_pesquisa_registo/1/3525",
        "Texto Voto Apresentado": "http://base.alra.pt:82/Doc_Voto/XIIIva1550_24.pdf",
        "Legislatura": "XIII",
        "Nº Entrada": "1550",
        "Data entrada": "11/07/2024",
        "Titulo": "Voto de Congratulação",
        "Autores": "CH",
        "Assunto": "Pela subida à Primeira Liga Portuguesa de Futebol do Clube Desportivo Santa Clara",
        "Anúncio em plenário": "11/07/2024",
        "Resultado": "Aprovado por unanimidade",
    }
    actual = fetch_record(Voto, 3525)._data
    assert expected == actual


@pytest.mark.network
def test_fetch_requerimento_atempada():
    expected = {
        "id": 8251,
        "url": "http://base.alra.pt:82/4DACTION/w_pesquisa_registo/4/8251",
        "Texto Requerimento": "http://base.alra.pt:82/Doc_Req/XIIIreque2.pdf",
        "Legislatura": "XIII",
        "Número": "2",
        "Data entrada": "29/02/2024",
        "Processo": "054.09.08",
        "Requerente(s)": "José Pacheco CH; José Sousa CH",
        "Assunto": "Falta de escoamento de pescado das Flores",
        "Data de envio ao G.R.": "06/03/2024",
        "Anúncio em plenário do requerimento": "13/03/2024",
        "Texto Resposta": "http://base.alra.pt:82/Doc_Req/XIIIrequeresp2.pdf",
        "Data da resposta do G.R.": "25/03/2024",
        "Data da entrada da resposta": "26/03/2024",
        "Anúncio em plenário da resposta": "09/04/2024",
    }
    actual = fetch_record(Requerimento, 8251)._data
    assert expected == actual


@pytest.mark.network
def test_fetch_iniciativa():
    expected = {
        "id": 3625,
        "url": "http://base.alra.pt:82/4DACTION/w_pesquisa_registo/3/3625",
        "Texto Iniciativa": "http://base.alra.pt:82/iniciativas/iniciativas/XIIIEPjDLR015.pdf",
        "Nota de Admissibilidade": "http://base.alra.pt:82/iniciativas/iniciativas/XIIInaPjDLR015.pdf",
        "Legislatura": "XIII",
        "Nº entrada Serviço": "1705",
        "Nº Processo": "105",
        "Nº proposta": "0015",
        "Titulo": "Projeto de Decreto Leg.",
        "Assunto": "Cria a Rede Pública de Creches da Região Autónoma dos Açores",
        "Tema": "Educação/Segurança Social",
        "Data de entrada": "31/07/2024",
        "Autor do texto inicial": "BE - Bloco de Esquerda",
        "Data de Despacho": "05/08/2024",
        "Limite Parecer": "30/09/2024",
        "Comissão": "Assuntos Sociais",
        "Data de envio": "05/08/2024",
    }
    actual = fetch_record(Iniciativa, 3625)._data
    assert expected == actual


@pytest.mark.network
def test_fetch_info():
    expected = {
        "id": 20085,
        "url": "http://base.alra.pt:82/4DACTION/w_pesquisa_registo/8/20085",
        "Texto Informação": "http://base.alra.pt:82/Doc_Noticias/NI20085.pdf",
        "Legislatura": "XIII",
        "Data": "16/08/2024",
        "Tipo": "Nota de Pesar",
        "Autor": "Presidência da ALRAA",
        "Assunto": "Nota de Pesar da Presidência da ALRAA - Presidente Luís Garcia manifesta profundo pesar pelo falecimento do antigo Presidente da Assembleia Legislativa Álvaro Monjardino",
    }
    actual = fetch_record(Info, 20085)._data
    assert expected == actual
