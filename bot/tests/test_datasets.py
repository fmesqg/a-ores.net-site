import csv
import gzip
import json
import sqlite3
from pathlib import Path

from bot import datasets
from bot.dados import (
    base,
    camaras,
    comum,
    credito,
    empresas,
    impostos,
    parlamento,
    publico,
    resumo,
    sqlite,
)

BASE_DAY = """---
date: 2026-11-25
title: Atualização (BASE)
layout: default
---
## Contratos publicados ontem

* [Empreitada X](https://www.base.gov.pt/Base4/pt/detalhe/?type=contratos&id=15998022)
  * Preço contratual: 120.963,33 €
  * Adjudicante: Junta Freguesia de Angústias
  * Adjudicatário: Biquadrada II - Açores, Lda
  * Tipo de procedimento: Concurso público
  * Data da assinatura: 14-10-2026
"""

ALRA_DAY = """---
date: 2026-11-25
---
## ALRA

### Requerimentos

* [Apoios ao bem-estar animal](http://base.alra.pt:82/4DACTION/w_pesquisa_registo/4/9637)
  * Alteração do estado: FORA DE PRAZO → RESPOSTA TADIA
  * [requerimento](http://base.alra.pt:82/Doc_Req/XIIIreque887.pdf)( data entrada: 21/10/2026)
  * [resposta](http://base.alra.pt:82/Doc_Req/XIIIrequeresp887.pdf) (data entrada resposta: 23/11/2026)
  * Requerente(s): Pedro Neves PAN

### Informações

* [Nota de Imprensa da Representação Parlamentar do BE - Título](http://base.alra.pt:82/4DACTION/w_pesquisa_registo/8/1)
  * [pdf](http://base.alra.pt:82/Doc_Noticias/NI1.pdf)

### Votos

* [Pelo falecimento de Alguém](http://base.alra.pt:82/4DACTION/w_pesquisa_registo/1/4028)
  * Voto de Congratulaçăo
  * Autores: PS
  * Resultado: Aprovado por unanimidade
"""

JORAA_DAY = """---
date: 2024-08-21
---
## JORAA

* [Delegação de competências](https://jo.azores.gov.pt/#/ato/56505c99)
  * Despacho n.º 1718/2024 de 21 de agosto de 2024
  * Soma dos montantes: 993,164.40 €
  * Secretaria Regional da Educação, Cultura e Desporto
  * Jornal Oficial II Série - Número 160
"""


def test_joraa_montante_old_and_new_lines():
    assert parlamento.joraa_montante(
        ["Despacho", "Soma dos montantes: 1,500.00 €"]
    ) == (1500.0, parlamento.JORAA_SOMA_ANTIGA)
    assert parlamento.joraa_montante(
        ["Despacho", "Montante: 25 010,49 € (soma de 8 valores)"]
    ) == (25010.49, "soma de 8 valores")
    assert parlamento.joraa_montante(["Despacho", "Entidade"]) == (None, "")


def test_euros_both_conventions():
    assert comum.euros("120.963,33 €", ",") == 120963.33
    assert comum.euros("12,987,000.00 €", ".") == 12987000.0
    assert comum.euros("", ",") is None


def test_iso_dates():
    assert comum.iso("14-10-2026") == "2026-10-14"
    assert comum.iso("( data entrada: 1/2/2026)") == "2026-02-01"
    assert comum.iso("sem data") == ""


def impic_row(**kw):
    """One data/base_impic/ row, for tests (only the columns given)."""
    from bot import base_impic

    d = dict.fromkeys(base_impic.COLS, "")
    d.update(kw)
    return [d[c] for c in base_impic.COLS]


def write_impic(data: Path, rows: list, name: str = "2026.csv.gz") -> None:
    from bot import base_impic

    (data / "base_impic").mkdir(parents=True, exist_ok=True)
    with gzip.open(data / "base_impic" / name, "wt", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(base_impic.COLS)
        w.writerows(rows)


ANGUSTIAS = impic_row(
    id="15998022",
    publicado="2026-11-26",
    data_assinatura="2026-10-14",
    preco="120963.33",
    adjudicante="Junta Freguesia de Angústias",
    adjudicatario="Biquadrada II - Açores, Lda",
    procedimento="Concurso público",
    objeto="Empreitada X",
)


def test_build_all(tmp_path):
    write_impic(tmp_path / "data", [ANGUSTIAS])
    tmp_path = tmp_path / "docs"
    tmp_path.mkdir()
    for coll, name, text in (
        ("_base_updates", "2026-11-25", BASE_DAY),  # not read for base.csv
        ("_alra_updates", "2026-11-25", ALRA_DAY),
        ("_joraa_updates", "2024-08-21", JORAA_DAY),
    ):
        (tmp_path / coll).mkdir(exist_ok=True)
        (tmp_path / coll / f"{name}.md").write_text(text, encoding="utf-8")

    meta = datasets.main(tmp_path)
    out = tmp_path / "dados"

    def rows(name):
        with open(out / f"{name}.csv", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))

    (b,) = rows("base")
    assert b["id"] == "15998022"
    assert b["publicado"] == "2026-11-26"
    assert b["preco"] == "120963.33"
    assert b["data_assinatura"] == "2026-10-14"
    assert b["adjudicatario"] == "Biquadrada II - Açores, Lda"

    a = {r["tipo"]: r for r in rows("alra")}
    req = a["Requerimentos"]
    assert req["estado"] == "RESPOSTA TADIA"
    assert req["data"] == "2026-10-21"
    assert req["autores"] == "Pedro Neves PAN"
    assert req["documento"].endswith("XIIIreque887.pdf")
    assert req["resposta"].endswith("XIIIrequeresp887.pdf")
    assert a["Informações"]["autores"] == "BE"
    assert a["Votos"]["estado"] == (
        "Voto de Congratulação · Aprovado por unanimidade"
    )

    (j,) = rows("joraa")
    assert j["montante"] == "993164.4"
    assert j["montante_tipo"] == parlamento.JORAA_SOMA_ANTIGA
    assert j["entidade"].startswith("Secretaria Regional da Educação")

    assert meta["base"]["linhas"] == 1
    assert json.loads((out / "meta.json").read_text())["base"]["ate"] == (
        "2026-11-26"
    )


