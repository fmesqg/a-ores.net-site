import datetime as dt

from bot import srea


def test_area_files_newest_last():
    page = (
        '<a href="https://srea.azores.gov.pt/wp-content/uploads/2026/11/'
        'B.xlsx">x</a> <a href="https://srea.azores.gov.pt/wp-content/'
        'uploads/2025/11/A.xlsx">y</a> <a href="/other.pdf">z</a>'
    )
    files = srea.area_files(page)
    assert [f.rsplit("/", 1)[-1] for f in files] == ["A.xlsx", "B.xlsx"]


def test_helpers():
    assert srea.number("-") is None
    assert srea.number("x") is None
    assert srea.number(" 4,5 ") == 4.5
    assert srea.year_of("2024*") == 2024
    assert srea.year_of(2012.0) == 2012
    assert srea.month_of("fev") == 2
    assert srea.month_of(3.0) == 3
    assert srea.place("41-Santa Maria") == "Santa Maria"
    assert srea.place("200-Região Autónoma dos Açores") == "Açores"
    assert srea.place("TOTAL") == "Açores"


def test_parse_ipc():
    d1, d2 = dt.datetime(2026, 9, 1), dt.datetime(2026, 10, 1)
    book = {
        "Q5": [
            ["Q5- IPC (Taxa de variação homóloga) Consumo individual; Mensal"],
            ["(voltar ao índice)"],
            ["Código", "Classes ECOICOP (1)", d1, d2],
            ["01", "Produtos alimentares", 2.0, "-"],
            ["03", "Vestuário e calçado", -1.5, -4.27],
        ],
        "Q6": [
            [
                "Q6- IPC (Taxa de variação homóloga) Agregados especiais; Mensal"
            ],
            ["Total e Agregados especiais", d1, d2],
            ["Total", 2.54, 2.64],
            ["Total exceto habitação", 2.4, 2.5],
        ],
        "Q4": [
            [
                "Q4- IPC (média dos últimos 12 meses) Agregados especiais; Mensal"
            ],
            ["Total e Agregados especiais", d1, d2],
            ["Total", 2.61, 2.68],
        ],
        "Q10": [["Q10- ... homóloga ... Agregados especiais; Anual"]],
    }
    rows = srea.parse_ipc(book)
    got = {
        (r["indicador"], r["rubrica"], r["periodo"]): r["valor"] for r in rows
    }
    assert got[("Variação homóloga", "Total", "2026-10")] == 2.64
    assert (
        got[("Variação homóloga", "Vestuário e calçado", "2026-10")] == -4.27
    )
    assert ("Variação homóloga", "Produtos alimentares", "2026-10") not in got
    assert (
        got[("Variação média dos últimos 12 meses", "Total", "2026-10")]
        == 2.68
    )
    assert not any(r["rubrica"] == "Total exceto habitação" for r in rows)
    assert rows[0]["data"].endswith("-01") and rows[0]["unidade"] == "%"


def test_parse_monthly():
    book = {
        "IAE": [
            ["Indicador de Atividade Económica (IAE-Açores)"],
            ["Anos", "Meses", "IAE-Açores"],
            [1996, "jan", "-"],
            [None, "fev", 3.5],
            [1997, "jan", 1.25],
        ]
    }
    rows = srea.parse_monthly(book, "iae", "IAE")
    assert [(r["periodo"], r["valor"]) for r in rows] == [
        ("1996-02", 3.5),
        ("1997-01", 1.25),
    ]


