#!/usr/bin/env python3
"""Jekyll page + daily RSS generation for the AO print edition.

The feed carries one small item per edition day; the item body is a link
list grouped by newspaper section. Each article lives on its own page at
``/ao/YYYYMMDD-NN/``.
"""

from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

SITE_BASE = "https://xn--aores-yra.net"
PAGES_DIR = Path(__file__).parent.parent / "docs" / "_ao"
FEED_RETENTION_DAYS = 90

# The front page only carries teasers: reworded headlines and one- or
# two-sentence blurbs whose real articles run inside the edition. "0" is
# the lead story, whose card omits the "Pág. N" marker the scraper reads.
FRONT_PAGE_NUMBERS = {"0", "1"}

# Sorts articles with no page number last rather than first.
_NO_PAGE = 10**6

FEED_TITLE = "Açoriano Oriental — Edição Impressa"
FEED_LINK = "https://www.acorianooriental.pt"
FEED_DESCRIPTION = "Edição impressa do Açoriano Oriental, uma entrada por dia"

_DAY_GUID_PREFIX = "ao-"


def _xml_safe(text: str) -> str:
    """Remove characters that are illegal in XML 1.0."""
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)


def _rss_pubdate(date_str: str) -> str:
    """Convert YYYY-MM-DD to RFC 2822 date string."""
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    return (
        f"{days[dt.weekday()]}, {dt.day:02d} {months[dt.month - 1]}"
        f" {dt.year} 00:00:00 +0000"
    )


def section_label(slug: str) -> str:
    """Human-readable label for a section slug."""
    return slug.replace("-", " ").title()


def day_slug(target_date: str) -> str:
    """YYYY-MM-DD -> YYYYMMDD."""
    return target_date.replace("-", "")


def _yaml_str(value: str) -> str:
    """Quote a string as a YAML scalar.

    JSON's double-quoted form is valid YAML, which avoids a pyyaml
    dependency the project does not otherwise carry.
    """
    return json.dumps(_xml_safe(value), ensure_ascii=False)


# --- Entries ---


def _page_key(page: str) -> int:
    return int(page) if page.isdigit() else _NO_PAGE


def build_entries(sections_data: dict, target_date: str) -> list[dict]:
    """Number the day's articles so the edition reads front-to-back.

    Sections are ordered by their lowest page number and articles by page
    within each section, so following the numbering is the same as
    flipping through the paper. Ties keep the print edition's own order.

    Front-page teasers, and articles with neither body nor excerpt, are
    dropped and do not consume a number. Articles with no page at all are
    kept, sorted last: the page number is missing, not the article.
    """
    stamp = day_slug(target_date)

    kept: dict[str, list[tuple[str, str, dict]]] = {}
    for section, articles in sections_data.items():
        for article in articles:
            page = str(article.get("page") or "").strip()
            if page in FRONT_PAGE_NUMBERS:
                continue
            body = article.get("body") or article.get("excerpt") or ""
            if not body.strip():
                continue
            kept.setdefault(section, []).append((page, body, article))

    positions = {section: i for i, section in enumerate(kept)}
    ordered = sorted(
        kept,
        key=lambda s: (
            min(_page_key(page) for page, _, _ in kept[s]),
            positions[s],
        ),
    )

    entries: list[dict] = []
    for section in ordered:
        # Stable, so articles on the same page keep the paper's order.
        for page, body, article in sorted(
            kept[section], key=lambda t: _page_key(t[0])
        ):
            slug = f"{stamp}-{len(entries) + 1:02d}"
            entries.append(
                {
                    "slug": slug,
                    "url": f"/ao/{slug}/",
                    "date": target_date,
                    "title": _xml_safe(article.get("title", "")),
                    "section": section,
                    "section_label": section_label(section),
                    "page": _xml_safe(page),
                    "author": _xml_safe(article.get("author") or ""),
                    "body": _xml_safe(body),
                    "source_url": article.get("url", ""),
                }
            )

    return entries


def _meta_suffix(entry: dict) -> str:
    """`` (p.6)`` / `` — Autor`` decorations, omitted when absent."""
    parts = ""
    if entry["page"]:
        parts += f" (p.{entry['page']})"
    if entry["author"]:
        parts += f" — {entry['author']}"
    return parts


def build_link_list(entries: list[dict], absolute: bool = False) -> str:
    """Render the entries as an HTML list grouped by section."""
    prefix = SITE_BASE if absolute else ""
    lines: list[str] = []
    current_section = None

    for entry in entries:
        if entry["section"] != current_section:
            if current_section is not None:
                lines.append("</ul>")
            current_section = entry["section"]
            lines.append(f"<h2>{html.escape(entry['section_label'])}</h2>")
            lines.append("<ul>")
        href = html.escape(prefix + entry["url"])
        label = html.escape(entry["title"] + _meta_suffix(entry))
        lines.append(f'<li><a href="{href}">{label}</a></li>')

    if current_section is not None:
        lines.append("</ul>")

    return "\n".join(lines)