def test_sqlite_fts(tmp_path):
    write_impic(tmp_path / "data", [ANGUSTIAS])
    tmp_path = tmp_path / "docs"
    tmp_path.mkdir()
    for coll in ("_alra_updates", "_joraa_updates"):
        (tmp_path / coll).mkdir()
    (tmp_path / "_alra_updates" / "2026-11-25.md").write_text(
        ALRA_DAY, encoding="utf-8"
    )
    (tmp_path / "_joraa_updates" / "2024-08-21.md").write_text(
        JORAA_DAY, encoding="utf-8"
    )
    datasets.main(tmp_path)
    con = sqlite3.connect(tmp_path / "dados" / "contratos.db")
    preco, tipo = con.execute(
        "select preco, typeof(preco) from base join base_fts "
        "on base_fts.rowid = base.rowid where base_fts match 'angustias'"
    ).fetchone()  # accent-insensitive: "Angústias"
    assert (preco, tipo) == (120963.33, "real")
    con = sqlite3.connect(tmp_path / "dados" / "parlamento.db")
    assert con.execute(
        "select count(*) from alra where resposta is null"
    ).fetchone() == (2,)
    assert not (tmp_path / "dados" / "acores.db").exists()


def test_pt_num():
    assert comum.pt_num(245328) == "245 328"
    assert comum.pt_num(39.38) == "39,4"
    assert comum.pt_num(5.94) == "5,94"
    assert comum.pt_num(75.0) == "75"
    assert comum.pt_num(-198.5) == "-198"


INE_COLS = [
    "varcd",
    "tema",
    "indicador",
    "periodo",
    "data",
    "nivel",
    "geocod",
    "local",
    "concelho",
    "ilha",
    "categoria",
    "valor",
    "unidade",
    "atualizado",
    "url",
]


def _ine(varcd, data, nivel, geocod, ilha, valor):
    return [
        varcd,
        "",
        "",
        data[:4],
        data,
        nivel,
        geocod,
        "",
        "",
        ilha,
        "",
        str(valor),
        "",
        "",
        f"https://www.ine.pt/xurl/indx/{varcd}",
    ]


BEO_COLS = [
    "quadro",
    "ordem",
    "nivel",
    "rubrica",
    "caminho",
    "dimensao",
    "medida",
    "ano",
    "mes",
    "data",
    "valor",
    "boletim",
]


def _beo(
    quadro, caminho, valor, ano="2025", mes="12", nivel="0", dim="Consolidado"
):
    return [
        quadro,
        "1",
        nivel,
        caminho.split(" › ")[-1],
        caminho,
        dim,
        "Montante (€)",
        ano,
        mes,
        f"{ano}-{int(mes):02d}-01",
        str(valor),
        f"https://example/BEO_{ano}_{mes}.pdf",
    ]


def test_resumo(tmp_path):
    ine = [
        _ine("0012918", "2024-01-01", "Região", "20", "", 1),  # older: ignored
        _ine("0012918", "2025-01-01", "Região", "20", "", 300),
        _ine("0012918", "2025-01-01", "País", "PT", "", 10000),
        _ine("0012918", "2025-01-01", "Concelho", "4201", "Flores", 100),
        _ine("0012918", "2025-01-01", "Concelho", "4301", "Pico", 150),
        _ine("0012918", "2025-01-01", "Concelho", "4302", "Pico", 50),
    ]
    rc = "Receita corrente › "
    s = "Síntese global"
    beo = [
        _beo(s, "Receita efetiva", 1000e6),
        _beo(s, rc + "Impostos diretos", 300e6),
        _beo(s, rc + "Impostos indiretos", 300e6),
        _beo(
            s,
            rc + "Transferências correntes › Administração central - Estado",
            200e6,
        ),
        _beo(
            s,
            "Receita de capital › Transferências de capital › Resto do mundo",
            100e6,
        ),
        _beo(s, "Despesa efetiva", 1200e6),
        _beo(s, "Despesa corrente › Despesas com pessoal", 500e6),
        _beo(s, "Saldo global", -200e6),
        _beo(
            s, "Receita efetiva", 9e9, ano="2026", mes="9"
        ),  # year not closed
        _beo(
            "Despesa do GRA por função", "Saúde n.e.", 400e6, nivel="1", dim=""
        ),
    ]
    resumo.write_resumo(
        tmp_path, {"ine": (INE_COLS, ine), "beo": (BEO_COLS, beo)}
    )
    r = json.loads((tmp_path / "_data" / "resumo.json").read_text())
    pop = r["ine"]["0012918"]
    assert (pop["acores"], pop["pt"], pop["periodo"]) == (300, 10000, "2025")
    assert [(i["ilha"], i["valor"], i["pct"]) for i in pop["ilhas"]] == [
        ("Pico", 200, 67),
        ("Flores", 100, 33),
    ]
    b = r["beo"]
    assert (
        b["ano"] == "2025" and b["saldo"] == -200 and b["saldo_abs_t"] == "200"
    )
    rec = {i["nome"]: i["valor"] for i in b["receitas"]}
    assert rec["Impostos cobrados nos Açores"] == 600
    assert rec["Transferências do Estado"] == 200
    assert rec["Do exterior (sobretudo fundos europeus)"] == 100
    assert rec["Outras receitas"] == 100
    assert b["funcoes"] == [
        {
            "nome": "Saúde",
            "valor": 400.0,
            "pct": 100,
            "valor_t": "400",
            "pct_t": "100",
        }
    ]
    assert b["despesa_hab"] == 4000000


SREA_COLS = [
    "serie",
    "indicador",
    "rubrica",
    "local",
    "periodo",
    "data",
    "valor",
    "unidade",
    "nota",
    "ficheiro",
    "pagina",
]


def _srea(serie, ind, rub, local, periodo, data, valor, nota=""):
    return [
        serie,
        ind,
        rub,
        local,
        periodo,
        data,
        str(valor),
        "%",
        nota,
        "f.xlsx",
        "https://srea/area/x/",
    ]


