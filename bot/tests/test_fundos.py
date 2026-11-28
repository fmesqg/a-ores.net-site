import json
import urllib.error
import urllib.parse

import pytest

from bot import fundos as f
from bot.dados import fundos


def test_prr_locations_keeps_azores_and_sums_shares():
    rows = [
        {"cd_projeto": "A", "cd_nutsii": "20", "ds_concelho": "Horta",
         "perc_valor_aprovado": "60", "perc_valor_pago": "100"},
        {"cd_projeto": "A", "cd_nutsii": "20", "ds_concelho": "Lagoa",
         "perc_valor_aprovado": "15", "perc_valor_pago": "100"},
        {"cd_projeto": "A", "cd_nutsii": "11", "ds_concelho": "Porto",
         "perc_valor_aprovado": "25", "perc_valor_pago": "0"},
        {"cd_projeto": "B", "cd_nutsii": "30", "ds_concelho": "Funchal",
         "perc_valor_aprovado": "100", "perc_valor_pago": "100"},
    ]  # fmt: skip
    loc = f.prr_locations(rows)
    assert set(loc) == {"A"}
    assert loc["A"]["aprovado"] == 75
    assert loc["A"]["concelhos"] == ["Horta", "Lagoa"]


def test_investment_lookup_falls_back_to_shorter_codes():
    inv = f.prr_investments(
        [
            {"Código do Investimento": "RE-C14-i03", "Código da Componente":
             "C14", "Designação da Componente": "Hidrogénio",
             "Designação do Investimento": "Transição energética"},
            {"Código do Investimento": "TC-C06-i03", "Código da Componente":
             "C06", "Designação da Componente": "Qualificações",
             "Designação do Investimento": "Escolas"},
        ]
    )  # fmt: skip
    assert f._investment("C14-i03-RAA", inv) == (
        "C14 Hidrogénio",
        "Transição energética",
    )
    assert f._investment("C06-i03.02", inv)[1] == "Escolas"
    assert f._investment("C99-i01", inv) == ("", "")


def test_prr_projects_applies_the_approved_share_to_paid():
    loc = {"A": {"aprovado": 50.0, "concelhos": ["Horta"]}}
    rows = [
        {"cd_projeto": "A", "ds_projeto": "Porto", "valor_aprovado": 1000,
         "valor_pago": 400, "cd_investimento": "C07-i05-RAA",
         "dt_referencia": "2026-11-27"},
        {"cd_projeto": "Z", "valor_aprovado": 5, "valor_pago": 5},
    ]  # fmt: skip
    (p,) = f.prr_projects(rows, loc, {})
    r = dict(zip(f.PRR_PROJETOS, p, strict=True))
    assert r["aprovado_acores"] == "500"
    assert r["pago_acores"] == "200"
    assert r["perc_acores"] == "50"
    assert r["concelhos"] == "Horta"


def test_prr_entities_only_for_azorean_projects():
    rows = [
        {"cd_projeto": "A", "nif_entidade": "512044040",
         "ds_entidade": "Município", "papel_entidade": "Beneficiário Final",
         "valor_contratado": 10, "valor_pago": 5},
        {"cd_projeto": "Z", "nif_entidade": "1", "ds_entidade": "Outro",
         "papel_entidade": "Beneficiário Final"},
    ]  # fmt: skip
    (e,) = f.prr_entities(rows, {"A"})
    assert e[:4] == ["A", "512044040", "Município", "Beneficiário Final"]


AZ = "-25.67,37.74"


@pytest.mark.parametrize(
    "programa,coords,esperado",
    [
        ("2014PT16M2OP004 - Açores - FEDER/FSE", [AZ], ""),
        ("2014PT16M2OP004 - Açores - FEDER/FSE", sorted(f.HOMONIMOS), ""),
        ("2014PT16M2OP006 - Madeira - FEDER/FSE", [AZ], f.NOTA_FORA),
        ("2021PT16FFPR003 - Programa Regional do Norte", [AZ], f.NOTA_FORA),
        ("2021TC16RFTN002 - Interreg VI-B", [AZ], f.NOTA_INTERREG),
        (
            "2021PT05SFPR001 - Programa Temático Demografia",
            ["-25.0676137,37.0028353"],
            f.NOTA_HOMONIMO,
        ),
        ("2021PT05SFPR001 - Demografia", [AZ, "-8.6,41.1"], f.NOTA_VARIOS),
        ("2021PT16CFPR001 - Ação Climática", [AZ], ""),
    ],
)
def test_nota(programa, coords, esperado):
    assert f.nota(programa, coords) == esperado


