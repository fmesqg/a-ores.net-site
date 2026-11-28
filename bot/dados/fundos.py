"""EU funds (PRR, Kohesio and the CAP payments published by the IFAP):
docs/_data/fundos.json."""

import json
from pathlib import Path

from .camaras import CAMARAS_IND
from .comum import _dicts, _f, _m, _texts

# programme (bot/ifap.py) -> key in fundos.json
PROGRAMAS = {
    "POSEI": "posei",
    "Desenvolvimento rural": "rural",
    "Pagamentos diretos": "diretos",
    "Mercados agrícolas": "mercados",
    "Outros": "outros",
}


def fundos_data(tables: dict) -> dict:
    """PRR and Kohesio totals for /financas/fundos-europeus/. PRR amounts
    are the Azorean share (aprovado_acores, pago_acores); a final
    beneficiary's amount is what it contracted, times the Azorean share of
    each project. Kohesio's projects with a note (another region's
    programme, Interreg) are left out of its totals."""
    out: dict = {}
    if "prr_projetos" in tables:
        proj = _dicts(tables["prr_projetos"])
        share = {p["projeto"]: _f(p["perc_acores"]) / 100 for p in proj}
        aprov = sum(_f(p["aprovado_acores"]) for p in proj)
        pago = sum(_f(p["pago_acores"]) for p in proj)
        conc: dict[str, list] = {}
        comp: dict[str, list] = {}
        for p in proj:
            cs = p["concelhos"].split("; ") if p["concelhos"] else []
            k = cs[0] if len(cs) == 1 else "Vários concelhos"
            for d, key in ((conc, k), (comp, p["componente"] or "?")):
                d.setdefault(key, [0, 0.0, 0.0])
                d[key][0] += 1
                d[key][1] += _f(p["aprovado_acores"])
                d[key][2] += _f(p["pago_acores"])

        def lista(d: dict) -> list[dict]:
            return [
                {
                    "nome": k,
                    "projetos": v[0],
                    "aprovado": _m(v[1]),
                    "pago": _m(v[2]),
                    "pct_pago": round(100 * v[2] / v[1]) if v[1] else 0,
                }
                for k, v in sorted(d.items(), key=lambda kv: -kv[1][1])
            ]

        ben: dict[str, list] = {}
        for e in _dicts(tables.get("prr_entidades", ([], []))):
            if e["papel"] != "Beneficiário Final":
                continue
            b = ben.setdefault(
                e["nif"] or e["entidade"], [e["entidade"], 0, 0.0]
            )
            b[1] += 1
            b[2] += _f(e["contratado"]) * share.get(e["projeto"], 1)
        datas = sorted(p["referencia"] for p in proj if p["referencia"])
        out["prr"] = {
            "projetos": len(proj),
            "aprovado": _m(aprov),
            "pago": _m(pago),
            "pct_pago": round(100 * pago / aprov) if aprov else 0,
            "beneficiarios": len(ben),
            "referencia": datas[-1] if datas else "",
            "concelhos": lista(conc),
            "componentes": lista(comp),
            "maiores": [
                {"nif": k, "nome": v[0], "projetos": v[1], "valor": _m(v[2])}
                for k, v in sorted(ben.items(), key=lambda kv: -kv[1][2])[:25]
            ],
        }
    if "kohesio_projetos" in tables:
        proj = _dicts(tables["kohesio_projetos"])
        boas = [p for p in proj if not p["nota"]]
        prog: dict[str, list] = {}
        for p in proj:
            g = prog.setdefault(
                p["programa"] or "?", [p["periodo"], p["nota"], 0, 0.0, 0.0]
            )
            g[2] += 1
            g[3] += _f(p["custo_total"])
            g[4] += _f(p["apoio_ue"])
        periodos = {}
        for p in boas:
            g = periodos.setdefault(p["periodo"] or "?", [0, 0.0])
            g[0] += 1
            g[1] += _f(p["apoio_ue"])
        ben = _dicts(tables.get("kohesio_beneficiarios", ([], [])))
        out["kohesio"] = {
            "projetos": len(boas),
            "apoio_ue": _m(sum(_f(p["apoio_ue"]) for p in boas)),
            "custo_total": _m(sum(_f(p["custo_total"]) for p in boas)),
            "excluidos": len(proj) - len(boas),
            "excluidos_ue": _m(
                sum(_f(p["apoio_ue"]) for p in proj if p["nota"])
            ),
            "periodos": [
                {"nome": k, "projetos": v[0], "apoio_ue": _m(v[1])}
                for k, v in sorted(periodos.items())
            ],
            "programas": [
                {
                    "nome": k,
                    "periodo": v[0],
                    "nota": v[1],
                    "projetos": v[2],
                    "custo_total": _m(v[3]),
                    "apoio_ue": _m(v[4]),
                }
                for k, v in sorted(prog.items(), key=lambda kv: -kv[1][4])
            ],
            "beneficiarios": len(ben),
            "maiores": [
                {
                    "nome": b["beneficiario"],
                    "projetos": int(b["projetos"] or 0),
                    "apoio_ue": _m(_f(b["apoio_ue"])),
                    "ligacao": b["ligacao"],
                }
                for b in ben[:25]
            ],
        }
    if "ifap_resumo" in tables:
        out["pac"] = pac_data(tables)
    return out


