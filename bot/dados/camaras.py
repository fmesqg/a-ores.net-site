"""The 19 câmaras municipais per inhabitant (INE) next to their BASE contracts: docs/_data/camaras.json."""

import json
import re
from pathlib import Path

from .comum import _dicts, _texts, _words

# /financas/camaras/: the 19 câmaras municipais per inhabitant, next to other
# sources for the same concelho.
CAMARAS_IND = {
    "pop": "0012918",
    "receita": "0013908",
    "despesa": "0013909",
    "rnf_hab": "0013899",
    "rendimento": "0012757",
    "dormidas": "0013210",
    "rsi": "0013420",
}
REFS = {"20": "Açores", "30": "Madeira", "PT": "Portugal"}
NAO_CAMARA = re.compile(
    r"associacao|servicos municipalizados|smas|operacoes municipais|"
    r"empresa municipal|\bei ?m\b|comunidade|comercio"
)
# the same name exists in mainland Portugal or Madeira
AMBIGUO = {"calheta": r"jorge|acores|raa", "lagoa": r"acores|raa"}


def municipio(adjudicante: str, concelhos: list[str]) -> str:
    """The concelho whose câmara is the BASE adjudicante, or "" (also for
    SMAS, municipal companies and associations of municipalities). BASE has
    several spellings: "Município de Lagoa (Açores)", "Câmara Municipal de
    Nordeste", "MUNICÍPIO DA RIBEIRA GRANDE", "Municipio da  Ribeira Grande".
    """
    n = _words(adjudicante)
    if not re.search(r"\b(municipio|camara municipal)\b", n):
        return ""
    if NAO_CAMARA.search(n):
        return ""
    keys = []
    for c in concelhos:
        k = _words(re.sub(r"\(R\.A\.A\.\)", "", c))
        keys.append((k.removeprefix("vila da "), c))
    for k, c in sorted(keys, key=lambda kc: -len(kc[0])):
        if re.search(rf"\b{k}\b", n):
            if k in AMBIGUO and not re.search(AMBIGUO[k], n):
                return ""
            return c
    return ""


def camaras_data(
    ine: tuple[list, list], base: tuple[list, list] | None = None
) -> dict:
    """Receitas and despesas of each câmara municipal per inhabitant (INE),
    with income, tourism and RSI for the same concelho and the contracts the
    câmara signed in BASE."""
    rows = [r for r in _dicts(ine) if r["varcd"] in CAMARAS_IND.values()]
    if not rows:
        return {}
    by: dict = {}
    for r in rows:
        if r["categoria"] or not r["valor"]:
            continue
        geo = r["geocod"]
        if r["nivel"] != "Concelho" and geo not in REFS:
            continue
        by.setdefault((r["varcd"], geo), {})[r["periodo"]] = float(r["valor"])

    def serie(k: str, geo: str) -> dict:
        return by.get((CAMARAS_IND[k], geo), {})

    anos = sorted(
        {
            a
            for (v, _), d in by.items()
            if v == CAMARAS_IND["despesa"]
            for a in d
        }
    )
    if not anos:
        return {}
    ano, inicio = anos[-1], anos[0]

    def ultimo(k: str) -> str:
        return max(
            (a for (v, _), d in by.items() if v == CAMARAS_IND[k] for a in d),
            default="",
        )

    anos_de = {k: ultimo(k) for k in ("rendimento", "dormidas", "rsi")}
    nomes = {}
    for r in rows:
        if r["nivel"] == "Concelho":
            nomes[r["geocod"]] = (r["local"], r["ilha"])
    contratos: dict = {}
    base_de = base_ate = ""
    if base:
        cols = base[0]
        b = [dict(zip(cols, r, strict=False)) for r in base[1]]
        concelhos = [n for n, _ in nomes.values()]
        por_ano: dict = {}  # (concelho, year) -> contract value
        for r in b:
            c = municipio(r["adjudicante"], concelhos)
            if c:
                k = (c, str(r["publicado"])[:4])
                por_ano[k] = por_ano.get(k, 0.0) + float(r["preco"] or 0)
        # the contracts published in the year of the INE spending
        b = [r for r in b if str(r["publicado"]).startswith(ano)]
        datas = sorted(r["publicado"] for r in b if r["publicado"])
        base_de, base_ate = (datas[0], datas[-1]) if datas else ("", "")
        for r in b:
            c = municipio(r["adjudicante"], concelhos)
            if c:
                d = contratos.setdefault(c, {"n": 0, "valor": 0.0})
                d["n"] += 1
                d["valor"] += float(r["preco"] or 0)

    def linha(geo: str, nome: str, ilha: str = "") -> dict | None:
        pop = serie("pop", geo).get(ano)
        desp = serie("despesa", geo).get(ano)
        if not pop or desp is None:
            return None
        rec = serie("receita", geo).get(ano, 0)
        pop0 = serie("pop", geo).get(inicio)
        desp0 = serie("despesa", geo).get(inicio)
        d = {
            "nome": nome,
            "ilha": ilha,
            "pop": int(pop),
            "despesa_m": round(desp / 1e6, 1),
            "receita_m": round(rec / 1e6, 1),
            "despesa_hab": round(desp / pop),
            "receita_hab": round(rec / pop),
            "rnf_hab": round(serie("rnf_hab", geo).get(ano, 0)),
        }
        if pop0 and desp0:
            d["despesa_hab_inicio"] = round(desp0 / pop0)
            d["var_pct"] = round(100 * (d["despesa_hab"] / (desp0 / pop0) - 1))
        for k, a in anos_de.items():
            v = serie(k, geo).get(a)
            if v is not None:
                d[k] = round(v, 1) if k == "rsi" else round(v)
        if nome in contratos:
            c = contratos[nome]
            d["contratos_n"] = c["n"]
            d["contratos_m"] = round(c["valor"] / 1e6, 1)
            d["contratos_hab"] = round(c["valor"] / pop)
        return d

    lista = [
        x for g, (n, i) in nomes.items() if (x := linha(g, n, i)) is not None
    ]
    lista.sort(key=lambda d: -d["despesa_hab"])
    refs = [x for g, n in REFS.items() if (x := linha(g, n)) is not None]
    out = {
        "ano": ano,
        "inicio": inicio,
        "anos_de": anos_de,
        "concelhos": lista,
        "refs": refs,
        "max_hab": max(d["despesa_hab"] for d in lista) if lista else 0,
        "base_de": base_de,
        "base_ate": base_ate,
        "sem_contratos": [d["nome"] for d in lista if "contratos_n" not in d],
        "url": {
            k: f"https://www.ine.pt/xurl/indx/{v}"
            for k, v in CAMARAS_IND.items()
        },
    }
    out["grafico"] = _dispersao(lista)
    if base:
        out["compras"] = compras_base(ine, nomes, por_ano, anos)
    return out


