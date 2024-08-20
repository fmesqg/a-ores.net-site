if __name__ == "__main__":
    import sys
    import os.path

    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from alra_bot.fetch import fetch_info, fetch_voto, fetch_requerimento, fetch_iniciativa

# TODO these tests, as they are, require network connection. Substitute so as o use html
# (or at least keep an offline version)


def test_fetch_voto():
    expected = {
        "id": 3525,
        "Texto Voto Apresentado": "http://base.alra.pt:82/Doc_Voto/XIIIva1550_24.pdf",
        "Legislatura": "XIII",
        "Nº Entrada": "1550",
        "Data entrada": "11/07/2024",
        "Titulo": "Voto de Congratulação",
        "Autores": "CH",
        "Assunto": "Pela subida à Primeira Liga Portuguesa de Futebol do Clube Desportivo Santa Clara",  # noqa: E501
        "Anúncio em plenário": "11/07/2024",
        "Resultado": "Aprovado por unanimidade",
    }
    actual = fetch_voto(3525)
    assert expected == actual


def test_fetch_requerimento_atempada():
    expected = {
        "id": 8251,
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
    actual = fetch_requerimento(8251)
    assert expected == actual


def test_fetch_iniciativa():
    expected = {
        "id": 3625,
        "Texto Iniciativa": "http://base.alra.pt:82/iniciativas/iniciativas/XIIIEPjDLR015.pdf",  # noqa: E501
        "Nota de": "http://base.alra.pt:82/iniciativas/iniciativas/XIIInaPjDLR015.pdf",
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
    actual = fetch_iniciativa(3625)
    assert expected == actual


def test_fetch_info():
    expected = {
        "id": 20085,
        "Texto Informação": "http://base.alra.pt:82/Doc_Noticias/NI20085.pdf",
        "Legislatura": "XIII",
        "Data": "16/08/2024",
        "Tipo": "Nota de Pesar",
        "Autor": "Presidência da ALRAA",
        "Assunto": "Nota de Pesar da Presidência da ALRAA - Presidente Luís Garcia manifesta profundo pesar pelo falecimento do antigo Presidente da Assembleia Legislativa Álvaro Monjardino",  # noqa: E501
    }
    actual = fetch_info(20085)
    assert expected == actual


if __name__ == "__main__":
    test_fetch_voto()
    test_fetch_requerimento_atempada()
    test_fetch_iniciativa()
    test_fetch_info()
