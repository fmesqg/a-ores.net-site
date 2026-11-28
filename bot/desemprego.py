"""Registered unemployment in the Azores by island and concelho, month by
month, from the regional employment directorate's monthly summaries.

Usage: python3 bot/desemprego.py data [--tudo]   (needs pypdf)

The Direção Regional de Qualificação Profissional e Emprego publishes a
three-page PDF a month, "Resumo - Desemprego registado nos Açores", on
emprego.azores.gov.pt (a WordPress site) and, until April 2024, on
portal.azores.gov.pt. The Azores have their own public employment services,
so the IEFP's statistics by concelho stop at the mainland and this is the
only source by concelho.

Both sites' pages and the WordPress API sit behind the Cloudflare challenge
(403, checked 28/11/2026); the uploaded files do not. So the files cannot
be listed: CONHECIDOS holds the addresses found through search engines,
each read once, and each run then asks for the months after the newest one
read by trying the usual names (`candidatos`: first
`02_DESEMPREGO_REGISTADO_<MÊS>_<ano>.pdf` in the next month's upload
folder). A month not found that way makes main() fail once the newest
month is older than MAX_IDADE days, so the weekly workflow emails: find the
file's address (a search engine, "DESEMPREGO_REGISTADO <mês> <ano>", or a
browser) and add it to CONHECIDOS. The month is read from the PDF's own
heading, not from its name.

Tables read (people at the end of the month, men / women / total):
  desemprego   registered unemployed, by island and by concelho (the
               region is the TOTAL row)
  medidas      people in employability measures: inserção
               socioprofissional, estágio, formação
  colocacoes   placements during the month, by island
plus `ofertas` (job offers received during the month, from the text).
Every table is checked: men + women = total, the islands and the concelhos
add up to the region, all 19 concelhos are there.

data/desemprego.csv is committed and accumulates: a file already read (same
name) is not downloaded again unless --tudo. Every request goes through
bot/gov.py (gov.UA, gov.wait()) like any request to *.azores.gov.pt; these
hosts are not in gov.LIGHT, so they share the strict clock, and a run makes
at most MAX_PEDIDOS requests.
"""

import csv
import io
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

try:
    from bot import gov
except ImportError:  # run as a script: python3 bot/desemprego.py
    import gov

UPLOADS = "https://emprego.azores.gov.pt/wp-content/uploads/"
PORTAL = "https://portal.azores.gov.pt/documents/36557/"
# the newest month must be at most this many days old (a month's summary
# comes out four to eight weeks after it ends)
MAX_IDADE = 120
MAX_PEDIDOS = 40

