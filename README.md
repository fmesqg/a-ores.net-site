# Açores.net

Civic information bot for the Azores — scrapes government and legislative data daily and publishes it as a Jekyll static site.

## Data sources

### Bot pipeline (government/legislative)

| Source | Content |
|--------|---------|
| [ALRA](http://base.alra.pt:82) | Parliamentary records (questions, votes, proposals) |
| [JORAA](https://jo.azores.gov.pt) | Government journal acts |
| [BASE](https://www.base.gov.pt) | Public procurement contracts |
| [Portal](https://portal.azores.gov.pt) | Government portal documents |

### News scrapers (`scrapers/`)

| Source | Script | Auth | Method |
|--------|--------|------|--------|
| [Açoriano Oriental](https://www.acorianooriental.pt) | `scrapers/ao.py` | Login (`.ao_config`) | HTML scraping |
| [RTP Açores](https://acores.rtp.pt) | `scrapers/rtp.py` | None | WordPress REST API |

## Setup

```bash
poetry install            # runtime deps
poetry install --with dev # + linting/testing
```

## Usage

```bash
poetry run python -m bot          # run full daily pipeline
poetry run pytest bot/tests/ -v   # run tests
poetry run ruff check bot/        # lint
poetry run black --check bot/     # format check
```

## News scrapers

Standalone scrapers for Azorean news sources. Output goes to `scrapers/output/`.

```bash
# AO print edition (requires .ao_config with credentials)
python3 scrapers/ao.py --date 2026-03-13

# RTP Açores (no auth needed)
python3 scrapers/rtp.py --date 2026-03-13
```

Both default to yesterday's date. See `scrapers/` for output JSON schemas.

For AO scraper setup: `cp .ao_config.example .ao_config` and fill in credentials.

## How it works

GitHub Actions runs the bot daily at 00:00 UTC. It fetches new data, computes deltas against `bot/state.jsonl`, writes Jekyll markdown + JSON, summarizes the day via Claude and posts to a Telegram channel, then commits any changes.

### Telegram daily summary

After writing markdown, the bot calls Claude to produce a concise Portuguese summary of the day's government activity and posts it to Telegram. Requires three GitHub secrets: `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`. Skips gracefully if unset.