def test_resumo_srea_and_json():
    vh, m12 = "Variação homóloga", "Variação média dos últimos 12 meses"
    td = "Taxa de desemprego"
    rows = [
        _srea("ipc", vh, "Total", "Açores", "2026-09", "2026-09-01", 2.5),
        _srea("ipc", vh, "Total", "Açores", "2026-10", "2026-10-01", 2.64),
        _srea("ipc", m12, "Total", "Açores", "2026-10", "2026-10-01", 2.68),
        _srea("ipc", vh, "Saúde", "Açores", "2026-10", "2026-10-01", 1),
        _srea("ipc", vh, "Transportes", "Açores", "2026-10", "2026-10-01", 5),
        _srea("ipc", vh, "Vestuário", "Açores", "2026-10", "2026-10-01", -4),
        _srea(
            "iae",
            "Indicador de atividade económica",
            "Total",
            "Açores",
            "2026-09",
            "2026-09-01",
            1.04,
        ),
        _srea(
            "desemprego",
            td,
            "Total",
            "Açores",
            "2025-T3",
            "2025-07-01",
            4.8,
            "fiabilidade reduzida",
        ),
        _srea(
            "desemprego",
            td,
            "Total",
            "Açores",
            "2026-T3",
            "2026-07-01",
            4.3,
            "fiabilidade reduzida",
        ),
    ]
    for y, v in (("2025", 10), ("2026", 9)):
        for m in ("01", "02"):
            for rub in ("Hotelaria", "Alojamento local"):
                for local, k in (("Açores", 3), ("Pico", 1)):
                    rows.append(
                        _srea(
                            "dormidas",
                            "Dormidas",
                            rub,
                            local,
                            f"{y}-{m}",
                            f"{y}-{m}-01",
                            v * k,
                        )
                    )
    # hotels already published March 2026, alojamento local not yet
    rows.append(
        _srea(
            "dormidas",
            "Dormidas",
            "Hotelaria",
            "Açores",
            "2026-03",
            "2026-03-01",
            999,
        )
    )
    for local, v in (("Açores", 20000), ("Corvo", 25000), ("Pico", 20000)):
        rows.append(
            _srea(
                "pib_hab",
                "PIB por habitante",
                "Preços correntes",
                local,
                "2024",
                "2024-01-01",
                v,
                "provisório",
            )
        )
    rows.append(
        _srea(
            "pib",
            "Produto interno bruto",
            "Preços correntes",
            "Açores",
            "2024",
            "2024-01-01",
            5753263000,
            "provisório",
        )
    )
    r = resumo.resumo_srea(SREA_COLS, rows)
    assert r["ipc"]["valor"] == 2.64 and r["ipc"]["media12"] == 2.68
    assert r["ipc"]["periodo"] == "outubro de 2026"
    assert r["ipc"]["antes"] == "outubro de 2025"
    assert [c["nome"] for c in r["ipc"]["mais"]] == [
        "Transportes",
        "Saúde",
        "Vestuário",
    ]
    assert r["ipc"]["menos"][0]["nome"] == "Vestuário"
    assert r["iae"] == {
        "valor": 1.0,
        "periodo": "setembro de 2026",
        "url": "https://srea/area/x/",
    }
    d = r["desemprego"]
    assert (d["valor"], d["antes"], d["periodo"]) == (
        4.3,
        4.8,
        "3.º trimestre de 2026",
    )
    t = r["dormidas"]
    assert t["periodo"] == "janeiro a fevereiro de 2026"
    assert (t["valor"], t["antes"], t["var"]) == (108, 120, -10.0)
    assert t["ilhas"] == [{"ilha": "Pico", "valor": 36, "var": -10.0}]
    p = r["pib_hab"]
    assert p["ano"] == "2024" and p["provisorio"] and p["acores"] == 20000
    assert p["total_mm"] == 5.8
    assert [(i["ilha"], i["pct"]) for i in p["por_ilha"]] == [
        ("Corvo", 100),
        ("Pico", 80),
    ]
    js = resumo.srea_json(SREA_COLS, rows)
    tot = next(
        s
        for s in js
        if s["serie"] == "ipc"
        and s["rubrica"] == "Total"
        and s["indicador"] == vh
    )
    assert tot["p"] == [["2026-09", 2.5], ["2026-10", 2.64]]
    une = next(s for s in js if s["serie"] == "desemprego")
    assert une["p"][-1] == ["2026-T3", 4.3, "fiabilidade reduzida"]


def test_resumo_tdc():
    tcols = ["conta", "tipo", "numero", "texto", "referencia", "situacao"]
    tcols += ["desde", "parecer", "sintese"]

    def t(conta, tipo, situacao="", desde=""):
        return [conta, tipo, "1", "x", "", situacao, desde, f"p{conta}", ""]

    trows = [
        t("2024", "recomendação", "Não implementada (2025)", "2013"),
        t("2024", "recomendação", "Parcialmente implementada (2025)", "2016"),
        t("2024", "recomendação", "Parcialmente implementada (2025)", "2006"),
        t("2024", "recomendação"),  # new in 2024, not assessed yet
        t("2025", "juízo"),
        t("2025", "reserva"),
        t("2025", "reserva"),
        t("2025", "recomendação"),
    ]
    vcols = ["quadro", "ordem", "nivel", "rubrica", "caminho", "ano"]
    vcols += ["valor", "unidade", "parecer"]
    conta = "Conta do sector público administrativo regional"
    vrows = [
        ["Indicadores", "1", "1", "Dívida total", "", "2024", "3492.9", "", ""],
        ["Indicadores", "1", "1", "Dívida total", "", "2025", "3728.8", "", ""],
        ["Indicadores", "2", "1", "Receita não registada na Conta", "",
         "2025", "613.0", "", ""],
        [conta, "21", "1", "Saldo global ou efetivo", "", "2025",
         "-199287231.59", "€", ""],
    ]  # fmt: skip
    r = resumo.resumo_tdc((tcols, trows), (vcols, vrows))
    assert (r["conta"], r["url"], r["reservas"]) == ("2025", "p2025", 2)
    assert r["recomendacoes"] == 1 and r["avaliadas"] == 3
    assert r["estados"] == [
        {"nome": "Não implementada", "n": 1},
        {"nome": "Parcialmente implementada", "n": 2},
    ]
    assert r["desde"] == 2006
    assert (r["divida"], r["divida_var"]) == (3728.8, 6.8)
    assert (r["saldo"], r["saldo_abs"]) == (-199.3, 199.3)
    assert r["receita_fora"] == 613.0 and "despesa_fora" not in r
    assert resumo.resumo_tdc(([], []), ([], [])) == {}


