from copy import deepcopy
from datetime import date, datetime

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
        self.boletins: set = set(self.data.get("boletins"))
        self.sigica: set = set(self.data.get("sigica"))
        self.alra_state = {k: self.data.get(k) for k in State.alra}

    @classmethod
    def get_updated_state(cls, prev_state, web_data: WebData):
        update_state: State = deepcopy(prev_state)
        update_state.datetime = NOW_DATETIME
        if not isinstance(web_data.joraa, FetchError):
            update_state.last_joraa_update = YESTERDAY_DATE
        if not isinstance(web_data.base, FetchError):
            update_state.last_base_update = YESTERDAY_DATE
        if not isinstance(web_data.portal, FetchError):
            update_state.data["sigica"] = set(update_state.data["sigica"]).union(
                web_data.portal.get("sigica")
            )
            update_state.data["boletins"] = set(update_state.data["boletins"]).union(
                web_data.portal.get("boletins")
            )
        if not isinstance(web_data.alra_ids, FetchError):
            update_state.alra_state = web_data.alra_ids
        return update_state