# month -> address, as found by search engines (November 2026)
CONHECIDOS = {
    "2022-08": PORTAL + "8391641/05_DESEMPREGO_REGISTADO_AGOSTO_2022.pdf",
    "2022-09": PORTAL + "8670662/05_DESEMPREGO_REGISTADO_SETEMBRO_2022.pdf",
    "2022-10": PORTAL + "8977114/05_DESEMPREGO_REGISTADO_OUTUBRO_2022.pdf",
    "2023-04": PORTAL + "10876411/05_DESEMPREGO_REGISTADO_ABRIL_2023.pdf",
    "2023-05": PORTAL + "11245599/05_DESEMPREGO_REGISTADO_MAIO_2023.pdf",
    "2023-06": PORTAL + "11575678/03_DESEMPREGO_REGISTADO_JUNHO_2023.pdf",
    "2023-07": PORTAL + "11877327/03_DESEMPREGO_REGISTADO_JULHO+2023.pdf",
    "2023-08": PORTAL + "12277907/05_DESEMPREGO_REGISTADO_AGOSTO_2023.pdf",
    "2023-09": PORTAL + "12587652/03_DESEMPREGO_REGISTADO_SETEMBRO_2023.pdf",
    "2023-10": PORTAL + "12587952/05_DESEMPREGO_REGISTADO_OUTUBRO_2023.pdf",
    "2023-11": PORTAL + "13345613/05_DESEMPREGO_REGISTADO_NOVEMBRO_2023.pdf",
    "2023-12": PORTAL + "13651474/05_DESEMPREGO_REGISTADO_DEZEMBRO_2023.pdf",
    "2024-01": PORTAL + "13885502/03_DESEMPREGO+REGISTADO_JANEIRO_2024.pdf",
    "2024-02": PORTAL + "14376407/02_DESEMPREGO_REGISTADO_FEVEREIRO_2024.pdf",
    "2024-03": UPLOADS + "2024/05/05_DESEMPREGO_REGISTADO_MARCO_2024.pdf",
    "2024-04": PORTAL + "15038451/02_DESEMPREGO_REGISTADO_ABRIL_2024.pdf",
    "2024-06": UPLOADS + "2024/07/02_DESEMPREGO_REGISTADO_JUNHO_2024.pdf",
    "2024-08": UPLOADS + "2024/09/02_DESEMPREGO_REGISTADO_AGOSTO_2024.pdf",
    "2024-09": UPLOADS + "2024/10/02_DESEMPREGO_REGISTADO_SETEMBRO_2024.pdf",
    "2024-11": UPLOADS + "2024/12/02_DESEMPREGO_REGISTADO_NOVEMBRO_2024.pdf",
    "2024-12": UPLOADS + "2025/02/02_DESEMPREGO_REGISTADO_dezembro_2024.pdf",
    "2025-01": UPLOADS + "2025/02/03_DESEMPREGO_REGISTADO_JANEIRO_2025.pdf",
    "2025-02": UPLOADS + "2025/03/02_DESEMPREGO_REGISTADO_FEVEREIRO_2025.pdf",
    "2025-03": UPLOADS + "2025/04/03_DESEMPREGO_REGISTADO_MARCO_2025.pdf",
    "2025-04": UPLOADS + "2025/05/03_DESEMPREGO_REGISTADO_ABRIL_2025.pdf",
    "2025-05": UPLOADS + "2025/07/02_DESEMPREGO_REGISTADO_MAIO_2025.pdf",
    "2025-06": UPLOADS + "2025/07/02_DESEMPREGO_REGISTADO_JUNHO_2025.pdf",
    "2025-07": UPLOADS + "2025/09/02_DESEMPREGO_REGISTADO_JULHO_2025.pdf",
    "2025-08": UPLOADS + "2025/09/02_DESEMPREGO_REGISTADO_AGOSTO_2025.pdf",
    "2025-10": UPLOADS + "2025/11/02_DESEMPREGO_REGISTADO_OUTUBRO_2025.pdf",
    "2026-01": UPLOADS + "2026/02/02_DESEMPREGO_REGISTADO_JANEIRO_2026.pdf",
    "2026-02": UPLOADS + "2026/03/02_DESEMPREGO_REGISTADO_FEVEREIRO_2026.pdf",
    "2026-03": UPLOADS + "2026/04/02_DESEMPREGO_REGISTADO_MARCO_2026.pdf",
    "2026-04": UPLOADS + "2026/05/02_DESEMPREGO_REGISTADO_ABRIL_2026.pdf",
    "2026-05": UPLOADS + "2026/06/02_DESEMPREGO_REGISTADO_05_2026.pdf",
}

MESES = [
    "JANEIRO",
    "FEVEREIRO",
    "MARCO",
    "ABRIL",
    "MAIO",
    "JUNHO",
    "JULHO",
    "AGOSTO",
    "SETEMBRO",
    "OUTUBRO",
    "NOVEMBRO",
    "DEZEMBRO",
]
ILHAS = {
    "SANTA MARIA": "2001",
    "SAO MIGUEL": "2002",
    "TERCEIRA": "2003",
    "GRACIOSA": "2004",
    "SAO JORGE": "2005",
    "PICO": "2006",
    "FAIAL": "2007",
    "FLORES": "2008",
    "CORVO": "2009",
}
NOMES_ILHAS = {
    "2001": "Santa Maria",
    "2002": "São Miguel",
    "2003": "Terceira",
    "2004": "Graciosa",
    "2005": "São Jorge",
    "2006": "Pico",
    "2007": "Faial",
    "2008": "Flores",
    "2009": "Corvo",
}
# name in the PDF (folded) -> (INE geocode, name)
CONCELHOS = {
    "VILA DO PORTO": ("2004101", "Vila do Porto"),
    "LAGOA": ("2004201", "Lagoa"),
    "NORDESTE": ("2004202", "Nordeste"),
    "PONTA DELGADA": ("2004203", "Ponta Delgada"),
    "POVOACAO": ("2004204", "Povoação"),
    "RIBEIRA GRANDE": ("2004205", "Ribeira Grande"),
    "VILA FRANCA DO CAMPO": ("2004206", "Vila Franca do Campo"),
    "ANGRA DO HEROISMO": ("2004301", "Angra do Heroísmo"),
    "PRAIA DA VITORIA": ("2004302", "Praia da Vitória"),
    "SANTA CRUZ DA GRACIOSA": ("2004401", "Santa Cruz da Graciosa"),
    "CALHETA": ("2004501", "Calheta"),
    "VELAS": ("2004502", "Velas"),
    "LAJES DO PICO": ("2004601", "Lajes do Pico"),
    "MADALENA": ("2004602", "Madalena"),
    "SAO ROQUE DO PICO": ("2004603", "São Roque do Pico"),
    "HORTA": ("2004701", "Horta"),
    "LAJES DAS FLORES": ("2004801", "Lajes das Flores"),
    "SANTA CRUZ DAS FLORES": ("2004802", "Santa Cruz das Flores"),
    "VILA DO CORVO": ("2004901", "Corvo"),
    "CORVO": ("2004901", "Corvo"),
}
MEDIDAS = {
    "INSERCAO SOCIOPROFISSIONAL": "Inserção socioprofissional",
    "ESTAGIO": "Estágio",
    "ESTAGIOS": "Estágio",
    "FORMACAO": "Formação",
}

