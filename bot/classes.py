from datetime import date


class FetchError(Exception):
    def __init__(self, info=None):
        self.info = info


class WebData:
    def __init__(self, joraa=None, alra=None, base=None, portal=None, alra_ids=None):
        self.joraa: dict[date, dict] = joraa
        self.alra = alra
        self.base: dict[date, dict] = base
        self.portal = portal
        self.alra_ids = alra_ids
