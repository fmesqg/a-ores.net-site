#!/usr/bin/env python3
"""Açoriano Oriental print edition scraper.

Two-phase approach:
  1. Scrape print edition section pages for structure (title, excerpt, author, page)
  2. Fetch full article body directly via print edition URL using artigo ID.
"""

from __future__ import annotations

import argparse
import configparser
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.acorianooriental.pt"
CONFIG_PATH = Path(__file__).parent.parent / ".ao_config"
OUTPUT_DIR = Path(__file__).parent / "output"
RSS_FEED_PATH = Path(__file__).parent.parent / "docs" / "rss" / "ao.xml"

ALL_SECTIONS = [
    "primeira-hora", "politica", "economia", "local", "sociedade",
    "9-ilhas", "desporto", "cultura", "pontos-de-vista", "da-europa",
]


def load_config():
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH)
    email = cfg["credentials"]["email"]
    password = cfg["credentials"]["password"]

    include = []
    exclude = []
    if cfg.has_section("sections"):
        raw_inc = cfg.get("sections", "include", fallback="")
        raw_exc = cfg.get("sections", "exclude", fallback="")
        if raw_inc.strip():
            include = [s.strip() for s in raw_inc.split(",") if s.strip()]
        if raw_exc.strip():
            exclude = [s.strip() for s in raw_exc.split(",") if s.strip()]

    if not include:
        include = list(ALL_SECTIONS)
    sections = [s for s in include if s not in exclude]
    return email, password, sections


def login(session: requests.Session, email: str, password: str):
    r = session.get(f"{BASE_URL}/iniciar-sessao")
    soup = BeautifulSoup(r.text, "lxml")
    csrf = soup.find("input", {"name": "login_form"})["value"]
    session.post(
        f"{BASE_URL}/iniciar-sessao",
        data={
            "username": email,
            "password": password,
            "remember": "",
            "login_form": csrf,
        },
    )
    if "ACORIANO_SID" not in {c.name for c in session.cookies}:
        print("Login failed", file=sys.stderr)
        sys.exit(1)


def _clean(text: str) -> str:
    """Normalize whitespace and remove &nbsp;."""
    text = text.replace("\xa0", " ").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", text).strip()


# --- Phase 1: Print edition structure ---

def scrape_section(session: requests.Session, target_date: str, section: str):
    """Scrape article cards from a print edition section page."""
    url = f"{BASE_URL}/pagina/edicao-impressa/{target_date}?seccao={section}"
    r = session.get(url)
    soup = BeautifulSoup(r.text, "lxml")

    articles = []
    seen_ids = set()

    for link in soup.find_all("a", href=re.compile(r"artigo=")):
        href = link.get("href", "")
        parsed = parse_qs(urlparse(href).query)
        artigo_id = parsed.get("artigo", [None])[0]
        if not artigo_id or artigo_id in seen_ids:
            continue
        seen_ids.add(artigo_id)

        title_el = link.find("strong")
        title = _clean(title_el.get_text(strip=True)) if title_el else ""
        if not title:
            continue

        excerpt_el = link.find("p")
        excerpt = _clean(excerpt_el.get_text(strip=True)) if excerpt_el else ""

        smalls = link.find_all("small")
        author = ""
        page_num = ""
        if len(smalls) >= 2:
            meta_text = smalls[-1].get_text(strip=True)
            pag_match = re.search(r"Pág\.\s*(\d+)", meta_text)
            if pag_match:
                page_num = pag_match.group(1)
            author_part = meta_text.split("|")[0].strip() if "|" in meta_text else ""
            if author_part and "Pág" not in author_part:
                author = author_part

        articles.append({
            "id": artigo_id,
            "title": title,
            "section": section,
            "page": page_num,
            "excerpt": excerpt,
            "author": author,
            "url": "",
            "body": "",
        })

    return articles


# --- Phase 2: Fetch full body via print edition artigo URL ---

def scrape_article(
    session: requests.Session, target_date: str, section: str, artigo_id: str
) -> str:
    """Fetch full body text from a print edition artigo page."""
    url = f"{BASE_URL}/pagina/edicao-impressa/{target_date}?seccao={section}&artigo={artigo_id}"
    try:
        r = session.get(url, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        article = soup.find("article", class_="article-preview")
        if not article:
            return ""

        parts = []

        # Excerpt (lead paragraph)
        excerpt_el = article.find("p")
        if excerpt_el:
            text = _clean(excerpt_el.get_text())
            if text:
                parts.append(text)

        # Body div contains <br>-separated paragraphs
        body_div = article.find("div", class_="has-text-grey")
        if body_div:
            for p in body_div.find_all("p"):
                text = _clean(p.get_text("\n"))
                # Split on <br> newlines into individual paragraphs
                for chunk in text.split("\n"):
                    chunk = chunk.strip()
                    if chunk:
                        parts.append(chunk)

        return "\n\n".join(parts)
    except requests.RequestException:
        return ""


# --- Output ---

def first_sentence(text: str, max_len: int = 200) -> str:
    """Extract first sentence, capped at max_len chars."""
    if not text:
        return ""
    for i, ch in enumerate(text):
        if ch == "." and i > 20 and (i + 1 >= len(text) or text[i + 1] in " \n"):
            sentence = text[: i + 1].replace("\n", " ")
            if len(sentence) <= max_len:
                return sentence
    clean = text.replace("\n", " ")[:max_len]
    return clean.rsplit(" ", 1)[0] + "..."


def build_summary(target_date: str, sections_data: dict) -> str:
    lines = [f"# Açoriano Oriental — {target_date} (Edição Impressa)\n"]
    for section, articles in sections_data.items():
        if not articles:
            continue
        label = section.replace("-", " ").title()
        lines.append(f"\n## {label}\n")
        for a in articles:
            body_text = a.get("body") or a.get("excerpt", "")
            summary = first_sentence(body_text)
            page_ref = f" (p.{a['page']})" if a.get("page") else ""
            author_ref = f" *{a['author']}*" if a.get("author") else ""
            lines.append(f"- **{a['title']}**{page_ref}{author_ref} — {summary}")
    return "\n".join(lines)


def _rss_pubdate(date_str: str) -> str:
    """Convert YYYY-MM-DD to RFC 2822 date string."""
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    # email.utils.formatdate would require an import; roll it manually
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return (
        f"{days[dt.weekday()]}, {dt.day:02d} {months[dt.month - 1]}"
        f" {dt.year} 00:00:00 +0000"
    )


def _xml_safe(text: str) -> str:
    """Remove characters that are illegal in XML 1.0."""
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)


