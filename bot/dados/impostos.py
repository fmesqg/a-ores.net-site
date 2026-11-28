"""IRS and IRC from the AT's statistics: docs/_data/irs.json and irc.json."""

import json
import re
from pathlib import Path

from .comum import _dicts, _fold, _texts, pt_num


def irs_data(at: tuple[list, list]) -> dict:
    """docs/_data/irs.json for /dados/irs/: IRS by tax bracket in the
    Azores in the latest year (AT), the top bracket year by year against
    Madeira, and the additional solidarity rate."""
    rows = [
        r
        for r in _dicts(at)
        if r["titularidade"] == "Total"
        and r["quadro"] == "Taxas de tributação"
    ]
    if not rows:
        return {}
    by: dict = {}
    for r in rows:
        by.setdefault((r["medida"], r["regiao"], int(r["ano"])), {})[
            int(r["escalao"])
        ] = (float(r["taxa"]), float(r["valor"]))
    anos = sorted({k[2] for k in by})
    ano = anos[-1]

    def pct(x: float | None) -> str:
        # rates keep every decimal (11,55 %, not 11,6 %)
        return "" if x is None else f"{x:g} %".replace(".", ",")

    def tab(medida: str, regiao: str, a: int) -> dict:
        return by.get((medida, regiao, a), {})

    agr = tab("Agregados", "Açores", ano)
    ren = tab("Rendimento englobado", "Açores", ano)
    irs = tab("IRS liquidado", "Açores", ano)
    cont = tab("Agregados", "Continente", ano)
    tot_a = sum(v for _, v in agr.values())
    tot_r = sum(v for _, v in ren.values())
    tot_i = sum(v for _, v in irs.values())
    escaloes = []
    for o in sorted(agr):
        n = agr[o][1]
        i = irs.get(o, (0, 0))[1]
        escaloes.append(
            {
                "ordem": o,
                "taxa_s": pct(agr[o][0]),
                "taxa_continente_s": pct(cont.get(o, (None, None))[0]),
                "agregados": int(n),
                "agregados_pct": round(100 * n / tot_a, 1),
                "rendimento_m": round(ren.get(o, (0, 0))[1] / 1e6, 1),
                "irs_m": round(i / 1e6, 1),
                "irs_pct": round(100 * i / tot_i, 1),
                "irs_medio": round(i / n) if n else 0,
            }
        )
    serie = []
    for a in anos:
        linha: dict = {"ano": a}
        for regiao, k in (("Açores", "acores"), ("Madeira", "madeira")):
            g = tab("Agregados", regiao, a)
            t = tab("IRS liquidado", regiao, a)
            if not g:
                continue
            topo = max(g)
            total = sum(v for _, v in g.values())
            linha[k] = int(g[topo][1])
            linha[k + "_taxa_s"] = pct(g[topo][0])
            linha[k + "_por_mil"] = round(1000 * g[topo][1] / total, 1)
            if t:
                linha[k + "_irs_pct"] = round(
                    100 * t[topo][1] / sum(v for _, v in t.values()), 1
                )
        serie.append(linha)
    adicional = {}
    for r in _dicts(at):
        if r["quadro"] != "Taxa adicional de solidariedade":
            continue
        if r["regiao"] != "Açores":
            continue
        d = adicional.setdefault(int(r["ano"]), {"ano": int(r["ano"])})
        k = "agregados" if r["medida"] == "Agregados" else "irs"
        d[k] = d.get(k, 0) + float(r["valor"])
    adic = []
    for a in sorted(adicional):
        d = adicional[a]
        adic.append(
            {
                "ano": a,
                "agregados": int(d.get("agregados", 0)),
                "irs_m": round(d.get("irs", 0) / 1e6, 2),
            }
        )
    fonte = next(
        r
        for r in _dicts(at)
        if int(r["ano"]) == ano and r["regiao"] == "Açores"
    )
    topo = escaloes[-1] if escaloes else {}
    return {
        "ano": ano,
        "primeiro": anos[0],
        "agregados": int(tot_a),
        "rendimento_m": round(tot_r / 1e6, 1),
        "irs_m": round(tot_i / 1e6, 1),
        "taxa_media": round(100 * tot_i / tot_r, 1) if tot_r else 0,
        "escaloes": escaloes,
        "topo": topo,
        "serie": serie,
        "adicional": adic,
        "dossie": fonte["dossie"],
        "url": fonte["url"],
    }


