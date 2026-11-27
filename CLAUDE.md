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
python3 -m scrapers.ao --date 2026-03-13    # requires .ao_config
python3 scrapers/rtp.py --date 2026-03-13   # no auth needed

# Run tests (network-dependent)
poetry run pytest bot/tests/ scrapers/tests/

# Format code
poetry run black .
poetry run isort .
```

Jekyll site (requires Ruby/Jekyll installed separately):
```bash
python3 bot/datasets.py docs   # generate docs/dados/ first (gitignored)
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

### Open datasets (`bot/datasets.py`)

Stdlib-only script, run as `python3 bot/datasets.py docs` (not `-m bot.datasets`, because `bot/__init__.py` imports the whole bot). It re-parses every `docs/_base_updates/`, `_alra_updates/` and `_joraa_updates/` page (all share the `* [title](url)` + `  * key: value` shape) and writes cumulative `docs/dados/{base,alra,joraa}.csv` (UTF-8 with BOM), `acores.db` (SQLite, typed, FTS5 `<table>_fts` with `content=[table]` so Datasette shows a search box) and `meta.json`. `docs/dados/` is gitignored: `.github/workflows/pages.yml` generates it and deploys the site (Pages source = GitHub Actions); the daily run calls that workflow after committing. BASE is deduplicated by contract id, ALRA by record URL (keeping first/last day seen and the last state), JORAA by act URL. `docs/dados.md` (`/dados/`) is a client-side search page over those CSVs: no libraries, state in the URL hash, filtered CSV export. It uses `layout: default`, because the repo's `page` layout chains to a `base.html` without `<head>`.

### INE indicators (`bot/ine.py`)

Stdlib-only, `python3 bot/ine.py data` (network, ~6 min). Fetches the curated `INDICATORS` list from the public INE API (`pindica.jsp?op=2&varcd=…&Dim1=T&Dim2=<*>20`: all periods, everything inside NUTS 20 = Azores region, concelhos, freguesias) plus `pindicaMeta.jsp` for unit and update date, and writes one long table `data/ine.csv` (committed). Extra dimensions are collapsed to their total ("HM", "Total…"); dimensions without one (quintiles) stay, described in `categoria`. NUTS III `200` duplicates NUTS II `20` and is dropped. Indicators keyed on the administrative division (concelho `4203`) reject `<*>20`; they are fetched whole and renamed to NUTS codes (`2004203`). INE returns 429 to parallel requests: keep one request per second. If more than half the indicators fail, the old CSV is kept. `python3 bot/ine.py procurar <termos>` searches INE's catalogue (`xml_indic.jsp?opc=2`) for regional indicators (`*` = already in the list). `.github/workflows/ine.yml` runs it weekly and redeploys Pages if the CSV changed; `bot/datasets.py` copies it to `docs/dados/ine.csv` and adds the `ine` table (+ `ine_fts`) to `acores.db`. Indicators are grouped in `THEMES` (the `tema` column); the CSV keeps that order, which is the order of the indicator list on `docs/ine.md` (`/dados/ine/`): one indicator at a time, pivoted to places × periods, with the Azores row as reference. `/dados/` (search over BASE/ALRA/JORAA) only links to it. INE suppresses small cells: medians/Gini/P90-P10 exist only for ~22 larger freguesias; NUTS 2024 concelho series start in 2021.

### Budget execution (`bot/beo.py`)

