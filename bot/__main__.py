from .fetch import fetch_all_data, fetch_current_state
from .utils import append_state, compute_delta_ids, get_prev_state, write_update
import datetime

# from .retro_fix_posts   import retro_fix_posts

if __name__ == "__main__":
    now = datetime.datetime.now(datetime.UTC)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    yesterday_yyyymmdd = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    current_state = fetch_current_state()
    previous_state = get_prev_state()
    delta = compute_delta_ids(previous_state, current_state)
    web_data = fetch_all_data(delta, date=yesterday_yyyymmdd)
    # TODO add here the logic to check Fetch errors and keep a log of such errors
    write_update(web_data, date=yesterday_yyyymmdd)
    append_state(current_state, timestamp)
    # retro_fix_posts()
