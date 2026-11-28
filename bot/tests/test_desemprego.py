import csv

import pytest

from bot import desemprego
from bot.dados import emprego

CONCELHOS = [
    ("VILA DO PORTO", 37, 52),
    ("LAGOA", 138, 168),
    ("NORDESTE", 56, 112),
    ("PONTA DELGADA", 619, 569),
    ("POVOAÇÃO", 135, 155),
    ("RIBEIRA GRANDE", 262, 473),
    ("VILA FRANCA DO CAMPO", 79, 128),
    ("ANGRA DO HEROÍSMO", 173, 195),
    ("PRAIA DA VITÓRIA", 104, 130),
    ("SANTA CRUZ DA GRACIOSA", 22, 24),
    ("CALHETA", 43, 64),
    ("VELAS", 37, 52),
    ("LAJES DO PICO", 53, 42),
    ("MADALENA", 36, 21),
    ("SÃO ROQUE DO PICO", 27, 39),
    ("HORTA", 42, 49),
    ("LAJES DAS FLORES", 5, 10),
    ("SANTA CRUZ DAS FLORES", 7, 8),
    ("VILA DO CORVO", 4, 2),
]
ILHAS = [
    ("SANTA MARIA", 37, 52),
    ("SÃO MIGUEL", 1289, 1605),
    ("TERCEIRA", 277, 325),
    ("GRACIOSA", 22, 24),
    ("SÃO JORGE", 80, 116),
    ("PICO", 116, 102),
    ("FAIAL", 42, 49),
    ("FLORES", 12, 18),
    ("CORVO", 4, 2),
]


def _n(x: int) -> str:
    return f"{x:,}".replace(",", ".")


def _linhas(rows):
    out = []
    for nome, h, m in rows:
        out.append(f"{nome} {_n(h)} {_n(m)} {_n(h + m)} 1,00% ")
    h = sum(r[1] for r in rows)
    m = sum(r[2] for r in rows)
    out.append(f"TOTAL {_n(h)} {_n(m)} {_n(h + m)} 100,00% ")
    return out


HEAD = [
    "DIREÇÃO REGIONAL DE QUALIFICAÇÃO PROFISSIONAL E EMPREGO ",
    "RESUMO - DESEMPREGO REGISTADO NOS AÇORES ",
    "MARÇO DE 2026 ",
]


def _texto(ilhas=ILHAS, concelhos=CONCELHOS):
    """The text pypdf gives for a summary, with the concelhos table broken
    over two pages as in the real PDFs."""
    c = _linhas(concelhos)
    return "\n".join(
        HEAD
        + [
            "Na ilha de São Miguel residiam 69,37% dos desempregados.",
            "ILHAS ",
        ]
        + ["DESEMPREGO REGISTADO PESO ", "RELATIVO HOMENS MULHERES TOTAL "]
        + _linhas(ilhas)
        + ["Em março de 2026, o desemprego por concelhos.", "CONCELHOS "]
        + ["RELATIVO HOMENS MULHERES TOTAL "]
        + c[:14]
        + [" ", "2 ", " "]
        + HEAD
        + ["CONCELHOS ", "RELATIVO HOMENS MULHERES TOTAL "]
        + c[14:]
        + ["MEDIDAS PARA A EMPREGABILIDADE ", "N.º DE PARTICIPANTES "]
        + ["HOMENS MULHERES TOTAL "]
        + ["INSERÇÃO SOCIOPROFISSIONAL 725 742 1.467 "]
        + ["ESTÁGIO 720 899 1.619 ", "FORMAÇÃO 132 195 327 "]
        + ["registaram entrada de 165 ofertas de emprego ao longo do "]
        + ["mês de março, nelas estando envolvidos 19 postos.", "ILHAS "]
        + ["COLOCAÇÕES PESO "]
        + ["SANTA MARIA 2 4 6 4,11% ", "SÃO MIGUEL 39 26 65 44,52% "]
        + ["TERCEIRA 17 16 33 22,60% ", "GRACIOSA 2 2 4 2,74% "]
        + ["SÃO JORGE 1 0 1 0,68% ", "PICO 10 12 22 15,07% "]
        + ["FAIAL 2 11 13 8,90% ", "FLORES 2 - 2 1,37% ", "CORVO - - - - "]
        + ["TOTAL 75 71 146 100,00% "]
    )


def test_parse():
    rows = desemprego.parse(_texto(), "x.pdf")
    r = {(x[1], x[2], x[4]): x for x in rows}
    assert {x[0] for x in rows} == {"2026-03"}
    assert r[("desemprego", "regiao", "Açores")][5:8] == [1879, 2293, 4172]
    pd = r[("desemprego", "concelho", "Ponta Delgada")]
    assert pd[3] == "2004203" and pd[7] == 1188
    assert r[("desemprego", "concelho", "Corvo")][3] == "2004901"
    assert len([x for x in rows if x[2] == "concelho"]) == 19
    assert r[("medidas", "medida", "Estágio")][7] == 1619
    assert r[("colocacoes", "ilha", "Corvo")][5:8] == [0, 0, 0]
    assert r[("colocacoes", "regiao", "Açores")][7] == 146
    assert r[("ofertas", "regiao", "Açores")][7] == 165


