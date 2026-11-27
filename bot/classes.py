from datetime import date


class FetchError(Exception):
    def __init__(self, info=None):
        self.info = info


class WebData:
    def __init__(
        self,
        joraa=None,
        alra=None,
        base=None,
        portal=None,
        alra_ids=None,
        joraa_backfill=None,
    ):
        self.joraa: dict[date, dict] = joraa
        # JORAA days still missing after this run's plan (fetch.joraa_plan)
        self.joraa_backfill: tuple[date, date] | None = joraa_backfill
        self.alra = alra
        self.base: dict[date, dict] = base
        self.portal = portal
        self.alra_ids = alra_ids
