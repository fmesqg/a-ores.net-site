"""Interactive Telegram bot with on-demand command handlers.

Commands:
  /ao    — Açoriano Oriental (today's headlines by section)
  /al    — ALRA parliamentary updates (latest file)
  /jo    — Jornal Oficial updates (latest file)
  /base  — BASE public contracts (latest file)

Run:
  TELEGRAM_BOT_TOKEN=... python -m bot.tgbot
"""

from __future__ import annotations

import html
import logging
import os
import re
import time
from datetime import date
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

DOCS_DIR = Path(__file__).parent.parent / "docs"
AO_DIR = DOCS_DIR / "_ao"
SITE_BASE = "https://xn--aores-yra.net"

_HELP = (
    "*Comandos disponíveis*\n"
    "/ao — Açoriano Oriental (hoje)\n"
    "/al — ALRA (assembleia legislativa)\n"
    "/jo — Jornal Oficial\n"
    "/base — Contratos públicos (BASE)"
)


# --- Data readers ---


def _strip_frontmatter(text: str) -> str:
    return re.sub(r"\A---\n.*?---\n", "", text, count=1, flags=re.DOTALL)


def _latest_doc(folder: str) -> str | None:
    files = sorted((DOCS_DIR / folder).glob("*.md"))
    if not files:
        return None
    return _strip_frontmatter(files[-1].read_text(encoding="utf-8")).strip()


def _split(text: str, limit: int = 4000) -> list[str]:
    """Split into Telegram-safe chunks on newline boundaries."""
    if len(text) <= limit:
        return [text]
    parts = []
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
        cut = text.rfind("\n", 0, limit)
        if cut <= 0:
            cut = limit
        parts.append(text[:cut])
        text = text[cut:].lstrip("\n")
    return parts


def _ao_day_file() -> Path | None:
    """Today's edition page, else the most recent one available."""
    today = AO_DIR / f"{date.today():%Y%m%d}.md"
    if today.exists():
        return today
    days = sorted(AO_DIR.glob("[0-9]" * 8 + ".md"))
    return days[-1] if days else None


_H2 = re.compile(r"<h2>(.*?)</h2>")
_LINK = re.compile(r'<li><a href="(.*?)">(.*?)</a></li>')


def reply_ao() -> list[str]:
    path = _ao_day_file()
    if path is None:
        return ["Sem dados do AO disponíveis."]

    stamp = path.stem
    edition = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}"
    body = _strip_frontmatter(path.read_text(encoding="utf-8"))
    lines = [f"*Açoriano Oriental — {edition}*"]

    for line in body.splitlines():
        heading = _H2.match(line.strip())
        if heading:
            lines.append(f"\n_{html.unescape(heading.group(1))}_")
            continue
        link = _LINK.match(line.strip())
        if link:
            url, label = link.group(1), html.unescape(link.group(2))
            lines.append(f"• [{label}]({SITE_BASE}{url})")

    if len(lines) == 1:
        return [f"Sem artigos do AO para {edition}."]

    return _split("\n".join(lines))


def reply_docs(folder: str, label: str) -> list[str]:
    content = _latest_doc(folder)
    if not content:
        return [f"Sem dados de {label} disponíveis."]
    return _split(content)


_COMMANDS: dict[str, tuple[str, object]] = {
    "/ao": ("Açoriano Oriental", lambda: reply_ao()),
    "/al": ("ALRA", lambda: reply_docs("_alra_updates", "ALRA")),
    "/jo": ("Jornal Oficial", lambda: reply_docs("_joraa_updates", "JORAA")),
    "/base": ("BASE", lambda: reply_docs("_base_updates", "BASE")),
    "/help": ("ajuda", lambda: [_HELP]),
    "/start": ("início", lambda: [_HELP]),
}


# --- Telegram API helpers ---


def _api(token: str, method: str, **kwargs) -> dict:
    r = requests.post(
        f"https://api.telegram.org/bot{token}/{method}",
        timeout=40,
        **kwargs,
    )
    return r.json()


def _send(token: str, chat_id: int | str, text: str) -> None:
    try:
        _api(
            token,
            "sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
            },
        )
    except Exception:
        logger.exception("sendMessage failed")


# --- Polling loop ---


def run(token: str) -> None:
    logger.info("Bot polling started")
    offset = 0
    while True:
        try:
            data = _api(
                token,
                "getUpdates",
                params={"offset": offset, "timeout": 30},
            )
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message") or update.get("channel_post")
                if not msg:
                    continue
                raw = msg.get("text", "").strip()
                if not raw.startswith("/"):
                    continue
                chat_id = msg["chat"]["id"]
                # strip @BotName suffix
                cmd = raw.split()[0].split("@")[0].lower()
                entry = _COMMANDS.get(cmd)
                if entry:
                    _, handler = entry
                    logger.info("cmd %s from chat %s", cmd, chat_id)
                    for chunk in handler():
                        _send(token, chat_id, chunk)
        except requests.RequestException as exc:
            logger.warning("Network error: %s — retrying in 10s", exc)
            time.sleep(10)
        except Exception:
            logger.exception("Unexpected poll error — retrying in 10s")
            time.sleep(10)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN not set")
    run(token)


if __name__ == "__main__":
    main()
