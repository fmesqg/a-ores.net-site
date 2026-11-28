"""Budget execution of the 19 Azorean câmaras, from the Anuário Financeiro
dos Municípios Portugueses (Ordem dos Contabilistas Certificados and IPCA).

    python3 bot/anuario.py data [--pdf FILE]

The DGAL publishes only what each câmara collected and paid, not what it
budgeted. The Anuário has two tables that compare both for the Azores:

- Quadro 2.6 "Grau de execução da receita cobrada": revenue collected as a
  share of the final (corrected) revenue budget, one row per câmara and one
  column per year for the last eleven years;
- R66 "Diferença entre a execução da receita liquidada e a execução dos
  compromissos": revenue assessed and expenditure committed, each as a share
  of the budget, for the last three years.

Writes data/anuario_execucao.csv (ano, geocod, municipio, receita_cobrada,
receita_liquidada, despesa_comprometida; percentages). Rows of years not in
the new edition are kept, and a newer edition wins for a repeated year.

The OCC page (occ.pt) does not link the PDF in its HTML, so each edition's
address goes in EDICOES by hand (one a year, out in November). Needs pypdf.
"""

import csv
import io
import re
import sys
import urllib.request
from pathlib import Path

if __package__:
    from .dgal import MUNICIPIOS, UA, azorean, pdf_text
else:
    from dgal import MUNICIPIOS, UA, azorean, pdf_text

# edition (year of the accounts) -> PDF
EDICOES = {
    2025: "https://www.occ.pt/sites/default/files/public/2026-11/"
    "DIG_anuario2025_capa.pdf",
}
COLS = [
    "ano",
    "geocod",
    "municipio",
    "receita_cobrada",
    "receita_liquidada",
    "despesa_comprometida",
]
PCT = r"-?\d{1,3},\d%"
# the Anuário's names for the câmaras whose DGAL name differs
NOMES = {"LAGOA (R.A.A.)": "LAGOA (SÃO MIGUEL)"}


def pct(s: str) -> float:
    return float(s.rstrip("%").replace(",", "."))


def nome(s: str) -> str:
    s = " ".join(s.split())
    return azorean(NOMES.get(s.upper(), s))


def _tabela(text: str, titulo: str) -> list[str]:
    """The lines of the table that starts at its title (not at the mention
    of the title in the list of tables or in the text)."""
    for m in re.finditer(re.escape(titulo), text):
        resto = text[m.end() : m.end() + 6000].splitlines()
        if any(re.match(r"^1 \D+ [PMG] ", linha) for linha in resto[:40]):
            return resto
    raise ValueError(f"table not found: {titulo}")


def parse_receita(text: str) -> list[dict]:
    """Quadro 2.6: revenue collected / final budget, per câmara and year."""
    linhas = _tabela(text, "Grau de execução da receita cobrada em")
    anos = None
    out = []
    for linha in linhas:
        if anos is None and re.fullmatch(r"(20\d\d ?)+", linha.strip()):
            anos = [int(a) for a in linha.split()]
            continue
        m = re.match(r"^\d{1,2} (\D+?) [PMG] ((?:" + PCT + r" ?)+)$", linha)
        if m and anos:
            key = nome(m.group(1))
            vals = re.findall(PCT, m.group(2))
            if not key or len(vals) != len(anos):
                raise ValueError(f"Quadro 2.6: unreadable row {linha!r}")
            out += [
                {"ano": a, "key": key, "receita_cobrada": pct(v)}
                for a, v in zip(anos, vals, strict=True)
            ]
        if linha.startswith("Grau execução Receita") or len(out) >= 19 * 11:
            break
    if len({r["key"] for r in out}) != len(MUNICIPIOS):
        raise ValueError(f"Quadro 2.6: {len(out)} values, not 19 câmaras")
    return out


def parse_compromissos(text: str) -> list[dict]:
    """R66: revenue assessed and expenditure committed / final budget, for
    the three years in the table's header."""
    linhas = _tabela(text, "R66 - Diferença entre a execução da receita")
    anos = None
    out = []
    for linha in linhas:
        if anos is None and re.fullmatch(r"(20\d\d ?){3}", linha.strip()):
            anos = [int(a) for a in linha.split()]
            continue
        m = re.match(r"^\d{1,2} (\D+?) [PMG] ((?:" + PCT + r" ?){9})$", linha)
        if m and anos:
            key = nome(m.group(1))
            if not key:
                raise ValueError(f"R66: unknown câmara {linha!r}")
            v = [pct(x) for x in re.findall(PCT, m.group(2))]
            for i, a in enumerate(anos):
                out.append(
                    {
                        "ano": a,
                        "key": key,
                        "receita_liquidada": v[3 * i],
                        "despesa_comprometida": v[3 * i + 1],
                    }
                )
        if linha.startswith("Média dos municípios"):
            break
    if len({r["key"] for r in out}) != len(MUNICIPIOS):
        raise ValueError(f"R66: {len(out)} values, not 19 câmaras")
    return out


def parse(text: str) -> list[dict]:
    rows: dict = {}
    for r in parse_receita(text) + parse_compromissos(text):
        geocod, municipio = MUNICIPIOS[r.pop("key")]
        k = (str(r["ano"]), geocod)
        rows.setdefault(
            k,
            {c: "" for c in COLS} | {"geocod": geocod, "municipio": municipio},
        ).update(r)
    return [rows[k] for k in sorted(rows)]


def merge(old: list[dict], new: list[dict]) -> list[dict]:
    novos = {(str(r["ano"]), r["geocod"]) for r in new}
    keep = [r for r in old if (r["ano"], r["geocod"]) not in novos]
    return sorted(keep + new, key=lambda r: (str(r["ano"]), r["geocod"]))


def main(out_dir: Path, pdf: Path | None = None) -> int:
    if pdf:
        data = pdf.read_bytes()
    else:
        url = EDICOES[max(EDICOES)]
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=300) as r:
            data = r.read()
    new = parse(pdf_text(data))
    path = out_dir / "anuario_execucao.csv"
    old = (
        list(csv.DictReader(path.open(encoding="utf-8")))
        if path.exists()
        else []
    )
    rows = merge(old, new)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(buf.getvalue(), encoding="utf-8")
    anos = sorted({str(r["ano"]) for r in rows})
    print(f"{len(rows)} rows, {anos[0]}-{anos[-1]}")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    pdf_arg = None
    if "--pdf" in args:
        i = args.index("--pdf")
        pdf_arg = Path(args[i + 1])
        del args[i : i + 2]
    sys.exit(main(Path(args[0] if args else "data"), pdf_arg))
