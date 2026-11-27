import csv
import sqlite3

from bot import datasets, ine

META = {
    "IndicadorNome": "Valor mediano do rendimento bruto declarado deduzido do "
    "IRS liquidado por sujeito passivo (€) por Localização geográfica (NUTS - "
    "2024); Anual - INE, Estatísticas do Rendimento ao nível local",
    "UnidadeMedida": "Euro (€)",
    "DataUltimaAtualizacao": "2026-07-24",
}

DATA = {
    "Dados": {
        "2024": [
            {
                "geocod": "20",
                "geodsg": "Região Autónoma dos Açores",
                "dim_3": "1",
                "dim_3_t": "HM",
                "valor": "11000",
            },
            {
                "geocod": "20",
                "geodsg": "Região Autónoma dos Açores",
                "dim_3": "2",
                "dim_3_t": "H",
                "valor": "12000",
            },
            {
                "geocod": "200",
                "geodsg": "Região Autónoma dos Açores",
                "dim_3": "1",
                "dim_3_t": "HM",
                "valor": "11000",
            },
            {
                "geocod": "2004206",
                "geodsg": "Vila Franca do Campo",
                "dim_3": "1",
                "dim_3_t": "HM",
                "valor": "10395",
            },
            {
                "geocod": "200420602",
                "geodsg": "Ponta Garça",
                "dim_3": "1",
                "dim_3_t": "HM",
                "valor": "9305.5",
            },
            {
                "geocod": "200420603",
                "geodsg": "Ribeira das Tainhas",
                "dim_3": "1",
                "dim_3_t": "HM",
                "sinal_conv": "-",
            },
            {
                "geocod": "1110601",
                "geodsg": "Lisboa",
                "dim_3": "1",
                "dim_3_t": "HM",
                "valor": "15000",
            },
        ]
    }
}


def test_period_date():
    assert ine.period_date("2024") == "2024-01-01"
    assert ine.period_date("Setembro de 2026") == "2026-09-01"
    assert ine.period_date("2.º Trimestre de 2026") == "2026-04-01"
    assert ine.period_date("2.º Semestre de 2024") == "2024-07-01"
    assert ine.period_date("2022 / 2023") == "2023-01-01"
    assert ine.period_date("2021 - 2025") == "2025-01-01"
    assert ine.period_date("sem ano") == ""


def test_nuts_and_level():
    assert ine.nuts("4203") == "2004203"
    assert ine.nuts("420301") == "200420301"
    assert ine.nuts("2004203") == "2004203"
    assert ine.nuts("1106") == "1106"  # mainland admin code: untouched
    assert ine.nuts("2") == "20" and ine.nuts("3") == "30"  # IPC NUTS II
    assert ine.nuts("1") == "1"
    assert ine.level("20") == "Região"
    assert ine.level("2004203") == "Concelho"
    assert ine.level("200420301") == "Freguesia"


def test_short_name():
    assert ine.short_name(META["IndicadorNome"]) == (
        "Valor mediano do rendimento bruto declarado deduzido do IRS "
        "liquidado por sujeito passivo (€)"
    )


def test_is_total():
    assert ine.is_total("HM")
    assert ine.is_total("Total de obras de edificação")
    assert not ine.is_total("1º quintil")


def test_rows_from():
    rows = [
        dict(zip(ine.COLS, r, strict=True))
        for r in ine.rows_from("0012757", DATA, META)
    ]
    # total (HM) only, NUTS III duplicate dropped, no Lisbon, no empty value
    assert [r["local"] for r in rows] == [
        "Região Autónoma dos Açores",
        "Vila Franca do Campo",
        "Ponta Garça",
    ]
    reg, conc, freg = rows
    assert reg["nivel"] == "Região" and reg["ilha"] == ""
    assert conc["ilha"] == "São Miguel" and conc["concelho"] == ""
    assert freg["concelho"] == "Vila Franca do Campo"
    assert freg["valor"] == 9305.5 and conc["valor"] == 10395
    assert freg["categoria"] == ""
    assert freg["data"] == "2024-01-01"
    assert freg["unidade"] == "Euro (€)"
    assert freg["url"] == "https://www.ine.pt/xurl/indx/0012757"


def test_rows_from_keeps_dimension_without_total():
    data = {
        "Dados": {
            "2024": [
                {
                    "geocod": "2004203",
                    "geodsg": "Ponta Delgada",
                    "dim_3_t": f"{q}º quintil",
                    "valor": str(q * 1000),
                }
                for q in (1, 2)
            ]
        }
    }
    rows = ine.rows_from("0012759", data, META)
    assert [r[ine.COLS.index("categoria")] for r in rows] == [
        "1º quintil",
        "2º quintil",
    ]


def test_rows_from_admin_division_codes():
    data = {
        "Dados": {
            "2025": [
                {
                    "geocod": "4203",
                    "geodsg": "Ponta Delgada",
                    "valor": "232.99",
                },
                {"geocod": "1106", "geodsg": "Lisboa", "valor": "100"},
            ]
        }
    }
    (row,) = ine.rows_from("0007822", data, META)
    assert row[ine.COLS.index("geocod")] == "2004203"
    assert row[ine.COLS.index("nivel")] == "Concelho"