def at_regioes(
    dist: tuple[list, list], imposto: str, medida: str, unidade: str
) -> dict[str, dict[int, float]]:
    """{regiao: {ano: valor}} from at_distritos. The AT's regional total
    when it prints one ("R. A. Açores", "RA MADEIRA", "TOTAL"); else, for
    the years it only prints the old districts, their sum (Angra, Horta
    and Ponta Delgada; Funchal is all of Madeira). Rates of the three
    Azorean districts cannot be added, so those years stay empty."""
    tot: dict[str, dict[int, float]] = {}
    parts: dict[str, dict[int, list]] = {}
    for r in _dicts(dist):
        if (r["imposto"], r["medida"], r["unidade"]) != (
            imposto,
            medida,
            unidade,
        ):
            continue
        reg, ano, v = r["regiao"], int(r["ano"]), float(r["valor"])
        lab = _fold(r["distrito"])
        if reg == "Total" or "acores" in lab or "madeira" in lab:
            tot.setdefault(reg, {})[ano] = v
        elif reg in ("Açores", "Madeira"):
            parts.setdefault(reg, {}).setdefault(ano, []).append(v)
    for reg, anos in parts.items():
        for ano, vs in anos.items():
            if ano in tot.get(reg, {}):
                continue
            if unidade != "%" or len(vs) == 1:
                tot.setdefault(reg, {})[ano] = sum(vs)
    return tot


def _pct_s(x: float | None) -> str:
    # rates keep every decimal (11,55 %, not 11,6 %)
    return "" if x is None else f"{x:g} %".replace(".", ",")


def _share(a: float | None, b: float | None) -> float | str:
    return round(100 * a / b, 1) if a and b else ""


def irs_pais(dist: tuple[list, list]) -> list[dict]:
    """IRS by region, year by year, from the 'por distrito' maps:
    households, tax, tax per household and the shares of the country."""
    g = {
        k: at_regioes(dist, "IRS", m, u)
        for k, m, u in (
            ("agr", "Agregados", "agregados"),
            ("irs", "IRS liquidado", "€"),
        )
    }
    out = []
    for a in sorted(g["irs"].get("Açores", {})):
        linha: dict = {"ano": a}
        for reg, k in (
            ("Açores", "acores"),
            ("Madeira", "madeira"),
            ("Total", "pais"),
        ):
            n = g["agr"].get(reg, {}).get(a)
            v = g["irs"].get(reg, {}).get(a)
            if not (n and v):
                continue
            linha[k + "_agregados"] = int(n)
            linha[k + "_irs_m"] = round(v / 1e6, 1)
            linha[k + "_por_agregado"] = round(v / n)
        tot_n = g["agr"].get("Total", {}).get(a)
        tot_v = g["irs"].get("Total", {}).get(a)
        linha["acores_agregados_pct"] = _share(
            g["agr"].get("Açores", {}).get(a), tot_n
        )
        linha["acores_irs_pct"] = _share(
            g["irs"].get("Açores", {}).get(a), tot_v
        )
        out.append(linha)
    return out


def irs_gerais(at: tuple[list, list]) -> dict:
    """The general IRS rates of the latest year, a row per bracket."""
    rows = [r for r in _dicts(at) if r["quadro"] == "Taxas gerais"]
    if not rows:
        return {}
    ano = max(int(r["ano"]) for r in rows)
    by: dict[int, dict] = {}
    for r in rows:
        if int(r["ano"]) != ano:
            continue
        o = int(r["escalao"])
        d = by.setdefault(o, {"ordem": o})
        d[
            {
                "Continente": "continente",
                "Açores": "acores",
                "Madeira": "madeira",
            }[r["regiao"]]
            + "_s"
        ] = _pct_s(float(r["taxa"]))
        d["limite"] = r["valor"]
    escaloes = []
    anterior = None
    for o in sorted(by):
        d = by[o]
        lim = float(d.pop("limite")) if d.get("limite") else None
        de = f"{pt_num(anterior)} €" if anterior else ""
        ate = f"{pt_num(lim)} €" if lim else ""
        d["escalao"] = (
            f"até {ate}"
            if not de
            else f"de {de} a {ate}" if ate else f"acima de {de}"
        )
        anterior = lim
        escaloes.append(d)
    return {"ano": ano, "escaloes": escaloes}


