"""Public employment (DGAEP) and its share of jobs: docs/_data/publico.json."""

import re

from .comum import _dicts, _mes, _num

AR_ACORES = "ADMINISTRAÇÃO REGIONAL DOS AÇORES"
AR_SER = "dos quais: SER - Entid. Reclassif."
AR_FORA = {
    AR_ACORES,
    "Órgãos do Governo Regional dos Açores",
    "Serviços e Fundos Autónomos da AR dos Açores",
}
CARREIRAS = {
    "Educ.infância e doc. ens. básico/secund.": (
        "Educadores de infância e professores do básico e secundário"
    ),
    "Assist. operacional/operário/auxiliar": (
        "Assistentes operacionais, operários e auxiliares"
    ),
    "Assistente técnico/administrativo": (
        "Assistentes técnicos e administrativos"
    ),
    "Técnico superior": "Técnicos superiores",
    "Enfermeiro": "Enfermeiros",
    "Médico": "Médicos",
    "Técnico diagnóstico e terapêutica": (
        "Técnicos de diagnóstico e terapêutica"
    ),
    "Técnico superior de saúde": "Técnicos superiores de saúde",
    "Docente ensino universitário": "Professores universitários",
    "Representantes do poder legislativo": (
        "Eleitos e membros de órgãos executivos"
    ),
    "Dirigente intermédio": "Dirigentes intermédios",
    "Dirigente superior": "Dirigentes superiores",
    "Informático": "Informáticos",
    "Magistrado": "Magistrados",
    "Oficial de justiça": "Oficiais de justiça",
    "Pessoal de inspeção": "Inspetores",
    "Polícia municipal": "Polícia municipal",
}
# the sub-rows of a group in Q1.7 ("Dirigente superior de 1.º grau",
# "Forças Armadas - Oficial", ...)
SUBCARREIRA = re.compile(r" de \d\.º| - ")
MESES_DGAEP = {
    "01": "janeiro",
    "04": "abril",
    "07": "julho",
    "10": "outubro",
}


def _dia(data: str) -> str:
    """'2026-09-30' -> '30 de setembro de 2026'."""
    return f"{int(data[8:10])} de {_mes(data)}"