def test_parse_desemprego():
    q = "{}.º trimestre {}"
    head = [None, None, q.format(1, 2026), None, q.format(2, 2026), None]
    head += ["Homóloga", "Voltar ao índice", q.format(1, 2021)]
    book = {
        "Quadro 10": [
            ["Q10. TAXA DE DESEMPREGO"],
            head,
            [None, None, "%"],
            ["Taxa de desemprego", "HM", 5.4, "§", 5.0, None],
            [None, "H", 5.8, "§", "x", None],
            ["Dos 16 aos 24 anos", "HM", "x", None, 18.4, "§"],
            [None, "H", 20, None, 21, None],
        ]
    }
    rows = srea.parse_desemprego(book)
    got = {(r["rubrica"], r["periodo"]): (r["valor"], r["nota"]) for r in rows}
    assert got[("Total", "2026-T1")] == (5.4, "fiabilidade reduzida")
    assert got[("Total", "2026-T2")] == (5.0, "")
    assert ("Homens", "2026-T2") not in got
    assert got[("Dos 16 aos 24 anos", "2026-T2")][0] == 18.4
    assert len(rows) == 4  # youth men are not kept
    assert {r["data"] for r in rows} == {"2026-01-01", "2026-04-01"}


def test_parse_dormidas():
    months = [None] * 5 + srea.MESES + ["Acumulado"]
    book = {
        "HT": [
            ["Dormidas por ilha na Hotelaria"],
            months,
            ["Dormidas (unidades)", None, None, None, 2025]
            + [10] * 12
            + [120],
            [None] * 4 + [2026, 11, 12] + [None] * 10 + [23],
            ["Corvo", None, None, None, 2026, 1, 2] + [None] * 10 + [3],
            ["Nota: provisórios"],
        ]
    }
    rows = srea.parse_dormidas(book, "Hotelaria")
    acores = [r for r in rows if r["local"] == "Açores"]
    assert len(acores) == 14 and sum(r["valor"] for r in acores) == 143
    corvo = [r for r in rows if r["local"] == "Corvo"]
    assert [(r["periodo"], r["valor"]) for r in corvo] == [
        ("2026-01", 1),
        ("2026-02", 2),
    ]
    assert all(r["rubrica"] == "Hotelaria" for r in rows)


def test_parse_pib_populacao_and_pib_hab():
    pib = {
        "1 - PIB preços correntes (€)": [
            [None] * 7 + ["Produto Interno Bruto"],
            [None] * 3 + srea.ILHAS + ["TOTAL"],
            ["Base 2021", None, 2021] + [100.0] * 9 + [900.0],
            [None, None, "2024*"] + [200.0] * 9 + [1800.0],
            [None, None, None, "* Valores provisórios."],
        ]
    }
    pop = {
        "Q01": [
            ["Ano", "RAA/Ilha", "Município", "Sexo"],
            [2024, "200-Região Autónoma dos Açores", None, 90],
            [2024, "49-Corvo", None, 10],
            [2024, "49-Corvo", "4901-Corvo", 10],
        ]
    }
    rows = srea.parse_pib(pib) + srea.parse_populacao(pop)
    p = {(r["serie"], r["local"], r["periodo"]): r for r in rows}
    assert p[("pib", "Corvo", "2024")]["valor"] == 200000
    assert p[("pib", "Corvo", "2024")]["nota"] == "provisório"
    assert p[("pib", "Açores", "2021")]["nota"] == ""
    assert p[("populacao", "Açores", "2024")]["valor"] == 90
    assert len([r for r in rows if r["serie"] == "populacao"]) == 2
    hab = {r["local"]: r["valor"] for r in srea.pib_hab(rows)}
    assert hab == {"Açores": 20000, "Corvo": 20000}


def test_merge_newer_wins(tmp_path):
    old = srea.row(
        "iae", "IAE", "Total", "Açores", "2026-08", "2026-08-01", 1.0, "%"
    )
    new = {**old, "valor": 1.5}
    other = {**old, "periodo": "2026-09", "data": "2026-09-01", "valor": 2}
    for r in (old, new, other):
        r["ficheiro"] = r["pagina"] = "u"
    path = tmp_path / "srea.csv"
    srea.write_csv(path, srea.merge([], [old, other]))
    rows = srea.merge(srea.read_csv(path), [new])
    assert [(r["periodo"], float(r["valor"])) for r in rows] == [
        ("2026-08", 1.5),
        ("2026-09", 2.0),
    ]
    srea.write_csv(path, rows)
    assert "2026-09,2026-09-01,2," in path.read_text(encoding="utf-8-sig")


