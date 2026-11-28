import csv

import pytest

from bot import eurostat
from bot.dados import europa


def _jsonstat(values, status=None):
    """A Eurostat JSON-stat answer: unit fixed, 2 regions x 3 years."""
    return {
        "id": ["freq", "unit", "geo", "time"],
        "size": [1, 1, 2, 3],
        "updated": "2026-10-30T23:00:00+0100",
        "dimension": {
            "geo": {"category": {"index": {"PT20": 0, "PT30": 1}}},
            "time": {"category": {"index": {"2023": 0, "2024": 1, "2025": 2}}},
        },
        "value": values,
        "status": status or {},
    }


def test_rows_of_maps_flat_index_to_region_and_year():
    data = _jsonstat({"0": 5.1, "2": 4.9, "4": 5.4}, {"2": "u"})
    rows = eurostat.rows_of("desemprego", data)
    got = {(r[4], r[7]): (r[8], r[9]) for r in rows}
    assert got == {
        ("PT20", "2023"): (5.1, ""),
        ("PT20", "2025"): (4.9, "u"),
        ("PT30", "2024"): (5.4, ""),
    }
    assert rows[0][5] == "Açores" and rows[0][6] == "acores"
    assert rows[0][11] == "2026-10-30"


def test_rows_of_rejects_unfixed_dimensions():
    data = _jsonstat({"0": 1})
    data["size"][1] = 2
    with pytest.raises(ValueError):
        eurostat.rows_of("desemprego", data)


def test_main_keeps_old_rows_of_a_failed_table(tmp_path, monkeypatch):
    old = [eurostat.COLS, ["camas", "x", "y", "z", "PT20", "Açores",
                           "acores", "2020", "600", "", "hlth_rs_bdsrg2",
                           "2026-01-01"]]  # fmt: skip
    with (tmp_path / "eurostat.csv").open("w", newline="") as f:
        csv.writer(f).writerows(old)

    def fake_get(table, filters):
        if table == "hlth_rs_bdsrg2":
            raise OSError("down")
        return _jsonstat({"0": 1.0})

    monkeypatch.setattr(eurostat, "get", fake_get)
    monkeypatch.setattr(eurostat, "PAUSE", 0)
    assert eurostat.main(tmp_path) == 1  # one table failed
    with (tmp_path / "eurostat.csv").open() as f:
        rows = list(csv.DictReader(f))
    camas = [r for r in rows if r["indicador"] == "camas"]
    assert [r["valor"] for r in camas] == ["600"]
    assert len({r["indicador"] for r in rows}) == len(eurostat.INDICADORES)


def test_eurostat_data_rank_and_other_year():
    cols = eurostat.COLS
    base = ["pib_ppc", "Economia", "PIB", "UE = 100"]
    rows = [
        [*base, "PT20", "Açores", "acores", "2024", "73", "p", "t", "d"],
        [*base, "PT30", "Madeira", "rup", "2024", "88", "", "t", "d"],
        [*base, "ES70", "Canárias", "rup", "2024", "72", "", "t", "d"],
        [*base, "FRY5", "Maiote", "rup", "2023", "30", "", "t", "d"],
        [*base, "PT", "Portugal", "pais", "2024", "82", "", "t", "d"],
    ]
    tabela, series = europa.eurostat_data(cols, rows)
    (linha,) = tabela["temas"][0]["linhas"]
    assert linha["ano"] == 2024
    # Maiote is another year, Portugal is not an outermost region
    assert linha["posicao"] == [2, 3]
    assert linha["valores"]["PT20"]["estado"] == "provisório"
    assert linha["valores"]["FRY5"]["outro_ano"] is True
    assert series["indicadores"][0]["s"]["PT20"] == [[2024, 73.0, "p"]]
