"""National exam results (bot/exames.py) for /dados/exames/:
docs/_data/exames.json, rendered by Jekyll."""

import json
from pathlib import Path

from .comum import pt_num

NIVEIS = {
    "secundario": {
        "nome": "Ensino secundário: exames nacionais",
        "escala": "0 a 200",
        "interna": "a classificação interna final (0 a 20)",
        "casas": 1,
        "principais": {"639": "Português", "635": "Matemática A"},
    },
    "basico": {
        "nome": "9.º ano: provas finais",
        "escala": "0 a 100",
        "interna": "o nível interno (1 a 5)",
        "casas": 2,
        "principais": {"91": "Português", "92": "Matemática"},
    },
}
REGIOES = ["AZ", "MD", "CO", "PT"]
# an exam enters the regions table when the Azores had this many
MIN_AZ = 100


def _d1(x: float) -> str:
    """Exam means with one decimal (pt_num drops decimals from 100 up)."""
    return f"{x:.1f}".replace(".", ",").replace("-", "\u2212")


def _f(v: str) -> float | None:
    return float(v) if v not in ("", None) else None


def exames_data(cols: list[str], rows: list[list]) -> dict:
    ix = {c: i for i, c in enumerate(cols)}
    recs = [{c: r[i] for c, i in ix.items()} for r in rows]
    out = {"niveis": []}
    for nivel, meta in NIVEIS.items():
        rs = [r for r in recs if r["nivel"] == nivel]
        if not rs:
            continue
        anos = sorted({int(r["ano"]) for r in rs})
        ano = anos[-1]
        ult = [r for r in rs if int(r["ano"]) == ano]
        reg = {
            (r["codigo"], r["exame"]): r for r in ult if r["tipo"] == "regiao"
        }
        exames = sorted(
            (
                r
                for r in ult
                if r["tipo"] == "regiao"
                and r["codigo"] == "AZ"
                and r["exame"] != "todos"
                and int(r["provas"]) >= MIN_AZ
            ),
            key=lambda r: -int(r["provas"]),
        )
        linhas = []
        for e in [("todos", None)] + [(r["exame"], r) for r in exames]:
            ex = e[0]
            az, pt = reg.get(("AZ", ex)), reg.get(("PT", ex))
            if not az:
                continue
            dif = float(az["media"]) - float(pt["media"]) if pt else None
            linhas.append(
                {
                    "exame": az["exame_nome"],
                    "todos": ex == "todos",
                    "provas_az": pt_num(int(az["provas"])),
                    "medias": {
                        g: _d1(float(reg[(g, ex)]["media"]))
                        for g in REGIOES
                        if (g, ex) in reg
                    },
                    "positivas_az": pt_num(float(az["positivas"])),
                    "positivas_pt": (
                        pt_num(float(pt["positivas"])) if pt else ""
                    ),
                    "dif": (
                        ("+" if dif > 0 else "") + _d1(dif)
                        if dif is not None
                        else ""
                    ),
                    "abaixo": dif is not None and dif < 0,
                }
            )
        # schools: newest year, with the mean of each year and the two
        # main exams
        hist: dict[str, dict] = {}
        for r in rs:
            if r["tipo"] == "escola" and r["exame"] == "todos":
                hist.setdefault(r["codigo"], {})[int(r["ano"])] = r["media"]
        por_exame = {
            (r["codigo"], r["exame"]): r
            for r in ult
            if r["tipo"] == "escola" and r["exame"] in meta["principais"]
        }
        escolas = []
        for r in ult:
            if r["tipo"] != "escola" or r["exame"] != "todos":
                continue
            interna = _f(r["media_interna"])
            escolas.append(
                {
                    "nome": r["nome"],
                    "concelho": r["concelho"],
                    "privada": r["publico"] == "PRI",
                    "provas": int(r["provas"]),
                    "media_n": float(r["media"]),
                    "media": _d1(float(r["media"])),
                    "interna": (
                        f"{interna:.{meta['casas']}f}".replace(".", ",")
                        if interna is not None
                        else ""
                    ),
                    "positivas": pt_num(float(r["positivas"])),
                    "posicao": r["posicao"],
                    "n_escolas": r["n_escolas"],
                    "anos": [
                        (
                            _d1(float(hist[r["codigo"]][a]))
                            if a in hist[r["codigo"]]
                            else ""
                        )
                        for a in anos
                    ],
                    "principais": [
                        (
                            _d1(float(por_exame[(r["codigo"], e)]["media"]))
                            if (r["codigo"], e) in por_exame
                            else ""
                        )
                        for e in meta["principais"]
                    ],
                }
            )
        escolas.sort(key=lambda e: -e["media_n"])
        todos_az = reg.get(("AZ", "todos"))
        todos_pt = reg.get(("PT", "todos"))
        out["niveis"].append(
            {
                "id": nivel,
                "nome": meta["nome"],
                "escala": meta["escala"],
                "interna": meta["interna"],
                "ano": ano,
                "anos": anos,
                "linhas": linhas,
                "escolas": escolas,
                "principais": list(meta["principais"].values()),
                "min_provas": 50,
                "n_escolas": next(
                    (e["n_escolas"] for e in escolas if e["n_escolas"]), ""
                ),
                "media_az": _d1(float(todos_az["media"])),
                "media_pt": _d1(float(todos_pt["media"])),
            }
        )
    return out


def write_exames(docs: Path, cols: list[str], rows: list[list]) -> None:
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "exames.json").write_text(
        json.dumps(exames_data(cols, rows), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