COLS = [
    "periodo",
    "tabela",
    "nivel",
    "geocod",
    "nome",
    "homens",
    "mulheres",
    "total",
    "ficheiro",
]

# a table row: a name in capitals, then men, women, total (and a share).
# Thousands are written with a dot ("1.799") or, until 2022, a space
# ("1 799"), so the numbers are read by `numeros`.
ROW = re.compile(r"^([A-Z][A-Z .'-]*?[A-Z])\s+(\d.*|-.*)$")
TOKEN = re.compile(r"^(\d{1,3}(?:\.\d{3})*|-)$")


def numeros(rest: str) -> tuple[int, int, int] | None:
    """Men, women and total from what follows a row's name. With thousands
    written with a space the split is ambiguous ("1 799 2 222 4 021"): the
    one where men + women = total wins."""
    toks = []
    for t in rest.split():
        if not TOKEN.match(t):
            break
        toks.append(t)
    if len(toks) < 3:
        return None
    if len(toks) == 3:
        return tuple(num(t) for t in toks)

    def grupos(ts):
        """Every way to read ts as consecutive numbers."""
        if not ts:
            yield []
            return
        if ts[0] == "-":
            for g in grupos(ts[1:]):
                yield [0] + g
            return
        for k in range(1, len(ts) + 1):
            if k > 1 and not re.fullmatch(r"\d{3}", ts[k - 1]):
                break
            v = int("".join(ts[:k]).replace(".", ""))
            for g in grupos(ts[k:]):
                yield [v] + g

    for g in grupos(toks):
        if len(g) >= 3 and g[0] + g[1] == g[2]:
            return g[0], g[1], g[2]
    return tuple(num(t) for t in toks[:3])


class Erro(Exception):
    """A summary that does not read as expected."""


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(s.upper().split())


def num(s: str) -> int:
    return 0 if s == "-" else int(s.replace(".", ""))


def mais(per: str, n: int) -> str:
    """'2026-03' plus n months."""
    y, m = map(int, per.split("-"))
    k = y * 12 + m - 1 + n
    return f"{k // 12}-{k % 12 + 1:02d}"


# --- reading --------------------------------------------------------------


class Blocked(Exception):
    """The site answered with a challenge or something other than a PDF."""


def candidatos(per: str) -> list[str]:
    """Likely addresses of a month's summary, most likely first: the names
    used since 2024 (prefix 02, 03 or 05; the month's name without accents,
    once its number), uploaded the next month or the one after."""
    y, m = per.split("-")
    nome = MESES[int(m) - 1]
    out = []
    for dobra, formas in ((1, (nome, m)), (2, (nome,))):
        pasta = mais(per, dobra).replace("-", "/")
        for pref in ("02", "03", "05"):
            for f in formas:
                out.append(
                    f"{UPLOADS}{pasta}/{pref}_DESEMPREGO_REGISTADO_{f}_{y}.pdf"
                )
    return out


def get(url: str) -> bytes | None:
    """The file, or None on a 404. Anything else that is not a PDF (a
    Cloudflare challenge above all) raises Blocked: stop rather than keep
    asking."""
    req = urllib.request.Request(url, headers=gov.HEADERS)
    gov.wait(urllib.parse.urlsplit(url).hostname)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        why = e.headers.get("cf-mitigated") or e.reason
        raise Blocked(f"{e.code} ({why}) em {url}") from e
    if not body.startswith(b"%PDF"):
        raise Blocked(f"a resposta não é um PDF em {url}")
    return body


