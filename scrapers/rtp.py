#!/usr/bin/env python3
"""RTP Açores scraper via WordPress REST API."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import requests

BASE_URL = "https://acores.rtp.pt"
API_URL = f"{BASE_URL}/wp-json/wp/v2"
OUTPUT_DIR = Path(__file__).parent / "output"


def fetch_categories() -> dict[int, str]:
    """GET /wp-json/wp/v2/categories → {id: name} mapping."""
    r = requests.get(f"{API_URL}/categories/", params={"per_page": 100})
    r.raise_for_status()
    return {cat["id"]: cat["name"] for cat in r.json()}


def fetch_posts(target_date: str) -> list[dict]:
    """Fetch all posts for a given date, paginating if needed."""
    next_day = (
        date.fromisoformat(target_date) + timedelta(days=1)
    ).isoformat()
    params = {
        "per_page": 100,
        "after": f"{target_date}T00:00:00",
        "before": f"{next_day}T00:00:00",
        "_embed": "",
    }

    all_posts = []
    page = 1
    while True:
        params["page"] = page
        r = requests.get(f"{API_URL}/posts/", params=params)
        if r.status_code == 400:
            break
        r.raise_for_status()
        posts = r.json()
        if not posts:
            break
        all_posts.extend(posts)
        page += 1

    return all_posts


def _strip_html(html: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", "", html)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&#8217;", "'")
        .replace("&amp;", "&")
    )
    return re.sub(r"\s+", " ", text).strip()


def parse_post(post: dict, categories: dict[int, str]) -> dict:
    """Extract structured data from a WP post object."""
    # Category from _embedded or fall back to category IDs
    cat_name = ""
    embedded = post.get("_embedded", {})
    terms = embedded.get("wp:term", [])
    if terms and terms[0]:
        cat_name = terms[0][0].get("name", "")
    if not cat_name and post.get("categories"):
        cat_name = categories.get(post["categories"][0], "")

    return {
        "id": post["id"],
        "title": _strip_html(post["title"]["rendered"]),
        "category": cat_name,
        "date": post["date"],
        "url": post["link"],
        "excerpt": _strip_html(post["excerpt"]["rendered"]),
        "body": _strip_html(post["content"]["rendered"]),
    }


def build_summary(target_date: str, articles: list[dict]) -> str:
    """Group articles by category into markdown."""
    lines = [f"# RTP Açores — {target_date}\n"]

    by_cat: dict[str, list[dict]] = {}
    for a in articles:
        by_cat.setdefault(a["category"], []).append(a)

    for cat, arts in by_cat.items():
        lines.append(f"\n## {cat}\n")
        for a in arts:
            excerpt = a["excerpt"][:200] if a["excerpt"] else ""
            lines.append(f"- **{a['title']}** — {excerpt}")

    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scrape RTP Açores via WP API"
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Target date YYYY-MM-DD (default: yesterday)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    target_date = args.date or (date.today() - timedelta(days=1)).isoformat()

    print("Fetching categories...")
    categories = fetch_categories()
    print(f"  {len(categories)} categories")

    print(f"Fetching posts for {target_date}...")
    raw_posts = fetch_posts(target_date)
    print(f"  {len(raw_posts)} posts")

    if not raw_posts:
        print("No posts found.", file=sys.stderr)
        sys.exit(0)

    articles = [parse_post(p, categories) for p in raw_posts]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = OUTPUT_DIR / f"rtp-{target_date}.json"
    with open(json_path, "w") as f:
        json.dump(
            {
                "date": target_date,
                "source": "rtp-acores",
                "articles": articles,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"Wrote {json_path}")

    md_path = OUTPUT_DIR / f"rtp-{target_date}.md"
    with open(md_path, "w") as f:
        f.write(build_summary(target_date, articles))
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
