"""Credit and companies from the Banco de Portugal (BPstat): docs/_data/credito.json."""

import json
from pathlib import Path

from .comum import MESES, _dicts, _texts, pt_num
from .impostos import _pct_s, _share

BPSTAT_SERIE = "https://bpstat.bportugal.pt/serie/"
M_EUR = "Milhões de euros"
PCT = "Percentagem"
MIL_DEV = "Milhares de devedores"
TODAS_CAE = (
    "Todas as atividades de sociedades não financeiras exceto "
    "atividades das sedes sociais"
)
# BdP's aggregates of other sectors, left out of the sector table
CAE_AGREGADOS = {
    TODAS_CAE,
    "Comércio, transportes, alojamento e restauração",
    "Indústrias, eletricidade, gás e água",
    "Atividades das sedes sociais",
    # "Outras atividades" overlaps the sectors listed on their own: those
    # ten add up to the total (7 728 companies in the Azores in 2025)
    "Outras atividades",
}
EMPRESAS_IND = [
    ("Número de empresas", "Número de empresas"),
    ("Número de pessoas ao serviço", "Número de pessoas"),
    ("Vendas e serviços prestados", "Milhares de euros"),
    ("Autonomia financeira", PCT),
    ("Financiamentos obtidos em percentagem do ativo", PCT),
    ("Custo dos financiamentos obtidos", PCT),
    ("Cobertura dos gastos de financiamento", "Número"),
    ("Rendibilidade do ativo", PCT),
    ("Rendibilidade dos capitais próprios", PCT),
    ("Empresas com resultado líquido negativo", "% das empresas"),
    ("Empresas com capital próprio negativo", "% das empresas"),
    ("Prazo médio de recebimentos", "Número de dias"),
    ("Prazo médio de pagamentos", "Número de dias"),
]
REG_K = {"Açores": "acores", "Madeira": "madeira", "Portugal": "pais"}


def _mes_ano(data: str) -> str:
    """'2026-10-31' -> 'outubro de 2026'."""
    return f"{MESES[int(data[5:7]) - 1]} de {data[:4]}"


def _populacao(ine: tuple[list, list] | None) -> dict[str, dict[int, float]]:
    """{regiao: {ano: residentes}} for the Azores, Madeira and Portugal
    (INE, 0012918)."""
    nomes = {"20": "Açores", "30": "Madeira", "PT": "Portugal"}
    out: dict[str, dict[int, float]] = {}
    for r in _dicts(ine) if ine else []:
        if r["varcd"] == "0012918" and r["geocod"] in nomes and r["valor"]:
            reg = nomes[r["geocod"]]
            out.setdefault(reg, {})[int(r["periodo"])] = float(r["valor"])
    return out


def _pop(pop: dict, regiao: str, data: str) -> tuple[float | None, int | None]:
    """Residents in the year of ``data``, or the latest year before it."""
    anos = [a for a in pop.get(regiao, {}) if a <= int(data[:4])]
    return (pop[regiao][max(anos)], max(anos)) if anos else (None, None)


def bp_series(bp: tuple[list, list]) -> dict[tuple, dict[str, dict]]:
    """{(conjunto, indicador, setor, detalhe, unidade): {regiao: {data:
    (valor, serie)}}}. Where the BdP gives no national total (loans and
    deposits), 'Portugal' is the sum of the regions (and of the deposits
    not tied to a branch): amounts and counts only, never percentages."""
    out: dict[tuple, dict[str, dict]] = {}
    for r in _dicts(bp):
        k = (
            r["conjunto"],
            r["indicador"],
            r["setor"],
            r["detalhe"],
            r["unidade"],
        )
        out.setdefault(k, {}).setdefault(r["regiao"], {})[r["data"]] = (
            float(r["valor"]),
            r["serie"],
        )
    for k, regs in out.items():
        if "Portugal" in regs or k[4] == PCT or k[0] == "empresas":
            continue
        soma: dict[str, float] = {}
        for datas in regs.values():
            for d, (v, _) in datas.items():
                soma[d] = soma.get(d, 0.0) + v
        regs["Portugal"] = {d: (round(v, 1), "") for d, v in soma.items()}
    return out


def _bp_fmt(unidade: str, v: float | None) -> str:
    if v is None:
        return ""
    if unidade == "Milhares de euros":
        return pt_num(round(v / 1000)) + " M€"
    if unidade in (PCT, "% das empresas"):
        return _pct_s(round(v, 1))
    if unidade == "Número de dias":
        return pt_num(v) + " dias"
    return pt_num(v)


