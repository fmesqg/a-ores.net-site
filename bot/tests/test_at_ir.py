from bot import at_ir as at_irs

N = None


def taxas_sheet(ano, medida="Número de Agregados", escala=None):
    rows = [
        ["Mapa 30 - Taxas de Tributação por Circunscrições Administrativas"],
        [medida],
        [ano],
        ["C - CONTINENTE"],
    ]
    if escala:
        rows.append([escala])
    rows += [
        ["TITULARIDADE"],
        ["Taxas (%)", "CASADOS", "NÃO CASADOS", "TOTAL", "%"],
        [13, 10, 20, 30, 0.5],
        [48, 1, 2, 3, 0.05],
        ["Total:", 33],
        ["A - AÇORES"],
    ]
    if escala:
        rows.append([escala])
    rows += [
        ["Taxas(%)", "CASADOS", "NÃO CASADOS", "TOTAL", "%"],
        [9.1, 4, 5, 9, 0.5],
        [33.599999999999994, 0.375, 0.451, 0.826, 0.0065],
        ["Total:", 9.826],
        ["Fonte: AT"],
    ]
    return rows


def test_parse_taxas_counts_and_millions():
    rows = at_irs.parse_taxas(taxas_sheet(2024), "2022-2024", "u")
    got = {(r[3], r[4], r[6]): r for r in rows}
    assert got[("Açores", 2, "Total")][5] == 33.6
    assert got[("Açores", 1, "Casados")][7] == 4
    assert got[("Continente", 2, "Não casados")][7] == 2
    assert len(rows) == 12
    money = at_irs.parse_taxas(
        taxas_sheet(
            2024,
            "IRS Liquidado - Valores Apurados",
            "Valores em Milhões de Euros",
        ),
        "2022-2024",
        "u",
    )
    m = {(r[3], r[4], r[6]): r for r in money}
    assert m[("Açores", 2, "Total")][1] == "IRS liquidado"
    assert m[("Açores", 2, "Total")][7] == 826000.0
    assert m[("Açores", 2, "Total")][8] == "€"


def test_parse_adicional():
    rows = [
        ["Mapa 41 - Taxa Adicional de Solidariedade"],
        ["IRS Liquidado à Taxa Adicional"],
        ["Açores"],
        ["Valores em Milhões de Euros"],
        ["Modelo 3"],
        ["Valores Escalão", 2022, 2023, 2024, "Var 22-23", "Var 23-24"],
        [" 80.000 € até 250.000 €", 0.37, 0.51, 0.68, 0.38, 0.33],
        ["Superior a 250.000 €", 0.33, 0.15, 0.18, -0.5, 0.17],
        ["TOTAL:", 0.7, 0.66, 0.86, 0, 0],
    ]
    got = at_irs.parse_adicional(rows, "2022-2024", "u")
    assert len(got) == 6
    first = got[0]
    assert first[:6] == [
        at_irs.ADICIONAL,
        "IRS liquidado",
        2022,
        "Açores",
        1,
        "80.000 € até 250.000 €",
    ]
    assert first[7] == 370000.0


def test_parse_book_finds_tables_by_content():
    book = {
        "Mapa 40": taxas_sheet(2017),  # same table, another number
        "Mapa 30": [
            ["Mapa 30 - IRS Liquidado por Escalões de Rendimento"],
            ["Número de Agregados"],
            [2017],
        ],
    }
    rows = at_irs.parse_book(book, "2015-2017", "u")
    assert {r[2] for r in rows} == {2017} and len(rows) == 12


def test_dossies_from_page():
    page = (
        '<a href="/pt/x/Documents/Notas_Previas_Dossier_Estatistico_IRS_2022_'
        '2024.xlsx">'
        '<a href="/pt/x/IRS_2016_2018/Documents/Dossier%20Estat%C3%ADstico_'
        '2020E000938986_A03.xlsx">'
        '<a href="/pt/x/Documents/Dossier_Estatistico_IRS_2018-2020_VF.xlsx">'
        '<a href="/pt/x/Documents/IRS2007_2009.xls">'
    )
    got = at_irs.dossies(page)
    assert sorted(got) == ["2016-2018", "2018-2020", "2022-2024"]
    assert got["2022-2024"].startswith("https://info.portaldasfinancas")


