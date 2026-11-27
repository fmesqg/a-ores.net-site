import datetime as dt

from bot import cfp

N = None


def test_reports_and_files():
    page = (
        '<a href="https://www.cfp.pt/pt/publicacoes/sectores-das-'
        "administracoes-publicas/sector-empresarial-do-estado-e-regional-"
        '2023-2024">a</a><a href="/pt/publicacoes/sectores-das-'
        'administracoes-publicas/sector-empresarial-regional-2022-2023">b</a>'
        '<a href="/pt/publicacoes/sectores-das-administracoes-publicas/'
        'sector-empresarial-do-estado-2021-2022">c</a>'
    )
    r = cfp.reports(page)
    assert [(x["de"], x["ate"]) for x in r] == [(2022, 2023), (2023, 2024)]
    assert r[0]["url"].startswith("https://www.cfp.pt/pt/")
    f = cfp.files(
        '<a href="https://www.cfp.pt/uploads/publicacoes_ficheiros/'
        'cfp_rel-09-2025.pdf">'
        '<a href="https://www.cfp.pt/uploads/x/fichas-individuais-see-e-ser-'
        '2023_2024.xlsx"><a href="https://www.cfp.pt/uploads/x/cfp-rel-09-'
        '2025-see-ds.xlsx">'
    )
    assert f["numero"] == "9/2025"
    assert f["fichas"].endswith("2023_2024.xlsx")
    assert f["series"].endswith("-ds.xlsx")


def test_parse_lista():
    book = {
        "Quadro 30": [
            (N, "Quadro 30 – Lista de empresas do SER"),
            (N, "Sector Empresarial da RAA (SERAA)| Regional"),
            (N, 3, "EDA, S.A.", "EDA", 0.501, "RAA", N, "D"),
            (
                N,
                4,
                "EDA Renováveis, S.A.",
                "EDA Renováveis",
                0.501,
                "EDA",
                N,
                "D",
                "a)",
            ),
            (
                N,
                8,
                "Sata Air Açores, S.A.",
                "SATA",
                1,
                "SATA Holding",
                "EPR",
                "H",
            ),
            (
                N,
                10,
                "Sata - Gestão de Aeródromos, S.A.",
                "SATA Aeródromos",
                1,
                "SATA Holding",
                "EPR ",
                "H",
            ),
            (N, "Sector Empresarial da RAA (SERAM)| Regional"),
            (N, 1, "CARAM", "CARAM", 1, "RAM", "EPR", "C"),
            (N, "Notas: Inclui as empresas ..."),
            (N, "a) EDA com 99,68% e SEGMA com 0,32%."),
            (N, "Notes: Includes ..."),
            (N, "a) EDA with 99.68%."),
        ]
    }
    lista = cfp.parse_lista(book)
    assert [e["sigla"] for e in lista] == [
        "EDA",
        "EDA Renováveis",
        "SATA",
        "SATA Aeródromos",
    ]
    assert lista[1]["nota"] == "EDA com 99,68% e SEGMA com 0,32%."
    assert lista[0]["ap"] == "" and lista[2]["ap"] == "sim"
    assert lista[0]["participacao"] == 0.501 and lista[0]["cae"] == "D"
    # "SATA Air Açores" must not take the loose key of "Sata - Gestão ..."
    assert cfp.match(lista, "SATA Air Açores, S.A.", "SATA")["sigla"] == "SATA"
    assert (
        cfp.match(lista, "SATA Gestão de Aeródromos, S.A.", "SATA Aerodromos")[
            "sigla"
        ]
        == "SATA Aeródromos"
    )
    assert cfp.match(lista, "CARAM - Centro de Abate", "CARAM") is None


def ficha(nome, anos, linhas):
    rows = [
        (N,) * 3,
        (N, N, "Desempenho económico-financeiro das empresas do SER - Ficha"),
        (N, N, nome),
        (N, N, "", *anos),
    ]
    rows += [(N, N, label, *vals) for label, vals in linhas]
    rows.append((N, N, "Fonte: Relatório e Contas 2024 e 2023"))
    return rows