def _vencidos(s: dict, setor: str, det: str, reg: str, d: str) -> dict:
    """Overdue ratio and share of debtors with overdue loans. The BdP's
    own figures for a region; for Portugal, worked out from the regional
    amounts and debtors (açores.net)."""

    def val(k, r=reg):
        got = s.get(k, {}).get(r, {}).get(d)
        return got[0] if got else None

    rk = ("emprestimos", "Rácio de empréstimos vencidos", setor, det, PCT)
    dk = ("emprestimos", "Devedores com empréstimos vencidos", setor, det, PCT)
    if reg != "Portugal":
        return {"racio": val(rk), "devedores": val(dk)}
    venc = val(("emprestimos", "Empréstimos vencidos", setor, det, M_EUR))
    tot = val(("emprestimos", "Empréstimos", setor, det, M_EUR))
    n = c = 0.0
    for r in s.get(dk, {}):
        pct = val(dk, r)
        num = val(("emprestimos", "Devedores", setor, det, MIL_DEV), r)
        if pct is not None and num:
            n += pct * num
            c += num
    return {
        "racio": (
            round(100 * venc / tot, 1) if venc is not None and tot else None
        ),
        "devedores": round(n / c, 1) if c else None,
    }


def _empresas_bp(s: dict, serie) -> dict:
    """Company indicators (Central de Balanços): the latest year for the
    Azores, Madeira and Portugal, the Azores by sector, and the Azores
    year by year."""

    def val(ind: str, unid: str, cae: str, reg: str, d: str):
        got = (
            s.get(("empresas", ind, "Empresas", cae, unid), {})
            .get(reg, {})
            .get(d)
        )
        return got[0] if got else None

    anos = sorted(
        s.get(
            (
                "empresas",
                "Número de empresas",
                "Empresas",
                TODAS_CAE,
                "Número de empresas",
            ),
            {},
        ).get("Açores", {})
    )
    if not anos:
        return {}
    d = anos[-1]
    comparar = []
    for ind, unid in EMPRESAS_IND:
        k = ("empresas", ind, "Empresas", TODAS_CAE, unid)
        linha = {"nome": ind, "url": serie(k)}
        for reg, rk in REG_K.items():
            linha[rk + "_s"] = _bp_fmt(unid, val(ind, unid, TODAS_CAE, reg, d))
        comparar.append(linha)
    setores = []
    caes = {k[3] for k in s if k[0] == "empresas"} - CAE_AGREGADOS
    for cae in caes:
        n = val("Número de empresas", "Número de empresas", cae, "Açores", d)
        if not n:
            continue

        def f(ind, unid, cae=cae):
            return _bp_fmt(unid, val(ind, unid, cae, "Açores", d))

        setores.append(
            {
                "nome": cae,
                "empresas": round(n),
                "pessoas_s": f(
                    "Número de pessoas ao serviço", "Número de pessoas"
                ),
                "vendas_s": f(
                    "Vendas e serviços prestados", "Milhares de euros"
                ),
                "autonomia_s": f("Autonomia financeira", PCT),
                "rendibilidade_s": f("Rendibilidade do ativo", PCT),
                "negativo_s": f(
                    "Empresas com resultado líquido negativo", "% das empresas"
                ),
                "pagamentos_s": f(
                    "Prazo médio de pagamentos", "Número de dias"
                ),
            }
        )
    setores.sort(key=lambda x: -x["empresas"])
    unidades = dict(EMPRESAS_IND)
    evolucao = []
    for a in reversed(anos):
        linha = {"ano": a[:4]}
        for ind, nome in (
            ("Número de empresas", "empresas"),
            ("Número de pessoas ao serviço", "pessoas"),
            ("Vendas e serviços prestados", "vendas"),
            ("Autonomia financeira", "autonomia"),
            ("Rendibilidade do ativo", "rendibilidade"),
            ("Empresas com resultado líquido negativo", "negativo"),
        ):
            u = unidades[ind]
            linha[nome + "_s"] = _bp_fmt(
                u, val(ind, u, TODAS_CAE, "Açores", a)
            )
        evolucao.append(linha)
    return {
        "ano": d[:4],
        "comparar": comparar,
        "setores": setores,
        "evolucao": evolucao,
    }


