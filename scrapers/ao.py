#!/usr/bin/env python3
"""Açoriano Oriental print edition scraper.

Two-phase approach:
  1. Scrape print edition section pages for structure (title, excerpt, author, page)
  2. Build a /noticia/ URL index from homepage + category pages, match by slugified
     title, and fetch full article bodies where available.
"""

from __future__ import annotations

import argparse
import configparser
import json
import re
import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.acorianooriental.pt"
CONFIG_PATH = Path(__file__).parent.parent / ".ao_config"
OUTPUT_DIR = Path(__file__).parent / "output"

ALL_SECTIONS = [
    "primeira-hora", "politica", "economia", "local", "sociedade",
    "9-ilhas", "desporto", "cultura", "pontos-de-vista", "da-europa",
]

CATEGORY_PAGES = [
    "/pagina/regional",
    "/pagina/nacional",
    "/pagina/economia",
    "/pagina/politica",
    "/pagina/sociedade",
    "/pagina/cultura",
    "/pagina/desporto",
    "/pagina/9-ilhas",
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


def _slugify(text: str) -> str:
    """NFKD normalize → ASCII → lowercase → hyphens."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


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


# --- Phase 2: Resolve full body via /noticia/ ---

def _collect_noticia_links(soup: BeautifulSoup) -> list[str]:
    """Extract all /noticia/ paths from a page."""
    paths = []
    for a in soup.find_all("a", href=re.compile(r"^/noticia/")):
        path = urlparse(a["href"]).path
        if path not in paths:
            paths.append(path)
    return paths


def build_noticia_index(session: requests.Session) -> dict[str, str]:
    """Scrape homepage + category pages → {slug: /noticia/path} lookup."""
    pages_to_scrape = ["/"] + CATEGORY_PAGES
    slug_to_path: dict[str, str] = {}

    for page in pages_to_scrape:
        url = f"{BASE_URL}{page}"
        try:
            r = session.get(url, timeout=15)
            soup = BeautifulSoup(r.text, "lxml")
            for path in _collect_noticia_links(soup):
                # /noticia/some-slug-here → extract last segment as slug
                segments = [s for s in path.split("/") if s]
                if len(segments) >= 2:
                    slug = segments[-1]
                    slug_to_path[slug] = path
        except requests.RequestException:
            print(f"  Warning: failed to fetch {page}", file=sys.stderr)

    return slug_to_path


def _match_article(title: str, index: dict[str, str]) -> str | None:
    """Try to match a print edition title to a /noticia/ URL slug.

    Strategy: slugify the title and check for substring matches in the index.
    Noticia slugs often contain the full title plus a numeric suffix.
    """
    title_slug = _slugify(title)
    if not title_slug:
        return None

    # Exact match
    if title_slug in index:
        return index[title_slug]

    # Title slug is contained within an index slug (most common case)
    for slug, path in index.items():
        if title_slug in slug:
            return path

    # Partial match: try with first N words for long titles
    words = title_slug.split("-")
    if len(words) >= 4:
        partial = "-".join(words[:5])
        for slug, path in index.items():
            if partial in slug:
                return path

    return None


def scrape_article(session: requests.Session, path: str) -> str:
    """Fetch full body text from a /noticia/ page."""
    url = f"{BASE_URL}{path}"
    try:
        r = session.get(url, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        parts = []

        # Strapline (lead paragraph)
        strapline = soup.select_one("div.strapline")
        if strapline:
            text = _clean(strapline.get_text())
            if text:
                parts.append(text)

        # Body paragraphs
        body = soup.select_one("div.body")
        if body:
            for p in body.find_all("p"):
                text = _clean(p.get_text())
                if text:
                    parts.append(text)

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

    # Phase 2: Resolve full bodies via /noticia/
    print("\nBuilding /noticia/ index...")
    noticia_index = build_noticia_index(session)
    print(f"  Indexed {len(noticia_index)} /noticia/ URLs")

    matched = 0
    for section, articles in sections_data.items():
        for article in articles:
            path = _match_article(article["title"], noticia_index)
            if path:
                article["url"] = f"{BASE_URL}{path}"
                body = scrape_article(session, path)
                if body:
                    article["body"] = body
                    matched += 1

    match_pct = (matched / total_articles * 100) if total_articles else 0
    print(f"\nPhase 2 done: {matched}/{total_articles} matched ({match_pct:.0f}%)")

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


if __name__ == "__main__":
    main()
