import csv
import datetime as dt
import io
import urllib.error

import pytest

from bot import bportugal as bp


def cube(values, next_page=None, as_list=False):
    """A JSON-stat page like BPstat's loans dataset: Rubrica (48) x
    Território de contraparte (59) x reference_date, two series per
    territory and one for the mainland region."""
    dims = {
        "48": {
            "label": "Rubrica",
            "category": {
                "index": {"1": 0, "2": 1},
                "label": {"1": "Empréstimos", "2": "Empréstimos vencidos"},
            },
        },
        "29": {
            "label": "Métrica",
            "category": {
                "index": ["9"],
                "label": {"9": "Valor em fim do período"},
            },
        },
        "59": {
            "label": "Território de contraparte",
            "category": {
                "index": ["20", "21", "30"],
                "label": {
                    "20": "Região Autónoma dos Açores (NUTS II)",
                    "21": "Região Autónoma dos Açores (NUTS III)",
                    "30": "Norte (NUTS II)",
                },
            },
        },
        "54": {
            "label": "Setor institucional de contraparte",
            "category": {
                "index": ["5"],
                "label": {"5": "Sociedades não financeiras"},
            },
        },
        "70": {
            "label": "Unidade de medida",
            "category": {"index": ["7"], "label": {"7": "Milhões de euros"}},
        },
        "reference_date": {
            "label": "Data",
            "category": {"index": ["2026-09-30", "2026-10-31"]},
        },
    }
    series = []
    for rub in ("1", "2"):
        for ter in ("20", "21", "30"):
            series.append(
                {
                    "id": int(f"{rub}{ter}"),
                    "label": "x",
                    "dimension_category": [
                        {"dimension_id": 48, "category_id": int(rub)},
                        {"dimension_id": 29, "category_id": 9},
                        {"dimension_id": 59, "category_id": int(ter)},
                        {"dimension_id": 54, "category_id": 5},
                        {"dimension_id": 70, "category_id": 7},
                    ],
                }
            )
    if as_list:
        values = [values.get(str(i)) for i in range(12)]
    return {
        "id": ["48", "29", "59", "54", "70", "reference_date"],
        "size": [2, 1, 3, 1, 1, 2],
        "dimension": dims,
        "value": values,
        "extension": {"series": series, "next_page": next_page},
    }


# flat index = ((rub * 3) + ter) * 2 + date
VALUES = {"0": 100.0, "1": 110.0, "2": 100.0, "3": 110.0, "4": 50.0, "7": 2.5}


@pytest.mark.parametrize("as_list", [False, True])
def test_observations_decodes_the_cube(as_list):
    got = list(bp.observations(cube(VALUES, as_list=as_list)))
    assert len(got) == 6
    serie, labels, date, v = got[1]
    assert (serie, date, v) == (120, "2026-10-31", 110.0)
    assert labels["Rubrica"] == "Empréstimos"
    assert labels["Território de contraparte"].startswith(
        "Região Autónoma dos Açores"
    )
    serie, labels, date, v = got[-1]
    assert (serie, labels["Rubrica"], date) == (
        220,
        "Empréstimos vencidos",
        "2026-10-31",
    )


def test_regiao_and_keep():
    assert bp.regiao(
        {
            "Território de contraparte": "Região Autónoma dos Açores (NUTS II)",
            "Território de referência": "Portugal",
        }
    ) == ("Açores", "NUTS II")
    # deposits: the counterpart is Portugal, the branch region is the reference
    assert bp.regiao(
        {
            "Território de contraparte": "Portugal",
            "Território de referência": "Concelho não alocado",
        }
    ) == ("Concelho não alocado", "")
    assert bp.keep("Açores", "NUTS II", "nuts2")
    assert not bp.keep("Açores", "NUTS III", "nuts2")
    assert bp.keep("Concelho não alocado", "", "nuts2")
    assert not bp.keep("Norte", "NUTS II", "ilhas")
    assert bp.keep("Portugal", "", "ilhas")


def test_read_follows_pages_and_drops_repeated_series():
    pages = {
        "first": cube(VALUES, next_page="https://x.test/second"),
        "second": cube({"1": 110.0}),  # the same series again
    }

    def fetch(url):
        return pages["second" if url.endswith("second") else "first"]

    rows = bp.read("emprestimos", 188, "abc", "nuts2", fetch)
    keys = [(r[1], r[4], r[5]) for r in rows]
    assert len(keys) == len(set(keys))
    got = {(r[1], r[4], r[5]): r for r in rows}
    assert got[("Empréstimos", "Açores", "2026-10-31")][6] == 110.0
    assert got[("Empréstimos", "Açores", "2026-10-31")][2] == "Empresas"
    assert got[("Empréstimos", "Açores", "2026-10-31")][8] == 120
    assert got[("Empréstimos vencidos", "Açores", "2026-10-31")][6] == 2.5
    assert all(r[4] != "" for r in rows)


def test_get_backs_off_on_503_and_gives_up_on_404(monkeypatch):
    calls, sleeps = [], []

    def urlopen(req, timeout):
        calls.append(req.full_url)
        if len(calls) < 3:
            raise urllib.error.HTTPError(req.full_url, 503, "busy", {}, None)
        return io.BytesIO(b'{"ok": 1}')

    monkeypatch.setattr(bp.urllib.request, "urlopen", urlopen)
    assert bp.get("https://x.test/u", sleep=sleeps.append) == {"ok": 1}
    assert sleeps == [1, 2]

    def not_found(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 404, "no", {}, None)

    monkeypatch.setattr(bp.urllib.request, "urlopen", not_found)
    with pytest.raises(urllib.error.HTTPError):
        bp.get("https://x.test/u", sleep=sleeps.append)
    assert sleeps == [1, 2]


def test_main_writes_csv_and_fails_when_stale(tmp_path, monkeypatch):
    monkeypatch.setattr(bp, "DATASETS", [("emprestimos", 188, "abc", "nuts2")])

    def fetch(url):
        return cube(VALUES)

    assert bp.main(tmp_path, today=dt.date(2026, 11, 27), fetch=fetch) == 0
    with open(tmp_path / "bportugal.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["regiao"] == "Açores"
    assert {r["regiao"] for r in rows} == {"Açores", "Norte"}
    assert bp.main(tmp_path, today=dt.date(2027, 6, 1), fetch=fetch) == 1
