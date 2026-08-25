#!/usr/bin/env python3
"""One-off migration of docs/rss/ao.xml to the one-item-per-day format.

The old feed carried one item per article, body text included, and had
grown to 14 MB. It is also the only surviving copy of the archive
(``scrapers/output/`` is gitignored), so the article pages are rebuilt
from it before it is rewritten.

Page numbers were never stored in the old feed, so backfilled articles
carry an empty ``page``.

Usage:
    python3 -m scrapers.migrate_ao_feed [--days 30] [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from scrapers import ao_pages

FEED_PATH = Path(__file__).parent.parent / "docs" / "rss" / "ao.xml"

_DATE_IN_URL = re.compile(r"/edicao-impressa/(\d{4}-\d{2}-\d{2})")


def group_by_date(feed_path: Path) -> dict[str, dict[str, list[dict]]]:
    """Read the legacy feed into {date: {section: [article, ...]}}.

    Document order is preserved: the old writer prepended each day's
    articles in scrape order, which is the print edition's own section
    order.
    """
    channel = ET.parse(feed_path).getroot().find("channel")
    if channel is None:
        return {}

    days: dict[str, dict[str, list[dict]]] = {}
    for item in channel.findall("item"):
        guid = item.findtext("guid", "") or ""
        match = _DATE_IN_URL.search(guid)
        if not match:
            continue
        target_date = match.group(1)

        query = parse_qs(urlparse(guid).query)
        section = (
            item.findtext("category") or query.get("seccao", ["outro"])[0]
        )

        article = {
            "id": query.get("artigo", [""])[0],
            "title": item.findtext("title", "") or "",
            "section": section,
            "page": "",
            "excerpt": "",
            "author": item.findtext("author", "") or "",
            "url": guid,
            "body": item.findtext("description", "") or "",
        }
        days.setdefault(target_date, {}).setdefault(section, []).append(
            article
        )

    return days


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="How many of the most recent editions to backfill",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be written without touching any file",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not FEED_PATH.exists():
        print(f"No feed at {FEED_PATH}")
        return

    days = group_by_date(FEED_PATH)
    if not days:
        print(
            f"{FEED_PATH} holds no legacy per-article items — already "
            "migrated. Nothing to do."
        )
        return

    keep = sorted(days, reverse=True)[: args.days]
    print(f"Feed holds {len(days)} editions; backfilling {len(keep)}")

    items: list[ET.Element] = []
    total_articles = 0

    for target_date in keep:
        entries = ao_pages.build_entries(days[target_date], target_date)
        total_articles += len(entries)
        if args.dry_run:
            print(f"  {target_date}: {len(entries)} articles")
            continue
        ao_pages.write_article_pages(entries, target_date)
        ao_pages.write_day_page(entries, target_date)
        items.append(ao_pages.build_feed_item(entries, target_date))
        print(f"  {target_date}: {len(entries)} articles")

    if args.dry_run:
        print(f"Dry run: {total_articles} articles, nothing written")
        return

    ao_pages.write_feed(items, FEED_PATH)
    size_kb = FEED_PATH.stat().st_size / 1024
    print(
        f"Wrote {total_articles} article pages, {len(items)} day pages, "
        f"feed now {size_kb:.0f} KB"
    )


if __name__ == "__main__":
    main()