COMPRAS = ("Aquisição de bens e serviços", "Aquisição de bens de capital")


def compras_base(
    ine: tuple[list, list], nomes: dict, por_ano: dict, anos: list[str]
) -> dict:
    """How much of each câmara's purchases (INE despesas: aquisição de bens
    e serviços + bens de capital) shows up as contracts it published on
    BASE in the same year. Multi-year contracts are counted in full in the
    year they are published, so the three-year sum is the fairer figure.
    Above 100 % is possible (a contract paid over several years)."""
    compras: dict = {}
    for r in _dicts(ine):
        if (
            r["varcd"] == CAMARAS_IND["despesa"]
            and r["categoria"] in COMPRAS
            and r["geocod"] in nomes
            and r["valor"]
        ):
            k = (nomes[r["geocod"]][0], r["periodo"])
            compras[k] = compras.get(k, 0.0) + float(r["valor"])
    if not compras:
        return {}
    tres = anos[-3:]

    def pct(c: float, b: float):
        return round(100 * b / c) if c else None

    def linha(nome: str, ilha: str = "") -> dict:
        c1, b1 = compras.get((nome, anos[-1]), 0.0), por_ano.get(
            (nome, anos[-1]), 0.0
        )
        c3 = sum(compras.get((nome, a), 0.0) for a in tres)
        b3 = sum(por_ano.get((nome, a), 0.0) for a in tres)
        return {
            "nome": nome,
            "ilha": ilha,
            "compras_m": round(c1 / 1e6, 1),
            "contratos_m": round(b1 / 1e6, 1),
            "pct": pct(c1, b1),
            "compras_3a_m": round(c3 / 1e6, 1),
            "contratos_3a_m": round(b3 / 1e6, 1),
            "pct_3a": pct(c3, b3),
        }

    lista = [linha(n, i) for n, i in nomes.values()]
    lista.sort(key=lambda d: (d["pct_3a"] is None, d["pct_3a"] or 0))
    serie = []
    for a in anos:
        c = sum(v for (_, y), v in compras.items() if y == a)
        b = sum(v for (n, y), v in por_ano.items() if y == a)
        serie.append(
            {
                "ano": a,
                "compras_m": round(c / 1e6, 1),
                "contratos_m": round(b / 1e6, 1),
                "pct": pct(c, b),
            }
        )
    c3 = sum(x["compras_3a_m"] for x in lista)
    b3 = sum(x["contratos_3a_m"] for x in lista)
    return {
        "anos": tres,
        "concelhos": lista,
        "serie": serie,
        "total_3a": {
            "compras_m": round(c3, 1),
            "contratos_m": round(b3, 1),
            "pct": pct(c3, b3),
        },
    }


