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
fetch_web_data() → compute_delta_ids() → write_update() → append_state()
```

1. **Fetch** (`fetch.py`) — Scrapes/calls APIs for all four data sources
2. **Delta** (`state.py`, `utils.py`) — Compares fetched IDs against `state.json` to find new/changed items
3. **Export** (`export.py`, `record.py`) — Converts records to Jekyll markdown with frontmatter
4. **State** (`utils.py`) — Writes the run's state to `state.json`, replacing the previous one

### Open datasets (`bot/datasets.py`)

Stdlib-only script, run as `python3 bot/datasets.py docs` (not `-m bot.datasets`, because `bot/__init__.py` imports the whole bot). `datasets.py` only runs `main()`; the code is split by source in the package `bot/dados/` (`base`, `parlamento`, `sqlite`, `resumo`, `empresas`, `publico`, `camaras`, `impostos`, `credito`, `fundos`, shared helpers in `comum`), with relative imports. `datasets.py` imports it as `.dados` when it is `bot.datasets` (tests) and as `dados` when run as a script (bot/ is then on `sys.path`). Tests import the modules (`from bot.dados import camaras`). BASE comes only from the IMPIC open data (`data/base_impic/`, see below); the daily `_base_updates/` pages are the feed, not the dataset (5 fields per contract). ALRA and JORAA come from the archives `data/alra.csv.gz` and `data/joraa.csv.gz` plus the `docs/_alra_updates/` and `_joraa_updates/` pages still in the repo (`* [title](url)` + `  * key: value`, parsed by `parlamento.build_alra`/`build_joraa`, which take the archive rows as a starting point). `python3 bot/arquivo.py` (stdlib; a step of the daily run, after the bot) rebuilds the two archives and deletes ALRA, JORAA and BASE pages older than `MANTER` (90) days, only once every link of a page is in the archive (else exit 1, nothing deleted). JORAA keeps the lines no column takes (beneficiary…) in `outros`; ALRA keeps every "Alteração do estado" in `historico`, and a page older than a record's `ultimo_dia` does not overwrite its state. `docs/404.html` sends old day URLs (`/joraa_updates/2025-03-14/`) to `/dados/#fonte=joraa&de=…&ate=…` (BASE: the day before, since a BASE page lists the previous day's contracts). It writes cumulative `docs/dados/*.csv` (UTF-8 with BOM), one SQLite file per theme (`contratos.db`, `parlamento.db`, …; typed, FTS5 `<table>_fts` with `content=[table]` so Datasette shows a search box) and `meta.json`. `check_base` runs before anything is published: a NIF that is not 9 digits or empty is an error (exit 1, so `pages.yml` does not deploy); a stale newest contract, or an entity with 10+ contracts a year falling below a quarter of that in the last 12 months, is a `::warning::` (kept in `meta.json` → `verificacao`). `docs/dados/` is gitignored: `.github/workflows/pages.yml` generates it and deploys the site (Pages source = GitHub Actions); the daily run calls that workflow after committing. ALRA is deduplicated by record URL (keeping first/last day seen and the last state), JORAA by act URL. `docs/dados.md` (`/dados/`) is a client-side search page over those CSVs: no libraries, state in the URL hash, filtered CSV export. BASE is also written per year (`docs/dados/base/<ano>.csv`, years in `meta.json` → `base.anos`): the page loads the 3 newest years, the years a "De" date asks for, or all of them on request (`todos=1` in the hash); `base.csv` stays whole for download. It uses `layout: default`, because the repo's `page` layout chains to a `base.html` without `<head>`.

### BASE contracts (`bot/base_impic.py`)

`python3 bot/base_impic.py data` (needs `ijson`; `--cache DIR` keeps the ~0.8 GB of zips) reads the IMPIC's yearly `contratos<ano>.zip` from dados.gov.pt (every BASE contract in the country since 2012, refreshed every week or two) and rewrites `data/base_impic/<ano>.csv.gz` (committed). A contract is kept when a place of execution is in the Azores or the contracting entity is Azorean: a first pass counts, per adjudicante NIF, contracts placed in the Azores vs elsewhere ("Portugal" alone counts for neither); `MIN_AZ` 5 and `AZ_SHARE` 90 % make it Azorean. Without that rule (which is also all the daily BASE search `distrito=20` does) Vila do Porto's contracts since 2024, most of Velas' and of the Unidade de Saúde de São Miguel's are lost, because they give only "Portugal" as the place. The IMPIC writes "-" for a party with no Portuguese NIF: stored empty. `.github/workflows/base_impic.yml` runs weekly and fails if the newest contract is older than `MAX_IDADE` (30 days).

