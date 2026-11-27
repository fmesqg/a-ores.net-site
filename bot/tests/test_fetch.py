from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest
import requests

from bot import beo, gov
from bot.classes import FetchError, WebData
from bot.fetch import (
    _fetch_data_dict_by_id,
    fetch_alra,
    fetch_alra_ids,
    fetch_beo_all,
    fetch_contratos_RAA,
    fetch_day_joraa,
    fetch_joraa,
    fetch_joraa_ato,
    fetch_portal,
    fetch_record,
    fetch_requerimentos,
    fetch_sigica_all,
    fetch_web_data,
    pre_fetch_alra,
)
from bot.record import (
    Info,
    Iniciativa,
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


def _head(found_months):
    """requests.head stand-in: 200 + PDF for URLs of the given months."""

    def head(url, **kwargs):
        resp = MagicMock()
        hit = any(f"BEO_{y}_{m:02d}_" in url for y, m in found_months)
        resp.status_code = 200 if hit else 404
        resp.headers = {
            "content-type": "application/pdf" if hit else "text/html"
        }
        return resp

    return head


class TestFetchBeoAll:
    def test_probes_unknown_months(self):
        with (
            patch(
                "bot.fetch.requests.head", side_effect=_head([(2026, 1)])
            ) as h,
            patch("bot.fetch.date") as d,
        ):
            d.today.return_value = date(2026, 3, 10)
            result = fetch_beo_all()
        assert result == {beo.pdf_url(2026, 1)}
        assert h.call_count == 14  # Jan 2025 .. Feb 2026

    def test_known_months_are_not_asked_again(self):
        known = frozenset({beo.pdf_url(2026, 1), beo.pdf_url(2025, 12)})
        with (
            patch("bot.fetch.requests.head", side_effect=_head([])) as h,
            patch("bot.fetch.date") as d,
        ):
            d.today.return_value = date(2026, 3, 10)
            result = fetch_beo_all(known)
        assert result == set(known)
        assert h.call_count == 12

    def test_cloudflare_challenge_is_an_error(self):
        def challenge(url, **kwargs):
            resp = MagicMock()
            resp.status_code = 403
            resp.headers = {"cf-mitigated": "challenge"}
            return resp

        with patch("bot.fetch.requests.head", side_effect=challenge):
            result = fetch_beo_all()
        assert isinstance(result, FetchError)

    def test_network_error(self):
        with patch(
            "bot.fetch.requests.head",
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

    def test_cloudflare_block_is_an_error(self):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "403 Forbidden"
        )
        with patch("bot.fetch.requests.get", return_value=mock_resp):
            result = fetch_sigica_all()
        assert isinstance(result, FetchError)


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
            mock.content = (
                b'<html><a href="/w_pesquisa_registo/4/100">x</a></html>'
            )
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

    def test_null_answer_is_a_fetch_error(self):
        # 2026-11-23: BASE answered null and the whole daily run crashed
        mock_resp = MagicMock()
        mock_resp.json.return_value = None
        with patch("bot.fetch.requests.post", return_value=mock_resp):
            result = fetch_contratos_RAA("2024-08-01")
        assert isinstance(result, FetchError)


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
    def test_returns_delta(self, portal_sigica_html, state_dict):
        prev = State(state_dict)
        mock = MagicMock()
        mock.content = portal_sigica_html.encode()
        with (
            patch("bot.fetch.requests.get", return_value=mock),
            patch("bot.fetch.requests.head", side_effect=_head([(2026, 1)])),
            patch("bot.fetch.date") as d,
        ):
            d.today.return_value = date(2026, 3, 10)
            result = fetch_portal(prev)
        assert result["boletins"] == {beo.pdf_url(2026, 1)}
        assert "sigica" in result

    def test_sigica_blocked_keeps_boletins(self, state_dict):
        prev = State(state_dict)
        blocked = MagicMock()
        blocked.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "403"
        )
        with (
            patch("bot.fetch.requests.get", return_value=blocked),
            patch("bot.fetch.requests.head", side_effect=_head([(2026, 2)])),
            patch("bot.fetch.date") as d,
        ):
            d.today.return_value = date(2026, 3, 10)
            result = fetch_portal(prev)
        assert result == {"boletins": {beo.pdf_url(2026, 2)}, "sigica": set()}

    def test_fetch_error(self, state_dict):
        prev = State(state_dict)
        timeout = requests.exceptions.Timeout("timeout")
        with (
            patch("bot.fetch.requests.get", side_effect=timeout),
            patch("bot.fetch.requests.head", side_effect=timeout),
        ):
            result = fetch_portal(prev)
        assert isinstance(result, FetchError)


class TestFetchJoraaAto:
    def test_success(self, joraa_ato_json):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = joraa_ato_json
        with patch("bot.fetch.requests.get", return_value=mock_resp) as get:
            result = fetch_joraa_ato("abc123")
        assert result == joraa_ato_json
        url = get.call_args.args[0]
        assert url == "https://jo.azores.gov.pt/api/public/ato/abc123"
        assert get.call_args.kwargs["headers"] == gov.HEADERS

    def test_cloudflare_challenge(self):
        mock_resp = MagicMock(status_code=403)
        mock_resp.raise_for_status.side_effect = requests.HTTPError("403")
        with patch("bot.fetch.requests.get", return_value=mock_resp):
            assert isinstance(fetch_joraa_ato("bad_id"), FetchError)


class TestFetchJoraa:
    days = [date(2026, 8, 12), date(2026, 8, 13), date(2026, 8, 14)]

    def run(self, day_results, ato=lambda id: {"id": id}):
        results = iter(day_results)
        with (
            patch(  # a function: FetchError results are returned, not raised
                "bot.fetch.fetch_day_joraa",
                side_effect=lambda date: next(results),
            ),
            patch("bot.fetch.fetch_joraa_ato", side_effect=ato) as atos,
        ):
            return fetch_joraa(self.days), atos

    def test_all_days_with_full_acts(self):
        result, atos = self.run([[{"id": "a"}], [], [{"id": "b"}]])
        assert result == {
            self.days[0]: [{"id": "a"}],
            self.days[1]: [],
            self.days[2]: [{"id": "b"}],
        }
        assert atos.call_count == 2

    def test_keeps_days_before_a_failure(self):
        err = FetchError("403")
        result, _ = self.run([[], err, []])
        assert result == {self.days[0]: []}

    def test_failed_act_stops_the_day(self):
        err = FetchError("403")
        result, atos = self.run(
            [[], [{"id": "a"}, {"id": "b"}], []], ato=lambda id: err
        )
        assert result == {self.days[0]: []}
        assert atos.call_count == 1

    def test_failure_on_first_day_is_an_error(self):
        err = FetchError("403")
        result, _ = self.run([err, [], []])
        assert result is err

    def test_stops_when_budget_spent(self, monkeypatch):
        monkeypatch.setattr("bot.fetch.JORAA_BUDGET", -1)
        result, _ = self.run([[], [], []])
        assert result == {}


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