def test_dossies_by_tax():
    page = (
        '<a href="/pt/x/Documents/Dossier_Estatistico_IRC_2022_2024.xlsx">'
        '<a href="/pt/x/IRC_2017_2019/Documents/Dossier_Estatistico_IRS_'
        '2017_2019.xlsx">'
        '<a href="/pt/x/Documents/Dossier_Estatistico_IRS_2021_2023.xlsx">'
        '<a href="/pt/x/IRC_2014_2016/Documents/20180424_IR_DE%20-%20IRC%20'
        'Dossier%20Estatistico%202014-2016.xlsx">'
    )
    assert sorted(at_irs.dossies(page, "IRC")) == [
        "2014-2016",
        "2017-2019",
        "2022-2024",
    ]
    assert sorted(at_irs.dossies(page, "IRS")) == ["2021-2023"]


def test_num_and_header():
    assert at_irs.num("13,1%") == 0.131
    assert at_irs.num("1.234,5") == 1234.5
    assert at_irs.num(0.21) == 0.21
    assert at_irs.num("-") is None
    head = ["Cód.", "DESIGNAÇÃO", 2022, "%", 2023, "%", 2024, "%", "Var."]
    assert at_irs.year_cols(head) == {2022: 2, 2023: 4, 2024: 6}
    # a data row whose numbers look like years is not a header
    assert at_irs.year_cols(["19", "HORTA", 2020, 0.2, 2021, 0.2]) is None
    assert at_irs.regiao("ANGRA DO HEROISMO") == "Açores"
    assert at_irs.regiao("R. A. AÇORES") == "Açores"
    assert at_irs.regiao("Funchal") == "Madeira"
    assert at_irs.regiao("TOTAL:") == "Total"


def irc_book():
    return {
        "M6 DIST": [
            ["CAP.I - NÚMERO DE DECLARAÇÕES - MAPA 6"],
            ["NÚMERO DE DECLARAÇÕES"],
            ["POR DISTRITO"],
            ["Cód.", "DESIGNAÇÃO", 2023, "%", 2024, "%", "Var."],
            ["11", "LISBOA", 100, 0.5, 110, 0.5, 0.1],
            ["25", "R. A. AÇORES", 8160, 0.014, 8513, 0.014, 0.04],
            ["TOTAL", None, 585754, 1, 604771, 1, 0.03],
        ],
        "M58 IRCV": [
            ["CAP.V - INDICADORES POR DISTRITO - MAPA 58"],
            ["IRC LIQUIDADO"],
            ["( Campo 358)"],
            ["VALORES  DECLARADOS"],
            ["(Valores em milhões de Euros)"],
            ["Cód.", "DESIGNAÇÃO", 2023, "%", 2024, "%"],
            ["25", "R. A. AÇORES", 53.79, 0.007, 64.07, 0.008],
            ["Fonte: AT - Autoridade Tributária e Aduaneira"],
        ],
        "M59 Dtxef": [
            ["CAP.V - INDICADORES POR DISTRITO - MAPA 59"],
            ["TAXAS MÉDIAS EFETIVAS (a)"],
            ["Cód.", "DESIGNAÇÃO", 2023, 2024, "Var. (p.p.)"],
            [19, "Angra do Heroísmo", "13,1%", 0.132, 0.1],
        ],
        "M13 NUMERO": [
            ["CAP.II - VALORES DECLARADOS - MAPA 13"],
            ["CÁLCULO DO IMPOSTO (a)"],
            ["NÚMERO DE DECLARAÇÕES"],
            ["DESIGNAÇÃO", 2023, 2024, "Var."],
            ["Coleta", 1, 2, 0],
            ["Imposto à taxa da Reg. Aut. dos Açores", 4403, 4562, 0.04],
        ],
        "M14 VALOR": [
            ["CAP.II - VALORES DECLARADOS - MAPA 14"],
            ["CÁLCULO DO IMPOSTO (a)"],
            ["VALORES DECLARADOS"],
            ["(Valores em milhões de Euros)"],
            ["DESIGNAÇÃO", 2023, 2024, "Var."],
            ["Imposto à taxa da Reg. Aut. dos Açores", 66.89, 75.63, 0.13],
        ],
        "M61 DER": [
            ["CAP.VI – RESUMO - MAPA 61"],
            ["DERRAMA ESTADUAL POR ESCALÕES"],
            ["VALORES DECLARADOS"],
            ["AÇORES"],
            ["Valores em Milhões de Euros"],
            ["ESCALÕES\n(Euros)", 2023, 2024, "Var."],
            ["Mais de 35.000.000", 0, 1.42, "-"],
            ["TOTAL", 3.87, 4.68, 0.2],
        ],
        "M64 Taxas": [
            ["CAP.VI – RESUMO QUADRO 64"],
            ["EVOLUÇÃO DAS TAXAS NOMINAIS EM IRC"],
            ["DESIGNAÇÃO", "2023", "2024"],
            ["Taxa geral", 0.21, 0.21],
            ["Taxas especificas"],
            ["    R. A. Açores"],
            ["    Taxa geral", 0.147, 0.147],
            ["Taxas excepcionais ( De Beneficio Fiscal )"],
            ["Interioridade", "12,5% / 21%", "12,5% / 21%"],
        ],
    }


