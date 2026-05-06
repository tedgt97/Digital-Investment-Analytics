# Implementation Status

## Current Version: 0.2.2

## Completed (Implemented & Working)

### FMP Client (`src/fmp/`)
- `config.py` — loads API key from `config/api_keys.txt` (file-based, not env vars)
- `client.py` — `FMPClient` with methods: `get_chart`, `get_historical_prices` (alias), `get_quote`, `get_income_statement`, `get_company_profile`, `get_request_usage`
- `usage.py` — `FMPUsageTracker` persists daily count to `config/fmp_usage.json`, resets at 3 PM ET
- `tools/fmp_cli.py` — CLI subcommands: `quote`, `chart`, `income`, `profile` → Parquet/JSON to `data/raw/`
- `__init__.py` — exports `config`, `FMPClient`

### FRED Client (`src/fred/`)
- `config.py` — loads API key from `config/api_keys.txt` (file-based, not env vars)
- `client.py` — `FREDClient` with methods: `get_series`, `get_series_observations`
- `tools/fred_cli.py` — CLI subcommands: `series`, `observations` → JSON/Parquet to `data/raw/`
- `__init__.py` — exports `config`, `FREDClient`

### Tests (`tests/`)
- `test_fmp_client.py` — 7 live-API tests (init, quote, chart, income, profile, invalid symbol, invalid date)
- `test_fred_client.py` — live-API tests for FREDClient methods
- `test_setup.py` — standalone setup verification script

### Docs
- `README.md` — investor-facing: short/medium-horizon roadmap, refreshable decision flow, gold pivot
- `README_DEV.md` — developer-facing: setup, CLI, as-of data guidance, target design spec (Layer A/B/C math)
- `.github/copilot-instructions.md` — AI agent orientation
- `version_list.txt` — changelog through ver.0.2.2

### Config
- `pyproject.toml` — editable install, extras: `[ml, dev, storage, all]`
- `config/api_keys.example.txt` — safe template (committed)
- `config/api_keys.txt` — real key (git-ignored)

## Next Up (Phase 1 — Gold Baseline Build)

- [x] Register FRED API key
- [x] Register Alpha Vantage API key
- [x] Build `src/fred/` client (macro, rates, FX, VIX)
- [ ] Build `src/alphavantage/` client (gold price, commodities, GDP)
- [ ] Pull initial gold price/history series and persist raw artifacts
- [ ] Build the first daily as-of processed dataset combining gold data with the current FRED starter macros
- [ ] Define the first label set for 1W / 2W / 1M / 3M horizons
- [ ] Train the initial deep learning baseline for gold
- [ ] Save prediction snapshots for rerun comparison
- [ ] Add `src/yfinance_/` market-context wrapper if the first baseline needs more support

## Later Expansion

- Expand to stocks after the gold baseline is stable
- Add semantic/news features after the numeric baseline is stable
- Research reinforcement learning for adaptive signal weighting or policy optimization after the supervised baseline is stable
