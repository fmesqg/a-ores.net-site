import datetime as dt

from bot import dgaep

N = None
AR = "ADMINISTRAÇÃO REGIONAL DOS AÇORES"


def q11():
    return [
        (N, "Voltar ao Índice"),
        (N, "Q.1.1 Emprego no setor das administrações públicas"),
        (N, N, "EMPREGO", N, N, " ESTRUTURA NO SUBSETOR (%)", N),
        (N, "Unidade: posto de trabalho", "2025", "2026", N, "2025", N),
        (N, N, "31 dez", "30 jun", "30 set(p)", "31 dez", "30 set"),
        (N, "ADMINISTRAÇÕES PÚBLICAS", 700, 710, 720, 100, 100),
        (N, AR, 30, 31, 32, 4.1, 4.2),
        (N, "Órgãos do Governo Regional dos Açores", 20, 21, 22, 1, 1),
        (N, "Educação, Cultura e Desporto", 12, 12, 13, 1, 1),
        (N, "Saúde e Segurança Social", 8, 9, 9, 1, 1),
        (N, "dos quais: SER - Entid. Reclassif. (ii)", 10, 10, 10, 1, 1),
        (N, "ADMINISTRAÇÃO REGIONAL DA MADEIRA", 40, 40, 41, 5, 5),
        (N, "Órgãos do Governo Regional da Madeira", 30, 30, 30, 1, 1),
        (N, "ADMINISTRAÇÃO LOCAL", 500, 500, 500, 70, 70),
        (N, "Fundos de Segurança Social da Adm. Regional dos Açores", 3, 3, 3),
        (N, "Fonte: DGAEP - SIOE"),
    ]


def test_parse_q11_keeps_azores_block_and_comparisons():
    rows = dgaep.parse_q11({"Q1.1": q11()})
    got = {(r["rubrica"], r["local"], r["data"]): r for r in rows}
    assert got[(AR, "Açores", "2026-09-30")]["valor"] == 32
    assert got[(AR, "Açores", "2026-09-30")]["provisorio"] == "p"
    assert got[(AR, "Açores", "2026-06-30")]["provisorio"] == ""
    # the footnote mark goes; the Madeira departments and the structure
    # block (%) are not read
    assert (
        "dos quais: SER - Entid. Reclassif.",
        "Açores",
        "2025-12-31",
    ) in got
    assert not any(
        "da Madeira" in r["rubrica"] and r["local"] == "Açores" for r in rows
    )
    assert {r["data"] for r in rows} == {
        "2025-12-31",
        "2026-06-30",
        "2026-09-30",
    }
    assert (
        got[("ADMINISTRAÇÕES PÚBLICAS", "Portugal", "2025-12-31")]["valor"]
        == 700
    )
    assert got[("ADMINISTRAÇÃO REGIONAL DA MADEIRA", "Madeira", "2026-09-30")]
    fss = "Fundos de Segurança Social da Adm. Regional dos Açores"
    assert got[(fss, "Açores", "2026-09-30")]["valor"] == 3


def test_parse_q17_azores_column_and_national_total():
    nuts = ["PORTUGAL", "CONTINENTE", "R.A. DOS AÇORES", "R.A. DA MADEIRA"]
    book = {
        "Q1.7": [
            (N, "Unidade: posto de trabalho", "ADMINISTRAÇÕES PÚBLICAS"),
            (
                N,
                N,
                "31 dez 2025",
                N,
                N,
                N,
                "30 set 2026 (p)",
                N,
                N,
                N,
                "VT (%) ",
            ),
            (N, " CARGO / CARREIRA / GRUPO", *nuts, *nuts, *nuts),
            (N, "Total", 700, 600, 25, 30, 720, 620, 26, 31, 1, 1, 1, 1),
            (N, "Dirigente superior:", 10, 8, 1, 1, 10, 8, 2, 1, 0, 0, 0, 0),
            (N, "Médico", 50, 45, 2, 3, 52, 46, 3, 3, 0, 0, 9, 0),
            (N, "Fonte: DGAEP - SIOE"),
            (N, "Notas:"),
        ]
    }
    rows = dgaep.parse_q17(book)
    got = {(r["rubrica"], r["local"], r["data"]): r["valor"] for r in rows}
    assert got[("Total", "Açores", "2026-09-30")] == 26
    assert got[("Total", "Portugal", "2025-12-31")] == 700
    assert got[("Dirigente superior", "Açores", "2026-09-30")] == 2
    assert got[("Total", "Madeira", "2026-09-30")] == 31
    assert ("Médico", "Portugal", "2026-09-30") not in got
    assert ("Médico", "Madeira", "2026-09-30") not in got
    assert len(rows) == 10  # the variation columns are not levels