### INE indicators (`bot/ine.py`)

Stdlib-only, `python3 bot/ine.py data` (network, ~6 min). Fetches the curated `INDICATORS` list from the public INE API (`pindica.jsp?op=2&varcd=…&Dim1=T&Dim2=<*>20`: all periods, everything inside NUTS 20 = Azores region, concelhos, freguesias) plus `pindicaMeta.jsp` for unit and update date, and writes one long table `data/ine.csv` (committed). Extra dimensions are collapsed to their total ("HM", "Total…"); dimensions without one (quintiles) stay, described in `categoria`. NUTS III `200` duplicates NUTS II `20` and is dropped. Indicators keyed on the administrative division (concelho `4203`) reject `<*>20`; they are fetched whole and renamed to NUTS codes (`2004203`). Values are multiplied by `10**Potencia10` from pindicaMeta: some euro series (câmaras' receitas/despesas, tourism proveitos) come in thousands while `UnidadeMedida` still says "Euro (€)". INE returns 429 to parallel requests: keep one request per second. If more than half the indicators fail, the old CSV is kept. `python3 bot/ine.py procurar <termos>` searches INE's catalogue (`xml_indic.jsp?opc=2`) for regional indicators (`*` = already in the list). `.github/workflows/ine.yml` runs it weekly and redeploys Pages if the CSV changed; `bot/datasets.py` copies it to `docs/dados/ine.csv` and adds the `ine` table (+ `ine_fts`) to `acores.db`. `DETALHE` (câmaras' receitas 0013908 and despesas 0013909) keeps every category of the economic classifier, with the total as `categoria` "" (so code reading totals is unchanged); INE lists two receitas categories twice, labelled "(corrente)"/"(capital)" by `dupes()`. `camaras.compras_base` compares each câmara's purchases (aquisição de bens e serviços + bens de capital) with the BASE contracts it published in the same year, per year and over the last three (`/financas/camaras/#compras`). Indicators are grouped in `THEMES` (the `tema` column); the CSV keeps that order, which is the order of the indicator list on `docs/ine.md` (`/dados/ine/`): one indicator at a time, pivoted to places × periods, with the Azores row as reference. `/dados/` (search over BASE/ALRA/JORAA) only links to it. INE suppresses small cells: medians/Gini/P90-P10 exist only for ~22 larger freguesias; NUTS 2024 concelho series start in 2021.

### Budget execution (`bot/beo.py`)

`python3 bot/beo.py data` (needs `pypdf`) adds new Boletins de Execução Orçamental to `data/beo.csv` (committed); `--tudo` re-downloads and re-parses all (~33 PDFs, identical output). The portal's listing page is behind Cloudflare since mid-2026, but the PDFs are not and follow `documents/36626/<FOLDERS[year]>/BEO_<ano>_<mm>_<Mês>+<ano>.pdf` (exceptions in `FILENAMES`). A new year needs its folder id in `FOLDERS`, copied from a January link in a browser; until then `main()` exits 1 after `STALE_DAYS`, so `.github/workflows/beo.yml` (weekly) fails and emails. Parsed: Quadro I (subsectors), III–V (amount + % of budget; their previous-year column fills 2023), VI (by function), VII (departments: names in the header before 2025, codes after; mapped by `DEPARTAMENTOS`). Values are year-to-date. Rubricas are matched across years by `key()` (COFOG code, bracketed acronym, else the folded label without spaces and "s", because Dec 2024's PDF text splits words after each "s"); labels and order come from the latest boletim. `docs/beo.md` (`/dados/beo/`) is the INE page's pivot/chart adapted: rows = rubricas or subsectors/departments, acumulado/mensal, "ano a ano" chart. The daily bot's `fetch_beo_all` uses the same addresses for the Portal RSS; SIGICA pages are blocked (403) and logged as errors.

### Tribunal de Contas (`bot/tdc.py`)

`python3 bot/tdc.py data` (needs `pypdf`) looks for the Parecer sobre a Conta da Região Autónoma dos Açores of each year from `FIRST` (2023) and adds new ones to `data/tdc.csv` (text: `juízo`, `reserva`, `ênfase`, `recomendação`) and `data/tdc_valores.csv` (figures), both committed; `--tudo` redoes all (~14 MB PDFs, slow server). The PDF links come from the year's page `detalhe.aspx?dset=<ano>` (plain HTML; file names change every year). Only the current layout (2023+) is parsed; older pareceres differ (2022: prose verdict; 2021: verdict at the end; 2023 has its account table and Apêndice I as images). Parsing: verdict section up to "Sumário" (bullets "•"; the LOPTC footnote is stripped); recommendations between "entende reiterar …" and "Decisão", split on their "Ponto … §§ …" references (2023 has no visible ordinals; elsewhere they break over lines, `ordinal_fix`); Apêndice I statuses matched with whitespace removed, linked to the previous year's recommendations by `key()` (letters only, "sector" = "setor"); the "Conta do sector público administrativo regional" table (two years per parecer, the later parecer wins); debt, unrecorded revenue/expenditure and solidarity transfers by regex from the verdict text. `.github/workflows/tdc.yml` runs weekly (one request while nothing is new) and fails if the parecer on the account of two years ago is missing. `docs/tdc.md` (`/dados/tdc/`; with `/dados/beo/` it forms the "Finanças" section: `docs/financas.md` at `/financas/` shows `resumo.tdc` and `resumo.beo`, and `secao: financas` + `_includes/financas-nav.html` give the three pages a shared sub-nav and keep "Finanças" highlighted in the header): figures table + one-row bar chart, verdict per year, recommendations × parecer status.

### SREA series (`bot/srea.py`)

`python3 bot/srea.py data` (needs `openpyxl` and `xlrd`) updates `data/srea.csv` (committed) from the Excel files of srea.azores.gov.pt (Serviço Regional de Estatística dos Açores): IPC (inflation), IAE and ICP (monthly activity and consumption), unemployment rate (Inquérito ao Emprego, Quadro 10) and people in work (`emprego`: Quadro 4 total and Quadro 6.1 by CAE-Rev.4 sector, both read by `parse_ie` from the same file), nights by island (hotels and alojamento local), GDP and population by island, and `pib_hab` computed from them; also average pay (`remuneracoes`, RMM), bank valuations of homes by concelho (`avaliacao`), homes sold (`transacoes`), bank loans (`emprestimos`), the INE regional accounts since 1995 for every NUTS II region (`creg`; `srea.json` keeps only Açores, Madeira, Portugal and Continente) and the regional public administration's accounts in SEC terms (`apr`, shown at `/dados/srea/#contas`). The fuel file is not read: its Azores sheet disagrees with the islands' sum since 2022. Each edition is a new upload with a changing name, so `SERIES` finds each file by a regex among the links of its area page (`/area/<slug>/`); a failed series makes `main()` return 1 (`.github/workflows/srea.yml`, weekly, still commits the others and then fails). Unemployment and nights files only hold the last quarters/two years, so history accumulates in the CSV (newer rows win by `KEY`). The "relatório" pages open a Reporting Services server behind Cloudflare: don't use it. `bot/datasets.py` writes `docs/dados/srea.json` (charts) and `resumo.srea` (numbers) for `docs/srea.md` (`/dados/srea/`, in the "Estatísticas" section with `docs/ine.md`: `secao: estatisticas`, `_includes/estatisticas-nav.html`) and `/introducao/`.

### Regional public companies (`bot/cfp.py`) and largest companies

`python3 bot/cfp.py data` (needs `openpyxl`) reads the Conselho das Finanças Públicas' yearly report on the regional public business sector (report pages `sector-empresarial-[...]regional-<ano>-<ano>` on `cfp.pt/pt/publicacoes/sectores-das-administracoes-publicas`): the "fichas individuais" Excel (one sheet per company, two years) and the report's data-series Excel (`-ds.xlsx`: list of companies, weight in the economy, the Region's net financial effort). Only the Azores (SERAA, the list between the "SERAA" and "SERAM" headings) is kept. Fichas name companies differently from the list ("Atlânticoline, S.A." vs "Atlântico Line, S.A."; "HDES, E.P.E.R."), so `match()` tries exact keys before the part before " - " — otherwise "Sata - Gestão de Aeródromos" takes the key "sata" of SATA Air Açores. Table cells are read by position: the Azores columns are empty where only Madeira has a value. `data/sper.csv` merges reports (latest wins per company/year/indicator); `sper_empresas.csv` and `sper_regiao.csv` keep each report's rows, because the CFP changed method (from report 9/2025 the financial effort excludes transfers to the three hospitals: 2023 is 339,3 M€ in 13/2024 and 75,1 M€ in 9/2025). `.github/workflows/cfp.yml` runs weekly. `data/maiores_<ano>.csv` is the "100 Maiores Empresas dos Açores" ranking (200 companies, thousands of euros), typed in from the Açoriano Oriental magazine published the following December; the user decided to publish it a year after the magazine. `bot/datasets.py` writes `docs/_data/sper.json` and `maiores.json` (public companies are matched to the ranking by their full CFP name, not the sigla). Pages: `docs/economia.md` (`/economia/`, menu "Economia", split into setor público / setor privado), `docs/setor_publico.md` (`/economia/setor-publico/`), `docs/sper.md` (`/dados/sper/`), `docs/maiores.md` (`/dados/maiores-empresas/`), sharing `secao: economia` and `_includes/economia-nav.html` (grouped: público, privado).

### Public employment (`bot/dgaep.py`)

`python3 bot/dgaep.py data` (needs `openpyxl`) rewrites `data/emprego_publico.csv` from the newest Excel of the DGAEP's quarterly Síntese Estatística do Emprego Público (SIOE data; each file carries the series since 2011, so the CSV is replaced, not merged): Q1.1 (Azores regional administration by department, plus Madeira and all of general government), Q1.7 (general government located in the Azores by career; the NUTS split is approximate, PSP/GNR are counted at their Lisbon HQ), Q1.9 and Q1.13 (pay). Headers are found by content ("EMPREGO", "R.A. DOS AÇORES", the pay block titles); variation columns (VT/VH) are skipped. In Q1.1 the row "dos quais: SER - Entid. Reclassif." (hospitals EPE) is additive to the departments: departments + it = the total. `bot/datasets.py` writes `docs/_data/publico.json`; its `peso` (public share of jobs) adds the CFP market companies (`ap` false) to Q1.7 and divides by SREA's employed population: an estimate, labelled as such on the page. `.github/workflows/dgaep.yml` runs weekly.

### Municipal accounts, debt and payment time (`bot/dgal.py`)

`python3 bot/dgal.py data` (needs `openpyxl` and `pypdf`; `--cache DIR` keeps the ~40 files) reads three pages of the DGAL's Portal Autárquico (`portalautarquico.dgal.gov.pt`, plain HTML, one request per second) and rewrites, for the 19 Azorean câmaras: `data/dgal_contas.csv.gz` (contas de gerência since 2020, SNC-AP: receita cobrada and despesa paga by economic code, balanço, demonstração de resultados; one xlsx per map and year, one row per município and one column per code; long table `ano, geocod, municipio, mapa, codigo, descricao, tipo, valor`, zeros dropped), `data/dgal_divida.csv` (debt against the legal limit of art. 52.º Lei 73/2013, one PDF a year since 2014) and `data/dgal_pmp.csv` (prazo médio de pagamentos, quarterly from the yearly PDF of all municipalities; the quarterly PDFs list only those above 60 days; a newer file wins for a repeated date). All committed. File URLs all say `filetype=pdf`; the real type is in Content-Disposition, and each account map comes as xlsx then an ods copy (the first is used). Pre-2020 accounts (POCAL, other classifier) are not read. Year tabs are `<div class="titleBlue">`. The debt PDFs write thousands with spaces ("42 534 483 15 942 648…"): `numbers()` tries every split and keeps the one where (5) = (2) − (3) − (4); 2014 uses dots. A câmara marked `**` sent no validated accounts that year (Praia da Vitória 2020–21, Angra 2021) and has no row. DGAL names map to INE geocodes in `MUNICIPIOS` ("LAGOA (SÃO MIGUEL)" → `2004201`). INE's câmaras receitas/despesas (0013908/9) are these same accounts (despesa matches to the euro). `.github/workflows/dgal.yml` runs weekly and fails if a table changes layout, a câmara is missing from the newest debt or accounts year, or the newest accounts are over two years old. It also writes `data/dgal_transferencias.csv` from the transfers page (only the current OE is posted, so older years are kept): Mapa 12 (FEF, FSM, IRS, IVA, excedente; amounts with cents, so rows split cleanly) and the "Variáveis" PDF, whose IRS column is what the câmara would get at the full 5 %; `irs_pct` = 5 × Mapa 12 IRS / that. Variáveis rows are read from the end: the last number is the IVA share (known from Mapa 12) and the IVA OE/24 column before the IRS is a lone `0` in the Azores. `bot/datasets.py` copies these to `docs/dados/` and `financas.db`; `camaras.divida_pmp` writes `camaras.json` → `divida` for `/financas/camaras/#divida`, and `camaras.contas_camaras` writes → `financas` for `#autonomia` (transfers share of revenue without loans or the previous balance, staff + interest over current revenue, investment per inhabitant), `#impostos` (derrama, IRS share, IMI per inhabitant) and `#orcamento`.

The DGAL does not publish budgets. `python3 bot/anuario.py data [--pdf FILE]` reads the Anuário Financeiro dos Municípios Portugueses (OCC/IPCA; one PDF a year, out in November; occ.pt does not link it in its HTML, so each edition's URL goes in `EDICOES` by hand): Quadro 2.6 (revenue collected / corrected budget, 11 years) and R66 (revenue assessed and expenditure committed / budget, 3 years) → `data/anuario_execucao.csv`, a newer edition winning per year. Tables are found by title (the second occurrence, after the list of tables) and fail unless all 19 câmaras are read. No workflow: run it when a new edition comes out. `data/derrama_municipal.csv` (derrama rates per câmara, AT Ofício Circulado of each July, p. 16) is typed in by hand: the PDF's text layer is scrambled. IMI rates per câmara are only in the Portal das Finanças behind login.

### CAP payments (`bot/ifap.py`)

`python3 bot/ifap.py data` (stdlib) reads the IFAP's yearly list of CAP beneficiaries (EU Reg. 2021/2116 art. 98): `apj13.ifap.pt/idigital.consultarFundos/pub/FEAGA_FEADER_<ano>.zip` (the "Lista Completa" button of the search page; ~12 MB, Latin-1 CSV with `;`, one row per beneficiary and measure plus a "Total" row, left out). Only the two latest financial years are online (16 Oct–15 Oct; older years are a 404). Azorean rows are districts 41–49 (one per island); geocode = `200` + district + concelho (`2004203`); some years write the concelho unpadded and without its name (`CONCELHOS`). `data/ifap_pagamentos.csv` (names) is rewritten with only the years the IFAP still publishes, following the law's two-year rule; `data/ifap_resumo.csv` keeps per-year totals by concelho and measure for every year read. POSEI is the single code `VII.1` (~75 M€ a year, most of the ~130 M€); POSEI paid to operators registered outside the Azores is not counted. `MEDIDAS` holds the IFAP's Portuguese measure names (`programa()` groups them). `.github/workflows/ifap.yml` runs weekly; `bot/dados/fundos.py` → `fundos.json` → `pac` for `/financas/fundos-europeus/#pac`.

### Eurostat regional indicators (`bot/eurostat.py`)

`python3 bot/eurostat.py data` (stdlib) reads ~20 Eurostat NUTS 2 tables (JSON-stat API, one request per table with every region) into `data/eurostat.csv`: `INDICADORES` fixes every dimension but geo and time (`rows_of` raises otherwise); `REGIOES` = the Azores, the other outermost regions (PT30, ES70, FRY1–5), PT, EU27_2020 and other islands (Baleares, Córsega, Sardenha, Creta, Malta, Chipre, Åland, Islândia). The Eurostat flag is kept (`estado`: p, e, b, u…); small regions have many `u` and suppressed LFS cells (Azores youth unemployment stops in 2014); regional SILC and demography tables have no EU27 value. A failed table keeps its old rows and makes `main()` return 1 (`.github/workflows/eurostat.yml`, weekly). `bot/dados/europa.py` writes `docs/_data/eurostat.json` (latest-year tables, rendered by Jekyll, with the Azores' rank among the outermost regions) and `docs/dados/eurostat.json` (series for the chart) for `docs/eurostat.md` (`/dados/eurostat/`, in the "Estatísticas" section).

### National exams (`bot/exames.py`)

`python3 bot/exames.py data [--tudo]` (stdlib + the `mdb-export`/`mdb-tables` commands of mdbtools: `brew install mdbtools`; the workflow apt-installs it) reads the Júri Nacional de Exames' databases for the press, linked from `infoescolas.pt/bds.asp`: `enes<ano>` (secondary exams) and `eneb<ano>` (9th grade provas finais), one zipped Access file per year, every exam in the country without names. The site keeps only three years, so `data/exames.csv` accumulates; a year is re-read when its file name changes (2025's came back as `_v2`). The InfoEscolas xlsx files are mainland-only; the exam databases include the Azores as district 19 with JNE concelho codes (`CONCELHOS` → INE geocodes). Counting follows the press rankings: 1st phase, internal students, exams for approval (secondary) / Português and Matemática by the school attended, `EscolaOrigem` (9th grade). Rows: each Azorean school plus regions AZ/MD/CO/PT (abroad left out); exam `todos` pools them and carries the school's national `posicao` among schools with ≥ `MIN_PROVAS` (50). `SALTAR` lists files that cannot be counted this way (2023 secondary: `Interno` is "N" on every row). The number of exams counted for approval changes with the rules (2024 has less than half of 2025's). `.github/workflows/exames.yml` runs weekly; `bot/dados/educacao.py` → `docs/_data/exames.json` → `docs/exames.md` (`/dados/exames/`, "Estatísticas" section).

### Registered unemployment (`bot/desemprego.py`)

`python3 bot/desemprego.py data [--tudo]` (needs `pypdf`) reads the monthly "Resumo - Desemprego registado nos Açores" PDFs of the Direção Regional de Qualificação Profissional e Emprego (registered unemployed by island and concelho, men/women/total; people in employability measures; placements by island; job offers) into `data/desemprego.csv` (committed, accumulates). The Azores run their own employment services, so the IEFP's concelho statistics are mainland-only. Files live on `emprego.azores.gov.pt/wp-content/uploads/` (until April 2024 also `portal.azores.gov.pt/documents/36557/`): the files answer 200, but the sites' pages and the WordPress API (`/wp-json/`) get the Cloudflare challenge, so nothing can be listed. `CONHECIDOS` holds the addresses found through search engines (Aug 2022–May 2026, with gaps); each run then tries `candidatos()` for the months after the newest known (`02_DESEMPREGO_REGISTADO_<MÊS>_<ano>.pdf` in the next month's upload folder first, at most `MAX_PEDIDOS` requests). When the newest month is older than `MAX_IDADE` days the run fails: find the file in a search engine and add it to `CONHECIDOS`. Every request uses `gov.UA`/`gov.wait()` on the shared clock, and `.github/workflows/desemprego.yml` (weekly, off-peak) is in the `azores-gov` concurrency group. Parsing checks men + women = total and that islands and concelhos add up to the region; the PDF's island table sometimes disagrees with its concelhos (every 2026 summary: Graciosa ~150 vs Santa Cruz da Graciosa ~46; Calheta jumps from ~35 to ~100 in Jan 2026, neither table follows 2025) while both add up to the region, so island rows are the sum of their concelhos (a `::warning::` when they differ). `bot/dados/emprego.py` → `docs/_data/desemprego.json` (per 1000 residents from INE 0012918, RSI per 1000 from 0013420) → `docs/desemprego.md` (`/dados/desemprego/`, "Estatísticas" section).

### Azores government sites (`bot/gov.py`)

Every request to `*.azores.gov.pt` (JORAA API, portal BEO/SIGICA in `fetch.py`, `beo.py`, `srea.py`, `desemprego.py`) sends `gov.UA` and calls `gov.wait()` first. Those sites are behind Cloudflare; the government's network team whitelists that User-Agent on condition of ≤20 requests/hour from 07:00 to 20:00 (Azores time) and ≥20 s between requests otherwise. Never parallelise these requests or change the UA without telling them. The workflows that call them (except SREA's) share the `azores-gov` concurrency group, so they queue instead of overlapping. JORAA was blocked (403 challenge) from 2026-08-11 until 2026-11-27. That day the government team added a firewall exception that matches host `jo.azores.gov.pt`, a path starting with `/api/public/` and exactly `gov.UA`; any other path or UA is blocked again. JORAA moves to a new platform in the first half of January 2027: check the runs then, and tell the team if the API changes. `fetch.joraa_plan` puts the newest days first (at most `JORAA_RECENT` = 3, oldest first, so `last_joraa_update` can move up to the last one done). Any older missing day goes into the `joraa_backfill` range in `state.jsonl`, which is worked from its newest day down with what is left of `JORAA_BUDGET` (3 h ≈ 15 days a night; one search plus one request per act, for `textoIntegral`). `State.get_updated_state` shrinks the range. While it is not empty, `datasets.write_joraa_estado` writes `docs/_data/joraa_estado.json`, and `_includes/joraa-atraso.html` shows the note on `/joraa_updates`, `/atualizacoes/`, `/dados/` and the guide. GitHub starts the daily run 4.5-9.5 h late, so its cron (19:31 UTC) is set to land after midnight UTC and outside the peak hours; at peak JORAA gets about one day of acts per run. The act's text is in `considerandos` and `normativos` (no `textoIntegral` since 2026; `anexos` are separate files, not read). `utils.joraa_amount` writes "Montante: 1 234,56 € (kind)" (base price of a procurement notice, sum of a list of grants, else the largest amount of the clauses without instalments or project cost); JORAA and BASE item lines start with the amount (`utils.item_line`: "* 1 234 € · [title](url)", whole euros; the exact value stays in its sub-bullet, which the datasets read, and `comum.ITEM` accepts both forms) and a day is sorted by it, largest first; `/dados/` defaults to newest day first, largest amount first within a day; pages before 28/11/2026 have "Soma dos montantes" (every amount added up), which `datasets.joraa_montante` labels in the `montante_tipo` column.

### Data Sources

| Source | Domain | Content |
|--------|--------|---------|
| ALRA | base.alra.pt:82 | Parliamentary records (questions, votes, proposals) |
| JORAA | jo.azores.gov.pt | Government journal acts, spending |
| BASE | base.gov.pt | Public procurement contracts |
| Portal | portal.azores.gov.pt | Government portal documents |

### Record Types (`record.py`)

Abstract `Record` base class with subclasses: `Requerimento`, `Iniciativa`, `Voto`, `Diario`, `Interven`, `Peti`, `Info`, `AudiARep`, `AudiGRep`. Each implements `to_markdown()`.

### Jekyll Site (`docs/`)

Minima theme, skin "solarized" (light/dark by the reader's system). `docs/assets/site.css` (linked from `_includes/custom-head.html`) holds the styles shared by several pages (cards `.numero`, tables `table.sper`, `.secao-nav`, chart classes) and the Solarized tones as variables (`--s03` … `--s3`), swapped in dark mode: write `var(--s01)`, not `#586e75`, in page styles; text on an accent background is `var(--sobre-acento)`. A page's own `<style>` keeps only what is specific to it; a page's `@media (prefers-color-scheme: dark)` block is for literal dark-mode colours (its variables are already swapped). On narrow screens `table.sper` inside `.tabela-scroll` gets smaller type and a sticky first column. The homepage has a "Casos" section (`/casos/eda-bencom/`, the câmaras purchases comparison). Data workflows commit through the composite action `.github/actions/commit-data` (`paths`, `message`; output `changed`). Five auto-generated collections (`_alra_updates/`, `_joraa_updates/`, `_base_updates/`, `_portal_updates/` from the bot; `_ao/` from the AO scraper, titles only) plus manual blog posts in `_posts/`.

### News Scrapers (`scrapers/`)

Standalone scripts, not part of the bot pipeline. Run manually or via cron.

**`scrapers/ao.py`** — Açoriano Oriental print edition:
- Two-phase: (1) scrape print section pages for metadata, (2) match to online `/noticia/` URLs for full body text.
- Requires login. Credentials in `.ao_config` (repo root, gitignored). Template: `.ao_config.example`.
- Scrapes every section the edition lists. `DEFAULT_EXCLUDE` is empty; `.ao_config` can still narrow it via `include`/`exclude`.
- Title-to-URL matching uses slugification with exact/substring/partial strategies (~60-80% match rate).
- Page/feed output is delegated to `scrapers/ao_pages.py` (see below). Articles with no body or excerpt are excluded. The article text stays in the local `scrapers/output/` (gitignored): the site publishes titles only.
- Must be run as a module (`python3 -m scrapers.ao`) because it imports `scrapers.ao_pages`.

**`scrapers/rtp.py`** — RTP Açores via WordPress REST API:
- Single-phase: `GET /wp-json/wp/v2/posts/` with date filtering and `_embed`.
- No auth required. Paginates automatically.
- Author names unavailable (user endpoint returns 401).

**Output:** `scrapers/output/{prefix}{date}.json` and `.md`. AO uses `{date}.*`, RTP uses `rtp-{date}.*`.

**Key schema differences:**
- AO: string IDs, `section` (slug), has `page`/`author` fields
- RTP: integer IDs, `category` (display name), no `page`/`author`

**`scrapers/ao_pages.py`** — Jekyll pages + daily RSS for the AO print edition, **titles only** (the AO is paywalled; until 2026-11-27 the site also served each article's full text at `/ao/YYYYMMDD-NN/`, removed for copyright):
- Each day gets one page `docs/_ao/YYYYMMDD.md` → `/ao/YYYYMMDD/`: titles grouped by section (title + page + author), each linking to the article on acorianooriental.pt. Writing a day deletes any old `YYYYMMDD-*.md` article page.
- `docs/rss/ao.xml` carries **one item per edition day** with the same link list. Retention: `FEED_RETENTION_DAYS` = 90 items.
- Re-running a date is idempotent: the day page and the day's feed item are replaced.
- Pages carry `noindex: true` (via the `ao` defaults in `docs/_config.yml` → `_includes/custom-head.html`) and `docs/robots.txt` disallows `/ao/`.
- Ordering: sections by their lowest page number, articles by page within each section, ties keeping the print edition's order. Articles with no page sort last.
- Front-page teasers (`page` in `FRONT_PAGE_NUMBERS` = `{"0", "1"}`) are dropped: they are reworded one-line blurbs for articles that run inside. Page `0` is the lead story, whose card omits the `Pág. N` marker.

## Key Details

- **State file:** `bot/state.json` (~75 KB, committed) is the last run's state: ALRA IDs by type (and requerimentos by status), JORAA's last day and backfill range, BASE's last day, portal documents seen. Each run replaces it (`utils.append_state`, atomic write, lists sorted so the diff shows only what changed); git keeps the history. Until November 2026 it was `bot/state.jsonl`, one line per run: `get_prev_state` and `write_joraa_estado` still read its last line if `state.json` is missing, and the first run that writes `state.json` deletes it.
- **Deploy:** `.github/workflows/pages.yml` builds Jekyll with `actions/jekyll-build-pages` and deploys on push to main, on manual dispatch and when called by the daily run.
- **CI/CD:** `.github/workflows/run-bot.yml` runs daily at 00:00 UTC, commits as `fmesqg-auto` if changes exist.
- **Code style:** black (line-length 79), isort (black profile), Python >=3.11.5. Pre-commit hooks configured (black, isort, ruff) via `.pre-commit-config.yaml` at repo root — run `pre-commit install` from root.
- **Tests:** `pytest bot/tests/` runs offline by default. Network-dependent tests are marked `@pytest.mark.network` and skipped unless opted in with `-m network`.
- **Content language:** Portuguese (Azores region).

## Tone and crossing data

- Pages for journalists (`docs/tutorial.md`) must not be condescending: keep only what is specific to these data, such as coverage gaps, what a column really is and source quirks. Do not explain mediana vs média, inflation, citing sources or asking for reaction.
- Municipal figures read better per inhabitant. `camaras_data` in `bot/datasets.py` divides INE spending by INE population and matches BASE adjudicantes to concelhos (`municipio`, which handles several spellings and leaves out SMAS and municipal companies). Prefer pages that put several sources side by side per concelho, and label the site's own calculations.