def test_sper_and_maiores():
    url = "https://www.cfp.pt/rel"
    scols = [
        "relatorio",
        "ano",
        "sigla",
        "empresa",
        "ordem",
        "indicador",
        "valor",
        "unidade",
        "fonte",
        "url",
        "ficheiro",
    ]

    def v(rel, ano, sigla, ind, valor):
        return [
            rel,
            str(ano),
            sigla,
            "",
            "0",
            ind,
            str(valor),
            "€",
            "",
            url,
            "f.xlsx",
        ]

    sper = (
        scols,
        [
            v("13/2024", 2023, "SATA", "Resultado Líquido", -9.97e6),
            v("9/2025", 2023, "SATA", "Resultado Líquido", -9.97e6),
            v("9/2025", 2024, "SATA", "Resultado Líquido", -11.6e6),
            v("9/2025", 2024, "SATA", "Volume de Negócios", 60.6e6),
            v("9/2025", 2024, "SATA", "Capital Próprio", -26e6),
            v("9/2025", 2024, "SATA", "Número de Trabalhadores", 991),
            v("9/2025", 2024, "EDA", "Resultado Líquido", 10.4e6),
            v("9/2025", 2024, "EDA", "Volume de Negócios", 264.6e6),
            v("9/2025", 2024, "EDA", "Capital Próprio", 290e6),
        ],
    )
    ecols = [
        "relatorio",
        "ordem",
        "sigla",
        "empresa",
        "cae",
        "participacao",
        "acionista",
        "ap",
        "nota",
        "url",
    ]
    lista_empresas = (
        ecols,
        [
            [
                "9/2025",
                "3",
                "EDA",
                "EDA, S.A.",
                "D",
                "0.501",
                "RAA",
                "",
                "",
                url,
            ],
            [
                "9/2025",
                "7",
                "SATA Holding",
                "Sata Holding, S.A.",
                "H",
                "1",
                "RAA",
                "",
                "",
                url,
            ],
            [
                "9/2025",
                "8",
                "SATA",
                "Sata Air Açores, S.A.",
                "H",
                "1",
                "SATA Holding",
                "sim",
                "",
                url,
            ],
        ],
    )
    rcols = [
        "relatorio",
        "quadro",
        "ordem",
        "grupo",
        "rubrica",
        "ano",
        "valor",
        "unidade",
        "nota",
        "url",
    ]
    esf = "Esforço financeiro líquido da Região"
    tot = "Esforço financeiro líquido (2)-(1)"
    regiao = (
        rcols,
        [
            ["13/2024", esf, "0", "", tot, "2023", "339.3", "M€", "", url],
            [
                "9/2025",
                esf,
                "0",
                "",
                "Dividendos",
                "2023",
                "3.1",
                "M€",
                "n",
                url,
            ],
            ["9/2025", esf, "1", "", tot, "2023", "75.1", "M€", "", url],
            ["9/2025", esf, "1", "", tot, "2024", "93.5", "M€", "", url],
            [
                "9/2025",
                "Peso na economia",
                "0",
                "Indicadores",
                "Peso do SERAA no PIB RAA",
                "2024",
                "7.6",
                "%",
                "",
                url,
            ],
        ],
    )
    s = empresas.sper_data(sper, lista_empresas, regiao)
    assert s["relatorio"] == "9/2025" and s["ano"] == 2024
    assert [e["sigla"] for e in s["empresas"]] == [
        "EDA",
        "SATA",
        "SATA Holding",
    ]
    sata = s["empresas"][1]
    assert sata["nome"] == "SATA Air Açores" and sata["ap"]
    assert sata["rl"] == -11.6 and sata["participacao"] == 100.0
    assert sata["rl_anos"] == [
        {"ano": 2023, "v": -9.97},
        {"ano": 2024, "v": -11.6},
    ]
    assert s["total"]["vn"] == 325.2 and s["total"]["prejuizo"] == 1
    assert s["sem_ficha"] == ["SATA Holding"]
    assert s["cp_negativo"] == ["SATA Air Açores"]
    assert s["esforco"]["total"] == 93.5
    assert s["esforco"]["antes"]["valor"] == 339.3
    assert s["esforco"]["antes"]["agora"] == 75.1
    assert s["vab_pib"] == 7.6

    mcols = [
        "ano",
        "posicao",
        "empresa",
        "ilha",
        "setor",
        "trabalhadores",
        "volume_negocios",
        "cresc_vn_pct",
        "resultado_liquido",
        "fonte",
        "url",
    ]
    maiores = (
        mcols,
        [
            [
                "2024",
                "1",
                "EDA - ELECTRICIDADE DOS AÇORES, S.A.",
                "São Miguel",
                "Energia",
                "783",
                "264566",
                "-2.6",
                "10431",
                "f",
                "u",
            ],
            [
                "2024",
                "2",
                "SATA AIR AÇORES - SOCIEDADE AÇORIANA, S.A.",
                "São Miguel",
                "Energia",
                "1000",
                "60600",
                "",
                "-11600",
                "f",
                "u",
            ],
            [
                "2024",
                "3",
                "SATA - OUTRA, LDA",
                "Terceira",
                "Comércio",
                "5",
                "1000",
                "1",
                "1",
                "f",
                "u",
            ],
        ],
    )
    lista = [dict(zip(ecols, r, strict=True)) for r in lista_empresas[1]]
    m = empresas.maiores_data(maiores, lista)
    assert [e["publica"] for e in m["empresas"]] == ["EDA", "SATA", ""]
    assert m["vn"] == 326.2 and m["prejuizo"] == 1 and m["publicas"] == 2
    assert m["ilhas"][0] == {
        "nome": "São Miguel",
        "n": 2,
        "vn": 325.2,
        "trabalhadores": 1783,
        "pct": 100,
    }


