import csv
import datetime as dt
import os
import sqlite3

import pytest

from bot import datasets, tdc

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
DOCS = {"parecer": "https://example.com/p.pdf", "sintese": "s.pdf"}


def pages(year):
    path = os.path.join(FIXTURES, f"tdc_{year}.txt")
    with open(path, encoding="utf-8") as f:
        return f.read().split("\f")


@pytest.fixture(scope="module")
def p2025():
    return tdc.parecer_rows(pages(2025), 2025, DOCS)


@pytest.fixture(scope="module")
def p2024():
    return tdc.parecer_rows(pages(2024), 2024, DOCS)


def of(rows, tipo):
    return [r for r in rows if r["tipo"] == tipo]


def test_documents_from_detail_page():
    folder = "/pt-pt/ProdutosTC/PareceresTribunalContas/pareceres-craa"
    page = (
        '<a href="/pt-pt/etica/Documents/Carta-Etica.pdf">Carta</a>'
        f"<h4><a target='_blank' href='{folder}/Documents/2025/"
        "pcraa2025-2pp.pdf'>Parecer em duas páginas</a></h4>"
        f"<h4><a target='_blank' href='{folder}/Documents/2025/"
        "pcraa2025.pdf'>Parecer sobre a Conta da Região Autónoma dos Açores"
        " de 2025</a></h4>"
    )
    docs = tdc.documents(page)
    assert docs["parecer"].endswith("/Documents/2025/pcraa2025.pdf")
    assert docs["parecer"].startswith("https://www.tcontas.pt/pt-pt/")
    assert docs["sintese"].endswith("pcraa2025-2pp.pdf")
    assert tdc.documents("<html>nada</html>") == {}


def test_juizo_reservas_enfases(p2025):
    rows = p2025[0]
    assert of(rows, "juízo")[0]["texto"] == (
        "Juízo de conformidade global, com reservas, ênfases e recomendações"
    )
    reservas = of(rows, "reserva")
    assert len(reservas) == 4
    assert "613 milhões de euros" in reservas[1]["texto"]
    enfases = of(rows, "ênfase")
    assert len(enfases) == 4
    # the footnote and the page number between pages are gone
    assert not any("LOPTC" in r["texto"] for r in reservas + enfases)
    assert enfases[1]["texto"].endswith("de 30 de dezembro.")


def test_recomendacoes(p2025, p2024):
    recs = of(p2025[0], "recomendação")
    assert [r["numero"] for r in recs] == list(range(1, 13))
    assert recs[0]["texto"].startswith("Apresentar à Assembleia Legislativa")
    assert recs[0]["texto"].endswith("grau de realização dos objetivos.")
    assert recs[0]["referencia"] == "Ponto 1.2, §§ 10 a 13"
    assert recs[2]["referencia"] == "Capítulo I §§ 43 a 45"
    # 2024: ordinals broken over lines ("1\n0\n.ª"), a new one at the end
    recs = of(p2024[0], "recomendação")
    assert len(recs) == 12
    assert recs[0]["referencia"] == "Ponto 1.2. §§ 5 a 8"
    assert not any(r["texto"].startswith("ª") for r in recs)
    assert recs[9]["referencia"] == (
        "Pontos 19.1.1 e 19.1.2. §§ 222, 223, 225 e 230 a 232."
    )
    assert recs[11]["texto"].startswith("Adotar medidas para corrigir")
    assert recs[11]["desde"] == "2024"  # "formula-se uma nova recomendação"
    assert recs[10]["desde"] == ""


def test_conta(p2025):
    values = {
        (v["caminho"], v["ano"]): v["valor"]
        for v in p2025[1]
        if v["quadro"] == tdc.CONTA
    }
    assert values[("Receita efetiva", 2025)] == 1672578005.62
    assert values[("Saldo global ou efetivo", 2025)] == -199287231.59
    assert values[("Saldo global ou efetivo", 2024)] == -120268254.74
    assert values[("Despesa não efetiva › Ativos financeiros", 2025)] == (
        4777492.69
    )
    assert values[("Receita não efetiva › Ativos financeiros", 2025)] == (
        5033452.65
    )
    assert len(values) == 44  # 22 rows x 2 years
    # 2025 says "Despesas com o pessoal", earlier pareceres "com pessoal"
    assert ("Despesa efetiva › Despesas com pessoal", 2025) in values


def test_indicadores(p2025, p2024):
    def ind(p):
        return {
            v["rubrica"]: v["valor"]
            for v in p[1]
            if v["quadro"] == tdc.INDICADORES
        }

    assert ind(p2025) == {
        "Dívida total": 3728.8,
        "Receita não registada na Conta": 613.0,
        "Despesa não registada na Conta": 528.0,
        "Transferências do Estado (princípio da solidariedade)": 206.0,
    }
    assert ind(p2024)["Despesa não registada na Conta"] == 354.9


