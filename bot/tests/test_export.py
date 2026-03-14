from bot.classes import FetchError
from bot.export import Export
from bot.record import (
    AudiGRep,
    Diario,
    Info,
    Iniciativa,
    Requerimento,
    Voto,
)


def test_export_fetch_error():
    result = Export.markdown(FetchError("timeout"))
    assert "Sem ligação" in result
    assert "ALRA" in result


def test_export_empty_dict():
    result = Export.markdown({})
    assert result == ""


def test_export_single_type():
    blob = {
        Info: [
            Info({"url": "http://x", "Assunto": "Test info"}),
        ]
    }
    result = Export.markdown(blob)
    assert "### Informações" in result
    assert "[Test info]" in result


def test_export_requerimentos_first():
    req_data = {
        "url": "http://x",
        "Assunto": "Req test",
        "Requerente(s)": "João",
        "Data entrada": "01/01/2024",
    }
    blob = {
        Info: [Info({"url": "http://x", "Assunto": "Info test"})],
        Requerimento: [
            (Requerimento(req_data), None, "NO PRAZO"),
        ],
    }
    result = Export.markdown(blob)
    req_pos = result.index("Requerimentos")
    info_pos = result.index("Informações")
    assert req_pos < info_pos


def test_export_multiple_types():
    blob = {
        Info: [Info({"url": "http://x", "Assunto": "Info"})],
        Voto: [Voto({"url": "http://x", "Assunto": "Voto"})],
        Diario: [Diario({"url": "http://x", "Número": "1"})],
    }
    result = Export.markdown(blob)
    assert "### Informações" in result
    assert "### Votos" in result
    assert "### Diários" in result


def test_export_skips_none_markdown():
    blob = {
        Diario: [
            Diario({"url": "http://x"}),  # no Número → returns None
        ],
    }
    result = Export.markdown(blob)
    assert "### Diários" in result
    # The body after the header should be empty (just the header + newline)
    assert result.strip().endswith("Diários")
