import datetime as dt
import io

import pytest

from bot import dgal
from bot.dados import camaras

PAGINA = """
<ul><li>2025</li><li>2019</li></ul>
<div class="titleBlue">2025</div>
<b>Contas de Gerência 2025</b>
<a href="/ficheiros/?content_id=A1&amp;filetype=pdf">Balanço</a>
<a href="/ficheiros/?content_id=A2&amp;filetype=pdf">Balanço</a>
<a href="/ficheiros/?content_id=B1">Demonstração dos Resultados</a>
<a href="/ficheiros/?content_id=C1">Demonstração de Execução Orçamental da
Despesa - Despesas Pagas Líquidas</a>
<a href="/ficheiros/?content_id=D1">Demonstração de Execução Orçamental da
Receita - Receitas Cobradas Líquidas</a>
<a href="/pt-PT/contactos/">Contactos</a>
<div class="titleBlue">2019</div>
<a href="/ficheiros/?content_id=E1">Balanço</a>
"""


def test_contas_links_first_of_each_pair_and_snc_years_only():
    got = dgal.contas_links(PAGINA)
    assert list(got) == [2025]
    assert got[2025]["balanco"].endswith("content_id=A1&filetype=pdf")
    assert got[2025]["balanco"].startswith(dgal.SITE)
    assert sorted(got[2025]) == ["balanco", "despesa", "receita", "resultados"]


def test_divida_and_pmp_links():
    page = (
        '<a href="/ficheiros/?id=1">Evolução endividamento total 2025</a>'
        '<a href="/ficheiros/?id=2">Evolução do endividamento total 2014</a>'
        '<a href="/ficheiros/?id=3">Evolução do endividamento médio e longo'
        " prazo</a>"
        '<a href="/ficheiros/?id=4">3T2026</a>'
        '<a href="/ficheiros/?id=5">2025</a>'
    )
    assert sorted(dgal.divida_links(page)) == [2014, 2025]
    assert list(dgal.pmp_links(page)) == [2025]


def test_azorean_names():
    assert dgal.azorean("LAGOA (SÃO MIGUEL)") == "LAGOA (SÃO MIGUEL)"
    assert dgal.azorean("LAGOA (São Miguel)") == "LAGOA (SÃO MIGUEL)"
    assert dgal.azorean("lagoa  (sao miguel)") == "LAGOA (SÃO MIGUEL)"
    assert dgal.azorean("LAGOA (ALGARVE)") == ""
    assert dgal.azorean("CALHETA (MADEIRA)") == ""
    assert dgal.azorean("MIRANDA DO CORVO") == ""
    assert len(dgal.MUNICIPIOS) == 19


def test_numbers_space_separated():
    toks = "42 534 483 15 942 648 365 521 0 15 577 126".split()
    got = dgal.numbers(toks, 5)
    want = [42534483, 15942648, 365521, 0, 15577126]
    assert want in got
    # only the right split satisfies (5) = (2) - (3) - (4), to the euro
    ok = [v for v in got if abs(v[1] - v[2] - v[3] - v[4]) <= 2]
    assert ok == [want]


DIVIDA = """Limite 2025
(1) (2) (3) (4) (5)=(2)-(3)-(4)
SANTARÉM ABRANTES 54 131 205 2 768 186 140 588 0 2 627 598
R. A. AÇORES NORDESTE 8 920 472 10 495 661 172 483 0 10 323 178
R. A. AÇORES PRAIA DA VITÓRIA **
R. A. AÇORES VELAS 7 713 634 3 221 288 9 094 33 056 3 179 138 b)
FARO LAGOA (ALGARVE) 82 762 512 5 858 727 3 354 221 0 2 504 506
"""


def test_parse_divida():
    rows = dgal.parse_divida(DIVIDA, 2025)
    assert [r["municipio"] for r in rows] == ["Nordeste", "Velas"]
    n = rows[0]
    assert (n["limite"], n["divida_total"], n["divida"]) == (
        8920472,
        10495661,
        10323178,
    )
    assert n["pct_limite"] == 115.7
    assert rows[1]["fam"] == 33056 and rows[1]["nota"] == "b)"


def test_parse_divida_2014_dots():
    t = "R. A. AÇORES LAGOA (São Miguel) 10.147.343 6.868.263 88.625 0 6.779.639"
    (r,) = dgal.parse_divida(t, 2014)
    assert r["geocod"] == "2004201" and r["divida"] == 6779639


def test_parse_divida_unreadable_fails():
    with pytest.raises(ValueError):
        dgal.parse_divida("R. A. AÇORES VELAS 1 2 3 4 5", 2025)
    with pytest.raises(ValueError):
        dgal.parse_divida("R. A. AÇORES ATLANTIDA 1 000 0 0 0 0", 2025)


