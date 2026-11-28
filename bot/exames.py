"""National exam results of Azorean schools, beside the Azores, Madeira,
the mainland and the whole country, from the Júri Nacional de Exames'
databases for the press (published by the DGEEC on infoescolas.pt).

Usage: python3 bot/exames.py data [--tudo]   (stdlib + the mdb-export
command of mdbtools: `brew install mdbtools`, `apt-get install mdbtools`)

The databases are Access files (.mdb) in one zip per year and level, linked
from infoescolas.pt/bds.asp: `enes<ano>` (secondary exams, 11th and 12th
grade) and `eneb<ano>` (9th grade provas finais). Each holds every exam
taken in the country, one row per exam, without names. The page keeps only
the last three years, so data/exames.csv accumulates; a year is read again
when its file name changes (2025's secondary file came back as `_v2`) or
with --tudo.

What is counted is what the press rankings count:
  secundario  1st phase, internal students, exams taken for approval;
              `media` = exam grade 0-200, `media_interna` = the school's
              internal final grade (CIF, 0-20) of the same students,
              `positivas` = % of exams at 95 or more
  basico      1st phase, internal students, Português (91) and
              Matemática (92) of the 9th grade, by the school the student
              attends (EscolaOrigem); `media` = 0-100 points,
              `media_interna` = the internal level (1-5), `positivas` = %
              at level 3 or more

Rows (tipo): one per Azorean school, exam and year, plus the regions
`AZ` (Açores), `MD` (Madeira), `CO` (mainland) and `PT` (the country,
schools abroad left out). Exam `todos` is every exam of the level pooled;
for schools it carries `posicao`/`n_escolas`: the school's place among
every school in the country with at least MIN_PROVAS exams (1 = highest
mean), as the rankings do. A mean over different exams depends on which
exams a school's students take: it is the press convention, not a
measure of the school.

The JNE codes the Azores as district 19 with its own concelho codes;
CONCELHOS maps them to INE geocodes.
"""

import csv
import io
import re
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path

PAGE = "https://infoescolas.pt/bds.asp"
BASE = "https://infoescolas.pt/"
UA = "acores.net open data (github.com/fmesqg/a-ores.net-site)"
LINK = re.compile(r"""docs/(?:\d{4}/)?(enes|eneb)(\d{4})[^"'/]*\.zip""")
MIN_PROVAS = 50
# the newest year must be at most this old (2025 came out in March 2026)
MAX_ATRASO = 2
# fewer Azorean schools than this in a year means a broken file
MIN_ESCOLAS = {"secundario": 15, "basico": 25}
PROVAS_BASICO = {"91": "Português", "92": "Matemática"}
# files that cannot be counted the same way: 2023's secondary file has
# Interno = "N" on every row of the country, so internal students cannot
# be told apart
SALTAR = {"enes2023_ComunicacaoSocial_24.zip"}

# JNE concelho code (district 19) -> (INE geocode, name)
CONCELHOS = {
    "01": ("2004301", "Angra do Heroísmo"),
    "02": ("2004501", "Calheta"),
    "03": ("2004401", "Santa Cruz da Graciosa"),
    "04": ("2004502", "Velas"),
    "05": ("2004302", "Praia da Vitória"),
    "11": ("2004901", "Corvo"),
    "12": ("2004701", "Horta"),
    "13": ("2004801", "Lajes das Flores"),
    "14": ("2004601", "Lajes do Pico"),
    "15": ("2004602", "Madalena"),
    "16": ("2004802", "Santa Cruz das Flores"),
    "17": ("2004603", "São Roque do Pico"),
    "21": ("2004201", "Lagoa"),
    "22": ("2004202", "Nordeste"),
    "23": ("2004203", "Ponta Delgada"),
    "24": ("2004204", "Povoação"),
    "25": ("2004205", "Ribeira Grande"),
    "26": ("2004206", "Vila Franca do Campo"),
    "27": ("2004101", "Vila do Porto"),
}
REGIOES = {
    "AZ": "Açores",
    "MD": "Madeira",
    "CO": "Continente",
    "PT": "Portugal",
}
NIVEIS = {"enes": "secundario", "eneb": "basico"}