def pac_data(tables: dict) -> dict:
    """CAP payments to beneficiaries in the Azores (bot/ifap.py): totals per
    financial year and programme (every year read), and for the latest
    year the measures, the concelhos (per inhabitant, INE population of
    the year the financial year ends in, or the latest before it) and the
    largest beneficiaries (only while the IFAP publishes the year)."""
    res = _dicts(tables["ifap_resumo"])
    anos = sorted({r["exercicio"] for r in res})
    if not anos:
        return {}
    ultimo = anos[-1]
    por_ano = []
    for a in anos:
        rs = [r for r in res if r["exercicio"] == a]
        prog = {p: 0.0 for p in PROGRAMAS}
        for r in rs:
            prog[r["programa"]] = prog.get(r["programa"], 0.0) + _f(
                r["montante"]
            )
        por_ano.append(
            {
                "ano": a,
                "total": _m(sum(prog.values())),
                "ue": _m(sum(_f(r["feaga"]) + _f(r["feader"]) for r in rs)),
                **{PROGRAMAS.get(p, "outros"): _m(v) for p, v in prog.items()},
            }
        )
    rs = [r for r in res if r["exercicio"] == ultimo]
    total = sum(_f(r["montante"]) for r in rs)
    med: dict[str, list] = {}
    conc: dict[str, list] = {}
    for r in rs:
        m = med.setdefault(r["medida"], [r["medida_nome"], r["programa"], 0.0])
        m[2] += _f(r["montante"])
        c = conc.setdefault(r["geocod"], [r["concelho"], r["ilha"], 0.0, 0.0])
        c[2] += _f(r["montante"])
        if r["programa"] == "POSEI":
            c[3] += _f(r["montante"])
    pop: dict[str, dict] = {}
    for r in _dicts(tables.get("ine", ([], []))):
        if (
            r["varcd"] == CAMARAS_IND["pop"]
            and r["nivel"] == "Concelho"
            and not r["categoria"]
            and r["valor"]
        ):
            pop.setdefault(r["geocod"], {})[r["periodo"]] = _f(r["valor"])

    def hab(geo: str) -> float:
        anos_p = [p for p in pop.get(geo, {}) if p <= ultimo]
        return pop[geo][max(anos_p)] if anos_p else 0.0

    concelhos = []
    for g, (nome, ilha, v, posei) in sorted(
        conc.items(), key=lambda kv: -kv[1][2]
    ):
        h = hab(g)
        concelhos.append(
            {
                "nome": nome,
                "ilha": ilha,
                "valor": _m(v),
                "posei": _m(posei),
                "por_hab": round(v / h) if h else None,
            }
        )
    ben: dict[str, list] = {}
    pag = _dicts(tables.get("ifap_pagamentos", ([], [])))
    for r in pag:
        if r["exercicio"] != ultimo:
            continue
        b = ben.setdefault(
            (r["beneficiario"], r["geocod"]), [r["concelho"], 0.0, 0.0]
        )
        b[1] += _f(r["montante"])
        if r["programa"] == "POSEI":
            b[2] += _f(r["montante"])
    valores = sorted((v[1] for v in ben.values()), reverse=True)
    top10 = max(1, len(valores) // 10)
    return {
        "ultimo": ultimo,
        "total": _m(total),
        "posei": _m(
            sum(_f(r["montante"]) for r in rs if r["programa"] == "POSEI")
        ),
        "beneficiarios": len(ben),
        "pct_top10": (
            round(100 * sum(valores[:top10]) / sum(valores))
            if valores and sum(valores)
            else None
        ),
        "anos_nomes": sorted({r["exercicio"] for r in pag}),
        "anos": por_ano,
        "medidas": [
            {
                "codigo": k,
                "nome": v[0],
                "programa": v[1],
                "valor": _m(v[2]),
                "pct": round(100 * v[2] / total) if total else 0,
            }
            for k, v in sorted(med.items(), key=lambda kv: -kv[1][2])
            if abs(v[2]) >= 50_000
        ],
        "concelhos": concelhos,
        "maiores": [
            {
                "nome": k[0],
                "concelho": v[0],
                "valor": round(v[1]),
                "posei": round(v[2]),
            }
            for k, v in sorted(ben.items(), key=lambda kv: -kv[1][1])[:25]
        ],
    }


def write_fundos(docs: Path, tables: dict) -> None:
    """docs/_data/fundos.json for /financas/fundos-europeus/."""
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "fundos.json").write_text(
        json.dumps(_texts(fundos_data(tables)), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
