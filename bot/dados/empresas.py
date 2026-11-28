"""Regional public companies (CFP) and the 100 largest companies: docs/_data/sper.json, maiores.json, economia."""

import json
import re
from pathlib import Path

from .comum import _dicts, _fold, _num, _texts
from .publico import publico_data


def _rel_key(rel: str) -> tuple[int, int]:
    n, y = rel.split("/")
    return int(y), int(n)


# CAE Rev. 3 sections, as the CFP list gives them (one letter).
CAE = {
    "A": "Agricultura e pesca",
    "C": "Indústria",
    "D": "Eletricidade e gás",
    "E": "Água e resíduos",
    "F": "Construção",
    "G": "Comércio",
    "H": "Transportes",
    "I": "Alojamento e restauração",
    "J": "Informação e comunicação",
    "L": "Imobiliário",
    "M": "Atividades técnicas",
    "N": "Serviços administrativos",
    "O": "Administração pública",
    "Q": "Saúde",
    "R": "Cultura e espetáculos",
}
SPER_IND = {
    "trabalhadores": "Número de Trabalhadores",
    "vn": "Volume de Negócios",
    "vab": "Valor Acrescentado Bruto (VAB)",
    "ebitda": "EBITDA",
    "rl": "Resultado Líquido",
    "cp": "Capital Próprio",
    "passivo": "Total do Passivo",
    "ativo": "Total do Ativo",
    "pessoal": "Gastos com Pessoal",
}
ESFORCO = "Esforço financeiro líquido da Região"
ESFORCO_TOTAL = "Esforço financeiro líquido (2)-(1)"


def sper_data(
    sper: tuple[list, list],
    empresas: tuple[list, list] | None = None,
    regiao: tuple[list, list] | None = None,
) -> dict:
    """data/sper*.csv (bot/cfp.py) for /dados/sper/ and /economia/: sector
    totals by year, one entry per company for the latest year, the
    Region's net financial effort and the sector's weight."""
    v = _dicts(sper)
    if not v:
        return {}
    by = {
        (r["sigla"], int(r["ano"]), r["indicador"]): _num(r["valor"])
        for r in v
    }
    anos = sorted({int(r["ano"]) for r in v})
    ano = anos[-1]
    rel = max({r["relatorio"] for r in v}, key=_rel_key)
    last = next(r for r in v if r["relatorio"] == rel)
    siglas = sorted({r["sigla"] for r in v})

    def amount(k: str, x: float, dec: int = 2) -> float:
        """People as integers, money in million euros (+ 0.0 drops -0.0)."""
        return int(x) if k == "trabalhadores" else round(x / 1e6, dec) + 0.0

    totais = []
    for a in anos:
        t: dict = {"ano": a}
        for k, ind in SPER_IND.items():
            xs = [
                by[s, a, ind]
                for s in siglas
                if by.get((s, a, ind)) is not None
            ]
            if xs:
                t[k] = amount(k, sum(xs), 1)
        t["prejuizo"] = sum(
            1 for s in siglas if (by.get((s, a, SPER_IND["rl"])) or 0) < 0
        )
        totais.append(t)
    out: dict = {
        "relatorio": rel,
        "url": last["url"],
        "ficheiro": last.get("ficheiro", ""),
        "ano": ano,
        "anos": [{"ano": a} for a in anos],
        "totais": totais,
        "total": totais[-1],
    }
    lista = (
        [e for e in _dicts(empresas) if e["relatorio"] == rel]
        if empresas
        else []
    )
    emp = []
    for e in lista or [{"sigla": s, "empresa": s} for s in siglas]:
        s = e["sigla"]
        part = _num(e.get("participacao", ""))
        d: dict = {
            "sigla": s,
            "nome": _curto(e["empresa"], s),
            "empresa": e["empresa"],
            "setor": CAE.get(e.get("cae", ""), e.get("cae", "")),
            "acionista": e.get("acionista", ""),
            "ap": e.get("ap") == "sim",
            "nota": e.get("nota", ""),
        }
        if part is not None:
            d["participacao"] = round(100 * part, 1)
        for k, ind in SPER_IND.items():
            x = by.get((s, ano, ind))
            if x is not None:
                d[k] = amount(k, x)
        d["rl_anos"] = [
            (
                {"ano": a, "v": amount("rl", by[s, a, SPER_IND["rl"]])}
                if by.get((s, a, SPER_IND["rl"])) is not None
                else {"ano": a}
            )
            for a in anos
        ]
        emp.append(d)
    emp.sort(key=lambda d: -d.get("vn", -1e9))
    out["empresas"] = emp
    out["n"] = len(emp)
    out["sem_ficha"] = [d["nome"] for d in emp if "vn" not in d]
    out["cp_negativo"] = [d["nome"] for d in emp if d.get("cp", 0) < 0]
    if regiao:
        out.update(_sper_regiao(_dicts(regiao), rel))
    return out


