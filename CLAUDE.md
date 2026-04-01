# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Açores.net is a civic information platform for the Azores. Two subsystems:

1. **Bot pipeline** (`bot/`) — Scrapes government and legislative data daily from four sources, converts to Jekyll markdown, publishes as a static site via GitHub Actions.
2. **News scrapers** (`scrapers/`) — Standalone scrapers for Azorean news (AO print edition, RTP Açores). Output structured JSON + Markdown for downstream use.

## Commands

```bash
# Install dependencies
poetry install

# Run the bot (full daily pipeline)
poetry run python -m bot

# Run news scrapers (standalone, default: yesterday)
python3 scrapers/ao.py --date 2026-03-13    # requires .ao_config
python3 scrapers/rtp.py --date 2026-03-13   # no auth needed

# Run tests (network-dependent)
poetry run pytest bot/tests/ scrapers/tests/

# Format code
poetry run black .
poetry run isort .
```

Jekyll site (requires Ruby/Jekyll installed separately):
```bash
cd docs && bundle exec jekyll serve
```

## Architecture

### Bot Pipeline (`bot/`)

Entry point: `bot/__main__.py`

```
fetch_web_data() → compute_delta_ids() → write_update() → write_daily_json() → summarize_and_post() → append_state()
```

1. **Fetch** (`fetch.py`) — Scrapes/calls APIs for all four data sources
2. **Delta** (`state.py`, `utils.py`) — Compares fetched IDs against `state.jsonl` to find new/changed items
3. **Export** (`export.py`, `record.py`) — Converts records to Jekyll markdown with frontmatter
4. **JSON feed** (`daily_json.py`) — Writes structured JSON to `docs/_data/daily/YYYY-MM-DD.json`
5. **Summarize** (`summarize.py`) — Reads the day's markdown files, calls Claude to produce a concise Portuguese summary, posts to Telegram. Skips gracefully if API keys are unset.
6. **State** (`utils.py`) — Appends current run's state to `state.jsonl` (auto-rotated at 60 lines)

### Data Sources

| Source | Domain | Content |
|--------|--------|---------|
| ALRA | base.alra.pt:82 | Parliamentary records (questions, votes, proposals) |
| JORAA | jo.azores.gov.pt | Government journal acts, spending |
| BASE | base.gov.pt | Public procurement contracts |
| Portal | portal.azores.gov.pt | Government portal documents |

### Record Types (`record.py`)

Abstract `Record` base class with subclasses: `Requerimento`, `Iniciativa`, `Voto`, `Diario`, `Interven`, `Peti`, `Info`, `AudiARep`, `AudiGRep`. Each implements `to_markdown()` and `to_dict()` (structured JSON serialization).

### Jekyll Site (`docs/`)

Minima theme. Four auto-generated collections (`_alra_updates/`, `_joraa_updates/`, `_base_updates/`, `_portal_updates/`) plus manual blog posts in `_posts/`. Structured JSON feed in `_data/daily/`.

### News Scrapers (`scrapers/`)

Standalone scripts, not part of the bot pipeline. Run manually or via cron.

**`scrapers/ao.py`** — Açoriano Oriental print edition:
- Two-phase: (1) scrape print section pages for metadata, (2) match to online `/noticia/` URLs for full body text.
- Requires login. Credentials in `.ao_config` (repo root, gitignored). Template: `.ao_config.example`.
- Config can filter sections via `include`/`exclude`; defaults to all when empty.
- Title-to-URL matching uses slugification with exact/substring/partial strategies (~60-80% match rate).
- RSS feed (`docs/rss/ao.xml`) excludes articles with no body or excerpt.

**`scrapers/rtp.py`** — RTP Açores via WordPress REST API:
- Single-phase: `GET /wp-json/wp/v2/posts/` with date filtering and `_embed`.
- No auth required. Paginates automatically.
- Author names unavailable (user endpoint returns 401).

**Output:** `scrapers/output/{prefix}{date}.json` and `.md`. AO uses `{date}.*`, RTP uses `rtp-{date}.*`.

**Key schema differences:**
- AO: string IDs, `section` (slug), has `page`/`author` fields
- RTP: integer IDs, `category` (display name), no `page`/`author`

**`bot/tgbot.py`** — Interactive Telegram bot (not part of the daily pipeline):
- Handles on-demand slash commands: `/ao`, `/al`, `/jo`, `/base`.
- Runs as a separate long-lived process, not invoked by `bot/__main__.py`.

## Key Details

- **State file:** `bot/state.jsonl` is an append-only ledger (~12 MB, committed). Each line is one bot run's full state. Delta computation depends on the last entry.
- **CI/CD:** `.github/workflows/run-bot.yml` runs daily at 00:00 UTC, commits as `fmesqg-auto` if changes exist. Passes `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` as env vars for the summary step.
- **Telegram summary:** `summarize.py` sends one daily message to a Telegram channel. Currently covers the 4 government sources only (not news scrapers). Model configurable via `ANTHROPIC_MODEL` env var (default: `claude-haiku-4-5-20251001`).
- **Code style:** black (line-length 79), isort (black profile), Python >=3.11. Pre-commit hooks configured (black, isort, ruff) via `.pre-commit-config.yaml` at repo root — run `pre-commit install` from root.
- **Tests:** `pytest bot/tests/` runs offline by default. Network-dependent tests are marked `@pytest.mark.network` and skipped unless opted in with `-m network`.
- **Content language:** Portuguese (Azores region).
- **RSS feeds:** Existing RSS/Jekyll output must not be affected by summary changes. The Telegram summary is a separate output channel.