def write_irs(docs: Path, tables: dict) -> None:
    data = irs_data(tables["at_irs"]) if "at_irs" in tables else {}
    if data:
        if "at_distritos" in tables:
            data["pais"] = irs_pais(tables["at_distritos"])
        data["gerais"] = irs_gerais(tables["at_irs"])
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "irs.json").write_text(
        json.dumps(_texts(data), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )


def _primeiro_num(s: str) -> float:
    """'Mais de 1.500.000 a 7.500.000' -> 1500000."""
    m = re.search(r"\d[\d.]*", s)
    return float(m[0].replace(".", "")) if m else 0.0


def irc_data(dist: tuple[list, list], irc: tuple[list, list]) -> dict:
    """docs/_data/irc.json for /dados/irc/: IRC in the Azores year by year
    (AT, Dossier Estatístico IRC), against Madeira and the country."""
    g = {
        k: at_regioes(dist, "IRC", m, u)
        for k, m, u in (
            ("decl", "Declarações", "declarações"),
            ("lucro", "Lucro tributável", "€"),
            ("prej", "Prejuízo fiscal", "€"),
            ("mc", "Matéria coletável", "€"),
            ("liq", "IRC liquidado", "€"),
            ("taxa", "Taxa média efetiva", "%"),
        )
    }
    anos = sorted(g["liq"].get("Açores", {}))
    if not anos:
        return {}
    linhas = _dicts(irc)

    def quadro(q: str, reg: str, unidade: str, escalao: str | None = None):
        return {
            int(r["ano"]): float(r["valor"])
            for r in linhas
            if r["quadro"] == q
            and r["regiao"] == reg
            and r["unidade"] == unidade
            and (escalao is None or r["escalao"] == escalao)
        }

    regional = quadro("Cálculo do imposto", "Açores", "€")
    regional_n = quadro("Cálculo do imposto", "Açores", "declarações")
    derrama = quadro("Derrama estadual", "Açores", "€", "Total")
    derrama_n = quadro("Derrama estadual", "Açores", "declarações", "Total")

    def v(k: str, a: int, reg: str = "Açores"):
        return g[k].get(reg, {}).get(a)

    def m(x: float | None) -> float | str:
        return "" if x is None else round(x / 1e6, 1)

    serie = []
    for a in anos:
        serie.append(
            {
                "ano": a,
                "declaracoes": int(v("decl", a) or 0),
                "lucro_m": m(v("lucro", a)),
                "prejuizo_m": m(v("prej", a)),
                "irc_m": m(v("liq", a)),
                "regional_m": m(regional.get(a)),
                "decl_pct": _share(v("decl", a), v("decl", a, "Total")),
                "irc_pct": _share(v("liq", a), v("liq", a, "Total")),
                "taxa_s": _pct_s(v("taxa", a)),
                "taxa_madeira_s": _pct_s(v("taxa", a, "Madeira")),
                "taxa_pais_s": _pct_s(v("taxa", a, "Total")),
                "derrama_m": m(derrama.get(a)) if a in derrama else "",
                "derrama_n": int(derrama_n[a]) if a in derrama_n else "",
            }
        )
    ano = anos[-1]
    ultimo = serie[-1]
    escaloes = [
        {
            "escalao": r["escalao"],
            "declaracoes": int(
                next(
                    (
                        float(x["valor"])
                        for x in linhas
                        if x["quadro"] == "Derrama estadual"
                        and x["regiao"] == "Açores"
                        and x["unidade"] == "declarações"
                        and x["ano"] == r["ano"]
                        and x["escalao"] == r["escalao"]
                    ),
                    0,
                )
            ),
            "valor_m": round(float(r["valor"]) / 1e6, 2),
        }
        for r in linhas
        if r["quadro"] == "Derrama estadual"
        and r["regiao"] == "Açores"
        and r["unidade"] == "€"
        and int(r["ano"]) == ano
        and r["escalao"] != "Total"
    ]
    escaloes.sort(key=lambda e: _primeiro_num(e["escalao"]))
    nominais: dict[str, dict] = {}
    for r in linhas:
        if r["quadro"] != "Taxas nominais" or int(r["ano"]) != ano:
            continue
        d = nominais.setdefault(r["escalao"], {"designacao": r["escalao"]})
        key = {
            "Continente": "continente",
            "Açores": "acores",
            "Madeira": "madeira",
        }
        d[key[r["regiao"]] + "_s"] = _pct_s(float(r["valor"]))
    fonte = next(
        r
        for r in _dicts(dist)
        if r["imposto"] == "IRC" and int(r["ano"]) == ano
    )
    # the general rate first, then the reduced and the normal rate
    ordem = sorted(
        nominais, key=lambda k: (not k.startswith("Taxa geral"), "<=" not in k)
    )
    return {
        "ano": ano,
        "primeiro": anos[0],
        "ultimo": ultimo,
        "lucro_cresc": _share(v("lucro", ano), v("lucro", anos[0])),
        "regional_n": int(regional_n.get(ano, 0)),
        "serie": serie,
        "derrama_escaloes": escaloes,
        "nominais": [nominais[k] for k in ordem],
        "dossie": fonte["dossie"],
        "url": fonte["url"],
    }


def write_irc(docs: Path, tables: dict) -> None:
    data = {}
    if "at_distritos" in tables and "at_irc" in tables:
        data = irc_data(tables["at_distritos"], tables["at_irc"])
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "irc.json").write_text(
        json.dumps(_texts(data), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
