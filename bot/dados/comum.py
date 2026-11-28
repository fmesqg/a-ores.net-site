"""Helpers shared by the bot/dados modules: reading the daily update pages, writing CSVs, numbers and words."""

import csv
import re
import unicodedata
from pathlib import Path

ITEM = re.compile(r"^\* \[(?P<title>.*)\]\((?P<url>[^)\s]+)\)\s*$")
SUB = re.compile(r"^\s{2,}\* (?P<text>.+)$")
LINK = re.compile(r"\[(?P<label>[^\]]*)\]\((?P<url>[^)\s]+)\)")
DMY = re.compile(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})")
STATE = re.compile(r"Alteração do estado:\s*(?P<old>.*?)\s*→\s*(?P<new>.+)")


def iso(text: str) -> str:
    """First dd/mm/yyyy or dd-mm-yyyy in text, as yyyy-mm-dd ('' if none)."""
    m = DMY.search(text or "")
    return f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}" if m else ""


def euros(text: str, decimal: str) -> float | None:
    """Parse '120.963,33 €' (decimal=',') or '993,164.40 €' (decimal='.')."""
    thousands = "." if decimal == "," else ","
    num = re.sub(r"[^\d" + re.escape(decimal) + "]", "", text)
    num = num.replace(thousands, "").replace(decimal, ".")
    try:
        return round(float(num), 2)
    except ValueError:
        return None


def parse_day(path: Path):
    """Yield (section, title, url, [sub-bullet lines]) for one daily page."""
    section, item = "", None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            if item:
                yield item
                item = None
            section = line.lstrip("#").strip()
        elif m := ITEM.match(line):
            if item:
                yield item
            item = (section, m["title"].strip(), m["url"], [])
        elif item and (m := SUB.match(line)):
            item[3].append(m["text"].strip())
    if item:
        yield item


def days(docs: Path, collection: str):
    for path in sorted((docs / collection).glob("????-??-??.md")):
        yield path.stem, path


def fields(subs: list[str]) -> dict[str, str]:
    """'Chave: valor' sub-bullets as a dict (plain text, links removed)."""
    out = {}
    for s in subs:
        plain = LINK.sub(r"\g<label>", s)
        if ":" in plain:
            key, val = plain.split(":", 1)
            out.setdefault(key.strip().lower(), val.strip())
    return out


def links(subs: list[str]) -> dict[str, str]:
    out = {}
    for s in subs:
        for m in LINK.finditer(s):
            out.setdefault(m["label"].strip().lower(), m["url"])
    return out


def write(out: Path, name: str, cols: list[str], rows: list[list]) -> dict:
    with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)
    return {"linhas": len(rows), "colunas": cols}


MESES = [
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
]


def _num(v: str) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _mes(data: str) -> str:
    return f"{MESES[int(data[5:7]) - 1]} de {data[:4]}"


def _dicts(table: tuple[list, list]) -> list[dict]:
    cols, rows = table
    return [dict(zip(cols, r, strict=False)) for r in rows]


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _words(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def pt_num(x: float) -> str:
    """245328 -> '245 328', 39.38 -> '39,4', 5.94 -> '5,94' (pt-PT, the
    thousands separator is a no-break space)."""
    dec = 0 if abs(x) >= 100 else 1 if abs(x) >= 10 else 2
    s = f"{x:,.{dec}f}".replace(",", "\u00a0").replace(".", ",")
    if "," in s:
        s = s.rstrip("0").rstrip(",")
    return s


def _texts(node, total: float | None = None):
    """Add 'k_t' (formatted) next to every number 'k', and 'pct' (share of
    total) to items of the lists, so the Liquid page needs no arithmetic."""
    if isinstance(node, dict):
        for k, v in list(node.items()):
            if isinstance(v, int | float) and not isinstance(v, bool):
                node[k + "_t"] = pt_num(v)
            elif isinstance(v, list):
                tot = {
                    "ilhas": node.get("acores"),
                    "receitas": node.get("receita"),
                    "despesas": node.get("despesa"),
                    "funcoes": node.get("funcoes_total"),
                }.get(k)
                for item in v:
                    if tot and isinstance(item, dict) and "valor" in item:
                        item["pct"] = round(100 * item["valor"] / tot)
                    _texts(item)
            else:
                _texts(v)
    return node


def _m(x: float) -> float:
    return round(x / 1e6, 1)


def _f(x: str) -> float:
    try:
        return float(x) if x else 0.0
    except ValueError:
        return 0.0