`python3 bot/beo.py data` (needs `pypdf`) adds new Boletins de Execução Orçamental to `data/beo.csv` (committed); `--tudo` re-downloads and re-parses all (~33 PDFs, identical output). The portal's listing page is behind Cloudflare since mid-2026, but the PDFs are not and follow `documents/36626/<FOLDERS[year]>/BEO_<ano>_<mm>_<Mês>+<ano>.pdf` (exceptions in `FILENAMES`). A new year needs its folder id in `FOLDERS`, copied from a January link in a browser; until then `main()` exits 1 after `STALE_DAYS`, so `.github/workflows/beo.yml` (weekly) fails and emails. Parsed: Quadro I (subsectors), III–V (amount + % of budget; their previous-year column fills 2023), VI (by function), VII (departments: names in the header before 2025, codes after; mapped by `DEPARTAMENTOS`). Values are year-to-date. Rubricas are matched across years by `key()` (COFOG code, bracketed acronym, else the folded label without spaces and "s", because Dec 2024's PDF text splits words after each "s"); labels and order come from the latest boletim. `docs/beo.md` (`/dados/beo/`) is the INE page's pivot/chart adapted: rows = rubricas or subsectors/departments, acumulado/mensal, "ano a ano" chart. The daily bot's `fetch_beo_all` uses the same addresses for the Portal RSS; SIGICA pages are blocked (403) and logged as errors.

### Tribunal de Contas (`bot/tdc.py`)

`python3 bot/tdc.py data` (needs `pypdf`) looks for the Parecer sobre a Conta da Região Autónoma dos Açores of each year from `FIRST` (2023) and adds new ones to `data/tdc.csv` (text: `juízo`, `reserva`, `ênfase`, `recomendação`) and `data/tdc_valores.csv` (figures), both committed; `--tudo` redoes all (~14 MB PDFs, slow server). The PDF links come from the year's page `detalhe.aspx?dset=<ano>` (plain HTML; file names change every year). Only the current layout (2023+) is parsed; older pareceres differ (2022: prose verdict; 2021: verdict at the end; 2023 has its account table and Apêndice I as images). Parsing: verdict section up to "Sumário" (bullets "•"; the LOPTC footnote is stripped); recommendations between "entende reiterar …" and "Decisão", split on their "Ponto … §§ …" references (2023 has no visible ordinals; elsewhere they break over lines, `ordinal_fix`); Apêndice I statuses matched with whitespace removed, linked to the previous year's recommendations by `key()` (letters only, "sector" = "setor"); the "Conta do sector público administrativo regional" table (two years per parecer, the later parecer wins); debt, unrecorded revenue/expenditure and solidarity transfers by regex from the verdict text. `.github/workflows/tdc.yml` runs weekly (one request while nothing is new) and fails if the parecer on the account of two years ago is missing. `docs/tdc.md` (`/dados/tdc/`): figures table + one-row bar chart, verdict per year, recommendations × parecer status.

### SREA series (`bot/srea.py`)

`python3 bot/srea.py data` (needs `openpyxl` and `xlrd`) updates `data/srea.csv` (committed) from the Excel files of srea.azores.gov.pt (Serviço Regional de Estatística dos Açores): IPC (inflation), IAE and ICP (monthly activity and consumption), unemployment rate (Inquérito ao Emprego, Quadro 10), nights by island (hotels and alojamento local), GDP and population by island, and `pib_hab` computed from them. Each edition is a new upload with a changing name, so `SERIES` finds each file by a regex among the links of its area page (`/area/<slug>/`); a failed series makes `main()` return 1 (`.github/workflows/srea.yml`, weekly, still commits the others and then fails). Unemployment and nights files only hold the last quarters/two years, so history accumulates in the CSV (newer rows win by `KEY`). The "relatório" pages open a Reporting Services server behind Cloudflare: don't use it. `bot/datasets.py` writes `docs/dados/srea.json` (charts) and `resumo.srea` (numbers) for `docs/srea.md` (`/dados/srea/`, "Economia") and `/acores-101/`.

JORAA has failed every day since 2026-08-11: jo.azores.gov.pt answers the API with a Cloudflare challenge (403 HTML), which `fetch_day_joraa` then fails to parse as JSON.

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

Minima theme. Five auto-generated collections (`_alra_updates/`, `_joraa_updates/`, `_base_updates/`, `_portal_updates/` from the bot; `_ao/` from the AO scraper) plus manual blog posts in `_posts/`. Structured JSON feed in `_data/daily/` (not used by any template).

### News Scrapers (`scrapers/`)

