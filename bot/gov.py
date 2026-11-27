"""Requests to the Azores government's sites (*.azores.gov.pt).

They sit behind the government's Cloudflare, but not all of them are set up
alike. jo.azores.gov.pt and portal.azores.gov.pt answer automated clients
with a challenge (403, cf-mitigated: challenge). The government's network
team grants an exception to one User-Agent, on condition that the client
stays slow (their reply of November 2026):

- 07:00-20:00 (Azores time): at most 20 requests per hour;
- otherwise: at least 20 seconds between requests.

srea.azores.gov.pt is not challenged: it answers any client with 200
(checked 27/11/2026), and the network team's contact said the hosts are
configured differently. It gets a light limit of its own (``LIGHT``),
tracked apart from the others, so the SREA bot does not wait on the
JORAA one. If SREA starts answering 403 or 429, bot/srea.py stops or
backs off.

Every request to those hosts must send ``UA`` and call ``wait(host)``
first. Stdlib only: bot/beo.py and bot/srea.py also run as plain scripts.
"""

import datetime as dt
import time
from zoneinfo import ZoneInfo

UA = (
    "acores.net-bot/1.0 "
    "(+https://xn--aores-yra.net/; https://github.com/fmesqg/a-ores.net-site)"
)
HEADERS = {"User-Agent": UA}
TZ = ZoneInfo("Atlantic/Azores")
PEAK = range(7, 20)  # hours, local time
PEAK_GAP = 3600 / 20  # seconds: 20 requests per hour
OFF_PEAK_GAP = 20
LIGHT = {"srea.azores.gov.pt": 3}  # host: seconds between requests

_sleep = time.sleep  # tests replace it
_last: dict[str, float] = {}


def gap(now: dt.datetime | None = None, host: str | None = None) -> float:
    """Seconds to leave between two requests to ``host`` at ``now``."""
    if host in LIGHT:
        return LIGHT[host]
    now = now or dt.datetime.now(dt.UTC)
    return PEAK_GAP if now.astimezone(TZ).hour in PEAK else OFF_PEAK_GAP


def wait(host: str | None = None) -> None:
    """Sleep until the next request to ``host`` is allowed, then record it
    as made. Each host in ``LIGHT`` keeps its own clock; every other host
    shares one, as the network team's limit covers them together."""
    key = host if host in LIGHT else "*"
    last = _last.get(key)
    if last is not None:
        delay = last + gap(host=host) - time.monotonic()
        if delay > 0:
            _sleep(delay)
    _last[key] = time.monotonic()
