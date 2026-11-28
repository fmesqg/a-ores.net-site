import csv

from bot import exames
from bot.dados import educacao


def _escolas():
    return [
        # two Azorean schools, one in Madeira, two on the mainland
        {"Escola": "1502", "Descr": "Escola Secundária Antero de Quental",
         "Distrito": "19", "Concelho": "23", "PubPriv": "PUB"},
        {"Escola": "2927", "Descr": "Colégio do Castanheiro ",
         "Distrito": "19", "Concelho": "23", "PubPriv": "PRI"},
        {"Escola": "5000", "Descr": "Funchal", "Distrito": "22",
         "Concelho": "03", "PubPriv": "PUB"},
        {"Escola": "0002", "Descr": "Sesimbra", "Distrito": "15",
         "Concelho": "11", "PubPriv": "PUB"},
        {"Escola": "0099", "Descr": "Lá fora", "Distrito": "99",
         "Concelho": "01", "PubPriv": "PRI"},
    ]  # fmt: skip


def _enes(rows):
    """rows: (school, exam, grade, cif, phase, internal, for approval)"""
    keys = ["Escola", "Exame", "Class_Exam", "CIF", "Fase", "Interno",
            "ParaAprov"]  # fmt: skip
    return {
        "tblEscolas": _escolas(),
        "tblExames": [
            {"Exame": "639", "Descr": "Português"},
            {"Exame": "635", "Descr": "Matemática A"},
        ],
        "tblHomologa_2025": [
            dict(zip(keys, map(str, r), strict=True)) for r in rows
        ],
    }


def test_links():
    html = (
        "<a href='docs/2025/enes2025_ComunicacaoSocial_v2.zip'>"
        "<a href='docs/2024/eneb2024_ComunicacaoSocial.zip'>"
        "<a href='docs/2025/InfoEscolas2025_3Ciclo_DadosPorEscola.xlsx'>"
    )
    assert exames.links(html) == {
        (2025, "secundario"): "docs/2025/enes2025_ComunicacaoSocial_v2.zip",
        (2024, "basico"): "docs/2024/eneb2024_ComunicacaoSocial.zip",
    }


def test_resumo_counts_only_internal_first_phase_for_approval(monkeypatch):
    monkeypatch.setattr(exames, "MIN_PROVAS", 2)
    tables = _enes(
        [
            ("1502", "639", 120, 14, 1, "S", "S"),
            ("1502", "639", 100, 12, 1, "S", "S"),
            ("1502", "635", 80, 13, 1, "S", "S"),
            ("1502", "639", 200, 20, 2, "S", "S"),  # 2nd phase: out
            ("1502", "639", 200, 20, 1, "N", "S"),  # external: out
            ("1502", "639", 200, 20, 1, "S", "N"),  # not for approval: out
            ("2927", "639", 150, 16, 1, "S", "S"),  # 1 exam: no rank
            ("5000", "639", 140, 15, 1, "S", "S"),
            ("5000", "635", 130, 15, 1, "S", "S"),
            ("0002", "639", 90, 11, 1, "S", "S"),
            ("0002", "639", 94, 11, 1, "S", "S"),
            ("0099", "639", 10, 10, 1, "S", "S"),  # abroad: not in PT
        ]
    )
    rows = exames.resumo(2025, "secundario", tables, "f.zip")
    r = {(x[3], x[8]): dict(zip(exames.COLS, x, strict=True)) for x in rows}
    aq = r[("1502", "todos")]
    assert aq["provas"] == 3 and aq["media"] == 100.0
    assert aq["media_interna"] == 13.0
    assert aq["positivas"] == round(100 * 2 / 3, 1)  # 120 and 100 >= 95
    assert aq["geocod"] == "2004203" and aq["concelho"] == "Ponta Delgada"
    # Funchal 135 > Antero 100 > Sesimbra 92: 2nd of 3 ranked
    assert (aq["posicao"], aq["n_escolas"]) == (2, 3)
    assert r[("2927", "todos")]["posicao"] == ""
    assert r[("2927", "todos")]["nome"] == "Colégio do Castanheiro"
    assert ("5000", "todos") not in r  # only Azorean schools are kept
    assert r[("AZ", "639")]["provas"] == 3
    assert r[("PT", "todos")]["provas"] == 8  # abroad left out
    assert r[("MD", "635")]["media"] == 130.0
    assert r[("CO", "todos")]["nome"] == "Continente"


