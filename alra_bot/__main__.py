from datetime import datetime
import os
from .export import Export
from .fetch import fetch_current_state
from .utils import append_state, compute_delta, get_prev_state


def export_delta(delta: dict[str, object]):
    markdowns = "\n\n".join([Export.markdown(i, delta[i]) for i in delta])
    date = str(datetime.now().date())
    page_font_matter = f"""---
layout: default
date: {date}
categories: alra-scrapper
---
"""
    path = os.path.join(os.path.dirname(__file__), "..", "_posts", f"{date}-alra.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(page_font_matter + markdowns)


if __name__ == "__main__":
    current_state = fetch_current_state()
    previous_state = get_prev_state()
    temp_curr = current_state.copy()
    temp_prev = previous_state.copy()
    temp_curr.pop("datetime")
    temp_prev.pop("datetime")
    if temp_prev != temp_curr:
        delta = compute_delta(previous_state, current_state)
        append_state(current_state)
        export_delta(delta)
    else:
        print("done")
