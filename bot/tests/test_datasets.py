import csv
import json
import sqlite3

from bot import datasets

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


def test_euros_both_conventions():
    assert datasets.euros("120.963,33 €", ",") == 120963.33
    assert datasets.euros("12,987,000.00 €", ".") == 12987000.0
    assert datasets.euros("", ",") is None


def test_iso_dates():
    assert datasets.iso("14-10-2026") == "2026-10-14"
    assert datasets.iso("( data entrada: 1/2/2026)") == "2026-02-01"
    assert datasets.iso("sem data") == ""


def test_build_all(tmp_path):
    for coll, name, text in (
        ("_base_updates", "2026-11-25", BASE_DAY),
        ("_base_updates", "2026-11-26", BASE_DAY),  # republished: one row
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
    assert j["entidade"].startswith("Secretaria Regional da Educação")

    assert meta["base"]["linhas"] == 1
    assert json.loads((out / "meta.json").read_text())["base"]["ate"] == (
        "2026-11-26"
    )


def test_sqlite_fts(tmp_path):
    (tmp_path / "_base_updates").mkdir()
    (tmp_path / "_base_updates" / "2026-11-25.md").write_text(
        BASE_DAY, encoding="utf-8"
    )
    for coll in ("_alra_updates", "_joraa_updates"):
        (tmp_path / coll).mkdir()
    (tmp_path / "_alra_updates" / "2026-11-25.md").write_text(
        ALRA_DAY, encoding="utf-8"
    )
    (tmp_path / "_joraa_updates" / "2024-08-21.md").write_text(
        JORAA_DAY, encoding="utf-8"
    )
    datasets.main(tmp_path)
    con = sqlite3.connect(tmp_path / "dados" / "acores.db")
    preco, tipo = con.execute(
        "select preco, typeof(preco) from base join base_fts "
        "on base_fts.rowid = base.rowid where base_fts match 'angustias'"
    ).fetchone()  # accent-insensitive: "Angústias"
    assert (preco, tipo) == (120963.33, "real")
    assert con.execute(
        "select count(*) from alra where resposta is null"
    ).fetchone() == (2,)


def test_pt_num():
    assert datasets.pt_num(245328) == "245 328"
    assert datasets.pt_num(39.38) == "39,4"
    assert datasets.pt_num(5.94) == "5,94"
    assert datasets.pt_num(75.0) == "75"
    assert datasets.pt_num(-198.5) == "-198"


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
    datasets.write_resumo(
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
