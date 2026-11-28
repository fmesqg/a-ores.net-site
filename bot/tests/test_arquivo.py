import datetime as dt

from bot import arquivo
from bot.dados.parlamento import (
    ALRA_COLS,
    JORAA_COLS,
    build_alra,
    build_joraa,
    read_archive,
)

HEAD = "---\ndate: {d}\nlayout: default\n---\n"
REQ = "http://base.alra.pt:82/4DACTION/w_pesquisa_registo/4/9641"
ATO = "https://jo.azores.gov.pt/#/ato/55e469c0"


def alra_page(estado_line: str) -> str:
    return (
        "## ALRA\n\n### Requerimentos\n\n"
        f"* [Impacto do SAFE]({REQ})\n"
        f"  * {estado_line}\n"
        "  * [requerimento](http://x/r.pdf)( data entrada: 26/10/2026)\n"
        "  * Requerente(s): Berto Messias PS\n"
    )


JORAA = (
    "## JORAA\n\n"
    f"* [Ampliação do Cemitério]({ATO})\n"
    "  * Acordo de cooperação n.º 234/2026 de 27 de novembro de 2026\n"
    "  * Montante: 100 000,00 € (valor)\n"
    "  * Presidência do Governo\n"
    "  * Junta de Freguesia de Achada\n"
    "  * Jornal Oficial II Série - Número 229\n"
)


def write(docs, coll, day, body):
    (docs / coll).mkdir(parents=True, exist_ok=True)
    (docs / coll / f"{day}.md").write_text(
        HEAD.format(d=day) + body, encoding="utf-8"
    )


def test_joraa_keeps_the_beneficiary(tmp_path):
    write(tmp_path, "_joraa_updates", "2026-11-27", JORAA)
    (r,) = build_joraa(tmp_path)
    row = dict(zip(JORAA_COLS, r, strict=True))
    assert row["entidade"] == "Presidência do Governo"
    assert row["outros"] == "Junta de Freguesia de Achada"
    assert row["montante"] == 100000.0


def test_alra_history_and_old_page_does_not_overwrite(tmp_path):
    write(
        tmp_path,
        "_alra_updates",
        "2026-11-26",
        alra_page("Alteração do estado: NO PRAZO → FORA DE PRAZO"),
    )
    (r,) = build_alra(tmp_path)
    row = dict(zip(ALRA_COLS, r, strict=True))
    assert row["historico"] == "2026-11-26 NO PRAZO → FORA DE PRAZO"
    # later the archive has a newer state; an older page comes back
    newer = list(r)
    newer[4], newer[6] = "RESPONDIDO", "2026-12-10"
    newer[11] += " | 2026-12-10 FORA DE PRAZO → RESPONDIDO"
    write(
        tmp_path,
        "_alra_updates",
        "2026-11-20",
        alra_page("Alteração do estado: ENTRADO → NO PRAZO"),
    )
    (r2,) = build_alra(tmp_path, [newer])
    row = dict(zip(ALRA_COLS, r2, strict=True))
    assert row["estado"] == "RESPONDIDO" and row["ultimo_dia"] == "2026-12-10"
    assert row["primeiro_dia"] == "2026-11-20"
    assert row["historico"].split(" | ") == [
        "2026-11-20 ENTRADO → NO PRAZO",
        "2026-11-26 NO PRAZO → FORA DE PRAZO",
        "2026-12-10 FORA DE PRAZO → RESPONDIDO",
    ]


def test_arquivo_folds_and_ages_out(tmp_path):
    docs, data = tmp_path / "docs", tmp_path / "data"
    data.mkdir()
    write(docs, "_joraa_updates", "2026-01-05", JORAA)
    write(docs, "_joraa_updates", "2026-11-27", JORAA.replace("55e4", "aaaa"))
    write(docs, "_alra_updates", "2026-01-05", alra_page("Estado: NO PRAZO"))
    write(docs, "_base_updates", "2026-01-05", "## BASE\n")
    assert arquivo.main(tmp_path, hoje=dt.date(2026, 11, 28)) == 0
    left = sorted(p.name for p in docs.rglob("*.md"))
    assert left == ["2026-11-27.md"]
    rows = read_archive(data / "joraa.csv.gz", JORAA_COLS)
    assert len(rows) == 2
    assert len(read_archive(data / "alra.csv.gz", ALRA_COLS)) == 1
    before = (data / "joraa.csv.gz").read_bytes()
    assert arquivo.main(tmp_path, hoje=dt.date(2026, 11, 28)) == 0
    assert (data / "joraa.csv.gz").read_bytes() == before  # idempotent


def test_arquivo_keeps_pages_it_cannot_account_for(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    (tmp_path / "data").mkdir()
    write(docs, "_joraa_updates", "2026-01-05", JORAA)
    write(docs, "_base_updates", "2026-01-05", "## BASE\n")
    # a builder that loses the act: nothing may be deleted
    monkeypatch.setitem(
        arquivo.FONTES,
        "_joraa_updates",
        ("joraa.csv.gz", JORAA_COLS, lambda docs, base: []),
    )
    assert arquivo.main(tmp_path, hoje=dt.date(2026, 11, 28)) == 1
    assert len(list(docs.rglob("*.md"))) == 2