PMP = """31/12/2024 31/03/2025 30/06/2025 30/09/2025 31/12/2025
SETÚBAL 137 172 177 181 174
PONTA DELGADA 21 21 18 20 15
LAGOA (SÃO MIGUEL) 43 N.d. N.d. N.d. N.d.
LAGOA (ALGARVE) 3 2 2 1 1
"""


def test_parse_and_merge_pmp():
    rows = dgal.parse_pmp(PMP, "PMP 4T2025.pdf")
    pd = [r for r in rows if r["municipio"] == "Ponta Delgada"]
    assert [(r["data"], r["dias"]) for r in pd][-1] == ("2025-12-31", 15)
    assert len([r for r in rows if r["geocod"] == "2004201"]) == 1
    old = [
        {
            "data": "2024-12-31",
            "geocod": "2004203",
            "municipio": "Ponta Delgada",
            "dias": 99,
            "ficheiro": "PMP 4T2024.pdf",
        }
    ]
    merged = dgal.merge_pmp(old + rows)
    dez = [
        r
        for r in merged
        if r["geocod"] == "2004203" and r["data"] == "2024-12-31"
    ]
    assert dez[0]["dias"] == 21  # the newer file wins


def test_parse_pmp_without_dates_fails():
    with pytest.raises(ValueError):
        dgal.parse_pmp("PONTA DELGADA 1 2 3 4 5", "x.pdf")


def test_parse_mapa():
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    N = None
    for r in (
        (N, N, "Município", N, N, "Ativo"),
        (N, N, N, N, N, "Ativos fixos tangíveis", "Inventários", "Caixa"),
        (N, N, "Designação", "NIF", N, "B01", "B02", "B03"),
        (N, N, "ABRANTES", "502661038", N, 10.0, 1.0, 2.0),
        (N, N, "CORVO", "512065837", N, 5.5, 0.0, N),
    ):
        ws.append(r)
    ws2 = wb.create_sheet()
    for r in (
        (N,) * 7 + ("Economica", N, "0100000000", "0101000000", "0102000000"),
        (N,) * 7 + ("Descrição", N, "Impostos diretos", "Sobre", "Outros"),
        (N,) * 7 + ("Tipo", N, "A", "M", "M"),
        (N, N, "CORVO", "512065837", N, "01/04/2026", N, N, N, 7, 3, 0),
    ):
        ws2.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    rows = dgal.parse_mapa(buf.getvalue(), 2025, "x")
    assert {r["municipio"] for r in rows} == {"Corvo"}
    assert [
        (r["codigo"], r["descricao"], r["tipo"], r["valor"]) for r in rows
    ] == [
        ("B01", "Ativos fixos tangíveis", "", 5.5),
        ("0100000000", "Impostos diretos", "A", 7.0),
        ("0101000000", "Sobre", "M", 3.0),
    ]


def test_check():
    hoje = dt.date(2026, 11, 28)
    contas = [{"ano": 2025, "geocod": g} for g, _ in dgal.MUNICIPIOS.values()]
    div = [{"ano": 2025, "geocod": "2004101"}]
    pmp = [{"data": "2025-12-31", "geocod": "2004101"}]
    erros = dgal.check(contas, div, pmp, hoje)
    assert erros == ["dívida 2025: 1 of 19 câmaras"]
    old = [dict(r, ano=2022) for r in contas]
    assert any("too old" in e for e in dgal.check(old, old, pmp, hoje))
    assert "PMP: nothing read" in dgal.check(contas, contas, [], hoje)


def test_divida_pmp_for_the_page():
    cols = dgal.COLS_DIVIDA
    divida = (
        cols,
        [
            [
                "2024",
                "2004202",
                "Nordeste",
                "9",
                "12",
                "0",
                "0",
                "12",
                "133.3",
                "",
            ],
            [
                "2025",
                "2004202",
                "Nordeste",
                "8",
                "10",
                "0",
                "0",
                "10",
                "125.0",
                "",
            ],
            ["2025", "2004502", "Velas", "9", "1", "0", "0", "1", "11.1", ""],
        ],
    )
    pmp = (
        dgal.COLS_PMP,
        [
            ["2025-09-30", "2004202", "Nordeste", "80", "f"],
            ["2025-12-31", "2004202", "Nordeste", "5", "f"],
        ],
    )
    d = camaras.divida_pmp(divida, pmp)
    assert d["ano"] == "2025" and d["acima"] == ["Nordeste"]
    n = d["concelhos"][0]
    assert (n["pct"], n["anos_acima"], n["pmp"], n["pmp_max"]) == (
        125,
        2,
        5,
        80,
    )
    assert d["sem_dados"] == [{"nome": "Velas", "anos": ["2024"]}]
    assert camaras.divida_pmp(None, None) == {}


