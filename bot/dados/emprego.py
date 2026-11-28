"""Registered unemployment (bot/desemprego.py) per concelho and island,
next to INE's resident population and RSI beneficiaries:
docs/_data/desemprego.json for /dados/desemprego/."""

import json
from pathlib import Path

from .comum import _dicts, _mes, pt_num

MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()
ILHA_DO_CONCELHO = {
    "2004101": "Santa Maria",
    "2004201": "São Miguel",
    "2004202": "São Miguel",
    "2004203": "São Miguel",
    "2004204": "São Miguel",
    "2004205": "São Miguel",
    "2004206": "São Miguel",
    "2004301": "Terceira",
    "2004302": "Terceira",
    "2004401": "Graciosa",
    "2004501": "São Jorge",
    "2004502": "São Jorge",
    "2004601": "Pico",
    "2004602": "Pico",
    "2004603": "Pico",
    "2004701": "Faial",
    "2004801": "Flores",
    "2004802": "Flores",
    "2004901": "Corvo",
}
POP = "0012918"  # População residente (N.º)
RSI = "0013420"  # RSI beneficiaries per 1000 inhabitants of working age


def _pct(x: float) -> str:
    s = f"{x:+.1f}".replace(".", ",").replace("-", "−")
    return s + " %"


def _menos(per: str, meses: int) -> str:
    y, m = map(int, per.split("-"))
    n = y * 12 + m - 1 - meses
    return f"{n // 12}-{n % 12 + 1:02d}"


def _ine(ine: list[dict], varcd: str) -> dict[str, tuple[str, float]]:
    """{geocod: (period, value)} of the newest period of an indicator."""
    out: dict[str, tuple[str, float]] = {}
    for r in ine:
        if r["varcd"] != varcd or r["categoria"] or not r["valor"]:
            continue
        g = r["geocod"]
        if g not in out or r["periodo"] > out[g][0]:
            out[g] = (r["periodo"], float(r["valor"]))
    return out


def desemprego_data(tables: dict) -> dict | None:
    if "desemprego" not in tables:
        return None
    rows = _dicts(tables["desemprego"])
    ine = _dicts(tables["ine"]) if "ine" in tables else []
    pop, rsi = _ine(ine, POP), _ine(ine, RSI)
    # islands: the sum of their concelhos (INE has no island rows)
    for g, (per, v) in list(pop.items()):
        if len(g) == 7 and g.startswith("200"):
            ilha = "200" + g[4]
            p0, v0 = pop.get(ilha, (per, 0))
            pop[ilha] = (per, v0 + v)
    des = [r for r in rows if r["tabela"] == "desemprego"]
    val = {(r["periodo"], r["geocod"]): r for r in des}
    meses = sorted({r["periodo"] for r in des})
    ult = meses[-1]
    hom, ant = _menos(ult, 12), _menos(ult, 1)

    def linha(r: dict) -> dict:
        g, t = r["geocod"], int(r["total"])
        d = {
            "nome": r["nome"],
            "geocod": g,
            "total": t,
            "total_txt": pt_num(t),
            "mulheres": round(100 * int(r["mulheres"]) / t) if t else "",
        }
        if g in pop:
            d["por_mil"] = round(1000 * t / pop[g][1], 1)
            d["por_mil_txt"] = f"{d['por_mil']:.1f}".replace(".", ",")
        h = val.get((hom, g))
        if h and int(h["total"]):
            d["homologa"] = _pct(100 * (t / int(h["total"]) - 1))
            d["subiu"] = t > int(h["total"])
        if g in rsi:
            d["rsi"] = pt_num(rsi[g][1])
        if g in ILHA_DO_CONCELHO:
            d["ilha"] = ILHA_DO_CONCELHO[g]
        return d

    ultimos = [r for r in des if r["periodo"] == ult]
    concelhos = sorted(
        (linha(r) for r in ultimos if r["nivel"] == "concelho"),
        key=lambda d: -d.get("por_mil", 0),
    )
    ilhas = [linha(r) for r in ultimos if r["nivel"] == "ilha"]
    regiao = linha(next(r for r in ultimos if r["nivel"] == "regiao"))
    a = val.get((ant, "20"))
    if a:
        regiao["mensal"] = _pct(100 * (regiao["total"] / int(a["total"]) - 1))
    # the region month by month: one row per year
    anos = sorted({p[:4] for p in meses}, reverse=True)
    grelha = []
    for y in anos:
        cel = []
        for m in range(1, 13):
            r = val.get((f"{y}-{m:02d}", "20"))
            cel.append(pt_num(int(r["total"])) if r else "")
        grelha.append({"ano": y, "meses": cel})
    # schemes and placements, newest month; placements also over 12 months
    medidas = [
        {"nome": r["nome"], "total": pt_num(int(r["total"]))}
        for r in rows
        if r["tabela"] == "medidas" and r["periodo"] == ult
    ]
    doze = {_menos(ult, i) for i in range(12)}
    coloc: dict[str, list[int]] = {}
    for r in rows:
        if r["tabela"] == "colocacoes" and r["periodo"] in doze:
            c = coloc.setdefault((r["geocod"], r["nome"]), [0, 0])
            c[0] += int(r["total"]) if r["periodo"] == ult else 0
            c[1] += int(r["total"])
    meses_coloc = len(
        {
            r["periodo"]
            for r in rows
            if r["tabela"] == "colocacoes" and r["periodo"] in doze
        }
    )
    colocacoes = [
        {"nome": k[1], "mes": pt_num(v[0]), "doze": pt_num(v[1])}
        # islands by code, the region last
        for k, v in sorted(
            coloc.items(), key=lambda kv: (kv[0][0] == "20", kv[0][0])
        )
    ]
    oferta = next(
        (
            pt_num(int(r["total"]))
            for r in rows
            if r["tabela"] == "ofertas" and r["periodo"] == ult
        ),
        "",
    )
    ano_pop = next(iter(pop.values()))[0] if pop else ""
    ano_rsi = next(iter(rsi.values()))[0] if rsi else ""
    return {
        "periodo": ult,
        "mes": _mes(ult),
        "mes_homologo": _mes(hom),
        "primeiro": _mes(meses[0]),
        "n_meses": len(meses),
        "regiao": regiao,
        "ilhas": ilhas,
        "concelhos": concelhos,
        "grelha": grelha,
        "meses_nomes": MESES,
        "medidas": medidas,
        "colocacoes": colocacoes,
        "meses_coloc": meses_coloc,
        "ofertas": oferta,
        "ano_pop": ano_pop,
        "ano_rsi": ano_rsi,
    }


def write_desemprego(docs: Path, tables: dict) -> None:
    data = desemprego_data(tables)
    if data is None:
        return
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "desemprego.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8"
    )