def test_parse_emprego_total_and_sectors():
    q = "{}.º trimestre {}"
    head = [None, None, q.format(2, 2026), None, q.format(3, 2026), None]
    head += ["Homóloga", "Voltar ao índice", q.format(1, 2021)]
    book = {
        "Quadro 4": [
            ["Q4. POPULAÇÃO EMPREGADA"],
            head,
            ["População empregada", "HM", 122.1, "", 121.3, ""],
            [None, "H", 63.6, "", 62.5, ""],
            ["Dos 16 aos 24 anos", "HM", 6.0, "§", 5.9, "§"],
        ],
        "Quadro 6.1": [
            ["Q6.1. POPULAÇÃO EMPREGADA POR SETOR (CAE-REV. 4)"],
            head,
            ["População empregada", "HM", 122.1, "", 121.3, ""],
            ["A: Agricultura, floresta e pesca", "HM", 7.8, "§", 6.8, "§"],
            [None, "M", "x", "", "x", ""],
            ["L: Atividades financeiras e de seguros", "HM", "x", "", "x", ""],
            ["P: Administração pública e defesa", "HM", 16.2, "", 16.2, ""],
        ],
    }
    rows = srea.parse_emprego(book)
    got = {(r["rubrica"], r["periodo"]): (r["valor"], r["nota"]) for r in rows}
    assert got[("Total", "2026-T3")] == (121.3, "")
    assert got[("A: Agricultura, floresta e pesca", "2026-T2")] == (
        7.8,
        "fiabilidade reduzida",
    )
    assert got[("P: Administração pública e defesa", "2026-T3")][0] == 16.2
    # the total of Quadro 6.1 repeats Quadro 4; men, youth and secret ("x")
    # cells are not kept
    assert len(rows) == 6
    assert {r["serie"] for r in rows} == {"emprego"}
    assert {r["unidade"] for r in rows} == {"milhares"}
    both = srea.parse_ie(book)
    assert len(both) == 6  # no Quadro 10 here


def test_parse_pagamentos():
    head = [
        "Ano",
        "Canal",
        "Mês",
        "Concelho",
        "Tipo de Operação",
        "Origem do cartão",
        "Valor (euros)",
    ]
    tpa, ca = "Terminais de Pagamento Automático", "Caixas Automáticos"
    book = {
        "PIVOT - Valor": [["", "Valor (€)"]],
        "DADOS - Valor": [
            head,
            ["2026", tpa, "Outubro", "Corvo", "Compras", "Portugal", 100],
            ["2026", tpa, "Outubro", "Corvo", "Compras", "Outro país", 40],
            ["2026", tpa, "Outubro", "Lagoa", "Compras", "Portugal", 10],
            ["2026", tpa, "Outubro", "Lagoa", "Outras Operações", "x", 99],
            ["2026", ca, "Março", "Lagoa", "Levantamentos", "Portugal", 7],
            ["2026", ca, "Março", "Lagoa", "Consultas", "Portugal", 0],
        ],
    }
    rows = srea.parse_pagamentos(book, "Valor", "€", concelhos=True)
    got = {(r["rubrica"], r["local"], r["periodo"]): r["valor"] for r in rows}
    assert got[("Compras em TPA", "Açores", "2026-10")] == 150
    assert got[("Compras em TPA", "Corvo", "2026-10")] == 140
    assert (
        got[("Compras em TPA com cartões estrangeiros", "Açores", "2026-10")]
        == 40
    )
    assert got[("Levantamentos em CA", "Lagoa", "2026-03")] == 7
    assert len(got) == 7
    only = srea.parse_pagamentos(book, "Número", "operações", concelhos=False)
    assert {r["local"] for r in only} == {"Açores"}


