import json
import os
from datetime import datetime, timedelta

from .constants import STATE_FILE
from .utils import compute_delta_ids, write_update


def retro_fix_posts():
    path = os.path.join(os.path.dirname(__file__), STATE_FILE)
    with open(path, mode="r") as f:
        states = [json.loads(line) for line in f.readlines()]
    previous_state, rest = states[0], states[1:]
    for current_state in rest:
        delta = compute_delta_ids(previous_state, current_state)
        input_date: datetime = datetime.strptime(
            current_state["datetime"], "%Y-%m-%d %H:%M:%S"
        )
        day_before = input_date - timedelta(days=1)
        write_update(delta, date=day_before.strftime("%Y-%m-%d"))
        previous_state = current_state


if __name__ == "__main__":
    retro_fix_posts()