def test_parse_ficha():
    f = cfp.parse_ficha(
        ficha(
            "EDA, S.A.",
            [2023, 2024],
            [
                ("Número de Trabalhadores", (769, 783)),
                ("Atividade Económica", ()),
                ("        Volume de Negócios", (271600059, 264565631)),
                ("Resultado Líquido", (17087133, 10431115)),
                ("Valor Acrescentado Bruto (VAB)*", (96092031, 94217565)),
            ],
        )
    )
    assert f["empresa"] == "EDA, S.A."
    assert f["fonte"] == "Fonte: Relatório e Contas 2024 e 2023"
    assert (2024, 1, "Volume de Negócios", 264565631.0) in f["valores"]
    assert (2023, 3, "Valor Acrescentado Bruto (VAB)", 96092031.0) in f[
        "valores"
    ]
    assert cfp.parse_ficha([(N, "Índice | Index")]) is None


def test_parse_esforco_by_position():
    book = {
        "Quadro 24": [
            (N, "Quadro 24 – Esforço financeiro líquido das Regiões"),
            (N, "Designação", "RAA", N, "Variação", N, N, "RAM"),
            (N, N, 2023, 2024, "Variação", N, N, 2023, 2024),
            (N, N, N, N, "M€", "%", N, N, N, "M€"),
            (N, "Dividendos*", 3.058, 3.5, 0.4, 0.1, N, 5.4, 4.6),
            # Madeira only: the Azores cells are empty
            (N, "Indemnizações compensatórias", N, N, N, N, N, 15, 23.9),
            (N, "Esforço financeiro líquido (2)-(1)", 75.1, 93.5),
            (N, "em % PIB regional", 0.014, 0.016, "+0,2 p.p."),
            (N, "Fontes: Conta da RAA. | Notas: (**) Excluem-se ..."),
        ]
    }
    rows = cfp.parse_esforco(book)
    got = {(r["rubrica"], r["ano"]): r["valor"] for r in rows}
    assert got[("Dividendos", 2024)] == 3.5
    assert not any(r["rubrica"].startswith("Indemniza") for r in rows)
    assert got[("Esforço financeiro líquido (2)-(1)", 2023)] == 75.1
    assert round(got[("em % PIB regional", 2024)], 6) == 1.6
    assert rows[0]["nota"].startswith("Fontes: Conta da RAA")


def test_parse_peso_azores_only():
    book = {
        "Quadro 3": [
            (N, "Quadro 3 - Peso do SEE e do SER na economia"),
            (N, N, "2023", "2024"),
            (N, "PIB - Produto Interno Bruto:"),
            (N, "Açores(*)", 5376, 5774),
            (N, "Madeira(*)", 6989, 7503),
            (N, "Número trabalhadores (milhares):"),
            (N, "SERAA", 7.5, 7.6),
            (N, "Sector Empresarial da RAA (SERAM)", 8.9, 8.8),
            (N, "Indicadores:"),
            (N, "Peso do SERAA no PIB RAA", 0.082, 0.076),
            (N, "Fontes: INE"),
        ]
    }
    rows = cfp.parse_peso(book)
    got = {(r["rubrica"], r["ano"]): (r["valor"], r["unidade"]) for r in rows}
    assert got[("Açores", 2024)] == (5774, "M€")
    assert got[("SERAA", 2023)] == (7.5, "milhares")
    assert round(got[("Peso do SERAA no PIB RAA", 2024)][0], 6) == 7.6
    assert not any(
        "SERAM" in r["rubrica"] or r["rubrica"] == "Madeira" for r in rows
    )


def test_merge_latest_report_wins_and_expected():
    old = {
        "relatorio": "13/2024",
        "sigla": "EDA",
        "ano": "2023",
        "ordem": "0",
        "indicador": "VN",
        "valor": "1",
    }
    new = {**old, "relatorio": "9/2025", "valor": "2"}
    other = {**old, "ano": "2022"}
    rows = cfp.merge([old, other], [new])
    assert [(r["ano"], r["valor"]) for r in rows] == [
        ("2022", "1"),
        ("2023", "2"),
    ]
    assert cfp.expected(dt.date(2026, 11, 27)) == 2024
    assert cfp.expected(dt.date(2027, 1, 10)) == 2024
    assert cfp.expected(dt.date(2027, 2, 1)) == 2025