def test_parse_q19_both_pay_blocks():
    book = {
        "Q1.9": [
            (
                N,
                "Unidade: euro",
                "Peso %",
                "REMUNERAÇÃO BASE MÉDIA MENSAL",
                N,
                N,
                N,
                "GANHO MÉDIO MENSAL",
                N,
                N,
                N,
            ),
            (N, N, N, 2025, 2026, "VT", "VH", 2025, 2026, "VT", "VH"),
            (
                N,
                N,
                N,
                "outubro",
                "julho (p)",
                "%",
                "%",
                "outubro",
                "julho (p)",
                "%",
                "%",
            ),
            (
                N,
                "ADMINISTRAÇÕES PÚBLICAS",
                100,
                1900,
                1974.15,
                1,
                4,
                2300,
                2371.1,
                1,
                5,
            ),
            (N, AR, 2.5, 1950, 1985.91, 1, 4, 2350, 2388.56, 0.7, 4.6),
            (
                N,
                "ADMINISTRAÇÃO REGIONAL DA MADEIRA",
                2.8,
                1990,
                1993.98,
                1,
                1,
                2380,
                2385.27,
                1,
                1,
            ),
        ]
    }
    rows = dgaep.parse_q19(book)
    got = {(r["indicador"], r["local"], r["data"]): r for r in rows}
    k = ("Ganho médio mensal", "Açores", "2026-07-01")
    assert got[k]["valor"] == 2388.56 and got[k]["provisorio"] == "p"
    assert (
        got[("Remuneração base média mensal", "Portugal", "2025-10-01")][
            "valor"
        ]
        == 1900
    )
    assert len(rows) == 12


def test_parse_q113_total_by_region():
    regions = ["PORTUGAL", N, "CONTINENTE", N, "R.A. DOS AÇORES", N]
    book = {
        "Q1.13": [
            (N, "Unidade: euro", "ADMINISTRAÇÕES PÚBLICAS"),
            (N, N, "julho 2026(p)", N, N, N, N, N, "VT RBMM (%) "),
            (N, " CARGO", *regions, "PORTUGAL"),
            (N, N, "RBMM", "GMM", "RBMM", "GMM", "RBMM", "GMM", N),
            (
                N,
                "Total",
                1974.15,
                2371.1,
                1977.68,
                2371.4,
                1890.68,
                2282.68,
                1.3,
            ),
            (N, "Médico", 4000, 5000, 4000, 5000, 4100, 5200, 1),
        ]
    }
    rows = dgaep.parse_q113(book)
    got = {(r["indicador"], r["local"]): r["valor"] for r in rows}
    assert got[("Ganho médio mensal", "Açores")] == 2282.68
    assert got[("Remuneração base média mensal", "Continente")] == 1977.68
    assert len(rows) == 6 and {r["data"] for r in rows} == {"2026-07-01"}


def test_latest_file_and_dates():
    page = (
        '<a href="https://www.dgaep.gov.pt/upload//DIOEP/2026/SIEP2T/'
        'dgaep-dioep_siep_2026_t2_20260814.xlsx">'
        '<a href="https://www.dgaep.gov.pt/upload//DIOEP/2026/SIEP3T/'
        'dgaep-dioep_siep_2026_t3_20261116.xlsx">'
        '<a href="/upload/DIOEP/2025/SIEP4T/DGAEP-DIOEP_SIEP_2025_T4.xlsx">'
    )
    assert dgaep.latest_file(page).endswith("siep_2026_t3_20261116.xlsx")
    assert dgaep.latest_file("<p>nada</p>") == ""
    assert dgaep.when("30 set 2026 (p)") == ("2026-09-30", True)
    assert dgaep.when("31 dez", 2011) == ("2011-12-31", False)
    assert dgaep.when("abril ", 2026) == ("2026-04-01", False)
    assert dgaep.when("julho 2026(p)") == ("2026-07-01", True)
    assert dgaep.when("VT (%)") == ("", False)


def test_main_fails_on_stale_or_partial(tmp_path, monkeypatch):
    book = {"Q1.1": q11()}
    monkeypatch.setattr(
        dgaep, "get", lambda url: b'href="x_siep_2026_t3.xlsx"'
    )
    monkeypatch.setattr(dgaep, "load", lambda data: book)
    # only Q1.1 can be read
    assert dgaep.main(tmp_path, dt.date(2026, 11, 27)) == 1
    assert not (tmp_path / "emprego_publico.csv").exists()