def test_publico_data():
    cols = ["quadro", "indicador", "ordem", "rubrica", "local", "data"]
    cols += ["valor", "unidade", "provisorio", "ficheiro", "pagina"]
    ar = publico.AR_ACORES
    pt = "Postos de trabalho"
    q17 = "Postos de trabalho nas administrações públicas, por carreira"
    rows = []

    def add(q, ind, ordem, rub, local, data, v, prov=""):
        rows.append(
            [q, ind, str(ordem), rub, local, data, str(v), "", prov, "f", "p"]
        )

    for data, k in (("2025-09-30", 0), ("2025-12-31", 0), ("2026-09-30", 1)):
        prov = "p" if k else ""
        add("Q1.1", pt, 42, ar, "Açores", data, 300 + 10 * k, prov)
        add(
            "Q1.1",
            pt,
            43,
            "Órgãos do Governo Regional dos Açores",
            "Açores",
            data,
            200,
            prov,
        )
        add(
            "Q1.1",
            pt,
            50,
            "Educação, Cultura e Desporto",
            "Açores",
            data,
            150 + 10 * k,
            prov,
        )
        add(
            "Q1.1",
            pt,
            51,
            "Saúde e Segurança Social",
            "Açores",
            data,
            50,
            prov,
        )
        add("Q1.1", pt, 57, publico.AR_SER, "Açores", data, 100, prov)
        add(
            "Q1.1",
            pt,
            81,
            "Fundos de Segurança Social da Adm. Regional dos Açores",
            "Açores",
            data,
            7,
            prov,
        )
        add("Q1.7", q17, 9, "Total", "Açores", data, 400 + 20 * k, prov)
        add("Q1.7", q17, 9, "Total", "Portugal", data, 10000, prov)
        add("Q1.7", q17, 11, "Dirigente superior", "Açores", data, 20, prov)
        add(
            "Q1.7",
            q17,
            12,
            "Dirigente superior de 1.º grau",
            "Açores",
            data,
            8,
            prov,
        )
        add("Q1.7", q17, 29, "Médico", "Açores", data, 30 + 5 * k, prov)
        add(
            "Q1.7",
            q17,
            45,
            "Polícia de Segurança Pública",
            "Açores",
            data,
            0,
            prov,
        )
    for local, v in (("Açores", 1890.68), ("Portugal", 1974.15)):
        add(
            "Q1.13",
            "Remuneração base média mensal",
            9,
            "Total",
            local,
            "2026-07-01",
            v,
            "p",
        )
        add(
            "Q1.13",
            "Remuneração base média mensal",
            9,
            "Total",
            local,
            "2026-04-01",
            v - 10,
        )
    scols = ["serie", "indicador", "rubrica", "local", "periodo", "data"]
    scols += ["valor", "unidade", "nota", "ficheiro", "pagina"]
    srows = [
        [
            "emprego",
            "População empregada",
            "Total",
            "Açores",
            "2026-T2",
            "2026-04-01",
            "122",
            "",
            "",
            "",
            "u",
        ],
        [
            "emprego",
            "População empregada",
            "Total",
            "Açores",
            "2026-T3",
            "2026-07-01",
            "2.5",
            "",
            "",
            "",
            "u",
        ],
        [
            "emprego",
            "População empregada por setor (CAE-Rev.4)",
            "P: Administração pública e defesa",
            "Açores",
            "2026-T3",
            "2026-07-01",
            "0.3",
            "",
            "",
            "",
            "u",
        ],
    ]
    sper = {
        "ano": 2024,
        "empresas": [
            {"nome": "SATA", "trabalhadores": 80, "ap": False},
            {"nome": "HDES", "trabalhadores": 70, "ap": True},
            {"nome": "Sem ficha", "ap": False},
        ],
    }
    d = publico.publico_data((cols, rows), (scols, srows), sper)
    assert d["data"] == "2026-09-30" and d["provisorio"]
    assert d["periodo"] == "30 de setembro de 2026"
    assert (d["ap"], d["ap_var"], d["ar"], d["ar_var"]) == (420, 20, 310, 10)
    assert d["ap_pct_pais"] == 4.2
    assert (d["fss"], d["outros"]) == (7, 103)
    # departments and the reclassified companies (last) add up to the total
    assert [x["nome"] for x in d["secretarias"]][
        0
    ] == "Educação, Cultura e Desporto"
    assert d["secretarias"][-1]["ser"] and d["secretarias_soma_ok"]
    # careers: groups only, no sub-rows, no zeros; the rest is "other"
    assert [c["nome"] for c in d["carreiras"]] == [
        "Médicos",
        "Dirigentes superiores",
    ]
    assert d["carreiras_resto"] == 420 - 35 - 20
    assert [e["ano"] for e in d["evolucao"]] == [2025, 2026]
    assert d["evolucao"][-1]["quando"] == "30 de setembro"
    assert d["salarios"]["acores"]["base"] == 1891
    assert d["salarios"]["mes"] == "julho de 2026"
    # 420 jobs in general government at the end of T3 + 80 in market
    # companies, out of 2 500 people in work
    w = d["peso"]
    assert (w["ap"], w["mercado"], w["publico"]) == (420, 80, 500)
    assert (w["publico_pct"], w["privado_pct"], w["um_em"]) == (20, 80, 5)
    assert w["periodo"] == "3.º trimestre de 2026" and w["setor_p_mil"] == 0.3
    assert publico.publico_data((cols, [])) == {}


def test_municipio_matches_spellings_and_skips_others():
    cs = [
        "Ribeira Grande",
        "Calheta (R.A.A.)",
        "Lagoa (R.A.A.)",
        "Vila da Praia da Vitória",
        "Santa Cruz das Flores",
        "Santa Cruz da Graciosa",
        "Ponta Delgada",
    ]
    m = camaras.municipio
    assert m("MUNICÍPIO DA RIBEIRA GRANDE", cs) == "Ribeira Grande"
    assert m("Municipio da  Ribeira Grande", cs) == "Ribeira Grande"
    assert m("Município de Calheta - São Jorge", cs) == "Calheta (R.A.A.)"
    assert m("Município de Lagoa (Açores)", cs) == "Lagoa (R.A.A.)"
    assert m("Município da Praia da Vitória", cs) == "Vila da Praia da Vitória"
    assert m("Município de Santa Cruz da Graciosa", cs) == (
        "Santa Cruz da Graciosa"
    )
    assert m("Câmara Municipal de Ponta Delgada", cs) == "Ponta Delgada"
    # Madeira's Calheta, the Algarve's Lagoa, SMAS and companies are not
    assert m("Município da Calheta", cs) == ""
    assert m("Município de Lagoa", cs) == ""
    assert m("SMAS Câmara Municipal de Ponta Delgada", cs) == ""
    assert m("Associação de Municípios da Ilha do Pico", cs) == ""
    assert m("Portos dos Açores, S.A.", cs) == ""


