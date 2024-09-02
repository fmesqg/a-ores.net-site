from .fetch import fetch_current_state
from .utils import append_state, compute_delta_ids, get_prev_state, write_update

# from .retro_fix_posts   import retro_fix_posts

if __name__ == "__main__":
    current_state = fetch_current_state()
    previous_state = get_prev_state()
    delta = compute_delta_ids(previous_state, current_state)
    write_update(delta)
    if delta:
        append_state(current_state)
    # retro_fix_posts()
