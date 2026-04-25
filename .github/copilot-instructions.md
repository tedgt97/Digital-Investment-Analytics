# Copilot Instructions -- Digital-Investment-Analytics

These notes orient AI coding agents to this repo's architecture, workflows, and conventions so you can be productive immediately.

## Big Picture
- Purpose: Build a multi-asset investment decision system. Currently in the data-collection phase (Phase 1); forecasting, scenario generation, and portfolio optimization are roadmap.
- Documentation:
  - `README.md`: Investor-facing -- vision, monthly operating loop, 3-layer architecture, Phase 1-4 roadmap.
  - `README_DEV.md`: Developer-facing -- setup, CLI, data layout, target design spec (Layer A/B/C math), testing notes.
- Core implemented layers:
  - `src/fmp/config.py`: Loads the FMP API key from `config/api_keys.txt` (file-based, not env-vars at runtime).
  - `src/fmp/client.py`: Thin client over FMP "stable" endpoints with shared `requests.Session`, central error handling, basic rate-limit delay, and Pandas conversion.
  - `src/fmp/usage.py`: Persists daily request counts to `config/fmp_usage.json`; resets at 3 PM US/Eastern.
  - `src/fmp/tools/fmp_cli.py`: CLI module to fetch and persist data to `data/raw/` as JSON/Parquet for downstream work.

## Key Conventions
- Installed-package imports use the `fmp` namespace (e.g., `from fmp.client import FMPClient`). Inside the package, prefer relative imports (e.g., `from .config import config`).
- Config source of truth is `config/api_keys.txt` with a required line `FMP_API_KEY=...`. Do NOT commit your real key; `.gitignore` excludes it. A safe template is at `config/api_keys.example.txt`.
- HTTP calls must go through `FMPClient._make_request(...)` so headers, API key, errors, request counting, and delay are consistent.
- Return types:
  - Price/financial series -> `pandas.DataFrame` (e.g., `get_chart`, `get_income_statement`).
  - Single-entity resources -> `dict` (e.g., `get_quote`, `get_company_profile`).
- Persistence (CLI):
  - DataFrames -> Parquet under `data/raw/<endpoint>/<symbol>/...`.
  - Dicts -> pretty-printed JSON under `data/raw/<endpoint>/<symbol>/...`.

## FMP Client Patterns (`src/fmp/client.py`)
- Base URL: `https://financialmodelingprep.com/stable`.
- API key automatically appended via `_make_request`.
- Session header: `User-Agent: Digital-Investment-Analytics/<ver>`.
- Built-in minimal delay `time.sleep(0.25)` to avoid burst limits.
- Implemented methods:
  - `get_chart(symbol, start_date, end_date)` -> DataFrame with `date, open, high, low, close, volume, change, changePercent, vwap`.
  - `get_historical_prices(...)` -> alias for `get_chart(...)` (backwards compatibility).
  - `get_quote(symbol)` -> dict.
  - `get_income_statement(symbol, period, limit)` -> DataFrame; parses `date` if present.
  - `get_company_profile(symbol)` -> dict.
  - `get_request_usage()` -> dict with `used`, `limit`, `remaining`.

## CLI Usage (`python -m fmp.tools.fmp_cli`)
- Subcommands: `quote`, `chart`, `income`, `profile`.
- Common flag: `--out` (default `data/raw`).
- Examples (PowerShell, from project root after `pip install -e .`):
  - `python -m fmp.tools.fmp_cli quote --symbol AAPL`
  - `python -m fmp.tools.fmp_cli chart --symbol AAPL --from 2024-01-01 --to 2024-01-31`
  - `python -m fmp.tools.fmp_cli income --symbol AAPL --period annual --limit 5`
  - `python -m fmp.tools.fmp_cli profile --symbol AAPL`
- Output paths:
  - Chart: `data/raw/chart/AAPL/2024-01-01_2024-01-31.parquet`
  - Quote: `data/raw/quote/AAPL/<timestamp>.json`
  - Income: `data/raw/income-statement/AAPL/<period>_<timestamp>.parquet`
  - Profile: `data/raw/profile/AAPL/<timestamp>.json`

## Developer Workflow
- Setup (PowerShell):
  - `python -m venv .venv`; `.venv\Scripts\Activate.ps1`
  - `pip install -e .` or `pip install -e ".[ml,dev,storage]"`
  - Copy `config/api_keys.example.txt` -> `config/api_keys.txt` and set your real key.
- Tests (live API): `pytest -q` (requires working internet + valid API key).
- Packaging: `pyproject.toml` uses `package-dir = {"" = "src"}` and auto-discovers packages under `src`, exposing `fmp` as the top-level import (`from fmp.client import FMPClient`). No console script is currently wired; use `python -m fmp.tools.fmp_cli` instead.

## House Rules
- Keep all HTTP interactions in `_make_request` and reuse the shared `Session`.
- Maintain return-type conventions (DataFrame vs dict) and Parquet/JSON persistence patterns when adding new endpoints/CLI commands.
- Tests call real endpoints; design new tests accordingly or mark/network-isolation explicitly if you refactor.

## Current Direction (ver.0.2.2)
- The project has pivoted to **Gold as the first asset** before expanding to the full US stock universe.
- Multi-source data architecture planned:
  - **FRED** — macro data: interest rates, treasury yields, CPI, FX, VIX (~25 series, unlimited free calls)
  - **Alpha Vantage** — gold/silver prices, commodities, GDP (25 free calls/day)
  - **yfinance** — gold futures/ETF with volume, equity indices (no API key)
  - **FMP** — reserved for US stock fundamentals in later expansion
- New client packages will follow the same patterns as `src/fmp/`: dedicated `client.py`, `config.py`, CLI tool, Parquet/JSON persistence.
- Immediate next steps: register FRED + Alpha Vantage API keys, build `src/fred/` and `src/alphavantage/` clients, add yfinance wrapper.

## Quick References
- Files to study first: `src/fmp/config.py`, `src/fmp/client.py`, `src/fmp/usage.py`, `src/fmp/tools/fmp_cli.py`, `tests/test_fmp_client.py`.
- Data directories: `data/raw/` for fetched artifacts; `data/processed/` for curated datasets; `models/` for trained artifacts.
- Target tech stack: Python, PyTorch, Pandas/Polars, NumPy/SciPy, Parquet storage, CVXPY (optional for portfolio optimization).