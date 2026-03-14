# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Açores.net is a civic information platform for the Azores. A Python bot scrapes government and legislative data daily from four sources, converts it to Jekyll-compatible markdown, and publishes it as a static site. GitHub Actions runs the bot on a daily cron schedule.

## Commands

```bash
# Install dependencies
poetry install

# Run the bot (full daily pipeline)
poetry run python -m bot

# Run tests (network-dependent)
poetry run pytest bot/tests/

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
fetch_web_data() → compute_delta_ids() → write_update() → write_daily_json() → append_state()
```

1. **Fetch** (`fetch.py`) — Scrapes/calls APIs for all four data sources
2. **Delta** (`state.py`, `utils.py`) — Compares fetched IDs against `state.jsonl` to find new/changed items
3. **Export** (`export.py`, `record.py`) — Converts records to Jekyll markdown with frontmatter
4. **JSON feed** (`daily_json.py`) — Writes structured JSON to `docs/_data/daily/YYYY-MM-DD.json`
5. **State** (`utils.py`) — Appends current run's state to `state.jsonl` (auto-rotated at 60 lines)

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

## Key Details

- **State file:** `bot/state.jsonl` is an append-only ledger (~12 MB, committed). Each line is one bot run's full state. Delta computation depends on the last entry.
- **CI/CD:** `.github/workflows/run-bot.yml` runs daily at 00:00 UTC, commits as `fmesqg-auto` if changes exist.
- **Code style:** black (line-length 79), isort (black profile), Python >=3.11.
- **Tests:** `pytest bot/tests/` runs offline by default. Network-dependent tests are marked `@pytest.mark.network` and skipped unless opted in with `-m network`.
- **Content language:** Portuguese (Azores region).
