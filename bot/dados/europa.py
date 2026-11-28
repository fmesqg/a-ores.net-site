"""Eurostat regional indicators (bot/eurostat.py): docs/_data/eurostat.json
(the latest-year table, rendered by Jekyll) and docs/dados/eurostat.json
(every year, for the chart on /dados/eurostat/)."""

import json
from pathlib import Path

from .comum import pt_num

# Eurostat flags shown on the page
ESTADOS = {
    "p": "provisório",
    "e": "estimado",
    "b": "quebra de série",
    "u": "pouco fiável (amostra pequena)",
    "d": "definição diferente",
    "bu": "quebra de série; pouco fiável",
    "pu": "provisório; pouco fiável",
    "du": "definição diferente; pouco fiável",
    "ep": "estimado; provisório",
    "bd": "quebra de série; definição diferente",
}


def _num(v: float, unidade: str) -> str:
    if unidade == "pessoas":
        return pt_num(round(v))
    if unidade in ("€", "PPC", "por mil hab.", "por 100 mil hab."):
        return pt_num(round(v))
    return pt_num(v)


def eurostat_data(cols: list[str], rows: list[list]) -> tuple[dict, dict]:
    """(page table, chart series). The table has, per indicator, each
    region's newest value and its year; the Azores' rank among the
    outermost regions with a value in the same year as the Azores'
    (1 = highest)."""
    ix = {c: i for i, c in enumerate(cols)}
    regioes: dict[str, dict] = {}
    ind: dict[str, dict] = {}
    for r in rows:
        g = r[ix["geo"]]
        regioes.setdefault(
            g, {"geo": g, "nome": r[ix["regiao"]], "grupo": r[ix["grupo"]]}
        )
        k = r[ix["indicador"]]
        d = ind.setdefault(
            k,
            {
                "id": k,
                "tema": r[ix["tema"]],
                "nome": r[ix["nome"]],
                "unidade": r[ix["unidade"]],
                "tabela": r[ix["tabela"]],
                "atualizado": r[ix["atualizado"]],
                "s": {},
            },
        )
        d["s"].setdefault(g, []).append(
            [int(r[ix["ano"]]), float(r[ix["valor"]]), r[ix["estado"]]]
        )
    for d in ind.values():
        for pts in d["s"].values():
            pts.sort()
    temas: list[dict] = []
    for d in ind.values():
        last = {g: pts[-1] for g, pts in d["s"].items()}
        az = last.get("PT20")
        rank = None
        if az:
            same = [
                p[1]
                for g, p in last.items()
                if regioes[g]["grupo"] in ("acores", "rup") and p[0] == az[0]
            ]
            if len(same) > 1:
                rank = [1 + sum(v > az[1] for v in same), len(same)]
        linha = {
            "id": d["id"],
            "nome": d["nome"],
            "unidade": d["unidade"],
            "tabela": d["tabela"],
            "ano": az[0] if az else None,
            "posicao": rank,
            "valores": {
                g: {
                    "v": _num(p[1], d["unidade"]),
                    "ano": p[0],
                    "estado": ESTADOS.get(p[2], p[2]),
                    "outro_ano": bool(az) and p[0] != az[0],
                }
                for g, p in last.items()
            },
        }
        if not temas or temas[-1]["tema"] != d["tema"]:
            temas.append({"tema": d["tema"], "linhas": []})
        temas[-1]["linhas"].append(linha)
    atual = max((d["atualizado"] for d in ind.values()), default="")
    tabela = {
        "regioes": list(regioes.values()),
        "temas": temas,
        "atualizado": atual,
    }
    series = {
        "regioes": list(regioes.values()),
        "indicadores": list(ind.values()),
    }
    return tabela, series


def write_eurostat(docs: Path, cols: list[str], rows: list[list]) -> None:
    tabela, series = eurostat_data(cols, rows)
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "eurostat.json").write_text(
        json.dumps(tabela, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (docs / "dados" / "eurostat.json").write_text(
        json.dumps(series, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
