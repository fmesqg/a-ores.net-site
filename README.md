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
| [`/tutorial/`](https://xn--aores-yra.net/tutorial/) | Guide for journalists: worked examples and what is particular to each source (no generic journalism advice) | `docs/tutorial.md` (figures written in by hand, as of Nov 2026) |
| [`/financas/`](https://xn--aores-yra.net/financas/) | Finanças: the Region's deficit, debt and money left out of the Conta; entry to BEO and TdC | `docs/financas.md` + `docs/_data/resumo.json` |
| [`/dados/ine/`](https://xn--aores-yra.net/dados/ine/) | INE indicators by concelho and freguesia, vs Madeira and Portugal | `data/ine.csv` |
| [`/economia/`](https://xn--aores-yra.net/economia/) | Economia, split into public and private sector: jobs in government, public companies, largest companies, the public/private share of jobs, and GDP, inflation and unemployment | `docs/economia.md` + `docs/_data/` |
| [`/financas/camaras/`](https://xn--aores-yra.net/financas/camaras/) | The 19 câmaras municipais per inhabitant (INE spending ÷ population), next to income, tourism, RSI and the câmara's BASE contracts for the same concelho | `data/ine.csv`, BASE; built into `docs/_data/camaras.json` |
| [`/economia/setor-publico/`](https://xn--aores-yra.net/economia/setor-publico/) | Public sector jobs in the Azores (Region, State, municipalities) by career and regional department, since 2011, and pay (DGAEP, SIOE) | `data/emprego_publico.csv` |
| [`/dados/srea/`](https://xn--aores-yra.net/dados/srea/) | Indicators (menu "Estatísticas", next to the INE page): prices, employment by sector, activity, tourism, GDP by island (SREA) | `data/srea.csv` |
| [`/dados/sper/`](https://xn--aores-yra.net/dados/sper/) | Regional public companies (SATA, EDA, hospitals...), company by company, and the Region's net financial effort (CFP) | `data/sper*.csv` |
| [`/dados/maiores-empresas/`](https://xn--aores-yra.net/dados/maiores-empresas/) | The 200 largest companies with head office in the Azores, by sector and island | `data/maiores_2024.csv` |
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
| [Conselho das Finanças Públicas](https://www.cfp.pt/pt/publicacoes/sectores-das-administracoes-publicas) | `python3 bot/cfp.py data` | `data/sper.csv`, `data/sper_empresas.csv`, `data/sper_regiao.csv` | weekly, `cfp.yml` |
| [DGAEP, Síntese Estatística do Emprego Público](https://www.dgaep.gov.pt/index.cfm?OBJID=ECA5D4CB-42B8-4692-A96C-8AAD63010A54) | `python3 bot/dgaep.py data` | `data/emprego_publico.csv` | weekly, `dgaep.yml` |
| 100 Maiores Empresas dos Açores (Açoriano Oriental, yearly magazine) | entered by hand from the magazine | `data/maiores_<ano>.csv` | once a year |
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