def test_parse_pde_newer_notification_wins():
    def post(date, text):
        return {"date": date, "link": f"https://srea/{date}/", "content": text}

    posts = [
        post(
            "2026-09-23",
            "<p>Em 2025 (resultados provisórios), a necessidade de "
            "financiamento da Administração Pública da Região Autónoma dos "
            "Açores foi de 305,5 milhões de euros (M€), tendo a dívida bruta "
            "(consolidada) atingido os 3.797,8 M€. O SREA…</p>",
        ),
        post(
            "2026-03-26",
            "<p>Em 2025 a necessidade de financiamento da Administração "
            "Pública da Região Autónoma dos Açores foi de 299,9 milhões de "
            "euros (M€), tendo a dívida bruta (consolidada) atingido os "
            "3.797,8 M€.</p>",
        ),
        post("2026-04-06", "<p>Inquéritos às famílias</p>"),
    ]
    rows = srea.parse_pde(posts)
    assert len(rows) == 4
    last = {r["indicador"]: r for r in rows[2:]}
    saldo = last["Saldo das administrações públicas regionais"]
    assert saldo["valor"] == -305.5
    assert saldo["nota"] == "provisório"
    assert saldo["ficheiro"] == "https://srea/2026-09-23/"
    assert last["Dívida bruta consolidada"]["valor"] == 3797.8
    assert srea.pt_number("3.797,8") == 3797.8