def test_datasets_includes_ine(tmp_path):
    docs, data = tmp_path / "docs", tmp_path / "data"
    for coll in ("_base_updates", "_alra_updates", "_joraa_updates"):
        (docs / coll).mkdir(parents=True)
    data.mkdir()
    with open(data / "ine.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(ine.COLS)
        w.writerows(ine.rows_from("0012757", DATA, META))

    meta = datasets.main(docs)
    assert meta["ine"]["linhas"] == 3
    assert meta["ine"]["indicadores"] == 1
    assert (meta["ine"]["de"], meta["ine"]["ate"]) == (
        "2024-01-01",
        "2024-01-01",
    )
    assert (docs / "dados" / "ine.csv").exists()

    con = sqlite3.connect(docs / "dados" / "acores.db")
    valor, tipo = con.execute(
        "select valor, typeof(valor) from ine join ine_fts "
        "on ine_fts.rowid = ine.rowid where ine_fts match 'garca'"
    ).fetchone()  # accent-insensitive: "Ponta Garça"
    assert (valor, tipo) == (9305.5, "real")


def test_non_annual_name_has_periodicity():
    meta = dict(META, Periodic="Mensal")
    row, *_ = ine.rows_from("0012088", DATA, meta)
    assert row[ine.COLS.index("indicador")].endswith("(€) – mensal")


def test_every_indicator_has_a_theme_and_rows_carry_it():
    assert (
        len(ine.INDICATORS)
        == len(ine.TEMA)
        == len({v for v, _ in ine.INDICATORS})
    )
    row, *_ = ine.rows_from("0012757", DATA, META)
    assert row[ine.COLS.index("tema")] == "Rendimento e IRS"


def test_reference_rows_portugal_and_madeira():
    data = {
        "Dados": {
            "2024": [
                {"geocod": "PT", "geodsg": "Portugal", "valor": "15075"},
                {
                    "geocod": "30",
                    "geodsg": "Região Autónoma da Madeira",
                    "valor": "15550",
                },
                {
                    "geocod": "300",
                    "geodsg": "Região Autónoma da Madeira",
                    "valor": "15550",
                },
                {"geocod": "3003101", "geodsg": "Funchal", "valor": "17000"},
                {
                    "geocod": "20",
                    "geodsg": "Região Autónoma dos Açores",
                    "valor": "15615",
                },
            ]
        }
    }
    rows = [
        dict(zip(ine.COLS, r, strict=True))
        for r in ine.rows_from("0012756", data, META)
    ]
    got = {r["geocod"]: r["nivel"] for r in rows}
    assert got == {"PT": "País", "30": "Região", "20": "Região"}  # no Funchal


def test_ine_news_newest_first():
    cols = ine.COLS

    def row(v, upd, periodo):
        r = dict.fromkeys(cols, "")
        r.update(
            varcd=v,
            indicador=f"I{v}",
            tema="T",
            atualizado=upd,
            geocod="20",
            periodo=periodo,
            data=ine.period_date(periodo),
        )
        return [r[c] for c in cols]

    rows = [
        row("1", "2026-01-01", "2024"),
        row("2", "2026-09-29", "2025"),
        row("2", "2026-09-29", "2024"),
    ]
    news = datasets.ine_news(cols, rows)
    assert [n["varcd"] for n in news] == ["2", "1"]
    assert news[0]["periodo"] == "2025"


def test_rows_from_scales_thousands():
    # Câmaras' revenue: UnidadeMedida "Euro (€)" but values in 10^3 €.
    data = {
        "Dados": {
            "2025": [
                {
                    "geocod": "2004203",
                    "geodsg": "Ponta Delgada",
                    "valor": "75105",
                },
                {"geocod": "20", "geodsg": "Açores", "valor": "0.5"},
            ]
        }
    }
    rows = ine.rows_from("0013908", data, {**META, "Potencia10": "3"})
    valor = ine.COLS.index("valor")
    assert [r[valor] for r in rows] == [75105000, 500]
    assert rows[0][ine.COLS.index("unidade")] == "Euro (€)"
    rows = ine.rows_from("0013908", data, {**META, "Potencia10": "0"})
    assert [r[valor] for r in rows] == [75105, 0.5]


def test_previous_rows_keeps_indicators_that_failed(tmp_path):
    p = tmp_path / "ine.csv"
    p.write_text(
        "﻿varcd,x\n0000087,a\n0012918,b\n9999999,c\n", encoding="utf-8"
    )
    # 0012918 was fetched again; 0000087 failed; 9999999 left the list
    assert ine.previous_rows(p, {"0012918"}) == [["0000087", "a"]]
    assert ine.previous_rows(tmp_path / "nada.csv", set()) == []


def test_censos_setores_keeps_concelhos_and_sections():
    o = {"dim_3_t": "HM", "dim_5_t": "Total"}
    data = {
        "Dados": {
            "2021": [
                {
                    **o,
                    "geocod": "4901",
                    "geodsg": "Corvo",
                    "dim_4_t": "Educação",
                    "valor": "14",
                },
                {
                    **o,
                    "geocod": "4901",
                    "geodsg": "Corvo",
                    "dim_4_t": "Construção",
                    "valor": "30",
                },
                {
                    **o,
                    "geocod": "490101",
                    "geodsg": "Corvo",
                    "dim_4_t": "Educação",
                    "valor": "14",
                },
                {
                    **o,
                    "geocod": "4901",
                    "geodsg": "Corvo",
                    "dim_4_t": "Educação",
                    "valor": "7",
                    "dim_3_t": "H",
                },
            ]
        }
    }
    assert ine.censos_setores(data) == [["Corvo", "Corvo", "P", 14]]
