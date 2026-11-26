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
