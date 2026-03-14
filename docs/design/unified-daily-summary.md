# Unified daily summary — design notes

## Goal

One Telegram message per day covering everything that happened in the Azores:
government data (ALRA, JORAA, BASE, portal) + news (AO, RTP).
Written in Portuguese, for citizens. Concise, scannable, informative.

## Current state

- **Bot pipeline** (`bot/`) scrapes 4 government sources, writes markdown to `docs/_*_updates/`, then `summarize.py` reads those files, sends them to Claude, posts the summary to Telegram.
- **News scrapers** (`scrapers/ao.py`, `scrapers/rtp.py`) are standalone scripts. They output JSON + markdown to `scrapers/output/`. They are NOT wired into the bot pipeline or the summary.

## Constraints

- RSS feeds and Jekyll site output must not change.
- Use Python for everything that can be done deterministically (aggregation, formatting, deduplication, spending totals). Use the LLM only for what Python can't do (narrative synthesis, prioritization by significance).
- Keep token usage low. Haiku-class model. Input should be pre-digested, not raw article bodies.
- The whole thing runs in one GitHub Actions job, daily.

## What the LLM should NOT do

- Parse HTML or JSON
- Calculate spending totals (Python can sum JORAA amounts and BASE contract prices)
- Deduplicate news (same story in AO and RTP — Python can fuzzy-match titles)
- Format the Telegram message (Python can apply bold, bullets, structure)

## What the LLM should do

- Pick the 5-8 most important items from a pre-structured briefing
- Write a one-sentence Portuguese summary for each
- Decide relative priority (political significance, public spending size, public interest)

## Proposed architecture

```
┌─────────────────────────────────────────────────────────┐
│  1. Bot pipeline (existing)                             │
│     fetch → delta → write markdown + JSON → state       │
└──────────────────────┬──────────────────────────────────┘
                       │ writes docs/_*_updates/YYYY-MM-DD.md
                       ▼
┌─────────────────────────────────────────────────────────┐
│  2. News scrapers (existing, need CI integration)       │
│     ao.py → scrapers/output/{date}.json                 │
│     rtp.py → scrapers/output/rtp-{date}.json            │
└──────────────────────┬──────────────────────────────────┘
                       │ writes scrapers/output/*.json
                       ▼
┌─────────────────────────────────────────────────────────┐
│  3. Python pre-processing (NEW — bot/daily_briefing.py) │
│     - Read government markdown from disk                │
│     - Read news JSON from scrapers/output/              │
│     - Compute: total JORAA spend, largest BASE contract │
│     - Deduplicate news across AO + RTP (title fuzzy)    │
│     - Build structured briefing (not raw markdown)      │
│     - Output: ~50-line structured text for LLM          │
└──────────────────────┬──────────────────────────────────┘
                       │ structured briefing string
                       ▼
┌─────────────────────────────────────────────────────────┐
│  4. LLM call (existing summarize.py, updated prompt)    │
│     - Receives pre-digested briefing, not raw markdown  │
│     - Picks top items, writes 1-sentence summaries      │
│     - Returns ~800 chars of formatted text              │
└──────────────────────┬──────────────────────────────────┘
                       │ summary text
                       ▼
┌─────────────────────────────────────────────────────────┐
│  5. Telegram post (existing post_to_telegram)           │
└─────────────────────────────────────────────────────────┘
```

## Pre-processing detail (step 3)

The briefing sent to the LLM should look like this (example):

```
DATA: 2026-03-13

JORAA (3 atos, total: 645.000 €):
- Contrato Programa AVEA: 620.000 € (Sec. Juventude)
- Retificação Anúncio 96/2026: 0 €
- Despacho pessoal: 25.000 €

BASE (5 contratos, maior: 150.000 €):
- Serviço de limpeza hospitalar: 150.000 € (Hospital Divino Espírito Santo → CleanAz)
- Manutenção elevadores: 45.000 € (...)
[top 5 by price]

ALRA:
- 2 novos requerimentos (PS, BE)
- 1 nova iniciativa: "Proposta sobre mobilidade inter-ilhas"
- 3 requerimentos mudaram estado

PORTAL:
- 1 novo boletim publicado

NOTÍCIAS (12 artigos, 3 fontes):
- [RTP] Prisão preventiva para 8 tripulantes — cocaína apreendida nos Açores
- [RTP] Paulo Rangel afasta revisão do acordo da Base das Lajes
- [AO] Hospital de Ponta Delgada: adjudicado programa funcional
- [RTP+AO] Subsídio de Mobilidade: petição com 5000 assinaturas
[deduplicated, sorted by relevance heuristic: category + keyword signals]
```

This is ~400 tokens input. Haiku generates ~200 tokens output. ~$0.001/day.

## CI changes needed

1. Run scrapers before the summary step (after bot writes, before state append)
2. AO scraper needs `.ao_config` credentials — either as a GitHub secret decoded to file, or skip AO in CI and only include RTP
3. Add `scrapers/` to workflow paths trigger

## Open questions

- Should AO run in CI or only locally? (needs login, may be fragile)
- News deduplication threshold — what fuzzy match ratio is good enough?
- Should the Telegram message have sections (governo / notícias) or be one flat list sorted by importance?
- Maximum message length — Telegram limit is 4096 chars, current target is 1000. Increase to ~1500 to fit news?

## Files to create/modify

| File | Change |
|------|--------|
| `bot/daily_briefing.py` | NEW — Python pre-processing: read sources, compute stats, deduplicate, build structured briefing |
| `bot/summarize.py` | Update `_build_daily_markdown` → use `daily_briefing.py` output instead of raw markdown |
| `bot/__main__.py` | Add scraper invocation step (or separate workflow step) |
| `.github/workflows/run-bot.yml` | Add scraper step, possibly AO credentials |
| `bot/tests/test_daily_briefing.py` | NEW — test pre-processing logic |