def divida_pmp(
    divida: tuple[list, list] | None,
    pmp: tuple[list, list] | None,
    ine: tuple[list, list] | None = None,
) -> dict:
    """Each câmara's debt against its legal limit (DGAL, latest year and the
    series since 2014) and its average payment time (PMP, latest quarter and
    the highest since 2020), for /financas/camaras/#divida."""
    if not divida or not divida[1]:
        return {}
    rows = _dicts(divida)
    anos = sorted({r["ano"] for r in rows})
    ano = anos[-1]
    ilhas, pop = {}, {}
    for r in _dicts(ine) if ine else []:
        if r["nivel"] == "Concelho":
            ilhas[r["geocod"]] = r["ilha"]
            if r["varcd"] == CAMARAS_IND["pop"] and r["valor"]:
                pop[(r["geocod"], r["periodo"])] = float(r["valor"])
    tempos: dict = {}
    for r in _dicts(pmp) if pmp else []:
        tempos.setdefault(r["geocod"], []).append((r["data"], int(r["dias"])))
    ult_pmp = max((d for v in tempos.values() for d, _ in v), default="")
    por: dict = {}
    for r in rows:
        por.setdefault(r["geocod"], {})[r["ano"]] = r
    lista = []
    for geo, serie in por.items():
        r = serie.get(ano)
        if not r:
            continue
        lim, div = float(r["limite"]), float(r["divida"])
        d = {
            "nome": r["municipio"],
            "ilha": ilhas.get(geo, ""),
            "limite_m": round(lim / 1e6, 1),
            "divida_m": round(div / 1e6, 1),
            "pct": round(100 * div / lim) if lim else None,
            "serie": [
                (
                    {"ano": a, "pct": round(float(serie[a]["pct_limite"]))}
                    if a in serie and serie[a]["pct_limite"]
                    else {"ano": a, "pct": None}
                )
                for a in anos
            ],
        }
        d["anos_acima"] = sum(
            1 for x in d["serie"] if x["pct"] is not None and x["pct"] > 100
        )
        p = pop.get((geo, ano)) or max(
            (v for (g, _), v in pop.items() if g == geo), default=0
        )
        if p:
            d["divida_hab"] = round(div / p)
        t = sorted(tempos.get(geo, []))
        if t:
            d["pmp"] = t[-1][1] if t[-1][0] == ult_pmp else None
            m = max(t, key=lambda x: x[1])
            d["pmp_max"], d["pmp_max_data"] = m[1], m[0]
        lista.append(d)
    lista.sort(key=lambda d: -(d["pct"] or 0))
    return {
        "ano": ano,
        "anos": anos,
        "concelhos": lista,
        "acima": [d["nome"] for d in lista if (d["pct"] or 0) > 100],
        "divida_m": round(sum(d["divida_m"] for d in lista), 1),
        "pmp_data": ult_pmp,
        # years a câmara sent no validated accounts (marked ** by the DGAL)
        "sem_dados": [
            {
                "nome": next(iter(por[g].values()))["municipio"],
                "anos": [a for a in anos if a not in por[g]],
            }
            for g in sorted(por)
            if len(por[g]) < len(anos)
        ],
    }


# DGAL economic codes (SNC-AP) used by contas_camaras
RECEITA_EFETIVA = [f"{c:02d}00000000" for c in (1, 2, 4, 5, 6, 7, 8, 9, 10)]
RECEITA_CORRENTE = [f"{c:02d}00000000" for c in (1, 2, 4, 5, 6, 7, 8)]
TRANSFERENCIAS = ["0600000000", "1000000000"]
DERRAMA, IMI = "0102050000", "0102020000"
PESSOAL, JUROS, INVESTIMENTO = "0100000000", "0300000000", "0700000000"


def _pct(a: float, b: float) -> float | None:
    return round(100 * a / b, 1) if b else None