def test_parse_irc():
    irc, dist = at_irs.parse_irc(irc_book(), "2022-2024", "u")
    d = {(r[1], r[2], r[3], r[4]): r[6] for r in dist}
    assert d[("Declarações", "declarações", 2024, "R. A. AÇORES")] == 8513
    assert d[("Declarações", "declarações", 2024, "TOTAL")] == 604771
    assert d[("IRC liquidado", "€", 2024, "R. A. AÇORES")] == 64070000.0
    assert d[("Taxa média efetiva", "%", 2023, "Angra do Heroísmo")] == 13.1
    assert {r[5] for r in dist} == {"Açores", "Continente", "Total"}
    c = {(r[0], r[2], r[3], r[6]): r[5] for r in irc}
    assert c[(at_irs.CALCULO, 2024, "Açores", "declarações")] == 4562
    assert c[(at_irs.CALCULO, 2024, "Açores", "€")] == 75630000.0
    assert c[(at_irs.DERRAMA, 2024, "Açores", "€")] in (1420000.0, 4680000.0)
    tot = [r for r in irc if r[0] == at_irs.DERRAMA and r[4] == "Total"]
    assert [r[5] for r in tot if r[2] == 2024] == [4680000.0]
    nom = {(r[3], r[2]): r[5] for r in irc if r[0] == at_irs.NOMINAIS}
    assert nom == {
        ("Continente", 2023): 21.0,
        ("Continente", 2024): 21.0,
        ("Açores", 2023): 14.7,
        ("Açores", 2024): 14.7,
    }


def test_parse_gerais():
    rows = [
        ["Mapa 45 – Taxas Gerais de IRS"],
        ["Ano 2024"],
        ["Rendimento Coletável (euros)", None, "Taxas (percentagem)"],
        [None, "Continente", "Açores", "Madeira"],
        ["Até 7703", 13, 9.1, 9.1],
        ["​ De mais de 7703 até 11623", 16.5, 11.549999999999999, 11.55],
        ["Superior a 80000", 48, 33.599999999999994, 47.52],
    ]
    got = at_irs.parse_gerais(rows, "2022-2024", "u")
    by = {(r[3], r[4]): (r[5], r[7]) for r in got}
    assert by[("Açores", 2)] == (11.55, 11623.0)
    assert by[("Madeira", 3)] == (47.52, "")
    assert len(got) == 9


def test_merge_newest_edition_wins():
    old = [["q", "m", 2022, "A", 1, "", "Total", 1, "€", "2020-2022", "u"]]
    new = [["q", "m", 2022, "A", 2, "", "Total", 5, "€", "2022-2024", "u"]]
    got = at_irs.merge(
        [old, new],
        key=lambda r: (r[0], r[1], r[2], r[3], r[4], r[6]),
        cover=lambda r: (r[0], r[1], r[2]),
    )
    assert got == new