def credito_data(bp: tuple[list, list], ine: tuple[list, list] | None) -> dict:
    """docs/_data/credito.json for /dados/credito/: loans, deposits, FDI
    and company indicators of the Banco de Portugal, with figures per
    resident from the INE population."""
    s = bp_series(bp)
    pop = _populacao(ine)
    E = "emprestimos"
    hab = (E, "Empréstimos", "Particulares", "Habitação", M_EUR)
    con = (E, "Empréstimos", "Particulares", "Consumo e outros fins", M_EUR)
    par = (E, "Empréstimos", "Particulares", "", M_EUR)
    emp = (E, "Empréstimos", "Empresas", "", M_EUR)
    dep = {
        st: ("depositos", "Depósitos", st, "", M_EUR)
        for st in ("Particulares", "Empresas", "Emigrantes")
    }
    if not s.get(par, {}).get("Açores"):
        return {}

    def val(k: tuple, reg: str, d: str) -> float | None:
        got = s.get(k, {}).get(reg, {}).get(d)
        return got[0] if got else None

    def serie(k: tuple, reg: str = "Açores") -> str:
        sid = next((x for _, x in s.get(k, {}).get(reg, {}).values() if x), "")
        return BPSTAT_SERIE + sid if sid else ""

    ultimo = max(s[par]["Açores"])
    dep_ult = max(s.get(dep["Particulares"], {}).get("Açores", {}) or [ultimo])

    por_hab = []
    pop_ano = None
    for nome, k, d in (
        ("Crédito à habitação", hab, ultimo),
        ("Crédito ao consumo e outros fins", con, ultimo),
        ("Empréstimos a empresas", emp, ultimo),
        ("Depósitos de particulares", dep["Particulares"], dep_ult),
        ("Depósitos de empresas", dep["Empresas"], dep_ult),
    ):
        linha: dict = {"nome": nome, "url": serie(k)}
        for reg, rk in REG_K.items():
            v, (p, pop_ano) = val(k, reg, d), _pop(pop, reg, d)
            linha[rk] = round(v * 1e6 / p) if v and p else ""
        por_hab.append(linha)
    rel: dict = {}
    for reg, rk in REG_K.items():
        e = val(par, reg, dep_ult)
        dp = val(dep["Particulares"], reg, dep_ult)
        rel[rk] = round(100 * e / dp) if e and dp else ""

    incumprimento = []
    for nome, setor, det in (
        ("Crédito à habitação", "Particulares", "Habitação"),
        ("Consumo e outros fins", "Particulares", "Consumo e outros fins"),
        ("Empresas", "Empresas", ""),
    ):
        linha = {
            "nome": nome,
            "url": serie(
                (E, "Rácio de empréstimos vencidos", setor, det, PCT)
            ),
        }
        for reg, rk in REG_K.items():
            got = _vencidos(s, setor, det, reg, ultimo)
            linha[rk + "_racio_s"] = _pct_s(got["racio"])
            linha[rk + "_devedores_s"] = _pct_s(got["devedores"])
        incumprimento.append(linha)

    datas = [
        d for d in s[par]["Açores"] if d.endswith("-12-31") or d == ultimo
    ]
    serie_anual = []
    for d in sorted(datas, reverse=True):
        linha = {"periodo": d[:4] if d.endswith("-12-31") else _mes_ano(d)}
        for k, nome in (
            (hab, "habitacao"),
            (con, "consumo"),
            (emp, "empresas"),
            (dep["Particulares"], "dep_particulares"),
            (dep["Empresas"], "dep_empresas"),
            (dep["Emigrantes"], "dep_emigrantes"),
        ):
            v = val(k, "Açores", d)
            linha[nome] = round(v) if v is not None else ""
        for setor in ("Particulares", "Empresas"):
            linha[f"vencidos_{setor.lower()}_s"] = _pct_s(
                val(
                    (E, "Rácio de empréstimos vencidos", setor, "", PCT),
                    "Açores",
                    d,
                )
            )
        serie_anual.append(linha)

    um_ano = f"{int(ultimo[:4]) - 1}{ultimo[4:]}"
    h, h0 = val(hab, "Açores", ultimo), val(hab, "Açores", um_ano)
    cards = {
        "habitacao_m": round(h) if h is not None else "",
        "habitacao_cresc_s": (
            _pct_s(round(100 * (h / h0 - 1), 1))
            if h is not None and h0
            else ""
        ),
        "devedores_habitacao_mil": val(
            (E, "Devedores", "Particulares", "Habitação", MIL_DEV),
            "Açores",
            ultimo,
        ),
        "empresas_m": round(val(emp, "Açores", ultimo) or 0),
        "dep_particulares_m": round(
            val(dep["Particulares"], "Açores", dep_ult) or 0
        ),
        "dep_emigrantes_m": round(
            val(dep["Emigrantes"], "Açores", dep_ult) or 0
        ),
    }

    ide = []
    k_ide = {
        det: ("ide", "Investimento direto do exterior", "", det, M_EUR)
        for det in ("Sedes", "Estabelecimentos")
    }
    for d in sorted(s.get(k_ide["Sedes"], {}).get("Açores", {}), reverse=True):
        linha = {"ano": d[:4]}
        for det, nome in (("Sedes", "sedes"), ("Estabelecimentos", "estab")):
            a = val(k_ide[det], "Açores", d)
            linha[nome] = round(a) if a is not None else ""
            linha[nome + "_pct"] = _share(a, val(k_ide[det], "Portugal", d))
        ide.append(linha)

    return {
        "ultimo": ultimo,
        "ultimo_mes": _mes_ano(ultimo),
        "depositos_mes": _mes_ano(dep_ult),
        "populacao_ano": pop_ano or "",
        "cards": cards,
        "por_habitante": por_hab,
        "credito_depositos": rel,
        "incumprimento": incumprimento,
        "serie": serie_anual,
        "ide": ide,
        "ide_url": serie(k_ide["Sedes"]),
        "empresas": _empresas_bp(s, serie),
    }


def write_credito(docs: Path, tables: dict) -> None:
    data = {}
    if "bportugal" in tables:
        data = credito_data(tables["bportugal"], tables.get("ine"))
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "credito.json").write_text(
        json.dumps(_texts(data), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