def test_acompanhamento_links_to_previous_year(p2025, p2024):
    acomp = p2025[2]
    assert len(acomp) == 11
    assert acomp[0]["situacao"] == "Parcialmente implementada"
    assert acomp[0]["desde"] == "2016"
    rows = [dict(r) for r in p2024[0]] + [dict(r) for r in p2025[0]]
    tdc.apply_status(rows, 2025, acomp)
    tdc.fill_desde(rows)
    recs = {
        (r["conta"], r["numero"]): r
        for r in rows
        if r["tipo"] == "recomendação"
    }
    assert recs[(2024, 1)]["situacao"] == "Parcialmente implementada (2025)"
    assert recs[(2024, 5)]["situacao"] == "Implementada (2025)"
    assert recs[(2024, 8)]["situacao"] == "Não implementada (2025)"
    assert recs[(2024, 8)]["desde"] == "2013"
    # the latest parecer's recommendations have no status yet, but their
    # first year carries over
    assert recs[(2025, 4)]["situacao"] == ""
    assert recs[(2025, 4)]["desde"] == "2013"


def test_status_from_broken_words():
    text = (
        "I – Acompanhamento de recomendações \nRecomendações \n anteriormente"
        " \n formuladas\n1\n.ª \nApresentar o quadro plurianual. \nP\narcialm"
        "ente \nimplementada \nRecomendação formulada, pela primeira vez, no "
        "\nRelatório e Parecer sobre a Conta de 201\n 6\n, tendo sido "
        "reiterada.\n2.ª \nConferir coerência aos mapas. \nPrejudicada \nO "
        "mapa.\nII – Processo orçamental\n"
    )
    assert tdc.parse_acompanhamento(text) == [
        {
            "chave": tdc.key("Apresentar o quadro plurianual."),
            "situacao": "Parcialmente implementada",
            "desde": "2016",
        },
        {
            "chave": tdc.key("Conferir coerência aos mapas."),
            "situacao": "Prejudicada",
            "desde": "",
        },
    ]


def test_merge_values_prefers_later_parecer():
    a = {
        "quadro": tdc.CONTA,
        "caminho": "Receita total",
        "ano": 2024,
        "ordem": 1,
        "valor": 1.0,
        "parecer": "https://x/2024/p.pdf",
    }
    b = {**a, "valor": 2.0, "parecer": "https://x/2025/p.pdf"}
    assert [r["valor"] for r in tdc.merge_values([b], [a])] == [2.0]


def test_main(tmp_path, monkeypatch):
    def fake_get(url):
        if "detalhe.aspx?dset=2025" in url:
            return (
                b"<a href='/pt-pt/ProdutosTC/PareceresTribunalContas/"
                b"pareceres-craa/Documents/2025/p.pdf'>Parecer sobre a Conta"
                b"</a>"
            )
        if "detalhe.aspx" in url:
            return b"<html></html>"
        return b"%PDF fake"

    monkeypatch.setattr(tdc, "get", fake_get)
    monkeypatch.setattr(tdc, "PAUSE", 0)
    monkeypatch.setattr(tdc, "FIRST", 2025)
    monkeypatch.setattr(tdc, "pdf_pages", lambda data: pages(2025))

    class Today(dt.date):
        @classmethod
        def today(cls):
            return cls(2026, 12, 1)

    monkeypatch.setattr(tdc.dt, "date", Today)
    assert tdc.main(tmp_path) == 0
    with open(tmp_path / "tdc.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["tipo"] == "juízo"
    assert rows[0]["parecer"].endswith("/2025/p.pdf")
    assert (tmp_path / "tdc_valores.csv").exists()

    # two years on, no parecer on the 2026 account: fail loudly
    class Later(dt.date):
        @classmethod
        def today(cls):
            return cls(2028, 2, 1)

    monkeypatch.setattr(tdc.dt, "date", Later)
    assert tdc.main(tmp_path) == 1


def test_main_blocked(tmp_path, monkeypatch):
    def blocked(url):
        raise tdc.Blocked("403 (challenge)")

    monkeypatch.setattr(tdc, "get", blocked)
    assert tdc.main(tmp_path) == 1


def test_datasets_includes_tdc(tmp_path):
    docs = tmp_path / "docs"
    for coll in ("_base_updates", "_alra_updates", "_joraa_updates"):
        (docs / coll).mkdir(parents=True)
    data = tmp_path / "data"
    data.mkdir()
    rows, values, _ = tdc.parecer_rows(pages(2025), 2025, DOCS)
    tdc.write_csv(data / "tdc.csv", rows, tdc.COLS)
    tdc.write_csv(data / "tdc_valores.csv", values, tdc.VCOLS)
    meta = datasets.main(docs)
    assert meta["tdc"]["linhas"] == len(rows)
    assert meta["tdc_valores"]["linhas"] == len(values)
    con = sqlite3.connect(docs / "dados" / "financas.db")
    hits = con.execute(
        "SELECT count(*) FROM tdc_fts WHERE tdc_fts MATCH 'solidariedade'"
    ).fetchone()[0]
    assert hits > 0
    assert con.execute(
        "SELECT valor FROM tdc_valores WHERE rubrica = 'Dívida total'"
    ).fetchone()[0] == pytest.approx(3728.8)
