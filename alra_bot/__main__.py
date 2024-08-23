import os
from datetime import datetime

from .export import Export
from .fetch import fetch_current_state
from .utils import append_state, compute_delta_ids, get_prev_state


def write_post(delta: dict[str, object]):
    markdown = Export.markdown(delta)
    date = str(datetime.now().date())
    page_font_matter = f"""---
layout: default
date: {date}
categories: alra-scrapper
---
"""
    path = os.path.join(os.path.dirname(__file__), "..", "_posts", f"{date}-alra.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(page_font_matter + markdown)


if __name__ == "__main__":
    current_state = fetch_current_state()
    previous_state = get_prev_state()
    delta = compute_delta_ids(previous_state, current_state)
    if delta:
        append_state(current_state)
        write_post(delta)