MAPA12 = """MAPA 12 - TRANSFERÊNCIAS PARA OS MUNICÍPIOS - OE/2026
ABRANTES 12 958 810,00 1 439 868,00 1 004 631,00 1 599 350,00 2 045 305,00 2 045 306,00 278 173,00 1 079 900,00
NORDESTE 4 074 882,00 452 765,00 148 950,00 95 601,00 1 299 815,00 1 299 815,00 38 159,00 339 573,00
PONTA DELGADA 7 735 059,00 859 451,00 2 972 204,00 3 071 690,00 4 334 970,00 4 334 971,00 331 381,00 644 588,00
VELAS 3 624 004,00 402 667,00 148 434,00 0,00 1 182 349,00 1 182 350,00 40 631,00 302 000,00
"""
VARIAVEIS = """NORDESTE 4 439 31 778 10 147 1 103 3 616 510 794 90 942 208 720 0 95 601 38 159
PONTA DELGADA 69 038 1 542 994 23 299 873 2 425 13 636 297 1 873 873 7 997 426 0 4 388 129 331 381
VELAS 4 949 60 373 11 738 1 053 2 416 550 181 141 505 242 145 0 166 771 40 631
NORDESTE 76 142 224
"""


def test_parse_transf_irs_share():
    rows = {
        r["municipio"]: r for r in dgal.parse_transf(2026, MAPA12, VARIAVEIS)
    }
    assert sorted(rows) == ["Nordeste", "Ponta Delgada", "Velas"]
    pd = rows["Ponta Delgada"]
    assert (pd["irs"], pd["irs_max"], pd["irs_pct"]) == (3071690, 4388129, 3.5)
    assert pd["fef"] == 7735059 + 859451 and pd["iva"] == 331381
    assert rows["Nordeste"]["irs_pct"] == 5.0
    assert rows["Velas"]["irs_pct"] == 0.0


def test_parse_transf_missing_variaveis_fails():
    with pytest.raises(ValueError):
        dgal.parse_transf(2026, MAPA12, "")


def test_transf_links():
    page = (
        '<a href="/ficheiros/?id=1">Variáveis - Repartição dos recursos'
        " públicos 2026</a>"
        '<a href="/ficheiros/?id=2">Mapa 12 - Duodécimos 2026</a>'
        '<a href="/ficheiros/?id=3">Fundo Social Municipal_Nota 1/2018</a>'
    )
    got = dgal.transf_links(page)
    assert list(got) == [2026]
    assert got[2026]["mapa12"].endswith("id=2")


def test_contas_camaras():
    C = dgal.COLS_CONTAS
    g, n = "2004202", "Nordeste"

    def row(ano, mapa, cod, val):
        return [ano, g, n, mapa, cod, "", "", str(val)]

    contas = (
        C,
        [
            row("2024", "receita", "0600000000", 60),
            row("2024", "receita", "0100000000", 40),
            row("2025", "receita", "0600000000", 80),
            row("2025", "receita", "1000000000", 10),
            row("2025", "receita", "0102050000", 5),
            row("2025", "receita", "0100000000", 10),
            row("2025", "receita", "1200000000", 500),  # loans: left out
            row("2025", "despesa", "0100000000", 30),
            row("2025", "despesa", "0300000000", 3),
            row("2025", "despesa", "0700000000", 20),
        ],
    )
    ine = (
        ["varcd", "geocod", "nivel", "ilha", "periodo", "valor"],
        [["0012918", g, "Concelho", "São Miguel", "2024", "10"]],
    )
    transf = (
        dgal.COLS_TRANSF,
        [["2026", g, n, "1", "1", "60", "100", "3.0", "1", "1"]],
    )
    derrama = (
        [
            "ano_lucro",
            "geocod",
            "municipio",
            "taxa_geral",
            "taxa_reduzida",
            "isencoes",
            "fonte",
            "url",
        ],
        [["2025", g, n, "1.5", "", "", "", ""]],
    )
    anuario = (
        [
            "ano",
            "geocod",
            "municipio",
            "receita_cobrada",
            "receita_liquidada",
            "despesa_comprometida",
        ],
        [["2024", g, n, "80.0", "", ""], ["2025", g, n, "90.0", "91", "70"]],
    )
    f = camaras.contas_camaras(contas, ine, transf, derrama, anuario)
    a = f["autonomia"][0]
    assert (a["transf"], a["transf_ini"]) == (90.0, 60.0)
    assert a["rigidez"] == 36.7  # (30 + 3) / 90 current revenue
    assert a["invest_hab"] == 2  # 20 € / 10 inhabitants
    i = f["impostos"][0]
    assert (i["derrama_taxa"], i["derrama_k"], i["irs_pct"]) == (1.5, 0, 3.0)
    assert f["irs_devolvem"] == ["Nordeste"]
    o = f["orcamento"][0]
    assert (o["cobrada"], o["cobrada_med"], o["anos_abaixo_85"]) == (
        90.0,
        85.0,
        1,
    )
    assert o["comprometida"] == 70.0
    assert camaras.contas_camaras(None) == {}
