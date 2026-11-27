import csv
import datetime as dt
import os
import sqlite3

import pytest

from bot import beo, datasets

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def pages(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        return f.read().split("\f")


@pytest.fixture(scope="module")
def setembro():
    return beo.boletim_rows(
        pages("beo_2026_09.txt"), 2026, 9, beo.pdf_url(2026, 9)
    )


def value(rows, quadro, rubrica, dimensao="", medida=beo.EUR, ano=2026):
    found = [
        r["valor"]
        for r in rows
        if r["quadro"] == quadro
        and r["rubrica"] == rubrica
        and r["dimensao"] == dimensao
        and r["medida"] == medida
        and r["ano"] == ano
    ]
    assert len(found) == 1, (quadro, rubrica, dimensao, found)
    return found[0]


def test_pdf_url():
    assert beo.pdf_url(2026, 3) == (
        "https://portal.azores.gov.pt/documents/36626/21646330/"
        "BEO_2026_03_Mar%C3%A7o+2026.pdf"
    )
    assert beo.pdf_url(2025, 11).endswith("BEO_2025_11_Novembro+05.pdf")
    assert beo.pdf_url(1999, 1) is None


def test_expected_months():
    months = beo.expected_months(dt.date(2024, 3, 15))
    assert months == [(2024, 1), (2024, 2)]


def test_split_line():
    label, nums = beo.split_line(
        "     Rendimentos de Propriedade 2 853 000,95 51 244,37 "
        "17 489,37 2 921 734,69"
    )
    assert label.strip() == "Rendimentos de Propriedade"
    assert [beo.number(n) for n in nums] == [
        2853000.95,
        51244.37,
        17489.37,
        2921734.69,
    ]
    assert beo.split_line(
        "SALDO GLOBAL -231 715 974,63 17 199 012,27 " "107,42%"
    )[1] == [
        "-231 715 974,63",
        "17 199 012,27",
        "107,42%",
    ]
    assert (
        beo.split_line("A receita fiscal situou-se nos 733,2 milhões") is None
    )


def test_tidy_and_key():
    assert beo.tidy("RECEITA CORRENTE") == "Receita corrente"
    assert beo.tidy("IMP.S/REND.PESS.SINGULARES (IRS)") == (
        "Imp.s/rend.pess.singulares (IRS)"
    )
    assert beo.tidy("Administração Central - Estado") == (
        "Administração central - Estado"
    )
    assert beo.tidy("076 SAÚDE N.E.") == "Saúde n.e."
    # the same rubrica, worded differently over the years
    assert beo.key("IMP.S/REND.PESS.SINGULARES (IRS)") == beo.key(
        "Imp.s/rend.pessoas singulares (IRS)"
    )
    assert beo.key("IMPOSTOS RODOVIARIOS") == beo.key("Imposto rodoviários")
    assert beo.key("Des pes as  com Pes s oal") == beo.key(
        "Despesas com Pessoal"
    )
    assert beo.key("076 SAÚDE N.E.") == "076"


def test_sintese_global(setembro):
    q = "Síntese global"
    assert value(setembro, q, "Saldo global", "Consolidado") == 33230146.17
    assert value(setembro, q, "Receita efetiva", "Governo Regional (GRA)") == (
        1405479291.98
    )
    irs = [
        r for r in setembro if r["quadro"] == q and "(IRS)" in r["rubrica"]
    ][0]
    assert irs["caminho"].startswith("Receita corrente › Impostos diretos › ")
    assert irs["nivel"] == 2


def test_execucao_and_previous_year(setembro):
    q = "Receita fiscal do GRA"
    assert value(setembro, q, "Receita fiscal") == 733241918.64
    assert value(setembro, q, "Receita fiscal", medida=beo.EXEC) == 75.90
    # the previous-year column is only kept before the first boletim
    assert not [r for r in setembro if r["ano"] == 2025]
    rows_2024 = beo.boletim_rows(
        pages("beo_2026_09.txt"), 2024, 9, "x"
    )  # pretend it is the 2024 boletim: its previous year is 2023
    assert [r for r in rows_2024 if r["ano"] == 2023]


def test_funcao_and_departamento(setembro):
    assert (
        value(setembro, "Despesa do GRA por função", "Saúde n.e.")
        == 431234369.79
    )
    assert (
        value(
            setembro,
            "Despesa do GRA por departamento",
            "Despesa efetiva",
            "Saúde e Segurança Social",
        )
        == 462100486.69
    )


def test_departments_from_spelled_out_header():
    rows = beo.parse(pages("beo_2024_12_quadro_vii.txt"), 2024)
    depts = [r["dimensao"] for r in rows if r["rubrica"] == "Despesa corrente"]
    assert depts[0] == "Assembleia Legislativa"
    assert "Saúde e Segurança Social" in depts
    assert depts[-1] == "Total"
    assert len(depts) == 13


def test_finish_uses_latest_labels():
    old = {
        "quadro": "Receita fiscal do GRA",
        "ordem": 3,
        "nivel": 2,
        "chave": beo.key("IMPOSTOS RODOVIARIOS"),
        "rubrica": "Impostos rodoviarios",
        "caminho": "Impostos indiretos › Impostos rodoviarios",
        "dimensao": "",
        "medida": beo.EUR,
        "ano": 2024,
        "mes": 1,
        "data": "2024-01-01",
        "valor": 1.0,
        "boletim": "a",
    }
    new = {
        **old,
        "ordem": 4,
        "rubrica": "Imposto rodoviários",
        "caminho": "Impostos indiretos › Imposto rodoviários",
        "ano": 2026,
        "data": "2026-01-01",
    }
    out = beo.finish([new, old])
    assert [r["data"] for r in out] == ["2024-01-01", "2026-01-01"]
    assert {r["rubrica"] for r in out} == {"Imposto rodoviários"}
    assert {r["ordem"] for r in out} == {4}


def test_main_adds_new_months_and_fails_when_stale(tmp_path, monkeypatch):
    text = pages("beo_2026_09.txt")
    monkeypatch.setattr(beo, "FIRST", (2026, 8))
    monkeypatch.setattr(
        beo, "download", lambda url: b"%PDF" if "_09_" in url else None
    )
    monkeypatch.setattr(beo, "pdf_pages", lambda data: text)

    class Today(dt.date):
        @classmethod
        def today(cls):
            return cls(2026, 10, 20)

    monkeypatch.setattr(beo.dt, "date", Today)
    assert beo.main(tmp_path) == 0
    with open(tmp_path / "beo.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert {r["mes"] for r in rows} == {"9"}
    assert rows[0]["boletim"].endswith("BEO_2026_09_Setembro+2026.pdf")

    # months later, nothing new: the workflow must fail loudly
    class Later(dt.date):
        @classmethod
        def today(cls):
            return cls(2027, 3, 1)

    monkeypatch.setattr(beo.dt, "date", Later)
    assert beo.main(tmp_path) == 1


def test_datasets_includes_beo(tmp_path):
    docs = tmp_path / "docs"
    for coll in ("_base_updates", "_alra_updates", "_joraa_updates"):
        (docs / coll).mkdir(parents=True)
    data = tmp_path / "data"
    data.mkdir()
    rows = beo.finish(beo.boletim_rows(pages("beo_2026_09.txt"), 2026, 9, "u"))
    beo.write_csv(data / "beo.csv", rows)
    meta = datasets.main(docs)
    assert meta["beo"]["linhas"] == len(rows)
    assert meta["beo"]["ultimo"]["periodo"] == "setembro de 2026"
    assert (docs / "_data" / "beo_ultimo.json").exists()
    con = sqlite3.connect(docs / "dados" / "financas.db")
    hits = con.execute(
        "SELECT count(*) FROM beo_fts WHERE beo_fts MATCH 'saude'"
    ).fetchone()[0]
    assert hits > 0


def _http_error(code, headers):
    import email.message
    import urllib.error

    msg = email.message.Message()
    for k, v in headers.items():
        msg[k] = v
    return urllib.error.HTTPError("u", code, "Forbidden", msg, None)


def test_download_blocked_fails_loudly(monkeypatch, tmp_path):
    def challenge(req, timeout):
        raise _http_error(403, {"cf-mitigated": "challenge"})

    monkeypatch.setattr(beo.urllib.request, "urlopen", challenge)
    with pytest.raises(beo.Blocked, match="challenge"):
        beo.download("https://example.com/x.pdf")

    def not_found(req, timeout):
        raise _http_error(404, {})

    monkeypatch.setattr(beo.urllib.request, "urlopen", not_found)
    assert beo.download("https://example.com/x.pdf") is None

    # and main() stops with an error instead of "not published yet"
    def blocked(url):
        raise beo.Blocked("403")

    monkeypatch.setattr(beo, "download", blocked)
    monkeypatch.setattr(beo, "FIRST", (2026, 8))
    assert beo.main(tmp_path) == 1
