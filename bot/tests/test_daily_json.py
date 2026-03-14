import json
import os
import tempfile
from datetime import date
from unittest.mock import patch

from bot.classes import FetchError, WebData
from bot.daily_json import write_daily_json
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


def _make_joraa_entry(id="abc123"):
    return {
        "id": id,
        "sumario": "Autoriza celebração de contrato",
        "textoIntegral": "A" * 600,
        "humanId": "RES/2024/001",
        "entidades": [{"nome": "Secretaria Regional das Finanças"}],
        "descricaoPublicacao": "Série I",
    }


def _make_base_entry(id=1):
    return {
        "id": id,
        "objectBriefDescription": "Serviço X",
        "initialContractualPrice": "1000 €",
        "contracting": "Câmara",
        "contracted": "Empresa",
        "contractingProcedureType": "Ajuste Direto",
        "signingDate": "2024-01-01",
    }


def _make_alra_data():
    req = Requerimento(
        {
            "id": 8300,
            "Assunto": "Centro de Processamento",
            "Requerente(s)": "Luís Silveira CDS-PP",
            "Data entrada": "01/01/2024",
            "url": "http://base.alra.pt:82/4DACTION/w_pesquisa_registo/4/8300",
        }
    )
    info = Info(
        {
            "id": 20087,
            "Assunto": "Nota informativa",
            "url": "http://base.alra.pt:82/4DACTION/w_pesquisa_registo/8/20087",
        }
    )
    voto = Voto(
        {
            "id": 3526,
            "Assunto": "Voto de pesar",
            "Autores": "PS",
            "Resultado": "Aprovado",
            "url": "http://base.alra.pt:82/4DACTION/w_pesquisa_registo/1/3526",
        }
    )
    return {
        Requerimento: [(req, "NO PRAZO", "RESPOSTA ATEMPADA")],
        Info: [info],
        Voto: [voto],
    }


def _read_json(tmpdir, filename):
    path = os.path.join(tmpdir, filename)
    with open(path) as f:
        return json.load(f)


def test_write_daily_json_all_sources():
    day = date(2024, 9, 2)
    web_data = WebData(
        joraa={day: [_make_joraa_entry()]},
        base={day: [_make_base_entry()]},
        alra=_make_alra_data(),
        portal={"boletins": {"https://example.com/beo"}, "sigica": set()},
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        with (
            patch("bot.daily_json._OUTPUT_DIR", tmpdir),
            patch("bot.daily_json.YESTERDAY_DATE", day),
        ):
            write_daily_json(web_data)

        data = _read_json(tmpdir, "2024-09-02.json")

        assert data["date"] == "2024-09-02"

        # JORAA
        assert len(data["joraa"]) == 1
        j = data["joraa"][0]
        assert j["id"] == "abc123"
        assert j["human_id"] == "RES/2024/001"
        assert len(j["text_excerpt"]) == 500

        # BASE
        assert len(data["base"]) == 1
        b = data["base"][0]
        assert b["id"] == 1
        assert b["buyer"] == "Câmara"

        # ALRA
        assert "requerimentos" in data["alra"]
        r = data["alra"]["requerimentos"][0]
        assert r["id"] == 8300
        assert r["state_change"]["from"] == "NO PRAZO"

        assert len(data["alra"]["informacoes"]) == 1
        assert len(data["alra"]["votos"]) == 1

        # Portal
        assert "https://example.com/beo" in data["portal"]["boletins"]


def test_write_daily_json_with_errors():
    day = date(2024, 9, 2)
    web_data = WebData(
        joraa=FetchError("JORAA timeout"),
        base=FetchError("BASE down"),
        alra=FetchError("ALRA unreachable"),
        portal=FetchError("Portal error"),
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        with (
            patch("bot.daily_json._OUTPUT_DIR", tmpdir),
            patch("bot.daily_json.YESTERDAY_DATE", day),
        ):
            write_daily_json(web_data)

        data = _read_json(tmpdir, "2024-09-02.json")

        assert "error" in data["joraa"]
        assert "error" in data["base"]
        assert "error" in data["alra"]
        assert "error" in data["portal"]


def test_record_to_dict_requerimento():
    data = {
        "id": 100,
        "Assunto": "Test assunto",
        "Requerente(s)": "João Silva",
        "Data entrada": "01/01/2024",
        "url": "http://example.com/100",
    }
    r = Requerimento(data)
    d = r.to_dict(prev="NO PRAZO", now="RESPOSTA ATEMPADA")
    assert d["id"] == 100
    assert d["title"] == "Test assunto"
    assert d["state_change"] == {
        "from": "NO PRAZO",
        "to": "RESPOSTA ATEMPADA",
    }
    assert d["requesters"] == "João Silva"


def test_record_to_dict_requerimento_new():
    data = {
        "id": 100,
        "Assunto": "Test",
        "Requerente(s)": "Ana",
        "url": "http://example.com/100",
    }
    r = Requerimento(data)
    d = r.to_dict(prev=None, now="NO PRAZO")
    assert d["state_change"] is None


def test_record_to_dict_voto():
    data = {
        "id": 3526,
        "Assunto": "Voto de pesar",
        "Autores": "PS",
        "Resultado": "Aprovado",
        "url": "http://example.com/v1",
    }
    d = Voto(data).to_dict()
    assert d["id"] == 3526
    assert d["authors"] == "PS"
    assert d["result"] == "Aprovado"


def test_record_to_dict_iniciativa():
    data = {
        "id": 3625,
        "Assunto": "Projeto de lei",
        "Autor do texto inicial": "PS",
        "Tema": "Educação",
        "url": "http://example.com/ini1",
    }
    d = Iniciativa(data).to_dict()
    assert d["author"] == "PS"
    assert d["topic"] == "Educação"


def test_record_to_dict_diario():
    data = {
        "id": 101,
        "Número": "45",
        "Data": "01/01/2024",
        "url": "http://example.com/d1",
    }
    d = Diario(data).to_dict()
    assert d["number"] == "45"
    assert d["date"] == "01/01/2024"


def test_record_to_dict_info():
    data = {
        "id": 20087,
        "Assunto": "Nota informativa",
        "url": "http://example.com/n1",
    }
    d = Info(data).to_dict()
    assert d["title"] == "Nota informativa"


def test_record_to_dict_peti():
    data = {
        "id": 200,
        "Assunto": "Petição Y",
        "Autor": "Maria",
        "Estado": "Em apreciação",
        "url": "http://example.com/p1",
    }
    d = Peti(data).to_dict()
    assert d["author"] == "Maria"
    assert d["state"] == "Em apreciação"


def test_record_to_dict_interven():
    data = {
        "id": 500,
        "Assunto": "Intervenção X",
        "Data": "03/03/2024",
        "url": "http://example.com/i1",
    }
    d = Interven(data).to_dict()
    assert d["date"] == "03/03/2024"


def test_record_to_dict_audi_gr():
    data = {
        "id": 50,
        "Assunto": "Audição governo",
        "url": "http://example.com/ag1",
    }
    d = AudiGRep(data).to_dict()
    assert d["title"] == "Audição governo"


def test_record_to_dict_audi_ar():
    data = {
        "id": 60,
        "Assunto": "Audição AR",
        "url": "http://example.com/aa1",
    }
    d = AudiARep(data).to_dict()
    assert d["title"] == "Audição AR"
