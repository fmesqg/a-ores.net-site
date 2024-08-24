import os
from datetime import datetime, timedelta

from .export import Export
from .fetch import fetch_current_state, fetch_joraa
from .utils import append_state, compute_delta_ids, get_prev_state, markdown_joraa


def write_post(delta: dict[str, object]):
    markdown = Export.markdown(delta)
    markdown_jo = (
        markdown_joraa(joraa_entries) if (joraa_entries := fetch_joraa()) else ""
    )
    date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    page_font_matter = f"""---
layout: default
date: {date}
categories: alra-scrapper
---
"""
    path = os.path.join(os.path.dirname(__file__), "..", "_posts", f"{date}-alra.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(page_font_matter + markdown + "\n\n" + markdown_jo)


if __name__ == "__main__":
    current_state = fetch_current_state()
    previous_state = get_prev_state()
    delta = compute_delta_ids(previous_state, current_state)
    if delta:
        append_state(current_state)
        write_post(delta)
