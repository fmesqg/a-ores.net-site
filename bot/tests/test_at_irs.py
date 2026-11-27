from bot import at_irs

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