def pdf_text(data: bytes) -> str:
    from pypdf import PdfReader  # only needed to read PDFs

    pages = PdfReader(io.BytesIO(data)).pages
    return "\n".join(p.extract_text() or "" for p in pages)


# --- parsing --------------------------------------------------------------


def periodo(text: str) -> str:
    """'2026-03' from the heading ('MARÇO DE 2026')."""
    m = re.search(rf"\b({'|'.join(MESES)})\s+DE\s+(\d{{4}})\b", fold(text))
    if not m:
        raise Erro("mês do resumo não encontrado")
    return f"{m[2]}-{MESES.index(m[1]) + 1:02d}"


def blocos(text: str) -> list[tuple[str, list[tuple]]]:
    """The tables in reading order: (header word, [(name, h, m, t)]). A
    table starts at a line that is only its header word (ILHAS,
    CONCELHOS, MEDIDAS PARA A EMPREGABILIDADE) and runs to its TOTAL row;
    a table broken over two pages continues after the repeated header."""
    out: list[tuple[str, list[tuple]]] = []
    tabela, linhas, fechada = "", [], True
    for line in text.splitlines():
        # "-SANTA MARIA 1 3 4" (February 2025), and the header alone or
        # with its column titles ("ILHAS DESEMPREGO REGISTADO PESO ...")
        f = fold(line).lstrip("- ")
        cab = f.split(" ")[0]
        if (
            cab in ("ILHAS", "CONCELHOS")
            and not re.search(r"\d", f)
            or f.startswith("MEDIDAS PARA A")
        ):
            f = cab if cab != "MEDIDAS" else f
            if f.split()[0] == tabela and not fechada:
                continue  # the same table, repeated after a page break
            tabela, linhas, fechada = f.split()[0], [], False
            out.append((tabela, linhas))
            continue
        if fechada or not (m := ROW.match(f)):
            continue
        if not (ns := numeros(m[2])):
            continue
        nome = m[1].strip()
        linhas.append((nome, *ns))
        fechada = nome == "TOTAL"
    return out


def ofertas(text: str) -> int | None:
    m = re.search(r"entrada de\s+([\d.]+)\s+ofertas", " ".join(text.split()))
    return num(m[1]) if m else None


def parse(text: str, ficheiro: str) -> list[list]:
    per = periodo(text)
    bl = blocos(text)
    ilhas = [b for b in bl if b[0] == "ILHAS"]
    conc = [b for b in bl if b[0] == "CONCELHOS"]
    med = [b for b in bl if b[0] == "MEDIDAS"]
    if not ilhas or len(conc) != 1:
        raise Erro(f"{per}: tabelas de ilhas/concelhos não encontradas")
    out = []

    def add(tabela, nivel, geo, nome, h, m, t):
        if h + m != t:
            raise Erro(f"{per} {tabela} {nome}: {h} + {m} != {t}")
        out.append([per, tabela, nivel, geo, nome, h, m, t, ficheiro])

    def ilhas_de(tabela, rows):
        soma = [0, 0, 0]
        for nome, h, m, t in rows:
            if nome == "TOTAL":
                if [h, m, t] != soma:
                    raise Erro(f"{per} {tabela}: soma das ilhas != total")
                add(tabela, "regiao", "20", "Açores", h, m, t)
            elif nome in ILHAS:
                geo = ILHAS[nome]
                add(tabela, "ilha", geo, NOMES_ILHAS[geo], h, m, t)
                soma = [soma[0] + h, soma[1] + m, soma[2] + t]
            else:
                raise Erro(f"{per} {tabela}: ilha desconhecida {nome!r}")

    ilhas_de("desemprego", ilhas[0][1])
    total = next((r[5:8] for r in out if r[2] == "regiao"), None)
    if total is None:
        raise Erro(f"{per}: sem total da região")
    vistos = set()
    soma = [0, 0, 0]
    for nome, h, m, t in conc[0][1]:
        if nome == "TOTAL":
            if [h, m, t] != soma or soma != total:
                raise Erro(f"{per}: soma dos concelhos != total")
            continue
        if nome not in CONCELHOS:
            raise Erro(f"{per}: concelho desconhecido {nome!r}")
        geo, n = CONCELHOS[nome]
        vistos.add(geo)
        add("desemprego", "concelho", geo, n, h, m, t)
        soma = [soma[0] + h, soma[1] + m, soma[2] + t]
    if len(vistos) != 19:
        raise Erro(f"{per}: {len(vistos)} concelhos em vez de 19")
    # islands from their concelhos: the PDF's island table sometimes
    # disagrees with its own concelhos (March 2026: Graciosa 153 against
    # Santa Cruz da Graciosa's 46) while both add up to the region
    por_ilha: dict[str, list[int]] = {}
    for r in out:
        if r[2] == "concelho":
            s = por_ilha.setdefault("200" + r[3][4], [0, 0, 0])
            s[0], s[1], s[2] = s[0] + r[5], s[1] + r[6], s[2] + r[7]
    for r in out:
        if r[1] == "desemprego" and r[2] == "ilha":
            soma_c = por_ilha[r[3]]
            if r[5:8] != soma_c:
                print(f"::warning::{per} {r[4]}: quadro das ilhas "
                      f"{r[7]}, concelhos {soma_c[2]}")  # fmt: skip
                r[5:8] = soma_c
    for nome, h, m, t in med[0][1] if med else []:
        if nome in MEDIDAS:
            add("medidas", "medida", "20", MEDIDAS[nome], h, m, t)
    if len(ilhas) > 1:
        # placements are secondary: a broken table (April 2026: "SANTA
        # MARIA - 2 - -", islands that do not add up) loses only them
        n = len(out)
        try:
            ilhas_de("colocacoes", ilhas[1][1])
        except Erro as e:
            print(f"::warning::{e}; colocações deixadas de fora")
            del out[n:]
    o = ofertas(text)
    if o is not None:
        out.append([per, "ofertas", "regiao", "20", "Açores", "", "", o,
                    ficheiro])  # fmt: skip
    return out


