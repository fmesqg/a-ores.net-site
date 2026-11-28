import pytest

from bot import anuario

QUADRO = """Quadro 2.6 – Grau de execução da receita cobrada em 2025 ... 47
texto
Quadro 2.6 - Grau de execução da receita cobrada em 2025 pelos Municípios da Região Autónoma dos Açores
Município
Dim.
Mandato 22-25
2024 2025
{linhas}
Grau execução Receita - Açores 90,9% 91,0%
"""
R66 = """R66 - Diferença entre a execução da receita liquidada e a execução dos compromissos nos municípios dos Açores
Município
Dim.
2023 2024 2025
Execução
{linhas}
Média dos municípios da R.A.A. 93,4% 88,2% 5,3%
"""


def _texto():
    nomes = [k.title() for k in anuario.MUNICIPIOS]
    nomes[nomes.index("Lagoa (São Miguel)")] = "Lagoa (R.A.A.)"
    q = "\n".join(
        f"{i + 1} {n} P 9{i % 10},0% 10{i % 10},5%"
        for i, n in enumerate(nomes)
    )
    r = "\n".join(
        f"{i + 1} {n} P 90,0% 80,0% 10,0% 91,0% 81,0% 10,0% 92,0% 82,0% 10,0%"
        for i, n in enumerate(nomes)
    )
    return QUADRO.format(linhas=q) + R66.format(linhas=r)


def test_parse():
    rows = anuario.parse(_texto())
    assert len(rows) == 19 * 3  # 2023 (R66 only), 2024, 2025
    pd = [r for r in rows if r["geocod"] == "2004203"]
    assert [r["ano"] for r in pd] == [2023, 2024, 2025]
    r25 = pd[-1]
    assert (r25["receita_liquidada"], r25["despesa_comprometida"]) == (
        92.0,
        82.0,
    )
    assert r25["receita_cobrada"] == 103.5
    assert pd[0]["receita_cobrada"] == ""
    lagoa = [r for r in rows if r["geocod"] == "2004201"]
    assert lagoa


def test_missing_camara_fails():
    texto = _texto().replace("\n19 ", "\nxx ", 1)
    with pytest.raises(ValueError):
        anuario.parse(texto)


def test_merge_newer_wins():
    old = [
        {"ano": "2015", "geocod": "1"},
        {"ano": "2024", "geocod": "1", "x": "old"},
    ]
    new = [{"ano": 2024, "geocod": "1", "x": "new"}]
    got = anuario.merge(old, new)
    assert [r.get("x") for r in got] == [None, "new"]