def update_rss_feed(articles: list[dict], target_date: str) -> int:
    """Append new articles to the RSS feed. Returns count of new items added."""
    existing_guids: set[str] = set()
    existing_items: list[ET.Element] = []

    if RSS_FEED_PATH.exists():
        tree = ET.parse(RSS_FEED_PATH)
        channel = tree.getroot().find("channel")
        if channel is not None:
            for item in channel.findall("item"):
                guid_el = item.find("guid")
                if guid_el is not None and guid_el.text:
                    existing_guids.add(guid_el.text)
                existing_items.append(item)

    new_items: list[ET.Element] = []
    for a in articles:
        if not a.get("url") or a["url"] in existing_guids:
            continue
        item = ET.Element("item")
        ET.SubElement(item, "title").text = _xml_safe(a["title"])
        ET.SubElement(item, "guid", isPermaLink="false").text = a["url"]
        ET.SubElement(item, "pubDate").text = _rss_pubdate(target_date)
        ET.SubElement(item, "category").text = a["section"]
        ET.SubElement(item, "description").text = _xml_safe(
            a.get("body") or a.get("excerpt", "")
        )
        if a.get("author"):
            ET.SubElement(item, "author").text = _xml_safe(a["author"])
        new_items.append(item)
        existing_guids.add(a["url"])

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Açoriano Oriental — Edição Impressa"
    ET.SubElement(channel, "link").text = BASE_URL
    ET.SubElement(channel, "description").text = (
        "Edição impressa do Açoriano Oriental"
    )
    for item in new_items + existing_items:
        channel.append(item)

    ET.indent(rss, space="  ")
    with open(RSS_FEED_PATH, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        ET.ElementTree(rss).write(f, encoding="utf-8", xml_declaration=False)

    return len(new_items)


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape AO print edition")
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Edition date YYYY-MM-DD (default: yesterday)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    target_date = args.date or (date.today() - timedelta(days=1)).isoformat()

    email, password, sections = load_config()
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })

    print("Logging in...")
    login(session, email, password)

    # Phase 1: Print edition structure
    sections_data = {}
    total_articles = 0

    for section in sections:
        print(f"Scraping section: {section}...")
        articles = scrape_section(session, target_date, section)
        print(f"  Found {len(articles)} articles")
        total_articles += len(articles)
        sections_data[section] = articles

    print(f"\nPhase 1 done: {total_articles} articles across {len(sections)} sections")

    # Deduplicate primeira-hora: remove articles whose title appears in another section
    if "primeira-hora" in sections_data:
        other_titles = set()
        for sec, arts in sections_data.items():
            if sec != "primeira-hora":
                other_titles.update(a["title"] for a in arts)
        before = len(sections_data["primeira-hora"])
        sections_data["primeira-hora"] = [
            a for a in sections_data["primeira-hora"] if a["title"] not in other_titles
        ]
        deduped = before - len(sections_data["primeira-hora"])
        if deduped:
            total_articles -= deduped
            print(f"Deduped {deduped} primeira-hora articles (kept {len(sections_data['primeira-hora'])})")

    # Phase 2: Fetch full bodies directly via print edition artigo URLs
    print("\nFetching full articles...")
    for section, articles in sections_data.items():
        for article in articles:
            artigo_url = f"{BASE_URL}/pagina/edicao-impressa/{target_date}?seccao={section}&artigo={article['id']}"
            article["url"] = artigo_url
            body = scrape_article(session, target_date, section, article["id"])
            if body:
                article["body"] = body

    print(f"Phase 2 done: fetched {total_articles} articles")

    # Write output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_articles = []
    for articles in sections_data.values():
        all_articles.extend(articles)

    json_path = OUTPUT_DIR / f"{target_date}.json"
    with open(json_path, "w") as f:
        json.dump(
            {"date": target_date, "edition": "impressa", "articles": all_articles},
            f, ensure_ascii=False, indent=2,
        )
    print(f"Wrote {json_path}")

    md_path = OUTPUT_DIR / f"{target_date}.md"
    with open(md_path, "w") as f:
        f.write(build_summary(target_date, sections_data))
    print(f"Wrote {md_path}")

    added = update_rss_feed(all_articles, target_date)
    print(f"RSS: added {added} new items → {RSS_FEED_PATH}")


if __name__ == "__main__":
    main()