def test_parse_checks_the_sums():
    bad = [("PONTA DELGADA", 600, 569)] + CONCELHOS[:3] + CONCELHOS[4:]
    with pytest.raises(desemprego.Erro, match="soma dos concelhos"):
        desemprego.parse(_texto(concelhos=bad), "x.pdf")
    texto = _texto().replace("LAGOA 138 168 306", "LAGOA 138 168 307")
    with pytest.raises(desemprego.Erro, match="138 \\+ 168"):
        desemprego.parse(texto, "x.pdf")


def test_parse_islands_come_from_the_concelhos(capsys):
    # the island table mixes up Graciosa and São Jorge, as in March 2026,
    # and still adds up to the region
    trocas = {"GRACIOSA": (65, 88), "SÃO JORGE": (37, 52)}
    ilhas = [(n, *trocas.get(n, (h, m))) for n, h, m in ILHAS]
    rows = desemprego.parse(_texto(ilhas=ilhas), "x.pdf")
    r = {(x[2], x[4]): x for x in rows if x[1] == "desemprego"}
    assert r[("ilha", "Graciosa")][5:8] == [22, 24, 46]
    assert r[("ilha", "São Jorge")][5:8] == [80, 116, 196]
    out = capsys.readouterr().out
    assert "Graciosa: quadro das ilhas 153, concelhos 46" in out


def test_numeros_with_space_thousands():
    # 2022 summaries write thousands with a space
    assert desemprego.numeros("1 799 2 222 4 021 69,1%") == (1799, 2222, 4021)
    assert desemprego.numeros("12 1 234 1 246 3%") == (12, 1234, 1246)
    assert desemprego.numeros("1.289 1.605 2.894 69,37%") == (1289, 1605, 2894)
    assert desemprego.numeros("2 - 2 1,37%") == (2, 0, 2)
    assert desemprego.numeros("- - - -") == (0, 0, 0)
    assert desemprego.numeros("2026, O DESEMPREGO") is None


def test_candidatos():
    c = desemprego.candidatos("2026-12")
    assert c[0] == (
        desemprego.UPLOADS
        + "2027/01/02_DESEMPREGO_REGISTADO_DEZEMBRO_2026.pdf"
    )
    assert (
        desemprego.UPLOADS + "2027/01/02_DESEMPREGO_REGISTADO_12_2026.pdf" in c
    )
    assert len(c) == len(set(c))


def test_main_reads_known_then_guesses(tmp_path, monkeypatch):
    monkeypatch.setattr(
        desemprego, "CONHECIDOS", {"2026-03": desemprego.UPLOADS + "a/m.pdf"}
    )
    abril = desemprego.candidatos("2026-04")[2]
    pedidos = []

    def fake_get(url):
        pedidos.append(url)
        return url.encode() if url.endswith(("m.pdf", abril)) else None

    def fake_text(blob):
        t = _texto()
        return (
            t.replace("MARÇO DE", "ABRIL DE")
            if blob.endswith(abril.encode())
            else t
        )

    class Hoje(desemprego.date):
        @classmethod
        def today(cls):
            return cls(2026, 6, 10)

    monkeypatch.setattr(desemprego, "get", fake_get)
    monkeypatch.setattr(desemprego, "pdf_text", fake_text)
    monkeypatch.setattr(desemprego, "date", Hoje)
    assert desemprego.main(tmp_path) == 0
    # March known, April on its third guess, May not found
    assert pedidos[:4] == [desemprego.UPLOADS + "a/m.pdf"] + (
        desemprego.candidatos("2026-04")[:3]
    )
    assert pedidos[4:] == desemprego.candidatos("2026-05")
    with (tmp_path / "desemprego.csv").open() as f:
        assert {r["periodo"] for r in csv.DictReader(f)} == {
            "2026-03",
            "2026-04",
        }
    # the known file is not downloaded again
    pedidos.clear()
    desemprego.main(tmp_path)
    assert pedidos == desemprego.candidatos("2026-05")


def test_desemprego_data():
    rows = desemprego.parse(_texto(), "x.pdf")
    antes = desemprego.parse(
        _texto().replace("MARÇO DE 2026", "MARÇO DE 2025"), "y.pdf"
    )
    tables = {
        "desemprego": (
            desemprego.COLS,
            [list(map(str, r)) for r in antes + rows],
        ),
        "ine": (
            ["varcd", "geocod", "periodo", "categoria", "valor"],
            [
                ["0012918", "2004203", "2024", "", "60000"],
                ["0012918", "2004203", "2025", "", "59400"],
                ["0012918", "20", "2025", "", "240000"],
            ],
        ),
    }
    d = emprego.desemprego_data(tables)
    assert d["periodo"] == "2026-03" and d["mes"] == "março de 2026"
    assert d["regiao"]["total"] == 4172
    assert d["regiao"]["homologa"] == "+0,0 %"
    pd = next(c for c in d["concelhos"] if c["nome"] == "Ponta Delgada")
    assert pd["por_mil"] == 20.0 and pd["ilha"] == "São Miguel"
    assert d["concelhos"][0]["nome"] == "Ponta Delgada"  # only one with pop
    assert d["grelha"][0]["ano"] == "2026"
    assert d["grelha"][0]["meses"][2] == "4\u00a0172"