def publico_data(
    emprego: tuple[list, list],
    srea: tuple[list, list] | None = None,
    sper: dict | None = None,
    ine: tuple[list, list] | None = None,
    censos: tuple[list, list] | None = None,
) -> dict:
    """data/emprego_publico.csv (bot/dgaep.py) for /economia/setor-publico/:
    jobs in general government in the Azores by career, the regional
    administration by department, the yearly series and pay; with the SREA
    employment survey and the CFP's market companies, the public and
    private shares of the jobs in the Azores (an estimate, see the page)."""
    rows = _dicts(emprego)
    if not rows:
        return {}

    def serie(quadro, rubrica, local="Açores", indicador=None) -> dict:
        return {
            r["data"]: _num(r["valor"])
            for r in rows
            if r["quadro"] == quadro
            and r["rubrica"] == rubrica
            and r["local"] == local
            and (indicador is None or r["indicador"] == indicador)
        }

    ar = serie("Q1.1", AR_ACORES)
    ap = serie("Q1.7", "Total")
    pt = serie("Q1.7", "Total", "Portugal")
    if not ar or not ap:
        return {}
    last = max(ar)
    antes = f"{int(last[:4]) - 1}{last[4:]}"
    q11 = [r for r in rows if r["quadro"] == "Q1.1" and r["local"] == "Açores"]
    fss = serie(
        "Q1.1",
        next(
            (r["rubrica"] for r in q11 if r["rubrica"].startswith("Fundos")),
            "",
        ),
    )
    out: dict = {
        "data": last,
        "periodo": _dia(last),
        "provisorio": any(r["provisorio"] for r in rows if r["data"] == last),
        "ficheiro": rows[0]["ficheiro"],
        "pagina": rows[0]["pagina"],
        "ap": int(ap[last]),
        "ap_var": int(ap[last] - ap[antes]) if antes in ap else None,
        "ap_pct_pais": (
            round(100 * ap[last] / pt[last], 1) if pt.get(last) else None
        ),
        "ar": int(ar[last]),
        "ar_var": int(ar[last] - ar[antes]) if antes in ar else None,
        "ar_inicio": int(ar[min(ar)]),
        "ano_inicio": int(min(ar)[:4]),
        "fss": int(fss.get(last) or 0),
    }
    # the rest of general government in the Azores: the State's services
    # (courts, university, ...) and the municipalities and parishes
    out["outros"] = out["ap"] - out["ar"] - out["fss"]

    # regional administration by department; the reclassified companies
    # (the hospitals EPE) are counted apart from the departments, and the
    # two add up to the total
    deps = []
    for _ordem, rub in sorted({(int(r["ordem"]), r["rubrica"]) for r in q11}):
        if rub in AR_FORA or rub.startswith("Fundos"):
            continue
        x = serie("Q1.1", rub)
        if last not in x:
            continue
        nome = rub
        if rub == AR_SER:
            nome = "Hospitais EPE e outras empresas públicas contadas como administração"
        elif rub == "Órgãos de Soberania e Entidades Independentes":
            nome = "Assembleia Legislativa e outros órgãos independentes"
        deps.append(
            {
                "nome": nome,
                "valor": int(x[last]),
                "var": int(x[last] - x[antes]) if antes in x else None,
                "pct": round(100 * x[last] / ar[last], 1),
                "ser": rub == AR_SER,
            }
        )
    deps.sort(key=lambda d: (d["ser"], -d["valor"]))
    out["secretarias"] = deps
    out["secretarias_soma_ok"] = sum(d["valor"] for d in deps) == out["ar"]

    # by career, everybody in general government in the Azores
    q17 = {
        r["rubrica"]
        for r in rows
        if r["quadro"] == "Q1.7" and r["local"] == "Açores"
    }
    car = []
    for rub in q17 - {"Total"}:
        if SUBCARREIRA.search(rub):
            continue
        x = serie("Q1.7", rub)
        if not x.get(last):
            continue
        car.append(
            {
                "nome": CARREIRAS.get(rub, rub),
                "valor": int(x[last]),
                "var": int(x[last] - x[antes]) if antes in x else None,
                "pct": round(100 * x[last] / ap[last], 1),
            }
        )
    car.sort(key=lambda d: -d["valor"])
    resto = out["ap"] - sum(d["valor"] for d in car[:10])
    out["carreiras"] = car[:10]
    out["carreiras_resto"] = resto
    out["carreiras_resto_pct"] = round(100 * resto / ap[last], 1)

    # one point a year (31 December) and the latest quarter
    anos = sorted({d[:4] for d in ar})
    evol = []
    for a in anos:
        d = (
            f"{a}-12-31"
            if f"{a}-12-31" in ar
            else (last if a == last[:4] else "")
        )
        if not d:
            continue
        evol.append(
            {
                "ano": int(a),
                "quando": "31 dez" if d.endswith("12-31") else _dia(d)[:-8],
                "ar": int(ar[d]),
                "ap": int(ap[d]) if d in ap else None,
            }
        )
    out["evolucao"] = evol
    out["evolucao_max"] = max((e["ap"] or e["ar"]) for e in evol)

    # pay: general government in each region (Q1.13) and the regional
    # administration (Q1.9), in the latest month surveyed
    pay = {}
    for quadro, rub, local, chave in (
        ("Q1.13", "Total", "Açores", "acores"),
        ("Q1.13", "Total", "Portugal", "pais"),
        ("Q1.9", AR_ACORES, "Açores", "ar"),
        ("Q1.9", "ADMINISTRAÇÃO REGIONAL DA MADEIRA", "Madeira", "madeira"),
    ):
        for ind, k in (
            ("Remuneração base média mensal", "base"),
            ("Ganho médio mensal", "ganho"),
        ):
            x = serie(quadro, rub, local, ind)
            if x:
                m = max(x)
                pay.setdefault(chave, {})[k] = round(x[m])
                pay["mes"] = f"{MESES_DGAEP.get(m[5:7], m[5:7])} de {m[:4]}"
    out["salarios"] = pay

    # public and private shares of the jobs in the Azores
    if srea:
        sr = _dicts(srea)
        emp = sorted(
            (
                r
                for r in sr
                if r["serie"] == "emprego"
                and r["indicador"] == "População empregada"
                and r["rubrica"] == "Total"
            ),
            key=lambda r: r["data"],
        )
        if emp:
            e = emp[-1]
            y, q = e["periodo"].split("-T")
            fim = f"{y}-{3 * int(q):02d}"
            ap_q = next((v for d, v in ap.items() if d[:7] == fim), None)
            total = _num(e["valor"]) * 1000
            setor_p = next(
                (
                    _num(r["valor"])
                    for r in sr
                    if r["serie"] == "emprego"
                    and r["periodo"] == e["periodo"]
                    and r["rubrica"].startswith("P:")
                ),
                None,
            )
            mercado = 0
            if sper:
                mercado = sum(
                    d.get("trabalhadores", 0)
                    for d in sper.get("empresas", [])
                    if not d.get("ap")
                )
            if ap_q:
                pub = ap_q + mercado
                out["peso"] = {
                    "periodo": f"{q}.º trimestre de {y}",
                    "emprego_mil": _num(e["valor"]),
                    "ap": int(ap_q),
                    "ap_pct": round(100 * ap_q / total, 1),
                    "mercado": mercado,
                    "mercado_ano": sper.get("ano") if sper else None,
                    "publico": int(pub),
                    "publico_pct": round(100 * pub / total),
                    "um_em": round(total / pub),
                    "privado": int(total - pub),
                    "privado_pct": 100 - round(100 * pub / total),
                    "setor_p_mil": setor_p,
                    "url": e["pagina"],
                }
    if ine:
        out["comparacao"] = _comparacao(rows, ine)
    if censos:
        out["ilhas"] = _ilhas_censos(censos)
    return out