def fake_kohesio(projects):
    """A fetch for read_kohesio. projects: [(item, program, fund)]."""
    calls = []

    def fetch(url):
        calls.append(url)
        path = urllib.parse.urlparse(url).path
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query))
        if path.endswith("/queries/funds"):
            out = [
                {"instance": "F1", "instanceLabel": "ERDF - Fundo (2014)"},
                {"instance": "F2", "instanceLabel": "ESF - Fundo (2014)"},
            ]
        elif path.endswith("/queries/programs"):
            out = [
                {"instance": "P1", "instanceLabel":
                 "2014PT16M2OP004 - Açores - FEDER/FSE", "funds": ["F1", "F2"]},
                {"instance": "P2", "instanceLabel": "2021X - Vazio",
                 "funds": ["F1"]},
            ]  # fmt: skip
        elif path.endswith("/beneficiaries"):
            out = {
                "list": [
                    {"id": f.ENTITY + "Q9", "label": "EDA", "budget": "10,5",
                     "euBudget": "8,25", "numberProjects": 2,
                     "cofinancingRate": "85.0"},
                ],
                "numberResults": 1,
            }  # fmt: skip
        else:
            got = [
                {"item": i, "labels": [i], "euBudgets": ["1,5"],
                 "totalBudgets": ["2"], "coordinates": [AZ]}
                for i, prog, fund in projects
                if q.get("program") in (None, prog)
                and q.get("fund") in (None, fund)
            ]  # fmt: skip
            off, lim = int(q.get("offset", 0)), int(q["limit"])
            out = {"list": got[off : off + lim], "numberResults": len(got)}
        return json.dumps(out).encode()

    return fetch, calls


def test_read_kohesio_assigns_programme_and_fund(monkeypatch):
    monkeypatch.setattr(f, "PAGE", 2)
    fetch, calls = fake_kohesio(
        [
            ("Q1", "P1", "F1"),
            ("Q2", "P1", "F1"),
            ("Q3", "P1", "F1"),
            ("Q4", "P1", "F2"),
            ("Q5", "P1", None),  # no fund: read with the programme alone
            ("Q6", None, None),  # in no programme listed for Portugal
        ]
    )
    projetos, ben = f.read_kohesio(fetch)
    by = {
        p[0]: dict(zip(f.KOHESIO_PROJETOS, p, strict=True)) for p in projetos
    }
    assert set(by) == {"Q1", "Q2", "Q3", "Q4", "Q5", "Q6"}
    assert by["Q3"]["fundo"] == "ERDF" and by["Q4"]["fundo"] == "ESF"
    assert by["Q5"]["programa"].startswith("2014PT16M2OP004")
    assert by["Q5"]["fundo"] == ""
    assert by["Q1"]["periodo"] == "2014-2020"
    assert by["Q6"]["programa"] == ""
    assert by["Q1"]["apoio_ue"] == "1.5"
    assert ben == [
        ["Q9", "EDA", 2, "10.5", "8.25", "85.0",
         "https://kohesio.ec.europa.eu/pt/beneficiaries/Q9"],
    ]  # fmt: skip


def test_get_retries_then_raises_on_404(monkeypatch):
    codes = iter([503, 404])

    def urlopen(req, timeout):
        raise urllib.error.HTTPError(req.full_url, next(codes), "x", {}, None)

    monkeypatch.setattr(f.urllib.request, "urlopen", urlopen)
    sleeps = []
    with pytest.raises(urllib.error.HTTPError) as e:
        f.get("https://example.org/", sleep=sleeps.append)
    assert e.value.code == 404 and sleeps == [1]


def test_fundos_data_totals():
    prr = (
        f.PRR_PROJETOS,
        [
            ["A", "x", "C07 Infra", "", "", "Horta", "50", "1000", "400",
             "500", "200", "1000", "0", "", "", "", "2026-11-27"],
            ["B", "y", "C07 Infra", "", "", "Horta; Lagoa", "100", "100",
             "100", "100", "100", "100", "0", "", "", "", "2026-11-27"],
        ],
    )  # fmt: skip
    ent = (
        f.PRR_ENTIDADES,
        [
            ["A", "1", "EDA", "Beneficiário Final", "", "", "1000", "0"],
            ["B", "1", "EDA", "Beneficiário Final", "", "", "100", "0"],
            ["B", "2", "DR", "Beneficiário Intermediário", "", "", "100", ""],
        ],
    )
    koh = (
        f.KOHESIO_PROJETOS,
        [
            ["Q1", "p", "2014X - Açores", "2014-2020", "ERDF", "", "", "4",
             "3000000", "", "", ""],
            ["Q2", "p", "2021Y - Norte", "2021-2027", "ERDF", "", "", "4",
             "2000000", "", f.NOTA_FORA, ""],
        ],
    )  # fmt: skip
    d = fundos.fundos_data(
        {"prr_projetos": prr, "prr_entidades": ent, "kohesio_projetos": koh}
    )
    assert d["prr"]["projetos"] == 2 and d["prr"]["beneficiarios"] == 1
    assert [c["nome"] for c in d["prr"]["concelhos"]] == [
        "Horta",
        "Vários concelhos",
    ]
    assert d["prr"]["maiores"][0]["valor"] == round((500 + 100) / 1e6, 1)
    assert d["kohesio"]["apoio_ue"] == 3.0
    assert d["kohesio"]["excluidos"] == 1
    assert d["kohesio"]["periodos"] == [
        {"nome": "2014-2020", "projetos": 1, "apoio_ue": 3.0}
    ]
