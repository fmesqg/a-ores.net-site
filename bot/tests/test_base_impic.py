import csv
import gzip
import io
import json
import zipfile

import pytest

from bot import base_impic


def contrato(**kw):
    r = {
        "idcontrato": "11758845",
        "tipoContrato": ["Aquisição de bens móveis"],
        "tipoprocedimento": "Ajuste Direto Regime Geral",
        "objectoContrato": "Fornecimento de fuelóleo &amp; afins",
        "adjudicante": [
            {
                "nifEntContrato": "512001306",
                "descEntContrato": "EDA - Electricidade dos Açores, SA",
                "NUTsCod": "PT200",
            }
        ],
        "adjudicatarios": [
            {"nifEntContrato": "512002850", "descEntContrato": "BENCOM, S.A."}
        ],
        "dataPublicacao": "2025-10-01",
        "dataCelebracaoContrato": "2025-09-30",
        "precoContratual": 64500000.0,
        "precoBaseProcedimento": 64500000.0,
        "PrecoTotalEfetivo": None,
        "CPV": [
            {"cpvID": "09135000-4", "cpvdescricao": "Fuelóleos"},
            {
                "cpvID": "09134100-8",
                "cpvdescricao": "Gasóleo",
                "CPVObjeto": "Principal",
            },
        ],
        "localExecucao": [
            "Portugal, Região Autónoma dos Açores, Horta",
            "Portugal, Região Autónoma dos Açores, Horta",
            "Portugal, Região Autónoma dos Açores",
        ],
        "concorrentes": ["512002850-BENCOM"],
        "Lotes": [{"NumPropostas": 1}, {"NumPropostas": 2}],
        "fundamentacao": "Artigo 24.º, n.º 1, alínea a)",
        "DescrAcordoQuadro": "",
        "numAcordoQuadro": "",
    }
    r.update(kw)
    return r


def test_row_and_filter():
    r = contrato()
    assert base_impic.in_azores(r)
    assert not base_impic.in_azores(
        contrato(localExecucao=["Portugal, Lisboa, Lisboa"])
    )
    assert not base_impic.in_azores(contrato(localExecucao=None))
    got = dict(zip(base_impic.COLS, base_impic.row(r), strict=True))
    assert got["id"] == 11758845
    assert got["objeto"] == "Fornecimento de fuelóleo & afins"
    assert got["adjudicatario_nif"] == "512002850"
    assert got["cpv"] == "09134100-8 Gasóleo"  # the "Principal" one
    assert got["local"] == "Horta; Açores"  # deduplicated, prefix dropped
    assert got["concorrentes"] == 1 and got["propostas"] == 2
    assert got["preco_efetivo"] == ""


def test_zips_and_years():
    ds = {
        "resources": [
            {"title": "contratos2026.xlsx", "url": "https://x/a.xlsx"},
            {"title": "contratos2025.zip", "url": "https://x/c2025.zip"},
            {"title": "x", "url": "https://x/r/contratos2012.zip"},
        ]
    }
    assert base_impic.zips(ds) == {
        2025: "https://x/c2025.zip",
        2012: "https://x/r/contratos2012.zip",
    }
    assert list(base_impic.anos("2012-2014")) == [2012, 2013, 2014]
    assert list(base_impic.anos("2020")) == [2020]


def test_main_writes_one_file_per_year(tmp_path, monkeypatch):
    pytest.importorskip("ijson")

    def zipped(items):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("Contratos.json", json.dumps(items))
        return buf.getvalue()

    files = {
        2024: [
            contrato(idcontrato="1", dataPublicacao="2024-12-30"),
            contrato(idcontrato="9", localExecucao=["Portugal, Porto, Porto"]),
        ],
        # the 2025 file holds a newer version of contract 1
        2025: [
            contrato(idcontrato="1", dataPublicacao="2025-01-02"),
            contrato(idcontrato="2", dataPublicacao="2025-10-01"),
        ],
    }
    cache = tmp_path / "cache"
    cache.mkdir()
    for y, items in files.items():
        (cache / f"contratos{y}.zip").write_bytes(zipped(items))
    ds = {
        "resources": [
            {"title": f"contratos{y}.zip", "url": f"https://x/{y}.zip"}
            for y in files
        ]
    }
    monkeypatch.setattr(base_impic, "get", lambda url: json.dumps(ds).encode())
    out = tmp_path / "data"
    (out / "base_impic").mkdir(parents=True)
    (out / "base_impic" / "2019.csv.gz").write_bytes(b"stale")
    assert (
        base_impic.main(
            out, cache, today=__import__("datetime").date(2025, 11, 1)
        )
        == 0
    )
    names = sorted(p.name for p in (out / "base_impic").iterdir())
    assert names == ["2025.csv.gz"]
    with gzip.open(out / "base_impic" / "2025.csv.gz", "rt") as f:
        rows = list(csv.DictReader(f))
    assert [r["id"] for r in rows] == ["2", "1"]
    # too old: fails
    assert (
        base_impic.main(
            out, cache, today=__import__("datetime").date(2026, 6, 1)
        )
        == 1
    )
