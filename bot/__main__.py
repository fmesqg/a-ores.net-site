from .fetch import fetch_web_data
from .state import State
from .utils import append_state, get_prev_state, write_update

if __name__ == "__main__":
    previous_state = get_prev_state()
    web_data = fetch_web_data(previous_state)
    new_state = State.get_updated_state(previous_state, web_data)
    write_update(web_data)
    append_state(new_state)