def test_camaras_data_per_inhabitant():
    cols = [
        "varcd",
        "nivel",
        "geocod",
        "local",
        "ilha",
        "categoria",
        "periodo",
        "valor",
    ]

    def r(v, nivel, geo, local, periodo, valor, ilha=""):
        return [v, nivel, geo, local, ilha, "", periodo, str(valor)]

    rows = []
    for geo, local, nivel, ilha, pop, desp in (
        ("2004901", "Corvo", "Concelho", "Corvo", 400, 2_000_000),
        (
            "2004203",
            "Ponta Delgada",
            "Concelho",
            "São Miguel",
            70_000,
            63_000_000,
        ),
        (
            "20",
            "Região Autónoma dos Açores",
            "Região",
            "",
            240_000,
            300_000_000,
        ),
        ("1", "Continente", "NUTS I", "", 1, 1),
    ):
        for ano, f in (("2021", 0.5), ("2025", 1)):
            rows.append(r("0012918", nivel, geo, local, ano, pop, ilha))
            rows.append(r("0013909", nivel, geo, local, ano, desp * f, ilha))
            rows.append(r("0013908", nivel, geo, local, ano, desp * f, ilha))
    base_cols = ["publicado", "adjudicante", "preco"]
    base = [
        ["2024-08-21", "Município do Corvo", "400000"],
        ["2025-01-02", "Município do Corvo", "40000"],
        ["2025-01-03", "Musami - Operações Municipais do Ambiente, EIM", "9"],
    ]
    # purchases by economic classifier (categoria) for Corvo, 2025
    for cat, v in (
        ("Aquisição de bens e serviços", 60_000),
        ("Aquisição de bens de capital", 20_000),
        ("Despesas com pessoal", 900_000),
    ):
        rows.append(
            [
                "0013909",
                "Concelho",
                "2004901",
                "Corvo",
                "Corvo",
                cat,
                "2025",
                str(v),
            ]
        )
    d = camaras.camaras_data((cols, rows), (base_cols, base))
    assert d["ano"] == "2025" and d["inicio"] == "2021"
    corvo, pdl = d["concelhos"]
    assert corvo["nome"] == "Corvo" and corvo["despesa_hab"] == 5000
    assert corvo["var_pct"] == 100
    # only the contracts published in the year of the spending (2025)
    assert corvo["contratos_n"] == 1 and corvo["contratos_hab"] == 100
    assert pdl["despesa_hab"] == 900 and "contratos_n" not in pdl
    assert d["sem_contratos"] == ["Ponta Delgada"]
    assert [x["nome"] for x in d["refs"]] == ["Açores"]
    assert d["base_de"] == "2025-01-02"
    k = d["compras"]
    assert k["anos"] == ["2021", "2025"]
    corvo_k = next(x for x in k["concelhos"] if x["nome"] == "Corvo")
    assert corvo_k["compras_m"] == 0.1 and corvo_k["pct"] == 50  # 40k / 80k
    assert corvo_k["pct_3a"] == 50  # the 2024 contract is outside the years
    assert (
        next(x for x in k["concelhos"] if x["nome"] == "Ponta Delgada")[
            "pct_3a"
        ]
        is None
    )
    assert len(d["grafico"]["pontos"]) == 2


def test_joraa_estado_backfill_note():
    line = {
        "datetime": "2026-11-28 01:30:00",
        "last_joraa_update": "2026-11-27",
    }
    assert parlamento.joraa_estado(line) == {}
    line["joraa_backfill"] = ["2026-08-12", "2026-11-05"]
    assert parlamento.joraa_estado(line) == {
        "atraso_de": "12/08/2026",
        "atraso_ate": "05/11/2026",
        "dias": 86,
    }
    # before the first run that plans a backfill
    old = {
        "datetime": "2026-11-27 09:26:17",
        "last_joraa_update": "2026-08-11",
    }
    assert parlamento.joraa_estado(old)["atraso_de"] == "12/08/2026"
    assert parlamento.joraa_estado(old)["atraso_ate"] == "26/11/2026"


def test_comparacao_acores_madeira_pais():
    cols = ["quadro", "rubrica", "local", "data", "valor", "provisorio"]
    rows = [
        ["Q1.7", "Total", "Açores", "2026-09-30", "25828", "p"],
        ["Q1.7", "Total", "Madeira", "2026-09-30", "27646", "p"],
        ["Q1.7", "Total", "Portugal", "2026-09-30", "764805", "p"],
        ["Q1.7", "Total", "Açores", "2025-12-31", "25000", ""],
        [
            "Q1.1",
            "ADMINISTRAÇÃO REGIONAL DOS AÇORES",
            "Açores",
            "2026-09-30",
            "19592",
            "p",
        ],
    ]
    icols = ["varcd", "geocod", "categoria", "valor", "data", "periodo"]
    q3 = ("2026-07-01", "3.º Trimestre de 2026")
    ine = [
        ["0012118", "20", "", "121300", *q3],
        ["0012118", "30", "", "137200", *q3],
        ["0012118", "PT", "", "5391000", *q3],
        ["0012118", "20", "", "119600", "2025-10-01", "4.º Trimestre de 2025"],
    ]
    k = publico._comparacao(
        [dict(zip(cols, r, strict=True)) for r in rows], (icols, ine)
    )
    assert k["data"] == "2026-09-30" and k["provisorio"]
    a, m, p = k["locais"]
    assert (a["local"], a["ap_pct"], a["ar_pct"]) == ("Açores", 21.3, 16.2)
    assert m["ap_pct"] == 20.2 and "ar" not in m
    assert p["ap_pct"] == 14.2
    # INE without the quarter: no comparison rather than a mismatched one
    assert (
        publico._comparacao(
            [dict(zip(cols, r, strict=True)) for r in rows], (icols, ine[3:])
        )
        == {}
    )


