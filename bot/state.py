from copy import deepcopy
from datetime import date, datetime, timedelta

from bot.classes import FetchError, WebData
from bot.constants import NOW_DATETIME, YESTERDAY_DATE


class State:
    alra = [
        "requerimentos",
        "informacoes",
        "diarios",
        "votos",
        "iniciativas",
        "intervencoes",
        "peticoes",
        "audi_gr",
        "audi_ar",
    ]

    def __init__(self, data: dict):
        self.data = data
        self.last_base_update: date = datetime.strptime(
            self.data.get("last_base_update"), "%Y-%m-%d"
        ).date()
        self.last_joraa_update: date = datetime.strptime(
            self.data.get("last_joraa_update"), "%Y-%m-%d"
        ).date()
        b = self.data.get("joraa_backfill")
        self.joraa_backfill: tuple[date, date] | None = (
            tuple(datetime.strptime(d, "%Y-%m-%d").date() for d in b)
            if b
            else None
        )
        self.boletins: set = set(self.data.get("boletins"))
        self.sigica: set = set(self.data.get("sigica"))
        self.alra_state = {k: self.data.get(k) for k in State.alra}

    @classmethod
    def get_updated_state(cls, prev_state, web_data: WebData):
        update_state: State = deepcopy(prev_state)
        update_state.datetime = NOW_DATETIME
        plan = web_data.joraa_backfill
        done = (
            set()
            if isinstance(web_data.joraa, FetchError) or not web_data.joraa
            else set(web_data.joraa)
        )
        if plan:
            start, end = plan
            # days up to the end of the backfill are the backfill's now
            update_state.last_joraa_update = max(
                [
                    prev_state.last_joraa_update,
                    end,
                    *(d for d in done if d > end),
                ]
            )
            back = [d for d in done if start <= d <= end]
            if back:  # worked from the newest day down
                end = min(back) - timedelta(days=1)
            update_state.joraa_backfill = (
                (start, end) if end >= start else None
            )
        elif done:
            # the last day fetched: a backlog may take several runs
            update_state.last_joraa_update = max(done)
        if not isinstance(web_data.base, FetchError):
            update_state.last_base_update = YESTERDAY_DATE
        if not isinstance(web_data.portal, FetchError):
            update_state.data["sigica"] = set(
                update_state.data["sigica"]
            ).union(web_data.portal.get("sigica"))
            update_state.data["boletins"] = set(
                update_state.data["boletins"]
            ).union(web_data.portal.get("boletins"))
        if not isinstance(web_data.alra_ids, FetchError):
            update_state.alra_state = web_data.alra_ids
        return update_state
