# Açores.net

Public data about the Azores, in one place and explained: statistics by
concelho and freguesia, the Regional Government's accounts, public contracts
and the work of the Legislative Assembly. Every number links to its official
source. Site: [açores.net](https://xn--aores-yra.net/) (Jekyll, deployed to
GitHub Pages by GitHub Actions).

## Site

| Page | What it shows | Built from |
|------|---------------|------------|
| [`/`](https://xn--aores-yra.net/) | Entry points, latest updates, opinion | `docs/index.md` |
| [`/introducao/`](https://xn--aores-yra.net/introducao/) | Introdução aos dados dos Açores: islands, who decides what, the Region's money, how people live, key terms | `docs/introducao.md` + `docs/_data/resumo.json` |
| [`/tutorial/`](https://xn--aores-yra.net/tutorial/) | Tutorial for journalists: worked examples, pitfalls, a checklist before publishing | `docs/tutorial.md` (figures written in by hand, as of Nov 2026) |
| [`/dados/ine/`](https://xn--aores-yra.net/dados/ine/) | INE indicators by concelho and freguesia, vs Madeira and Portugal | `data/ine.csv` |
| [`/dados/srea/`](https://xn--aores-yra.net/dados/srea/) | Economia: prices, employment, activity, tourism, GDP by island (SREA) | `data/srea.csv` |
| [`/dados/beo/`](https://xn--aores-yra.net/dados/beo/) | Budget execution (Boletins de Execução Orçamental), month by month | `data/beo.csv` |
| [`/dados/tdc/`](https://xn--aores-yra.net/dados/tdc/) | Tribunal de Contas opinions on the Region's accounts | `data/tdc.csv`, `data/tdc_valores.csv` |
| [`/dados/`](https://xn--aores-yra.net/dados/) | Search and CSV export of contracts (BASE), Assembly records (ALRA) and Jornal Oficial acts (JORAA) | `docs/_{base,alra,joraa}_updates/` |
| [`/atualizacoes/`](https://xn--aores-yra.net/atualizacoes/), [RSS](https://xn--aores-yra.net/rsss) | What came in each day | `docs/_*_updates/`, `docs/rss/` |
| [`/blog`](https://xn--aores-yra.net/blog) | Opinion and older analyses | `docs/_posts/` |

`docs/dados/` (CSVs, SQLite with full-text search, JSON for the charts) and
`docs/_data/resumo.json` are not committed: `python3 bot/datasets.py docs`
generates them at build time.

## Sources and jobs

| Source | Command | Output | When |
|--------|---------|--------|------|
| [ALRA](http://base.alra.pt:82) (Assembly), [JORAA](https://jo.azores.gov.pt) (Jornal Oficial), [BASE](https://www.base.gov.pt) (contracts), [Portal](https://portal.azores.gov.pt) | `python -m bot` | `docs/_*_updates/`, `docs/rss/`, `bot/state.jsonl` | daily, `run-bot.yml` |
| [Açoriano Oriental](https://www.acorianooriental.pt) print edition (login) | `python -m scrapers.ao` | `docs/_ao/` | daily, `run-bot.yml` |
| [INE](https://www.ine.pt) | `python3 bot/ine.py data` | `data/ine.csv` | weekly, `ine.yml` |
| [SREA](https://srea.azores.gov.pt) | `python3 bot/srea.py data` | `data/srea.csv` | weekly, `srea.yml` |
| [Portal](https://portal.azores.gov.pt) (BEO PDFs) | `python3 bot/beo.py data` | `data/beo.csv` | weekly, `beo.yml` |
| [Tribunal de Contas](https://www.tcontas.pt) | `python3 bot/tdc.py data` | `data/tdc.csv`, `data/tdc_valores.csv` | weekly, `tdc.yml` |
| all of the above | `python3 bot/datasets.py docs` | `docs/dados/`, `docs/_data/` | every deploy, `pages.yml` |

Requests to `*.azores.gov.pt` (JORAA, Portal, SREA) go through `bot/gov.py`:
a fixed User-Agent and a pace agreed with the Regional Government's network
team. Don't parallelise them or change the User-Agent.

[`CLAUDE.md`](CLAUDE.md) has the details of each script: formats, quirks of
each source, and what to do when one breaks.

## Development

Python ≥ 3.11.5 (CI uses 3.13), with [Poetry](https://python-poetry.org):

```bash
poetry install --with dev
poetry run pytest bot/tests/ scrapers/tests/   # offline; add -m network for live tests
poetry run ruff check bot/ scrapers/
poetry run black --check bot/ scrapers/
```

The weekly scripts run on their own with a few extra packages: `pypdf` (BEO,
TdC), `openpyxl` and `xlrd` (SREA); the INE script needs only the standard
library.

To preview the site (needs Ruby and Bundler):

```bash
python3 bot/datasets.py docs
cd docs && bundle install && bundle exec jekyll serve
```

The AO scraper needs a login: `cp .ao_config.example .ao_config` and fill it
in.