# --- Pages ---


def _frontmatter(fields: dict) -> str:
    lines = ["---"]
    for key, value in fields.items():
        if value == "" or value is None:
            continue
        lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def write_article_pages(entries: list[dict], target_date: str) -> int:
    """Write one page per article, replacing any previous run's output."""
    stamp = day_slug(target_date)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    for stale in PAGES_DIR.glob(f"{stamp}-*.md"):
        stale.unlink()

    for i, entry in enumerate(entries):
        fields = {
            "layout": "ao_article",
            "kind": "article",
            "title": _yaml_str(entry["title"]),
            "date": target_date,
            "edition": _yaml_str(target_date),
            "section": _yaml_str(entry["section"]),
            "section_label": _yaml_str(entry["section_label"]),
            "page": _yaml_str(entry["page"]) if entry["page"] else "",
            "author": _yaml_str(entry["author"]) if entry["author"] else "",
            "source_url": (
                _yaml_str(entry["source_url"]) if entry["source_url"] else ""
            ),
            "day_url": f"/ao/{stamp}/",
            "prev_url": entries[i - 1]["url"] if i > 0 else "",
            "next_url": (
                entries[i + 1]["url"] if i + 1 < len(entries) else ""
            ),
        }
        paragraphs = [
            f"<p>{html.escape(p.strip())}</p>"
            for p in entry["body"].split("\n\n")
            if p.strip()
        ]
        page = _frontmatter(fields) + "\n\n" + "\n\n".join(paragraphs) + "\n"
        (PAGES_DIR / f"{entry['slug']}.md").write_text(page, encoding="utf-8")

    return len(entries)


def write_day_page(entries: list[dict], target_date: str) -> Path:
    """Write the edition index page listing every article by section."""
    stamp = day_slug(target_date)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    fields = {
        "layout": "ao_day",
        "kind": "day",
        "title": _yaml_str(f"Açoriano Oriental — {target_date}"),
        "date": target_date,
        "edition": _yaml_str(target_date),
        "article_count": str(len(entries)),
    }
    body = build_link_list(entries) or "<p>Sem artigos nesta edição.</p>"
    path = PAGES_DIR / f"{stamp}.md"
    path.write_text(_frontmatter(fields) + "\n\n" + body + "\n", "utf-8")
    return path


# --- Feed ---


def build_feed_item(entries: list[dict], target_date: str) -> ET.Element:
    stamp = day_slug(target_date)
    item = ET.Element("item")
    ET.SubElement(item, "title").text = (
        f"Açoriano Oriental — {target_date} ({len(entries)} artigos)"
    )
    ET.SubElement(item, "link").text = f"{SITE_BASE}/ao/{stamp}/"
    ET.SubElement(item, "guid", isPermaLink="false").text = (
        f"{_DAY_GUID_PREFIX}{target_date}"
    )
    ET.SubElement(item, "pubDate").text = _rss_pubdate(target_date)
    ET.SubElement(item, "description").text = build_link_list(
        entries, absolute=True
    )
    return item


def _item_date(item: ET.Element) -> str:
    guid = item.findtext("guid", "") or ""
    if guid.startswith(_DAY_GUID_PREFIX):
        return guid[len(_DAY_GUID_PREFIX) :]
    return ""


def write_daily_feed(
    entries: list[dict], target_date: str, feed_path: Path
) -> int:
    """Replace this day's feed item, keeping the newest days only.

    Returns the number of items in the resulting feed.
    """
    items: list[ET.Element] = []
    if feed_path.exists():
        channel = ET.parse(feed_path).getroot().find("channel")
        if channel is not None:
            items = [
                item
                for item in channel.findall("item")
                if _item_date(item) and _item_date(item) != target_date
            ]

    items.append(build_feed_item(entries, target_date))
    items.sort(key=_item_date, reverse=True)
    items = items[:FEED_RETENTION_DAYS]

    write_feed(items, feed_path)
    return len(items)


def write_feed(items: list[ET.Element], feed_path: Path) -> None:
    """Serialize a list of day items into the RSS file."""
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = FEED_TITLE
    ET.SubElement(channel, "link").text = FEED_LINK
    ET.SubElement(channel, "description").text = FEED_DESCRIPTION
    for item in items:
        channel.append(item)

    ET.indent(rss, space="  ")
    feed_path.parent.mkdir(parents=True, exist_ok=True)
    with open(feed_path, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        ET.ElementTree(rss).write(f, encoding="utf-8", xml_declaration=False)