def test_get_retries_then_raises_on_403(monkeypatch):
    import io
    import urllib.error

    calls = []

    def urlopen(req, timeout):
        calls.append(req.full_url)
        code = 503 if len(calls) == 1 else 403
        raise urllib.error.HTTPError(req.full_url, code, "x", {}, io.BytesIO())

    monkeypatch.setattr(srea.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(srea.gov, "wait", lambda host=None: None)
    monkeypatch.setattr(srea.gov, "_sleep", lambda s: None)
    try:
        srea.get("https://srea.azores.gov.pt/x")
    except urllib.error.HTTPError as e:
        assert e.code == 403
    assert len(calls) == 2


def test_parse_creg():
    book = {
        "Indice ": [["Índice"], ["Quadro 1", "PIB"]],
        "Quadro 14": [
            ["Quadro 14"],
            ["Contas Regionais (Base 2021)"],
            ["Produto interno bruto por habitante (PT=100)"],
            [],
            [None, None, "Unidade: percentagem"],
            [
                "Anos",
                "Portugal",
                "R. A. Açores",
                "R. A. Madeira",
                "Extra-Regio",
            ],
            [2023, 100, 87.5, 90, 1],
            ["2024Po", 100, 88.1, "x", 1],
        ],
    }
    rows = srea.parse_creg(book)
    p = {(r["local"], r["periodo"]): r for r in rows}
    assert set(p) == {
        ("Portugal", "2023"),
        ("Açores", "2023"),
        ("Madeira", "2023"),
        ("Portugal", "2024"),
        ("Açores", "2024"),
    }
    r = p[("Açores", "2024")]
    assert r["valor"] == 88.1 and r["nota"] == "provisório"
    assert r["indicador"] == "Produto interno bruto por habitante (PT=100)"
    assert r["unidade"] == "%" and p[("Açores", "2023")]["nota"] == ""


def test_parse_apr():
    book = {
        "Q": [
            ["Receitas e Despesas da Administração Pública Regional"],
            ["Unidade: milhões de euros"],
            ["Operação SEC", 2024, 2025],
            [None, "Final", "Provisório"],
            ["Receitas totais", 1656.262, 1877.4],
            ["     Investimento (1)", 126.6, 188.2],
            ["Saldo total", -281.6, -305.5],
            ["Por Memória:"],
            ["Produto Interno Bruto, a preços de mercado", 5753.3, "x"],
            [
                "Dívida Bruta consolidada da Administração Pública",
                3394.4,
                3797.8,
            ],
            ["Fonte:"],
            ["INE/SREA", 1, 2],
        ]
    }
    p = {(r["rubrica"], r["periodo"]): r for r in srea.parse_apr(book)}
    assert len(p) == 8
    assert p[("Investimento", "2025")]["valor"] == 188.2
    assert p[("Saldo total", "2025")]["nota"] == "provisório"
    assert p[("Saldo total", "2024")]["nota"] == ""
    assert p[("Dívida bruta consolidada", "2025")]["valor"] == 3797.8


def test_parse_remuneracoes():
    d = dt.datetime
    book = {
        "RMM - RAA": [
            [None],
            [
                None,
                "Trimestre terminado no mês",
                None,
                "Variação homóloga nominal",
                None,
                "Variação homóloga real",
            ],
            [
                None,
                "Número de trabalhadores",
                "Remuneração bruta regular média",
                "Número de trabalhadores",
                "Remuneração bruta regular média",
                "Remuneração bruta regular média",
            ],
            [None, "milhares", "euros", "%", "%", "%"],
            [d(2026, 9, 1), 97.76, 1405.6, 0.6, 5.0, 2.1],
        ]
    }
    p = {r["indicador"]: r for r in srea.parse_remuneracoes(book)}
    assert set(p) == {
        "Número de trabalhadores",
        "Remuneração bruta regular média",
        "Remuneração bruta regular média: variação homóloga real",
    }
    assert p["Remuneração bruta regular média"]["unidade"] == "€"
    assert p["Número de trabalhadores"]["periodo"] == "2026-09"


def test_parse_avaliacao():
    d = dt.datetime
    book = {
        "Indice": [["Valor mediano"]],
        "Quadro 1": [
            ["Quadro 1 - Valor mediano"],
            ["Período", "1º Quartil", "Mediana", "Mediana - Apartamentos"],
            [d(2026, 10, 1), 1100, 1613, 2355],
        ],
        "Quadro 2": [
            ["Quadro 2 - Valor mediano"],
            ["Periodo", "Mediana - Horta", "Mediana - Corvo"],
            [d(2026, 10, 1), 1562, "..."],
        ],
        "Quadro 3": [["Quadro 3"], ["Período", "Mediana - Horta - X"]],
    }
    p = {
        (r["rubrica"], r["local"]): r["valor"]
        for r in srea.parse_avaliacao(book)
    }
    assert p == {
        ("Habitação", "Açores"): 1613,
        ("Apartamentos", "Açores"): 2355,
        ("Habitação", "Horta"): 1562,
    }


def test_parse_transacoes():
    head = ["Período", "Total", None, "Região Autónoma dos Açores", None]
    book = {
        "Q1": [
            ["Valor"],
            head,
            ["", "Valor", "Nº", "Valor", "Nº"],
            ["2T2026", 9, 9, 139857, 621],
        ],
        "Q2": [["Valor"], head, ["1T2026", 9, 9, 35192, 100]],
    }
    p = {
        (r["indicador"], r["rubrica"], r["periodo"]): r
        for r in srea.parse_transacoes(book)
    }
    assert p[("Valor", "Total", "2026-T2")]["valor"] == 139857000
    assert p[("Número", "Total", "2026-T2")]["valor"] == 621
    assert p[("Número", "Novos", "2026-T1")]["data"] == "2026-01-01"
    assert len(p) == 4


def test_parse_emprestimos():
    d = dt.datetime
    book = {
        "Particulares": [
            ["Empréstimos Bancários concedidos a particulares"],
            [
                "Data",
                "Empréstimos - Particulares - Habitação ",
                "Empréstimos - Particulares",
                "Rácio empréstimos vencidos - Particulares - Habitação",
            ],
            [
                None,
                "Valor em fim do período",
                "Contagem de devedores",
                "Rácio de empréstimos vencidos",
            ],
            [None, "Milhões €", "Milhares", "%"],
            [d(2026, 9, 30), 2592.6, 50.2, 0.1],
        ]
    }
    p = {
        (r["indicador"], r["rubrica"]): r for r in srea.parse_emprestimos(book)
    }
    assert set(p) == {
        ("Valor em fim do período", "Particulares - Habitação"),
        ("Rácio de empréstimos vencidos", "Particulares - Habitação"),
    }
    r = p[("Valor em fim do período", "Particulares - Habitação")]
    assert r["valor"] == 2592.6 and r["periodo"] == "2026-09"