def test_ilhas_censos_sums_concelhos():
    cols = ["concelho", "ilha", "secao", "valor", "url"]
    u = "https://www.ine.pt/xurl/indx/0012344"
    rows = [
        ["Corvo", "Corvo", "O", "69", u],
        ["Corvo", "Corvo", "P", "14", u],
        ["Corvo", "Corvo", "Q", "26", u],
        ["Corvo", "Corvo", "Total", "219", u],
        ["Lajes das Flores", "Flores", "O", "200", u],
        ["Lajes das Flores", "Flores", "Total", "800", u],
        ["Santa Cruz das Flores", "Flores", "O", "281", u],
        ["Santa Cruz das Flores", "Flores", "Total", "891", u],
    ]
    il = publico._ilhas_censos((cols, rows))
    flores, corvo = il["lista"]  # in the islands' order, west last
    assert flores["empregados"] == 1691 and flores["o_pct"] == 28.4
    assert corvo["opq_pct"] == 49.8
    assert il["acores"]["empregados"] == 1910
    c = il["concelhos"]
    assert len(c) == 3
    assert [x["o_pct"] for x in c] == sorted(
        (x["o_pct"] for x in c), reverse=True
    )
    assert {x["nome"]: x["ilha"] for x in c}["Lajes das Flores"] == "Flores"


def test_salario_pib_latest_common_year():
    cols = ["varcd", "periodo", "geocod", "categoria", "valor", "url"]
    vals = {
        "0014103": {"20": 20000, "30": 25000, "PT": 24000},
        "0012749": {"20": 11000, "30": 11000, "PT": 12000},
        "0012656": {"20": 1000, "30": 1100, "PT": 1200},
    }
    rows = [
        [v, "2024", g, "", str(x), f"u{v}"]
        for v, d in vals.items()
        for g, x in d.items()
    ]
    rows.append(["0014103", "2025", "20", "", "21000", "u"])  # alone
    out = resumo.salario_pib(cols, rows)
    assert out["ano"] == "2024"
    a = out["locais"][0]
    assert a["local"] == "Açores" and a["mediana_pct"] == 55
    assert a["ganho_ano"] == 14000 and a["ganho_pct"] == 70
    assert resumo.salario_pib(cols, rows[:3]) == {}


