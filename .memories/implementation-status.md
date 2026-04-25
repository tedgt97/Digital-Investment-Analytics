# Implementation Status

## Current Version: 0.2.2

## Completed (Implemented & Working)

### FMP Client (`src/fmp/`)
- `config.py` — loads API key from `config/api_keys.txt` (file-based, not env vars)
- `client.py` — `FMPClient` with methods: `get_chart`, `get_historical_prices` (alias), `get_quote`, `get_income_statement`, `get_company_profile`, `get_request_usage`
- `usage.py` — `FMPUsageTracker` persists daily count to `config/fmp_usage.json`, resets at 3 PM ET
- `tools/fmp_cli.py` — CLI subcommands: `quote`, `chart`, `income`, `profile` → Parquet/JSON to `data/raw/`
- `__init__.py` — exports `config`, `FMPClient`

### Tests (`tests/`)
- `test_fmp_client.py` — 7 live-API tests (init, quote, chart, income, profile, invalid symbol, invalid date)
- `test_setup.py` — standalone setup verification script

### Docs
- `README.md` — investor-facing: vision, monthly loop, 3-layer architecture, Phase 1-4 roadmap, gold pivot
- `README_DEV.md` — developer-facing: setup, CLI, data layout, target design spec (Layer A/B/C math)
- `.github/copilot-instructions.md` — AI agent orientation
- `version_list.txt` — changelog through ver.0.2.2

### Config
- `pyproject.toml` — editable install, extras: `[ml, dev, storage, all]`
- `config/api_keys.example.txt` — safe template (committed)
- `config/api_keys.txt` — real key (git-ignored)

## Not Started (Phase 1 — Gold Data Foundation)

- [x] Register FRED API key
- [x] Register Alpha Vantage API key
- [ ] Build `src/fred/` client (macro, rates, FX, VIX)
- [ ] Build `src/alphavantage/` client (gold price, commodities, GDP)
- [ ] Add `src/yfinance_/` wrapper (gold volume, equity indices)
- [ ] Initial gold data pull — full history for all gold-relevant series
- [ ] Consolidate raw data into ML-ready panel (`data/processed/`)
- [ ] EDA notebook: gold price vs macro features
- [ ] Feature engineering: rolling windows, returns, regime indicators
- [ ] Baseline signals for sanity checks

## Future (Phases 2-4)

- Phase 2: Deep quantile model + scenario generation
- Phase 3: Portfolio optimization + long/short decision engine
- Phase 4: Dynamic stop / force-sale optimization