def contas_camaras(
    contas: tuple[list, list] | None,
    ine: tuple[list, list] | None = None,
    transf: tuple[list, list] | None = None,
    derrama: tuple[list, list] | None = None,
    anuario: tuple[list, list] | None = None,
) -> dict:
    """What the DGAL accounts say about each câmara, for
    /financas/camaras/#autonomia, #impostos and #orcamento:

    - autonomia: transfers (current + capital) as a share of effective
      revenue (without loans, sale of financial assets or the previous
      year's balance), the first and latest year; staff + interest as a
      share of current revenue; investment (aquisição de bens de capital)
      per inhabitant, latest year and the average of all years;
    - impostos: the derrama rate the câmara set (AT) and what it raised,
      IMI per inhabitant, and the share of its residents' IRS it keeps
      (0-5 %, OE transfers) with what it gives back;
    - orcamento: revenue collected / final budget (Anuário), latest year,
      average and lowest, and expenditure committed / budget."""
    if not contas or not contas[1]:
        return {}
    v: dict = {}
    nomes: dict = {}
    for r in _dicts(contas):
        if r["mapa"] in ("receita", "despesa"):
            k = (r["geocod"], r["ano"], r["mapa"], r["codigo"])
            v[k] = v.get(k, 0.0) + float(r["valor"] or 0)
            nomes[r["geocod"]] = r["municipio"]
    anos = sorted({k[1] for k in v})
    ano = anos[-1]
    ilhas, pop = {}, {}
    for r in _dicts(ine) if ine else []:
        if r["nivel"] == "Concelho":
            ilhas[r["geocod"]] = r["ilha"]
            if r["varcd"] == CAMARAS_IND["pop"] and r["valor"]:
                pop[(r["geocod"], r["periodo"])] = float(r["valor"])

    def hab(geo: str, a: str) -> float:
        return pop.get((geo, a)) or max(
            (p for (g, per), p in pop.items() if g == geo and per <= a),
            default=0,
        )

    def soma(geo, a, mapa, codigos):
        return sum(v.get((geo, a, mapa, c), 0.0) for c in codigos)

    tr = {r["geocod"]: r for r in _dicts(transf)} if transf else {}
    tr_ano = max((r["ano"] for r in tr.values()), default="")
    tr = {g: r for g, r in tr.items() if r["ano"] == tr_ano}
    der = {r["geocod"]: r for r in _dicts(derrama)} if derrama else {}
    der_ano = max((r["ano_lucro"] for r in der.values()), default="")
    exe: dict = {}
    for r in _dicts(anuario) if anuario else []:
        exe.setdefault(r["geocod"], {})[r["ano"]] = r
    exe_anos = sorted({a for s in exe.values() for a in s})

    autonomia, impostos, orcamento = [], [], []
    for geo in sorted(nomes):
        base = {"nome": nomes[geo], "ilha": ilhas.get(geo, "")}
        serie = []
        for a in anos:
            ef = soma(geo, a, "receita", RECEITA_EFETIVA)
            if ef:
                serie.append(
                    (a, _pct(soma(geo, a, "receita", TRANSFERENCIAS), ef))
                )
        if not serie or serie[-1][0] != ano:
            continue
        corr = soma(geo, ano, "receita", RECEITA_CORRENTE)
        rig = soma(geo, ano, "despesa", [PESSOAL, JUROS])
        inv = {
            a: soma(geo, a, "despesa", [INVESTIMENTO]) / hab(geo, a)
            for a in anos
            if hab(geo, a) and soma(geo, a, "receita", RECEITA_EFETIVA)
        }
        autonomia.append(
            base
            | {
                "transf": serie[-1][1],
                "transf_ini": serie[0][1],
                "transf_ini_ano": serie[0][0],
                "receita_m": round(
                    soma(geo, ano, "receita", RECEITA_EFETIVA) / 1e6, 1
                ),
                "rigidez": _pct(rig, corr),
                "invest_hab": round(inv.get(ano, 0)),
                "invest_hab_med": (
                    round(sum(inv.values()) / len(inv)) if inv else None
                ),
            }
        )
        p = hab(geo, ano)
        d = der.get(geo, {})
        t = tr.get(geo)
        imp = base | {
            "derrama_taxa": (
                float(d["taxa_geral"]) if d.get("taxa_geral") else 0
            ),
            "derrama_reduzida": d.get("taxa_reduzida", ""),
            "derrama_isencoes": d.get("isencoes", ""),
            "derrama_k": round(soma(geo, ano, "receita", [DERRAMA]) / 1e3),
            "imi_hab": (
                round(soma(geo, ano, "receita", [IMI]) / p) if p else None
            ),
        }
        if t:
            dado = float(t["irs_max"]) - float(t["irs"])
            imp |= {
                "irs_pct": float(t["irs_pct"]),
                "irs_devolvido_k": round(dado / 1e3),
                "irs_devolvido_hab": round(dado / p) if p else None,
            }
        impostos.append(imp)
        e = exe.get(geo, {})
        cob = [
            (a, float(r["receita_cobrada"]))
            for a, r in sorted(e.items())
            if r["receita_cobrada"]
        ]
        if cob:
            ult = e[exe_anos[-1]] if exe_anos and exe_anos[-1] in e else {}
            mini = min(cob, key=lambda x: x[1])
            orcamento.append(
                base
                | {
                    "cobrada": (
                        cob[-1][1] if cob[-1][0] == exe_anos[-1] else None
                    ),
                    "cobrada_med": round(sum(x for _, x in cob) / len(cob), 1),
                    "cobrada_min": mini[1],
                    "cobrada_min_ano": mini[0],
                    "anos_abaixo_85": sum(1 for _, x in cob if x < 85),
                    "comprometida": (
                        float(ult["despesa_comprometida"])
                        if ult.get("despesa_comprometida")
                        else None
                    ),
                }
            )
    autonomia.sort(key=lambda d: -(d["transf"] or 0))
    impostos.sort(key=lambda d: (-d["derrama_taxa"], -(d.get("irs_pct") or 0)))
    orcamento.sort(key=lambda d: d["cobrada_med"])
    out = {
        "ano": ano,
        "ano_ini": anos[0],
        "autonomia": autonomia,
        "impostos": impostos,
        "derrama_ano": der_ano,
        "irs_ano": tr_ano,
        "cobram_derrama": sum(1 for d in impostos if d["derrama_taxa"]),
        "irs_devolvem": [
            d["nome"] for d in impostos if d.get("irs_pct", 5) < 5
        ],
        "irs_devolvido_k": sum(d.get("irs_devolvido_k", 0) for d in impostos),
    }
    if orcamento:
        out |= {
            "orcamento": orcamento,
            "orc_ano": exe_anos[-1],
            "orc_ini": exe_anos[0],
            "orc_anos": len(exe_anos),
        }
    return out


