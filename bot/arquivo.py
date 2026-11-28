"""Fold the daily ALRA and JORAA pages into the archive and drop old pages.

Usage: python3 bot/arquivo.py [repo_dir] [--manter DIAS]   (stdlib only)

The daily run writes one page per source per day under docs/. This script,
run right after it:

1. rebuilds data/alra.csv.gz and data/joraa.csv.gz from the archive plus
   every page still in docs/_alra_updates/ and docs/_joraa_updates/
   (parlamento.build_alra / build_joraa), so the archive is the dataset;
2. deletes the pages of those two collections and of docs/_base_updates/
   older than ``MANTER`` days (90), but only pages whose every link is in
   the new archive (BASE pages: the IMPIC files in data/base_impic/ are the
   archive, so they are only aged out).

Old day URLs (/joraa_updates/2025-03-14/) are sent by docs/404.html to the
search page filtered by that day. Exits 1, deleting nothing, if a page has
a link missing from the archive.
"""

import datetime as dt
import sys
from pathlib import Path

try:
    from .dados.comum import days, parse_day
    from .dados.parlamento import (
        ALRA_COLS,
        JORAA_COLS,
        build_alra,
        build_joraa,
        read_archive,
        write_archive,
    )
except ImportError:  # run as python3 bot/arquivo.py
    from dados.comum import days, parse_day
    from dados.parlamento import (
        ALRA_COLS,
        JORAA_COLS,
        build_alra,
        build_joraa,
        read_archive,
        write_archive,
    )

MANTER = 90  # days of pages kept in docs/
FONTES = {
    # collection: (archive, columns, builder)
    "_alra_updates": ("alra.csv.gz", ALRA_COLS, build_alra),
    "_joraa_updates": ("joraa.csv.gz", JORAA_COLS, build_joraa),
}


def main(repo: Path, manter: int = MANTER, hoje: dt.date | None = None) -> int:
    docs, data = repo / "docs", repo / "data"
    hoje = hoje or dt.datetime.now(dt.UTC).date()
    limite = (hoje - dt.timedelta(days=manter)).isoformat()
    velhas: list[Path] = []
    for coll, (nome, cols, build) in FONTES.items():
        path = data / nome
        rows = build(docs, read_archive(path, cols))
        write_archive(path, cols, rows)
        urls = {r[cols.index("url")] for r in rows}
        for day, page in days(docs, coll):
            if day >= limite:
                continue
            falta = [u for _, _, u, _ in parse_day(page) if u not in urls]
            if falta:
                print(f"::error::{page}: {len(falta)} links not in {nome}")
                return 1
            velhas.append(page)
        print(f"{nome}: {len(rows)} rows")
    velhas += [p for d, p in days(docs, "_base_updates") if d < limite]
    for p in velhas:
        p.unlink()
    print(f"{len(velhas)} pages older than {limite} removed")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    dias = MANTER
    if "--manter" in args:
        i = args.index("--manter")
        dias = int(args[i + 1])
        del args[i : i + 2]
    sys.exit(main(Path(args[0] if args else "."), dias))