def _sper_regiao(rows: list[dict], rel: str) -> dict:
    out: dict = {}
    mine = [r for r in rows if r["relatorio"] == rel]
    esf = [r for r in mine if r["quadro"] == ESFORCO]
    if esf:
        anos = sorted({int(r["ano"]) for r in esf})
        linhas: dict[str, dict] = {}
        for r in esf:
            ln = linhas.setdefault(
                r["rubrica"],
                {"rubrica": r["rubrica"], "unidade": r["unidade"], "v": {}},
            )
            ln["v"][int(r["ano"])] = _num(r["valor"])
        out["esforco"] = {
            "relatorio": rel,
            "url": esf[0]["url"],
            "nota": next((r["nota"] for r in esf if r["nota"]), ""),
            "anos": [{"ano": a} for a in anos],
            "linhas": [
                {
                    "rubrica": ln["rubrica"],
                    "unidade": ln["unidade"],
                    "total": ln["rubrica"].startswith("Esforço"),
                    "valores": [
                        {"v": ln["v"][a]} if a in ln["v"] else {} for a in anos
                    ],
                }
                for ln in linhas.values()
            ],
        }
        tot = {
            int(r["ano"]): _num(r["valor"])
            for r in esf
            if r["rubrica"] == ESFORCO_TOTAL
        }
        if tot:
            a = max(tot)
            out["esforco"].update(ano=a, total=tot[a])
            # The same year in an older report, when the method differed.
            for r in rows:
                if (
                    r["relatorio"] != rel
                    and r["quadro"] == ESFORCO
                    and r["rubrica"] == ESFORCO_TOTAL
                    and int(r["ano"]) in tot
                    and abs(_num(r["valor"]) - tot[int(r["ano"])]) > 1
                ):
                    out["esforco"]["antes"] = {
                        "relatorio": r["relatorio"],
                        "url": r["url"],
                        "ano": int(r["ano"]),
                        "valor": _num(r["valor"]),
                        "agora": tot[int(r["ano"])],
                    }
    peso = [r for r in mine if r["quadro"] == "Peso na economia"]
    for k, start in (
        ("vab_pib", "Peso do SERAA"),
        ("emprego", "Proporção do SERAA"),
    ):
        xs = [r for r in peso if r["rubrica"].startswith(start)]
        if xs:
            r = max(xs, key=lambda r: int(r["ano"]))
            out[k] = round(_num(r["valor"]), 1)
            out["peso_ano"] = int(r["ano"])
    return out


def _curto(empresa: str, sigla: str) -> str:
    """Readable short name: 'Sata Air Açores, S.A.' -> 'SATA Air Açores',
    'HDES - Hospital Divino Espirito Santo, E.P.E.R.' -> 'HDES'."""
    nome = empresa.split(",")[0].strip()
    if " - " in nome or len(nome) > 22:
        return sigla
    return re.sub(r"^Sata\b", "SATA", nome)


def _company_keys(name: str, loose: bool) -> set[str]:
    out = {_fold(name.split(",")[0])}
    if loose:
        out.add(_fold(name.split(" - ")[0]))
    return out