ORDEM_ILHAS = [
    "Santa Maria",
    "São Miguel",
    "Terceira",
    "Graciosa",
    "São Jorge",
    "Pico",
    "Faial",
    "Flores",
    "Corvo",
]


def _ilhas_censos(censos: tuple[list, list]) -> dict:
    """Employed residents of each island in CAE sections O (public
    administration, defence, social security), P (education) and Q (health
    and social work), 2021 census (data/censos2021_setores.csv)."""
    soma: dict = {}
    conc: dict = {}
    ilha_de: dict = {}
    for r in _dicts(censos):
        for k, tab in ((r["ilha"], soma), (r["concelho"], conc)):
            d = tab.setdefault(k, {"O": 0, "P": 0, "Q": 0, "Total": 0})
            d[r["secao"]] += int(r["valor"])
        ilha_de[r["concelho"]] = r["ilha"]
    if not soma:
        return {}
    soma["Açores"] = {
        k: sum(d[k] for d in soma.values()) for k in ("O", "P", "Q", "Total")
    }

    def linha(nome: str, tab: dict | None = None) -> dict:
        d = (tab or soma)[nome]
        t = d["Total"]
        return {
            "ilha": ilha_de.get(nome, nome) if tab else nome,
            "nome": nome,
            "empregados": t,
            "o": d["O"],
            "o_pct": round(100 * d["O"] / t, 1),
            "p_pct": round(100 * d["P"] / t, 1),
            "q_pct": round(100 * d["Q"] / t, 1),
            "opq_pct": round(100 * (d["O"] + d["P"] + d["Q"]) / t, 1),
        }

    ilhas = [linha(n) for n in ORDEM_ILHAS if n in soma]
    concelhos = sorted(
        (linha(n, conc) for n in conc), key=lambda x: -x["o_pct"]
    )
    return {
        "lista": ilhas,
        "concelhos": concelhos,
        "max_pct_concelho": max(x["opq_pct"] for x in concelhos),
        "acores": linha("Açores"),
        "max_pct": max(x["opq_pct"] for x in ilhas),
        "url": _dicts(censos)[0]["url"],
    }


EMPREGADOS = "0012118"  # INE, Inquérito ao Emprego, quarterly, NUTS II
AR_LOCAL = {
    "Açores": "ADMINISTRAÇÃO REGIONAL DOS AÇORES",
    "Madeira": "ADMINISTRAÇÃO REGIONAL DA MADEIRA",
}


def _comparacao(rows: list[dict], ine: tuple[list, list]) -> dict:
    """General government jobs (DGAEP Q1.7, by NUTS) as a share of the
    employed population (INE) in the Azores, Madeira and Portugal, for the
    latest quarter both have."""
    ap = {
        (r["local"], r["data"]): _num(r["valor"])
        for r in rows
        if r["quadro"] == "Q1.7" and r["rubrica"] == "Total"
    }
    ar = {
        (r["local"], r["data"]): _num(r["valor"])
        for r in rows
        if r["quadro"] == "Q1.1" and AR_LOCAL.get(r["local"]) == r["rubrica"]
    }
    nomes = {"20": "Açores", "30": "Madeira", "PT": "Portugal"}
    emp = {}
    for r in _dicts(ine):
        if r["varcd"] == EMPREGADOS and not r["categoria"] and r["valor"]:
            if r["geocod"] in nomes:
                emp[(nomes[r["geocod"]], r["data"])] = (
                    _num(r["valor"]),
                    r["periodo"],
                )

    def inicio(d: str) -> str:  # 2026-09-30 -> 2026-07-01
        return f"{d[:4]}-{int(d[5:7]) - 2:02d}-01"

    datas = sorted({d for (_, d) in ap}, reverse=True)  # quarter ends
    for d in datas:
        if all((n, d) in ap and (n, inicio(d)) in emp for n in nomes.values()):
            break
    else:
        return {}
    locais = []
    for n in nomes.values():
        e, periodo = emp[(n, inicio(d))]
        x = {
            "local": n,
            "ap": int(ap[(n, d)]),
            "empregados": int(e),
            "ap_pct": round(100 * ap[(n, d)] / e, 1),
        }
        if (n, d) in ar:
            x["ar"] = int(ar[(n, d)])
            x["ar_pct"] = round(100 * ar[(n, d)] / e, 1)
        locais.append(x)
    return {
        "data": d,
        "periodo": periodo,
        "provisorio": any(
            r["provisorio"]
            for r in rows
            if r["quadro"] == "Q1.7" and r["data"] == d
        ),
        "locais": locais,
        "max_pct": max(x["ap_pct"] for x in locais),
        "url_ine": f"https://www.ine.pt/xurl/indx/{EMPREGADOS}",
    }