# --- main -----------------------------------------------------------------


def read_csv(path: Path) -> list[list]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return [[r[c] for c in COLS] for r in csv.DictReader(f)]


def main(data_dir: Path, tudo: bool = False) -> int:
    path = data_dir / "desemprego.csv"
    old = read_csv(path)
    lidos = {r[-1] for r in old}
    erro = False
    novos: dict[str, list[list]] = {}
    pedidos = 0

    def ler(url: str) -> bool | None:
        """Read one address into novos: True if read, None on a 404, False
        if it could not be parsed (reported)."""
        nonlocal pedidos, erro
        pedidos += 1
        blob = get(url)
        if blob is None:
            return None
        ficheiro = url.rsplit("/", 1)[-1]
        try:
            rows = parse(pdf_text(blob), ficheiro)
        except Exception as e:  # noqa: BLE001 - report, keep the rest
            print(f"::error::{ficheiro}: {e}")
            erro = True
            return False
        print("read", rows[0][0], url)
        novos[rows[0][0]] = rows
        return True

    try:
        for per, url in sorted(CONHECIDOS.items()):
            if pedidos >= MAX_PEDIDOS:
                print(f"stopped after {pedidos} requests")
                break
            if not tudo and url.rsplit("/", 1)[-1] in lidos:
                continue
            if ler(url) is None:
                print(f"::error::{per}: 404 em {url}")
                erro = True
        # the months after the newest one known, up to last month
        per = mais(max({r[0] for r in old} | set(novos) | set(CONHECIDOS)), 1)
        fim = mais(date.today().strftime("%Y-%m"), -1)
        while per <= fim and pedidos < MAX_PEDIDOS:
            if not any(ler(u) is not None for u in candidatos(per)):
                print(f"{per}: not found")
                break
            per = mais(per, 1)
    except Blocked as e:
        print(f"::error::{e}")
        erro = True
    rows = [r for r in old if r[0] not in novos]
    rows += [r for v in novos.values() for r in v]
    ordem = {"desemprego": 0, "medidas": 1, "colocacoes": 2, "ofertas": 3}
    niveis = {"regiao": 0, "ilha": 1, "concelho": 2, "medida": 3}
    rows.sort(key=lambda r: (r[0], ordem[r[1]], niveis[r[2]], r[3], r[4]))
    if novos:
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(COLS)
            w.writerows(rows)
        print(path, len(rows), "rows,", len(novos), "months read")
    ultimo = max((r[0] for r in rows), default="")
    if not ultimo:
        print("::error::no month read")
        return 1
    y, m = map(int, ultimo.split("-"))
    if (date.today() - date(y, m, 1)).days > MAX_IDADE:
        print(f"::error::newest month is {ultimo}: add the address of the "
              "next summary to CONHECIDOS")  # fmt: skip
        erro = True
    return 1 if erro else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.exit(
        main(Path(args[0] if args else "data"), tudo="--tudo" in sys.argv)
    )
