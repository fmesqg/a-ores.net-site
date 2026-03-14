# Açores.net

Civic information bot for the Azores — scrapes government and legislative data daily and publishes it as a Jekyll static site.

## Data sources

| Source | Content |
|--------|---------|
| [ALRA](http://base.alra.pt:82) | Parliamentary records (questions, votes, proposals) |
| [JORAA](https://jo.azores.gov.pt) | Government journal acts |
| [BASE](https://www.base.gov.pt) | Public procurement contracts |
| [Portal](https://portal.azores.gov.pt) | Government portal documents |

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

## How it works

GitHub Actions runs the bot daily at 00:00 UTC. It fetches new data, computes deltas against `bot/state.jsonl`, writes Jekyll markdown + JSON, and commits any changes.
