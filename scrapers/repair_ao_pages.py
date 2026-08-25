#!/usr/bin/env python3
"""Fill in the page numbers the legacy feed never stored.

Editions backfilled by ``migrate_ao_feed`` carry no ``page``, so the
front-page teaser filter in :mod:`scrapers.ao_pages` cannot see them.
This re-fetches only the print edition's *section index* pages (roughly
nine per edition, not one request per article), maps ``artigo`` id to
page number, and regenerates the affected days.

Usage:
    python3 -m scrapers.repair_ao_pages [--days 30] [--dry-run]
"""

from __future__ import annotations

import argparse
import html
import json
import re
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

from scrapers import ao_pages
from scrapers.ao import (
    BASE_URL,
    discover_sections,
    load_config,
    login,
    scrape_article,
    scrape_section,
)

FEED_PATH = Path(__file__).parent.parent / "docs" / "rss" / "ao.xml"

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n\n(.*)\Z", re.DOTALL)
_FIELD = re.compile(r"^(\w+): (.*)$", re.MULTILINE)
_PARAGRAPH = re.compile(r"<p>(.*?)</p>", re.DOTALL)


def _parse_frontmatter(block: str) -> dict[str, str]:
    """Invert ao_pages._frontmatter: quoted values are JSON scalars."""
    meta = {}
    for key, raw in _FIELD.findall(block):
        raw = raw.strip()
        meta[key] = json.loads(raw) if raw.startswith('"') else raw
    return meta


def read_day(stamp: str) -> tuple[str, list[dict]]:
    """Rebuild {section: [article]} for one edition from its pages on disk.

    Returns the edition date and the articles in their existing order,
    which is the order the print edition listed them.
    """
    articles = []
    target_date = ""
    for path in sorted(ao_pages.PAGES_DIR.glob(f"{stamp}-*.md")):
        match = _FRONTMATTER.match(path.read_text(encoding="utf-8"))
        if not match:
            continue
        meta = _parse_frontmatter(match.group(1))
        target_date = meta.get("edition", "")
        source_url = meta.get("source_url", "")
        body = "\n\n".join(
            html.unescape(p.strip())
            for p in _PARAGRAPH.findall(match.group(2))
        )
        articles.append(
            {
                "id": parse_qs(urlparse(source_url).query).get("artigo", [""])[
                    0
                ],
                "title": meta.get("title", ""),
                "section": meta.get("section", ""),
                "page": meta.get("page", ""),
                "excerpt": "",
                "author": meta.get("author", ""),
                "url": source_url,
                "body": body,
            }
        )
    return target_date, articles


def fetch_edition(
    session: requests.Session, target_date: str, known_ids: set[str]
) -> tuple[dict[str, str], list[dict], int]:
    """Re-read an edition's section index pages.

    Returns page numbers keyed by artigo id, plus any article that is not
    already on disk (a section that was excluded when the edition was
    first scraped), and the number of requests made.
    """
    pages: dict[str, str] = {}
    missing: list[dict] = []
    made = 1

    for section in discover_sections(session, target_date):
        for card in scrape_section(session, target_date, section):
            made += 1
            if card["page"]:
                pages[card["id"]] = card["page"]
            if card["id"] in known_ids:
                continue
            card["url"] = (
                f"{BASE_URL}/pagina/edicao-impressa/{target_date}"
                f"?seccao={section}&artigo={card['id']}"
            )
            card["body"] = scrape_article(
                session, target_date, section, card["id"]
            )
            made += 1
            missing.append(card)
            time.sleep(0.3)
        time.sleep(0.3)

    return pages, missing, made


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Regenerate from the pages already on disk, no requests",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    stamps = sorted(
        {p.stem for p in ao_pages.PAGES_DIR.glob("[0-9]" * 8 + ".md")},
        reverse=True,
    )[: args.days]
    if not stamps:
        print("No backfilled editions found.")
        return

    session = None
    if not args.no_fetch:
        email, password, _, _ = load_config()
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36"
                )
            }
        )
        print("Logging in...")
        login(session, email, password)

    repaired = 0
    requests_made = 0
    total_before = total_after = 0

    for stamp in stamps:
        target_date, articles = read_day(stamp)
        if not target_date:
            print(f"  {stamp}: unreadable, skipped")
            continue

        added = 0
        if session is not None:
            known = {a["id"] for a in articles}
            page_by_id, missing, made = fetch_edition(
                session, target_date, known
            )
            requests_made += made
            for article in articles:
                article["page"] = page_by_id.get(
                    article["id"], article["page"]
                )
            articles.extend(missing)
            added = len(missing)

        sections_data: dict[str, list[dict]] = {}
        for article in articles:
            sections_data.setdefault(article["section"], []).append(article)

        entries = ao_pages.build_entries(sections_data, target_date)
        matched = sum(1 for a in articles if a["page"])
        total_before += len(articles)
        total_after += len(entries)
        print(
            f"  {target_date}: {len(articles)} -> {len(entries)} articles "
            f"({matched}/{len(articles)} pages, +{added} recovered)"
        )

        if args.dry_run:
            continue
        ao_pages.write_article_pages(entries, target_date)
        ao_pages.write_day_page(entries, target_date)
        # Merge per day rather than rewriting the feed wholesale, so a
        # partial --days run cannot drop the editions it did not touch.
        ao_pages.write_daily_feed(entries, target_date, FEED_PATH)
        repaired += 1

    if args.dry_run:
        print(
            f"Dry run: {total_before} -> {total_after} articles, "
            f"{requests_made} requests, nothing written"
        )
        return

    print(
        f"Repaired {repaired} editions: {total_before} -> {total_after} "
        f"articles, {requests_made} requests"
    )


if __name__ == "__main__":
    main()