def maiores_data(
    maiores: tuple[list, list], sper_lista: list[dict] | None = None
) -> dict:
    """The largest companies (data/maiores_<ano>.csv, in thousands of euros)
    for /dados/maiores-empresas/ and /economia/, with the regional public
    companies among them marked."""
    m = _dicts(maiores)
    if not m:
        return {}
    # Full CFP names only: a sigla such as "SATA" would also match a private
    # "SATA - ..." company by its loose key.
    publicas = {}
    for e in sper_lista or []:
        for k in _company_keys(e["empresa"], False):
            publicas[k] = e["sigla"]

    def num(x: str) -> float:
        return _num(x) or 0.0

    emp = []
    for r in m:
        sigla = next(
            (
                publicas[k]
                for k in _company_keys(r["empresa"], True)
                if k in publicas
            ),
            "",
        )
        d = {
            "posicao": int(r["posicao"]),
            "empresa": r["empresa"],
            "ilha": r["ilha"],
            "setor": r["setor"],
            "trabalhadores": int(num(r["trabalhadores"])),
            "vn": round(num(r["volume_negocios"]) / 1e3, 1),
            "rl": round(num(r["resultado_liquido"]) / 1e3, 1),
            "publica": sigla,
        }
        if r["cresc_vn_pct"]:
            d["cresc_vn"] = num(r["cresc_vn_pct"])
        emp.append(d)
    emp.sort(key=lambda d: d["posicao"])
    vn = sum(d["vn"] for d in emp)

    def groups(key: str) -> list[dict]:
        g: dict[str, dict] = {}
        for d in emp:
            x = g.setdefault(
                d[key], {"nome": d[key], "n": 0, "vn": 0.0, "trabalhadores": 0}
            )
            x["n"] += 1
            x["vn"] += d["vn"]
            x["trabalhadores"] += d["trabalhadores"]
        out = sorted(g.values(), key=lambda x: -x["vn"])
        for x in out:
            x["vn"] = round(x["vn"], 1)
            x["pct"] = round(100 * x["vn"] / vn) if vn else 0
        return out

    pub = [d for d in emp if d["publica"]]
    return {
        "ano": int(m[0]["ano"]),
        "fonte": m[0]["fonte"],
        "url": m[0]["url"],
        "n": len(emp),
        "vn": round(vn, 1),
        "trabalhadores": sum(d["trabalhadores"] for d in emp),
        "top10_pct": (
            round(100 * sum(d["vn"] for d in emp[:10]) / vn) if vn else 0
        ),
        "prejuizo": sum(1 for d in emp if d["rl"] < 0),
        "publicas": len(pub),
        "publicas_pct": (
            round(100 * sum(d["vn"] for d in pub) / vn) if vn else 0
        ),
        "privadas": len(emp) - len(pub),
        "privadas_vn": round(vn - sum(d["vn"] for d in pub), 1),
        "privadas_trabalhadores": sum(
            d["trabalhadores"] for d in emp if not d["publica"]
        ),
        "setores": groups("setor"),
        "ilhas": groups("ilha"),
        "empresas": emp,
    }


def write_economia(docs: Path, tables: dict) -> None:
    """docs/_data/sper.json, maiores.json and publico.json for the Economia
    section."""
    (docs / "_data").mkdir(exist_ok=True)
    sper: dict = {}
    if "sper" in tables:
        sper = sper_data(
            tables["sper"],
            tables.get("sper_empresas"),
            tables.get("sper_regiao"),
        )
    maiores: dict = {}
    if "maiores" in tables:
        lista = (
            [
                e
                for e in _dicts(tables["sper_empresas"])
                if e["relatorio"] == sper.get("relatorio")
            ]
            if "sper_empresas" in tables
            else []
        )
        maiores = maiores_data(tables["maiores"], lista)
        posicao = {
            d["publica"]: d["posicao"]
            for d in maiores["empresas"]
            if d["publica"]
        }
        for d in sper.get("empresas", []):
            if d["sigla"] in posicao:
                d["posicao"] = posicao[d["sigla"]]
        if sper:
            sper["maiores_ano"] = maiores["ano"]
    publico: dict = {}
    if "emprego_publico" in tables:
        publico = publico_data(
            tables["emprego_publico"],
            tables.get("srea"),
            sper,
            tables.get("ine"),
            tables.get("censos2021_setores"),
        )
    for name, data in (
        ("sper", sper),
        ("maiores", maiores),
        ("publico", publico),
    ):
        (docs / "_data" / f"{name}.json").write_text(
            json.dumps(_texts(data), ensure_ascii=False, indent=1),
            encoding="utf-8",
        )