Standalone scripts, not part of the bot pipeline. Run manually or via cron.

**`scrapers/ao.py`** — Açoriano Oriental print edition:
- Two-phase: (1) scrape print section pages for metadata, (2) match to online `/noticia/` URLs for full body text.
- Requires login. Credentials in `.ao_config` (repo root, gitignored). Template: `.ao_config.example`.
- Scrapes every section the edition lists. `DEFAULT_EXCLUDE` is empty; `.ao_config` can still narrow it via `include`/`exclude`.
- Title-to-URL matching uses slugification with exact/substring/partial strategies (~60-80% match rate).
- Page/feed output is delegated to `scrapers/ao_pages.py` (see below). Articles with no body or excerpt are excluded.
- Must be run as a module (`python3 -m scrapers.ao`) because it imports `scrapers.ao_pages`.

**`scrapers/rtp.py`** — RTP Açores via WordPress REST API:
- Single-phase: `GET /wp-json/wp/v2/posts/` with date filtering and `_embed`.
- No auth required. Paginates automatically.
- Author names unavailable (user endpoint returns 401).

**Output:** `scrapers/output/{prefix}{date}.json` and `.md`. AO uses `{date}.*`, RTP uses `rtp-{date}.*`.

**Key schema differences:**
- AO: string IDs, `section` (slug), has `page`/`author` fields
- RTP: integer IDs, `category` (display name), no `page`/`author`

**`scrapers/ao_pages.py`** — Jekyll pages + daily RSS for the AO print edition:
- `docs/rss/ao.xml` carries **one item per edition day**; its body is a link list grouped by newspaper section (title + page + author). Retention: `FEED_RETENTION_DAYS` = 90 items.
- Each article gets a page at `docs/_ao/YYYYMMDD-NN.md` → `/ao/YYYYMMDD-NN/`, numbered from `-01` in the print edition's own section order. Each day also gets an index page `docs/_ao/YYYYMMDD.md` → `/ao/YYYYMMDD/`.
- Article bodies are written as escaped `<p>` blocks, not markdown, because print text contains `*`, `_`, `#`, `[`.
- Re-running a date is idempotent: stale `YYYYMMDD-*.md` files are deleted and the day's feed item is replaced.
- Pages carry `noindex: true` (via the `ao` defaults in `docs/_config.yml` → `_includes/custom-head.html`) and `docs/robots.txt` disallows `/ao/`, since they host paywalled print text.
- Ordering: sections by their lowest page number, articles by page within each section, ties keeping the print edition's order — so slug `-01` is the front of the paper. Articles with no page sort last.
- Front-page teasers (`page` in `FRONT_PAGE_NUMBERS` = `{"0", "1"}`) are dropped: they are reworded one-line blurbs for articles that run inside. Page `0` is the lead story, whose card omits the `Pág. N` marker.
- `scrapers/repair_ao_pages.py` re-derives backfilled editions: it re-reads the section index pages to recover page numbers and any section missing from disk, then regenerates. `--no-fetch` regenerates from disk alone (use after changing ordering or filter rules); `--dry-run` reports without writing.

## Key Details

- **State file:** `bot/state.jsonl` is an append-only ledger (~12 MB, committed). Each line is one bot run's full state. Delta computation depends on the last entry.
- **Deploy:** `.github/workflows/pages.yml` builds Jekyll with `actions/jekyll-build-pages` and deploys on push to main, on manual dispatch and when called by the daily run.
- **CI/CD:** `.github/workflows/run-bot.yml` runs daily at 00:00 UTC, commits as `fmesqg-auto` if changes exist.
- **Code style:** black (line-length 79), isort (black profile), Python >=3.11.5. Pre-commit hooks configured (black, isort, ruff) via `.pre-commit-config.yaml` at repo root — run `pre-commit install` from root.
- **Tests:** `pytest bot/tests/` runs offline by default. Network-dependent tests are marked `@pytest.mark.network` and skipped unless opted in with `-m network`.
- **Content language:** Portuguese (Azores region).