COLS = [
    "ano",
    "nivel",
    "tipo",
    "codigo",
    "nome",
    "geocod",
    "concelho",
    "publico",
    "exame",
    "exame_nome",
    "provas",
    "media",
    "media_interna",
    "positivas",
    "posicao",
    "n_escolas",
    "ficheiro",
]


def links(html: str) -> dict[tuple[int, str], str]:
    """{(year, level): path} of the database zips on the page."""
    out = {}
    for m in LINK.finditer(html):
        out[(int(m[2]), NIVEIS[m[1]])] = m[0]
    return out


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def mdb(path: Path, table: str) -> list[dict]:
    out = subprocess.run(
        ["mdb-export", str(path), table],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return list(csv.DictReader(io.StringIO(out)))


def mdb_tables(path: Path) -> list[str]:
    out = subprocess.run(
        ["mdb-tables", "-1", str(path)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [t for t in out.splitlines() if t]


def regiao(distrito: str) -> str | None:
    if distrito == "19":
        return "AZ"
    if distrito == "22":
        return "MD"
    if distrito in ("", "99"):  # abroad
        return None
    return "CO"


def provas(nivel: str, tables: dict[str, list[dict]]):
    """Yield (school, exam, exam name, grade, internal grade, positive)
    for the exams counted (see the module docstring)."""
    hom = next(v for k, v in tables.items() if k.startswith("tblHomologa"))
    if nivel == "secundario":
        nomes = {r["Exame"]: r["Descr"] for r in tables["tblExames"]}
        for r in hom:
            if (r["Fase"], r["Interno"], r["ParaAprov"]) != ("1", "S", "S"):
                continue
            if not r["Class_Exam"]:
                continue
            nota = int(r["Class_Exam"])
            cif = int(r["CIF"]) if r["CIF"] else None
            e = r["Exame"]
            yield r["Escola"], e, nomes.get(e, e), nota, cif, nota >= 95
    else:
        for r in hom:
            if (r["Fase"], r["TipoAluno"]) != ("1", "I"):
                continue
            e = r["Prova"]
            if e not in PROVAS_BASICO or not r["ExamPontos"]:
                continue
            nivel_int = int(r["FreqNivel"]) if r["FreqNivel"] else None
            yield (
                r["EscolaOrigem"],
                e,
                PROVAS_BASICO[e],
                int(r["ExamPontos"]),
                nivel_int,
                int(r["ExamNivel"] or 0) >= 3,
            )


class Soma:
    __slots__ = ("n", "s", "ni", "si", "pos")

    def __init__(self):
        self.n = self.s = self.ni = self.si = self.pos = 0

    def add(self, nota, interna, positiva):
        self.n += 1
        self.s += nota
        self.pos += positiva
        if interna is not None:
            self.ni += 1
            self.si += interna

    def media(self):
        return self.s / self.n


def resumo(
    ano: int, nivel: str, tables: dict[str, list[dict]], ficheiro: str
) -> list[list]:
    escolas = {r["Escola"]: r for r in tables["tblEscolas"]}
    soma: dict[tuple[str, str], Soma] = defaultdict(Soma)
    nomes: dict[str, str] = {}
    for esc, e, nome, nota, interna, pos in provas(nivel, tables):
        nomes[e] = nome
        reg = regiao(escolas.get(esc, {}).get("Distrito", ""))
        keys = [esc] + ([reg, "PT"] if reg else [])
        for k in keys:
            for ex in (e, "todos"):
                soma[(k, ex)].add(nota, interna, pos)
    nomes["todos"] = (
        "Todos os exames"
        if nivel == "secundario"
        else ("Português e Matemática")
    )
    # national place of each school on all exams pooled
    medias = sorted(
        (
            (s.media(), k)
            for (k, ex), s in soma.items()
            if ex == "todos" and k in escolas and s.n >= MIN_PROVAS
        ),
        reverse=True,
    )
    vals = [m for m, _ in medias]
    posicao = {k: 1 + sum(v > m for v in vals) for m, k in medias}
    out = []
    for (k, ex), s in sorted(soma.items()):
        if k in REGIOES:
            tipo, nome, geo, conc, pub = "regiao", REGIOES[k], "", "", ""
            if k == "AZ":
                geo = "20"
        else:
            r = escolas.get(k, {})
            if r.get("Distrito") != "19":
                continue
            tipo, nome = "escola", r["Descr"].strip()
            geo, conc = CONCELHOS.get(r["Concelho"], ("", r["Concelho"]))
            pub = r.get("PubPriv", "")
        rank = posicao.get(k) if ex == "todos" else None
        out.append(
            [
                ano,
                nivel,
                tipo,
                k,
                nome,
                geo,
                conc,
                pub,
                ex,
                nomes[ex],
                s.n,
                round(s.media(), 1),
                round(s.si / s.ni, 2) if s.ni else "",
                round(100 * s.pos / s.n, 1),
                rank or "",
                len(medias) if rank else "",
                ficheiro,
            ]
        )
    return out


def read_zip(blob: bytes, tmp: Path) -> dict[str, list[dict]]:
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        name = next(n for n in z.namelist() if n.lower().endswith(".mdb"))
        path = tmp / "base.mdb"
        path.write_bytes(z.read(name))
    return {t: mdb(path, t) for t in mdb_tables(path)}


def read_csv(path: Path) -> list[list]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return [[r[c] for c in COLS] for r in csv.DictReader(f)]


def main(data_dir: Path, tudo: bool = False) -> int:
    path = data_dir / "exames.csv"
    old = read_csv(path)
    lidos = {(int(r[0]), r[1]): r[-1] for r in old}
    found = links(get(PAGE).decode("latin-1"))
    if not found:
        print("::error::no database links on", PAGE)
        return 1
    novos: dict[tuple[int, str], list[list]] = {}
    erro = False
    with tempfile.TemporaryDirectory() as tmp:
        for (ano, nivel), href in sorted(found.items()):
            ficheiro = href.rsplit("/", 1)[-1]
            if not tudo and lidos.get((ano, nivel)) == ficheiro:
                continue
            if ficheiro in SALTAR:
                print("skipped (SALTAR):", href)
                continue
            print("reading", href)
            try:
                tables = read_zip(get(BASE + href), Path(tmp))
                rows = resumo(ano, nivel, tables, ficheiro)
            except Exception as e:  # noqa: BLE001 - report, keep the rest
                print(f"::error::{href}: {e}")
                erro = True
                continue
            n = len({r[3] for r in rows if r[2] == "escola"})
            if n < MIN_ESCOLAS[nivel]:
                print(f"::error::{href}: only {n} Azorean schools")
                erro = True
                continue
            print(ano, nivel, n, "Azorean schools", len(rows), "rows")
            novos[(ano, nivel)] = rows
    rows = [r for r in old if (int(r[0]), r[1]) not in novos]
    rows += [r for v in novos.values() for r in v]
    rows.sort(key=lambda r: (-int(r[0]), r[1] != "secundario", r[2], r[3]))
    if novos:
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(COLS)
            w.writerows(rows)
        print(path, len(rows), "rows")
    ultimo = max((int(r[0]) for r in rows), default=0)
    if ultimo < date.today().year - MAX_ATRASO:
        print(f"::error::newest exam year is {ultimo}")
        erro = True
    return 1 if erro else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.exit(
        main(Path(args[0] if args else "data"), tudo="--tudo" in sys.argv)
    )
