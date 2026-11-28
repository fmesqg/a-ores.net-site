"""Headline numbers for /introducao/ and the section pages (INE, BEO, SREA, Tribunal de Contas): docs/_data/resumo.json."""

import json
from pathlib import Path

from .comum import MESES, _mes, _num, _texts


def ine_news(cols: list[str], rows: list[list], limit: int = 8) -> list[dict]:
    """Indicators most recently updated by INE, newest first, with the
    latest period they cover."""
    c = {k: i for i, k in enumerate(cols)}
    by: dict[str, dict] = {}
    for r in rows:
        x = by.setdefault(
            r[c["varcd"]],
            {
                "varcd": r[c["varcd"]],
                "indicador": r[c["indicador"]],
                "tema": r[c["tema"]],
                "atualizado": r[c["atualizado"]],
                "data": "",
                "periodo": "",
            },
        )
        if r[c["geocod"]] == "20" and r[c["data"]] > x["data"]:
            x["data"], x["periodo"] = r[c["data"]], r[c["periodo"]]
    news = sorted(
        by.values(), key=lambda x: (x["atualizado"], x["data"]), reverse=True
    )
    return news[:limit]


def write_ine_news(docs: Path, cols: list[str], rows: list[list]) -> None:
    """docs/_data/ine_novidades.json, for the home page (Jekyll reads _data
    at build time; pages.yml runs this script before Jekyll)."""
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "ine_novidades.json").write_text(
        json.dumps(ine_news(cols, rows), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )


# Indicators shown on /introducao/ (Açores vs Madeira vs país, latest year).
RESUMO_INE = (
    "0012918",  # população residente
    "0012909",  # índice de envelhecimento
    "0012757",  # rendimento mediano após IRS por sujeito passivo
    "0012656",  # ganho médio mensal
    "0013420",  # RSI por 1000 habitantes
    "0014698",  # renda mediana, novos contratos (€/m²)
    "0013210",  # dormidas por 100 habitantes
    "0014103",  # PIB por habitante
    "0014663",  # inflação (IPC, variação homóloga)
    "0012136",  # taxa de desemprego, trimestral
    "0012749",  # rendimento bruto mediano por sujeito passivo
)
PIB_HAB, MEDIANA_BRUTO, GANHO = "0014103", "0012749", "0012656"


def salario_pib(cols: list[str], rows: list[list]) -> dict:
    """Gross pay against GDP per head, Açores/Madeira/país, for the latest
    year with the three series: the median gross income declared per
    taxpayer (IRS, annual) and the mean monthly earnings (Quadros de
    Pessoal) times 14, an açores.net estimate of a year's pay."""
    c = {k: i for i, k in enumerate(cols)}
    val: dict[tuple, float] = {}
    url = {}
    for r in rows:
        v, g = r[c["varcd"]], r[c["geocod"]]
        if v in (PIB_HAB, MEDIANA_BRUTO, GANHO) and g in ("20", "30", "PT"):
            if not r[c["categoria"]] and (x := _num(r[c["valor"]])):
                val[(v, g, r[c["periodo"]])] = x
                url[v] = r[c["url"]]
    anos = [
        a
        for a in {k[2] for k in val}
        if all(
            (v, g, a) in val
            for v in (PIB_HAB, MEDIANA_BRUTO, GANHO)
            for g in ("20", "30", "PT")
        )
    ]
    if not anos:
        return {}
    ano = max(anos)
    locais = []
    for g, nome in (("20", "Açores"), ("30", "Madeira"), ("PT", "Portugal")):
        pib = val[(PIB_HAB, g, ano)]
        med = val[(MEDIANA_BRUTO, g, ano)]
        ganho = val[(GANHO, g, ano)]
        locais.append(
            {
                "local": nome,
                "pib": pib,
                "mediana": med,
                "mediana_pct": round(100 * med / pib),
                "ganho": ganho,
                "ganho_ano": round(ganho * 14),
                "ganho_pct": round(100 * ganho * 14 / pib),
            }
        )
    return {
        "ano": ano,
        "locais": locais,
        "url_pib": url[PIB_HAB],
        "url_mediana": url[MEDIANA_BRUTO],
        "url_ganho": url[GANHO],
    }


def resumo_ine(cols: list[str], rows: list[list]) -> dict:
    """Latest Região/país values of RESUMO_INE, plus population by island."""
    c = {k: i for i, k in enumerate(cols)}
    out: dict = {}
    for v in RESUMO_INE:
        own = [r for r in rows if r[c["varcd"]] == v and not r[c["categoria"]]]
        top = [r for r in own if r[c["geocod"]] in ("20", "30", "PT")]
        if not top:
            continue
        last = max(r[c["data"]] for r in top)
        x = {"periodo": "", "url": "", "unidade": ""}
        for r in top:
            if r[c["data"]] != last:
                continue
            key = {"20": "acores", "30": "madeira", "PT": "pt"}[r[c["geocod"]]]
            x[key] = _num(r[c["valor"]])
            x["periodo"], x["url"] = r[c["periodo"]], r[c["url"]]
            x["unidade"] = r[c["unidade"]]
        if v == "0012918":
            ilhas: dict[str, float] = {}
            for r in own:
                if r[c["data"]] == last and r[c["nivel"]] == "Concelho":
                    n = _num(r[c["valor"]]) or 0
                    ilhas[r[c["ilha"]]] = ilhas.get(r[c["ilha"]], 0) + n
            x["ilhas"] = [
                {"ilha": k, "valor": round(n)}
                for k, n in sorted(ilhas.items(), key=lambda t: -t[1])
            ]
        out[v] = x
    return out


def resumo_beo(cols: list[str], rows: list[list]) -> dict:
    """The last complete year of the budget execution bulletins, consolidated:
    where the money came from, what it paid and the balance (millions of €)."""
    c = {k: i for i, k in enumerate(cols)}
    euro = [r for r in rows if r[c["medida"]] == "Montante (€)"]
    sint = [
        r
        for r in euro
        if r[c["quadro"]] == "Síntese global"
        and r[c["dimensao"]] == "Consolidado"
    ]
    anos = sorted({r[c["ano"]] for r in sint if r[c["mes"]] == "12"})
    if not anos:
        return {}
    ano = anos[-1]
    dez = [r for r in sint if r[c["ano"]] == ano and r[c["mes"]] == "12"]
    by = {r[c["caminho"]]: _num(r[c["valor"]]) or 0.0 for r in dez}

    def m(*paths: str) -> float:
        return round(sum(by.get(p, 0.0) for p in paths) / 1e6, 1)

    rc, rk = "Receita corrente › ", "Receita de capital › "
    receita = m("Receita efetiva")
    impostos = m(rc + "Impostos diretos", rc + "Impostos indiretos")
    estado = m(
        rc + "Transferências correntes › Administração central - Estado",
        rk + "Transferências de capital › Administração central - Estado",
    )
    exterior = m(
        rc + "Transferências correntes › Resto do mundo",
        rk + "Transferências de capital › Resto do mundo",
    )
    dc = "Despesa corrente › "
    despesa = m("Despesa efetiva")
    pessoal = m(dc + "Despesas com pessoal")
    bens = m(dc + "Aquisição de bens e serviços correntes")
    juros = m(dc + "Juros e outros encargos")
    capital = m("Despesa de capital")
    func = [
        r
        for r in euro
        if r[c["quadro"]] == "Despesa do GRA por função"
        and r[c["ano"]] == ano
        and r[c["mes"]] == "12"
        and r[c["nivel"]] == "1"
    ]
    funcoes = sorted(
        (
            {
                "nome": r[c["rubrica"]].removesuffix(" n.e."),
                "valor": round((_num(r[c["valor"]]) or 0) / 1e6, 1),
            }
            for r in func
        ),
        key=lambda x: -x["valor"],
    )
    total_f = round(sum(x["valor"] for x in funcoes), 1)
    if len(funcoes) > 5:
        resto = round(total_f - sum(x["valor"] for x in funcoes[:5]), 1)
        funcoes = funcoes[:5] + [{"nome": "Todas as outras", "valor": resto}]
    return {
        "ano": ano,
        "boletim": dez[0][c["boletim"]] if dez else "",
        "receita": receita,
        "receitas": [
            {"nome": "Impostos cobrados nos Açores", "valor": impostos},
            {"nome": "Transferências do Estado", "valor": estado},
            {
                "nome": "Do exterior (sobretudo fundos europeus)",
                "valor": exterior,
            },
            {
                "nome": "Outras receitas",
                "valor": round(receita - impostos - estado - exterior, 1),
            },
        ],
        "despesa": despesa,
        "despesas": [
            {"nome": "Salários e outros custos com pessoal", "valor": pessoal},
            {"nome": "Compras de bens e serviços", "valor": bens},
            {
                "nome": "Investimento e apoios ao investimento",
                "valor": capital,
            },
            {"nome": "Juros da dívida", "valor": juros},
            {
                "nome": "Outras despesas",
                "valor": round(despesa - pessoal - bens - capital - juros, 1),
            },
        ],
        "saldo": m("Saldo global"),
        "saldo_abs": abs(m("Saldo global")),
        "funcoes": funcoes,
        "funcoes_total": total_f,
    }


def srea_json(cols: list[str], rows: list[list]) -> list[dict]:
    """data/srea.csv grouped by series, for the charts on /dados/srea/:
    one entry per (serie, indicador, rubrica, local) with its points."""
    c = {k: i for i, k in enumerate(cols)}
    by: dict[tuple, dict] = {}
    for r in sorted(rows, key=lambda r: r[c["data"]]):
        k = tuple(r[c[x]] for x in ("serie", "indicador", "rubrica", "local"))
        s = by.setdefault(
            k,
            {
                "serie": k[0],
                "indicador": k[1],
                "rubrica": k[2],
                "local": k[3],
                "unidade": r[c["unidade"]],
                "pagina": r[c["pagina"]],
                "p": [],
            },
        )
        s["ficheiro"] = r[c["ficheiro"]]
        p = [r[c["periodo"]], _num(r[c["valor"]])]
        if r[c["nota"]]:
            p.append(r[c["nota"]])
        s["p"].append(p)
    return list(by.values())


def resumo_srea(cols: list[str], rows: list[list]) -> dict:
    """Latest SREA figures for /introducao/ and /dados/srea/."""
    c = {k: i for i, k in enumerate(cols)}

    def pts(serie, indicador, rubrica="Total", local="Açores") -> list:
        return sorted(
            (
                r
                for r in rows
                if r[c["serie"]] == serie
                and r[c["indicador"]] == indicador
                and r[c["rubrica"]] == rubrica
                and r[c["local"]] == local
            ),
            key=lambda r: r[c["data"]],
        )

    def v(r) -> float:
        return _num(r[c["valor"]]) or 0.0

    out: dict = {}
    vh = pts("ipc", "Variação homóloga")
    if vh:
        last = vh[-1]
        m12 = {
            r[c["data"]]: v(r)
            for r in pts("ipc", "Variação média dos últimos 12 meses")
        }
        classes = sorted(
            (
                {"nome": r[c["rubrica"]], "valor": v(r)}
                for r in rows
                if r[c["serie"]] == "ipc"
                and r[c["indicador"]] == "Variação homóloga"
                and r[c["rubrica"]] != "Total"
                and r[c["data"]] == last[c["data"]]
            ),
            key=lambda x: -x["valor"],
        )
        out["ipc"] = {
            "valor": v(last),
            "cem": round(100 + v(last), 2),
            "media12": m12.get(last[c["data"]]),
            "periodo": _mes(last[c["data"]]),
            "antes": _mes(
                f"{int(last[c['data']][:4]) - 1}{last[c['data']][4:]}"
            ),
            "mais": classes[:3],
            "menos": classes[-2:][::-1],
            "url": last[c["pagina"]],
        }
    for serie, ind in (
        ("iae", "Indicador de atividade económica"),
        ("icp", "Indicador do consumo privado"),
    ):
        s = pts(serie, ind)
        if s:
            out[serie] = {
                "valor": round(v(s[-1]), 1),
                "periodo": _mes(s[-1][c["data"]]),
                "url": s[-1][c["pagina"]],
            }
    d = pts("desemprego", "Taxa de desemprego")
    if d:
        last = d[-1]
        y, q = last[c["periodo"]].split("-T")
        prev = {r[c["periodo"]]: v(r) for r in d}.get(f"{int(y) - 1}-T{q}")
        out["desemprego"] = {
            "valor": v(last),
            "antes": prev,
            "periodo": f"{q}.º trimestre de {y}",
            "periodo_antes": f"{q}.º trimestre de {int(y) - 1}",
            "nota": last[c["nota"]],
            "url": last[c["pagina"]],
        }
    dorm = [r for r in rows if r[c["serie"]] == "dormidas"]
    if dorm:
        # the last month both kinds of accommodation have published
        last = min(
            max(r[c["data"]] for r in dorm if r[c["rubrica"]] == k)
            for k in {r[c["rubrica"]] for r in dorm}
        )
        y, m = int(last[:4]), int(last[5:7])

        def ytd(local, year):
            return sum(
                v(r)
                for r in dorm
                if r[c["local"]] == local
                and r[c["data"]][:4] == str(year)
                and int(r[c["data"]][5:7]) <= m
            )

        ilhas = []
        for local in sorted({r[c["local"]] for r in dorm} - {"Açores"}):
            a, b = ytd(local, y), ytd(local, y - 1)
            ilhas.append(
                {
                    "ilha": local,
                    "valor": round(a),
                    "var": round(100 * (a - b) / b, 1) if b else None,
                }
            )
        ilhas.sort(key=lambda x: -x["valor"])
        a, b = ytd("Açores", y), ytd("Açores", y - 1)
        out["dormidas"] = {
            "valor": round(a),
            "antes": round(b),
            "var": round(100 * (a - b) / b, 1) if b else None,
            "periodo": (
                f"janeiro a {MESES[m - 1]} de {y}"
                if m > 1
                else f"janeiro de {y}"
            ),
            "ilhas": ilhas,
            "url": dorm[0][c["pagina"]],
        }
    ph = [r for r in rows if r[c["serie"]] == "pib_hab"]
    if ph:
        ano = max(r[c["periodo"]] for r in ph)
        last = [r for r in ph if r[c["periodo"]] == ano]
        top = max(v(r) for r in last if r[c["local"]] != "Açores")
        reg = next((r for r in last if r[c["local"]] == "Açores"), None)
        total = next(
            (
                v(r)
                for r in rows
                if r[c["serie"]] == "pib"
                and r[c["local"]] == "Açores"
                and r[c["periodo"]] == ano
            ),
            None,
        )
        out["pib_hab"] = {
            "ano": ano,
            "provisorio": any(r[c["nota"]] for r in last),
            "acores": v(reg) if reg else None,
            "total_mm": round(total / 1e9, 1) if total else None,
            "por_ilha": [
                {
                    "ilha": r[c["local"]],
                    "valor": v(r),
                    "pct": round(100 * v(r) / top),
                }
                for r in sorted(last, key=lambda r: -v(r))
                if r[c["local"]] != "Açores"
            ],
            "url": last[0][c["pagina"]],
        }
    return out


def resumo_tdc(tdc: tuple[list, list], valores: tuple[list, list]) -> dict:
    """Latest Tribunal de Contas parecer for /financas/: debt, deficit,
    money left out of the Conta, reservations and what happened to the
    recommendations of the previous parecer."""
    cols, rows = tdc
    t = [dict(zip(cols, r, strict=False)) for r in rows]
    if not t:
        return {}
    conta = max(r["conta"] for r in t)
    last = [r for r in t if r["conta"] == conta]
    out: dict = {
        "conta": conta,
        "url": last[0]["parecer"],
        "juizo": next((r["texto"] for r in last if r["tipo"] == "juízo"), ""),
        "reservas": sum(r["tipo"] == "reserva" for r in last),
        "recomendacoes": sum(r["tipo"] == "recomendação" for r in last),
    }
    # Recommendations of the previous parecer, as assessed in this one.
    prev = [
        r
        for r in t
        if r["tipo"] == "recomendação" and r["situacao"].endswith(f"({conta})")
    ]
    if prev:
        estados: dict[str, int] = {}
        for r in prev:
            k = r["situacao"].rsplit(" (", 1)[0]
            estados[k] = estados.get(k, 0) + 1
        out["avaliadas"] = len(prev)
        out["estados"] = [{"nome": k, "n": n} for k, n in estados.items()]
        desde = [int(r["desde"]) for r in prev if r["desde"].isdigit()]
        if desde:
            out["desde"] = min(desde)
    vcols, vrows = valores
    v = [dict(zip(vcols, r, strict=False)) for r in vrows]

    def val(rubrica: str, ano: str, quadro: str) -> float | None:
        for r in v:
            if (r["rubrica"], r["ano"], r["quadro"]) == (rubrica, ano, quadro):
                return _num(r["valor"])
        return None

    ind, conta_q = (
        "Indicadores",
        "Conta do sector público administrativo regional",
    )
    anterior = str(int(conta) - 1)
    divida = val("Dívida total", conta, ind)
    divida_ant = val("Dívida total", anterior, ind)
    if divida is not None:
        out["divida"] = divida
        if divida_ant:
            out["divida_var"] = round(100 * (divida / divida_ant - 1), 1)
    saldo = val("Saldo global ou efetivo", conta, conta_q)
    if saldo is not None:
        out["saldo"] = round(saldo / 1e6, 1)
        out["saldo_abs"] = abs(out["saldo"])
    for k, rub in (
        ("receita_fora", "Receita não registada na Conta"),
        ("despesa_fora", "Despesa não registada na Conta"),
    ):
        x = val(rub, conta, ind)
        if x is not None:
            out[k] = x
    return out


def write_resumo(docs: Path, tables: dict) -> None:
    """docs/_data/resumo.json: the few numbers /introducao/ and /financas/ show, computed
    here so that page does not download the full CSVs."""
    out: dict = {}
    if "ine" in tables:
        out["ine"] = resumo_ine(*tables["ine"])
        out["salario_pib"] = salario_pib(*tables["ine"])
    if "beo" in tables:
        out["beo"] = resumo_beo(*tables["beo"])
        pop = out.get("ine", {}).get("0012918", {}).get("acores")
        if out["beo"] and pop:
            out["beo"]["despesa_hab"] = round(
                out["beo"]["despesa"] * 1e6 / pop
            )
    if "srea" in tables:
        out["srea"] = resumo_srea(*tables["srea"])
    if "tdc" in tables and "tdc_valores" in tables:
        out["tdc"] = resumo_tdc(tables["tdc"], tables["tdc_valores"])
    (docs / "_data").mkdir(exist_ok=True)
    (docs / "_data" / "resumo.json").write_text(
        json.dumps(_texts(out), ensure_ascii=False, indent=1), encoding="utf-8"
    )
