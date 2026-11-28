import csv
import zipfile

from bot import ifap
from bot.dados import fundos

HEADER = (
    "EXERCICIO;DENOMINACAO;NOME_GRUPO_EMPRESAS;NIF_GRUPO_EMPRESAS;DISTRITO;"
    "DESCRICAO_DISTRITO;CONCELHO;DESCRICAO_CONCELHO;CODIGO_POSTAL;MEDIDA;"
    "MONTANTE_FEAGA;MONTANTE_FEADER;MONTANTE_COFINANCIADO;"
    "MONTANTE_FEADER_COFINANCIADO;MONTANTE"
)
LINES = [
    # an Azorean farm with two measures and its Total row
    '"2025";"  JOSÉ   DA SILVA";;;"42";"ILHA DE SAO MIGUEL";"03";'
    '"PONTA DELGADA";"9500";"VII.1";1000.5;0;0;0;1000.5',
    '"2025";"  JOSÉ   DA SILVA";;;"42";"ILHA DE SAO MIGUEL";"03";'
    '"PONTA DELGADA";"9500";"V.2";0;850;150;1000;1000',
    '"2025";"  JOSÉ   DA SILVA";;;"42";"ILHA DE SAO MIGUEL";"03";'
    '"PONTA DELGADA";"9500";"Total";1000.5;850;150;1000;2000.5',
    # concelho without a leading zero nor a name (seen in the 2024 file)
    '"2025";"COOPERATIVA X";;;"45";"ILHA DE SAO JORGE";"2";"";"9800";'
    '"VII.1";500;0;0;0;500',
    # Madeira and the mainland are left out
    '"2025";"MADEIRENSE";;;"31";"ILHA DA MADEIRA";"03";"FUNCHAL";"9000";'
    '"VII.1";900;0;0;0;900',
    '"2025";"ALENTEJANO";;;"12";"PORTALEGRE";"07";"ELVAS";"7350";'
    '"I.1";100;0;0;0;100',
]


def _zip(tmp_path):
    path = tmp_path / "FEAGA_FEADER_2025.zip"
    text = "\r\n".join([HEADER, *LINES]) + "\r\n"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("FEAGA_FEADER_2025.csv", text.encode("latin-1"))
    return path


def test_azores_rows(tmp_path):
    rows = ifap.azores_rows(_zip(tmp_path))
    assert len(rows) == 3  # no Total, no Madeira, no mainland
    r = dict(zip(ifap.PAG_COLS, rows[0], strict=True))
    assert r["beneficiario"] == "JOSÉ DA SILVA"
    assert r["geocod"] == "2004203"
    assert r["concelho"] == "Ponta Delgada"
    assert r["ilha"] == "São Miguel"
    assert r["programa"] == "POSEI"
    assert r["montante"] == 1000.5
    v2 = dict(zip(ifap.PAG_COLS, rows[1], strict=True))
    assert (v2["feader"], v2["cofinanciado"], v2["montante"]) == (
        850,
        150,
        1000,
    )
    assert v2["programa"] == "Desenvolvimento rural"
    sj = dict(zip(ifap.PAG_COLS, rows[2], strict=True))
    assert (sj["geocod"], sj["concelho"]) == ("2004502", "Velas")


def test_programa():
    assert ifap.programa("VII.1") == "POSEI"
    assert ifap.programa("I.6") == "Pagamentos diretos"
    assert ifap.programa("IV.3") == "Mercados agrícolas"
    assert ifap.programa("VI.24") == "Desenvolvimento rural"
    assert ifap.programa("X.2") == "Desenvolvimento rural"
    assert ifap.programa("X.1") == "Outros"


def test_resumo_counts_beneficiaries_once_per_concelho_and_measure(tmp_path):
    rows = ifap.azores_rows(_zip(tmp_path))
    rows.append(list(rows[0]))
    rows[-1][1] = "MARIA"
    out = {(r[3], r[4]): r for r in ifap.resumo(rows)}
    posei_pd = out[("2004203", "VII.1")]
    assert posei_pd[7] == 2  # beneficiários
    assert posei_pd[-1] == 2001.0


def test_main_keeps_old_totals_and_only_published_names(tmp_path, monkeypatch):
    src = _zip(tmp_path)

    def fake_download(year, dest):
        if year != 2025:
            return False
        dest.write_bytes(src.read_bytes())
        return True

    monkeypatch.setattr(ifap, "download", fake_download)
    monkeypatch.setattr(ifap, "MIN_TOTAL", 0)
    data = tmp_path / "data"
    data.mkdir()
    old = [ifap.RES_COLS, ["2020", "Pico", "Madalena", "2004602", "VII.1",
                           "POSEI", "POSEI", "3", "10", "0", "0", "10"]]  # fmt: skip
    with (data / "ifap_resumo.csv").open("w", newline="") as f:
        csv.writer(f).writerows(old)
    assert ifap.main(data) == 0
    with (data / "ifap_resumo.csv").open() as f:
        anos = {r["exercicio"] for r in csv.DictReader(f)}
    assert anos == {"2020", "2025"}
    with (data / "ifap_pagamentos.csv").open() as f:
        assert {r["exercicio"] for r in csv.DictReader(f)} == {"2025"}


def test_main_fails_without_any_year(tmp_path, monkeypatch):
    monkeypatch.setattr(ifap, "download", lambda year, dest: False)
    assert ifap.main(tmp_path) == 1


def test_pac_data(tmp_path):
    rows = ifap.azores_rows(_zip(tmp_path))
    pag = (ifap.PAG_COLS, [[str(v) for v in r] for r in rows])
    res = (ifap.RES_COLS, [[str(v) for v in r] for r in ifap.resumo(rows)])
    ine_cols = ["varcd", "nivel", "categoria", "geocod", "periodo", "valor"]
    ine = (ine_cols, [["0012918", "Concelho", "", "2004203", "2024", "1000"]])
    out = fundos.fundos_data(
        {"ifap_resumo": res, "ifap_pagamentos": pag, "ine": ine}
    )["pac"]
    assert out["ultimo"] == "2025"
    assert out["beneficiarios"] == 2
    assert out["anos"][0]["posei"] == round(1500.5 / 1e6, 1)
    pd = next(c for c in out["concelhos"] if c["nome"] == "Ponta Delgada")
    assert pd["por_hab"] == 2  # 2000,5 € / 1000 inhabitants (2024)
    assert out["maiores"][0]["nome"] == "JOSÉ DA SILVA"
    assert out["maiores"][0]["posei"] == 1000  # rounded to the euro