def test_resumo_basico_uses_school_of_origin():
    keys = ["EscolaInsc", "EscolaOrigem", "Prova", "Fase", "TipoAluno",
            "FreqNivel", "ExamNivel", "ExamPontos"]  # fmt: skip
    hom = [
        ("0002", "1502", "91", "1", "I", "3", "3", "60"),
        ("1502", "1502", "92", "1", "I", "2", "2", "40"),
        ("1502", "1502", "82", "1", "I", "2", "2", "40"),  # other test
        ("1502", "1502", "92", "1", "4", "2", "2", "40"),  # self-proposed
    ]
    tables = {
        "tblEscolas": _escolas(),
        "tblHomologa_2025": [dict(zip(keys, r, strict=True)) for r in hom],
    }
    rows = exames.resumo(2025, "basico", tables, "b.zip")
    r = {(x[3], x[8]): dict(zip(exames.COLS, x, strict=True)) for x in rows}
    assert r[("1502", "todos")]["provas"] == 2
    assert r[("1502", "todos")]["media"] == 50.0
    assert r[("1502", "todos")]["positivas"] == 50.0
    assert r[("1502", "92")]["exame_nome"] == "Matemática"


def test_main_skips_known_file_and_keeps_old_years(tmp_path, monkeypatch):
    old = [exames.COLS, ["2022", "basico", "regiao", "AZ", "Açores", "20",
                         "", "", "todos", "x", "10", "50", "3", "50", "",
                         "", "eneb2022.zip"]]  # fmt: skip
    with (tmp_path / "exames.csv").open("w", newline="") as f:
        csv.writer(f).writerows(old)
    page = (
        b"docs/2023/enes2023_ComunicacaoSocial_24.zip "
        b"docs/2025/enes2025_ComunicacaoSocial_v2.zip"
    )
    fetched = []

    def fake_get(url):
        fetched.append(url)
        return page if url == exames.PAGE else b"zip"

    monkeypatch.setattr(exames, "get", fake_get)
    monkeypatch.setattr(exames, "MIN_ESCOLAS", {"secundario": 1})
    monkeypatch.setattr(
        exames,
        "read_zip",
        lambda blob, tmp: _enes([("1502", "639", 120, 14, 1, "S", "S")]),
    )
    assert exames.main(tmp_path) == 0
    assert not any("enes2023" in u for u in fetched)
    with (tmp_path / "exames.csv").open() as f:
        anos = {r["ano"] for r in csv.DictReader(f)}
    assert anos == {"2022", "2025"}
    # same file name again: nothing downloaded
    fetched.clear()
    assert exames.main(tmp_path) == 0
    assert fetched == [exames.PAGE]


def test_exames_data():
    tables = _enes(
        [
            ("1502", "639", 120, 14, 1, "S", "S"),
            ("0002", "639", 100, 12, 1, "S", "S"),
        ]
    )
    rows = exames.resumo(2025, "secundario", tables, "f.zip")
    out = educacao.exames_data(
        exames.COLS, [[str(v) for v in r] for r in rows]
    )
    (n,) = out["niveis"]
    assert n["ano"] == 2025
    assert n["media_az"] == "120,0" and n["media_pt"] == "110,0"
    (todos,) = n["linhas"]  # Português has fewer than 100 Azorean exams
    assert todos["dif"] == "+10,0"
    (e,) = n["escolas"]
    assert e["principais"] == ["120,0", ""]  # Português, no Matemática A
