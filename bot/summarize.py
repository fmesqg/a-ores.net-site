import logging
import os
import re
from datetime import date

import anthropic
import requests

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
Es um assistente que resume a atividade diária do governo dos Açores \
para um canal de Telegram.

Regras:
- Escreve em português (contexto açoriano).
- Máximo 5 pontos, priorizados por montante de despesa pública e \
relevância política.
- Menciona o total de despesa JORAA, o maior contrato BASE, e \
quaisquer novas iniciativas parlamentares.
- Se uma fonte teve erro, menciona-o brevemente.
- Máximo 1000 caracteres.
- Sem saudações nem despedidas — apenas o resumo.
- Usa negrito (*negrito*) para nomes de entidades e montantes.
- Formato: lista com marcadores (• ou -).
"""

_UPDATE_FOLDERS = [
    "_alra_updates",
    "_joraa_updates",
    "_base_updates",
    "_portal_updates",
]


def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter delimited by ---."""
    return re.sub(r"\A---\n.*?---\n", "", text, count=1, flags=re.DOTALL)


def _build_daily_markdown(target_date: date | None = None) -> str:
    """Read today's markdown files from disk and concatenate them."""
    if target_date is None:
        from .constants import YESTERDAY_DATE

        target_date = YESTERDAY_DATE

    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    sections = []
    for folder in _UPDATE_FOLDERS:
        path = os.path.join(docs_dir, folder, f"{target_date}.md")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                content = _strip_frontmatter(f.read()).strip()
            if content:
                sections.append(content)
    return "\n\n".join(sections)


def summarize(daily_markdown: str) -> str | None:
    """Call Claude to summarize the day's changes. Returns None on failure."""
    model = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Resume as alterações de hoje:\n\n" + daily_markdown
                    ),
                }
            ],
        )
        return response.content[0].text
    except Exception:
        logger.exception("LLM summarization failed")
        return None


def post_to_telegram(text: str) -> bool:
    """POST to Telegram Bot API. Returns True on success."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        logger.warning("Telegram credentials not set, skipping post")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.ok:
            logger.info("Telegram message sent")
            return True
        logger.warning(
            "Telegram API error %s: %s", resp.status_code, resp.text
        )
        return False
    except Exception:
        logger.exception("Telegram post failed")
        return False


def summarize_and_post() -> None:
    """Top-level entry point. Skips if keys missing. Swallows errors."""
    if not os.environ.get("ANTHROPIC_API_KEY") or not os.environ.get(
        "TELEGRAM_BOT_TOKEN"
    ):
        logger.info("Summarize/Telegram keys not set, skipping")
        return

    try:
        md = _build_daily_markdown()
        if not md.strip():
            logger.info("No changes to summarize")
            return
        summary = summarize(md)
        if summary:
            post_to_telegram(summary)
    except Exception:
        logger.exception("summarize_and_post failed")