def test_base_comes_from_impic_only(tmp_path):
    (tmp_path / "docs" / "_base_updates").mkdir(parents=True)
    (tmp_path / "docs" / "_base_updates" / "2025-10-01.md").write_text(
        "# BASE\n\n"
        "* [Fuelóleo](https://www.base.gov.pt/Base4/pt/detalhe/"
        "?type=contratos&id=11758845)\n"
        "  * Adjudicante: EDA\n  * Adjudicatário: BENCOM\n"
        "  * Preço contratual: 64.500.000,00 €\n"
        "* [Só no robô](https://www.base.gov.pt/Base4/pt/detalhe/"
        "?type=contratos&id=99)\n",
        encoding="utf-8",
    )
    folder = tmp_path / "data" / "base_impic"
    folder.mkdir(parents=True)
    from bot import base_impic

    def gz(name, rows):
        with gzip.open(folder / name, "wt", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(base_impic.COLS)
            w.writerows(rows)

    blank = [""] * (len(base_impic.COLS) - 1)

    def r(**kw):
        d = dict(zip(base_impic.COLS, ["", *blank], strict=True))
        d.update(kw)
        return [d[c] for c in base_impic.COLS]

    gz(
        "2025.csv.gz",
        [
            r(
                id="11758845",
                publicado="2025-09-30",
                preco="64500000.0",
                adjudicatario_nif="512002850",
                adjudicante_nif="512001306",
                concorrentes="1",
                propostas="1",
            )
        ],
    )
    gz(
        "2014.csv.gz",
        [
            r(
                id="1000",
                publicado="2014-03-02",
                preco="0.0",
                adjudicante="EDA",
                adjudicatario="BENCOM",
                adjudicatario_nif="-",
                procedimento="Ajuste Direto",
            )
        ],
    )
    meta = datasets.main(tmp_path / "docs")
    assert meta["base"]["linhas"] == 2
    assert meta["base"]["de"] == "2014-03-02"
    assert "diario_de" not in meta["base"]
    assert meta["base"]["anos"] == {"2025": 1, "2014": 1}  # newest first
    assert list(meta["base"]["anos"]) == ["2025", "2014"]
    assert (tmp_path / "docs" / "dados" / "base" / "2014.csv").exists()
    with open(
        tmp_path / "docs" / "dados" / "base.csv", encoding="utf-8-sig"
    ) as f:
        rows = {x["id"]: x for x in csv.DictReader(f)}
    assert "99" not in rows  # the daily pages are not read
    assert rows["11758845"]["publicado"] == "2025-09-30"
    assert "recolha" not in rows["11758845"]
    assert rows["11758845"]["concorrentes"] == "1"
    assert "adjudicatario_nif" not in rows["11758845"]  # only in contratos.db
    old = rows["1000"]
    assert old["preco"] == "0.0"
    assert old["url"].endswith("id=1000")
    con = sqlite3.connect(tmp_path / "docs" / "dados" / "contratos.db")
    assert con.execute(
        "select adjudicatario_nif, propostas from base where id = 11758845"
    ).fetchone() == ("512002850", 1)
    assert con.execute(
        "select adjudicatario_nif from base where id = 1000"
    ).fetchone()[0] in ("", None)


def test_at_regioes_sums_old_districts_only_when_needed():
    cols = [
        "imposto",
        "medida",
        "unidade",
        "ano",
        "distrito",
        "regiao",
        "valor",
    ]
    rows = [
        [
            "IRS",
            "Agregados",
            "agregados",
            "2019",
            "ANGRA DO HEROISMO",
            "Açores",
            "30",
        ],
        ["IRS", "Agregados", "agregados", "2019", "HORTA", "Açores", "10"],
        [
            "IRS",
            "Agregados",
            "agregados",
            "2019",
            "PONTA DELGADA",
            "Açores",
            "60",
        ],
        [
            "IRS",
            "Agregados",
            "agregados",
            "2019",
            "RA AÇORES",
            "Açores",
            "100",
        ],
        ["IRS", "Agregados", "agregados", "2018", "HORTA", "Açores", "9"],
        [
            "IRS",
            "Agregados",
            "agregados",
            "2018",
            "PONTA DELGADA",
            "Açores",
            "50",
        ],
        ["IRS", "Agregados", "agregados", "2018", "FUNCHAL", "Madeira", "70"],
        ["IRS", "Agregados", "agregados", "2018", "TOTAL:", "Total", "900"],
        ["IRS", "Taxa efetiva", "%", "2018", "HORTA", "Açores", "7"],
        ["IRS", "Taxa efetiva", "%", "2018", "PONTA DELGADA", "Açores", "8"],
        ["IRS", "Taxa efetiva", "%", "2018", "FUNCHAL", "Madeira", "9"],
    ]
    got = impostos.at_regioes((cols, rows), "IRS", "Agregados", "agregados")
    assert got["Açores"] == {2019: 100.0, 2018: 59.0}
    assert got["Madeira"] == {2018: 70.0}
    assert got["Total"] == {2018: 900.0}
    taxa = impostos.at_regioes((cols, rows), "IRS", "Taxa efetiva", "%")
    assert "Açores" not in taxa and taxa["Madeira"] == {2018: 9.0}


def test_write_dbs_one_file_per_theme(tmp_path):
    tables = {
        "tdc": (
            ["conta", "tipo", "texto", "referencia", "situacao"],
            [["2024", "reserva", "Texto", "", ""]],
        ),
        "bportugal": (
            ["indicador", "regiao", "data", "valor"],
            [["Depósitos", "Açores", "2026-10-31", "1.5"]],
        ),
    }
    info = sqlite.write_dbs(tmp_path, tables)
    assert set(info) == {"financas", "empresas"}
    assert info["empresas"]["tabelas"] == ["bportugal"]
    con = sqlite3.connect(tmp_path / "empresas.db")
    assert con.execute("select valor from bportugal").fetchone() == (1.5,)
    # bportugal has no FTS index
    names = {
        r[0]
        for r in con.execute(
            "select name from sqlite_master where type='table'"
        )
    }
    assert "bportugal_fts" not in names
    tables["nova"] = (["x"], [["1"]])
    try:
        sqlite.write_dbs(tmp_path, tables)
    except ValueError as e:
        assert "nova" in str(e)
    else:
        raise AssertionError("a table with no database must fail")


BP_COLS = [
    "conjunto",
    "indicador",
    "setor",
    "detalhe",
    "regiao",
    "data",
    "valor",
    "unidade",
    "serie",
]


def _bp(rows):
    return (BP_COLS, [[str(x) for x in r] for r in rows])


def test_credito_data_sums_the_country_and_works_out_its_ratios():
    d = "2026-10-31"
    rows = []
    for reg, emp, venc, dev, pct, depo in (
        ("Açores", 100, 2, 10, 5, 80),
        ("Norte", 300, 9, 30, 10, 400),
    ):
        rows += [
            [
                "emprestimos",
                "Empréstimos",
                "Particulares",
                "",
                reg,
                d,
                emp,
                "Milhões de euros",
                1,
            ],
            [
                "emprestimos",
                "Empréstimos vencidos",
                "Particulares",
                "",
                reg,
                d,
                venc,
                "Milhões de euros",
                2,
            ],
            [
                "emprestimos",
                "Devedores",
                "Particulares",
                "",
                reg,
                d,
                dev,
                "Milhares de devedores",
                3,
            ],
            [
                "emprestimos",
                "Devedores com empréstimos vencidos",
                "Particulares",
                "",
                reg,
                d,
                pct,
                "Percentagem",
                4,
            ],
            [
                "emprestimos",
                "Rácio de empréstimos vencidos",
                "Particulares",
                "",
                reg,
                d,
                2.0,
                "Percentagem",
                5,
            ],
            [
                "depositos",
                "Depósitos",
                "Particulares",
                "",
                reg,
                d,
                depo,
                "Milhões de euros",
                6,
            ],
        ]
    s = credito.bp_series(_bp(rows))
    k = ("emprestimos", "Empréstimos", "Particulares", "", "Milhões de euros")
    assert s[k]["Portugal"][d][0] == 400
    # percentages are never summed
    pk = (
        "emprestimos",
        "Rácio de empréstimos vencidos",
        "Particulares",
        "",
        "Percentagem",
    )
    assert "Portugal" not in s[pk]
    got = credito._vencidos(s, "Particulares", "", "Portugal", d)
    assert got["racio"] == 2.8  # 11 / 400
    assert got["devedores"] == 8.8  # (5*10 + 10*30) / 40
    assert (
        credito._vencidos(s, "Particulares", "", "Açores", d)["racio"] == 2.0
    )
    ine = (
        ["varcd", "periodo", "geocod", "valor"],
        [
            ["0012918", "2025", "20", "250000"],
            ["0012918", "2025", "PT", "10000000"],
        ],
    )
    out = credito.credito_data(_bp(rows), ine)
    assert out["ultimo_mes"] == "outubro de 2026"
    assert out["credito_depositos"]["acores"] == 125  # 100 / 80
    assert out["credito_depositos"]["pais"] == 83  # 400 / 480
    assert out["serie"][0]["periodo"] == "outubro de 2026"


def test_check_base_nif_errors_and_missing_entity():
    import datetime as dt

    def row(publicado, adj_nif="512063770", nif="512002850"):
        r = dict.fromkeys(base.BASE_ALL, "")
        r.update(
            publicado=publicado,
            adjudicante="Município de Vila do Porto",
            adjudicante_nif=adj_nif,
            adjudicatario_nif=nif,
        )
        return [r[c] for c in base.BASE_ALL]

    old = [
        row(f"{y}-{m:02d}-01")
        for y in (2022, 2023, 2024)
        for m in range(1, 13)
        if f"{y}-{m:02d}" < "2024-10"
    ]  # 12 a year until September 2024, then one in a year
    old += [row("2025-06-01", adj_nif="600000000")] * 12
    ok = base.check_base(
        old + [row("2025-10-01", nif="512002850 | ")], dt.date(2025, 10, 5)
    )
    assert ok["erros"] == []
    assert any("Município de Vila do Porto" in a for a in ok["avisos"])
    bad = base.check_base([row("2025-10-01", nif="-")], dt.date(2025, 10, 5))
    assert "adjudicatario_nif '-'" in bad["erros"][0]
    stale = base.check_base([row("2025-01-01")], dt.date(2025, 10, 5))
    assert stale["avisos"] == ["o contrato mais recente é de 2025-01-01"]
