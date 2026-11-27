import datetime as dt

from bot import gov


def at(hour, month=1):
    """A moment at ``hour`` Azores time (UTC-1 in winter, UTC in summer)."""
    local = dt.datetime(2026, month, 15, hour, 30, tzinfo=gov.TZ)
    return local.astimezone(dt.UTC)


def test_gap_by_azores_hour():
    assert gov.gap(at(6)) == 20
    assert gov.gap(at(7)) == 180  # 20 requests per hour
    assert gov.gap(at(19)) == 180
    assert gov.gap(at(20)) == 20
    assert gov.gap(at(7, month=7)) == 180


def test_wait_spaces_requests(monkeypatch):
    clock = [1000.0]
    slept = []

    def sleep(seconds):
        slept.append(seconds)
        clock[0] += seconds

    monkeypatch.setattr(gov.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(gov, "_sleep", sleep)
    monkeypatch.setattr(gov, "gap", lambda now=None: 20)
    gov.wait()  # first request: no wait
    clock[0] += 5
    gov.wait()
    clock[0] += 30
    gov.wait()  # already 30 s later
    assert slept == [15]


def test_user_agent_is_ascii_and_names_the_site():
    gov.UA.encode("ascii")
    assert gov.UA.startswith("acores.net-bot/")
    assert gov.HEADERS == {"User-Agent": gov.UA}