def _ponto(x: float, y: float, nome: str, rotulos: dict) -> dict:
    p = {"x": x, "y": y, "nome": nome, "rotulo": nome in rotulos}
    if nome in rotulos:
        dx, dy, ancora = rotulos[nome]
        p.update(lx=round(x + dx, 1), ly=round(y + dy, 1), ancora=ancora)
    return p


def _dispersao(lista: list[dict]) -> dict:
    """Positions for the scatter of population (log scale) against spending
    per inhabitant, in a 600 x 300 viewBox."""
    import math

    if not lista:
        return {}
    w, h, esq, dir_, top, fundo = 600, 300, 56, 16, 12, 34
    xs = [500, 1000, 5000, 10000, 50000]
    lo, hi = math.log10(300), math.log10(100000)
    ymax = 1000 * math.ceil(max(d["despesa_hab"] for d in lista) / 1000)

    def x(v):
        return round(
            esq + (math.log10(v) - lo) / (hi - lo) * (w - esq - dir_), 1
        )

    def y(v):
        return round(top + (1 - v / ymax) * (h - top - fundo), 1)

    # label the extremes only; on the right edge the label goes to the left
    rotulos = {
        "Corvo": (8, 4, "start"),
        "Lajes das Flores": (8, 4, "start"),
        "Angra do Heroísmo": (-8, -8, "end"),
        "Ponta Delgada": (-8, 18, "end"),
    }
    return {
        "w": w,
        "h": h,
        "esq": esq,
        "dir": w - dir_,
        "base": h - fundo,
        "top": top,
        "pontos": [
            _ponto(x(d["pop"]), y(d["despesa_hab"]), d["nome"], rotulos)
            for d in lista
        ],
        "xt": [{"x": x(v), "v": v} for v in xs],
        "yt": [{"y": y(v), "v": v} for v in range(0, ymax + 1, 2000)],
    }


def write_camaras(docs: Path, tables: dict) -> None:
    """docs/_data/camaras.json for /financas/camaras/."""
    base = tables.get("base")
    data = camaras_data(tables["ine"], base) if "ine" in tables else {}
    d = divida_pmp(
        tables.get("dgal_divida"), tables.get("dgal_pmp"), tables.get("ine")
    )
    if d:
        data["divida"] = d
    f = contas_camaras(
        tables.get("dgal_contas"),
        tables.get("ine"),
        tables.get("dgal_transferencias"),
        tables.get("derrama_municipal"),
        tables.get("anuario_execucao"),
    )
    if f:
        data["financas"] = f
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "camaras.json").write_text(
        json.dumps(_texts(data), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
