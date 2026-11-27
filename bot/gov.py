"""Requests to the Azores government's sites (*.azores.gov.pt).

They sit behind Cloudflare. The government's network team grants an
exception to one User-Agent, on condition that the client stays slow
(their reply of November 2026):

- 07:00-20:00 (Azores time): at most 20 requests per hour;
- otherwise: at least 20 seconds between requests.

Every request to those hosts must send ``UA`` and call ``wait()`` first.
Stdlib only: bot/beo.py and bot/srea.py also run as plain scripts.
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

_sleep = time.sleep  # tests replace it
_last: float | None = None


def gap(now: dt.datetime | None = None) -> float:
    """Seconds to leave between two requests at ``now``."""
    now = now or dt.datetime.now(dt.UTC)
    return PEAK_GAP if now.astimezone(TZ).hour in PEAK else OFF_PEAK_GAP


def wait() -> None:
    """Sleep until the next request is allowed, then record it as made."""
    global _last
    if _last is not None:
        delay = _last + gap() - time.monotonic()
        if delay > 0:
            _sleep(delay)
    _last = time.monotonic()
