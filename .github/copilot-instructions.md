# Copilot Instructions — Digital-Investment-Analytics

These notes orient AI coding agents to this repo’s architecture, workflows, and conventions so you can be productive immediately.

## Big Picture
- Purpose: Fetch US stock market data from the Financial Modeling Prep (FMP) API, store locally, and support ML workflows.
- Core layers:
  - `src/fmp/config.py`: Loads the FMP API key from `config/api_keys.txt` (file-based, not env-vars at runtime).
  - `src/fmp/client.py`: Thin client over FMP “stable” endpoints with shared `requests.Session`, central error handling, basic rate-limit delay, and Pandas conversion.
  - `src/fmp/tools/fmp_cli.py`: CLI module to fetch and persist data to `data/raw/` as JSON/Parquet for downstream work.

## Key Conventions
- Installed-package imports use the `fmp` namespace (e.g., `from fmp.client import FMPClient`). Inside the package, prefer relative imports (e.g., `from .config import config`).
- Config source of truth is `config/api_keys.txt` with a required line `FMP_API_KEY=...`. The global `config` instance is created in `src/fmp/config.py` and used by `FMPClient`.
- HTTP calls must go through `FMPClient._make_request(...)` so headers, API key, errors, request counting, and delay are consistent.
- Return types:
  - Price/financial series → `pandas.DataFrame` (e.g., `get_chart`, `get_income_statement`).
  - Single-entity resources → `dict` (e.g., `get_quote`, `get_company_profile`).
- Persistence (CLI):
  - DataFrames → Parquet under `data/raw/<endpoint>/<symbol>/...`.
  - Dicts → pretty-printed JSON under `data/raw/<endpoint>/<symbol>/...`.

## FMP Client Patterns (`src/fmp/client.py`)
- Base URL: `https://financialmodelingprep.com/stable`.
- API key automatically appended via `_make_request`.
- Session header: `User-Agent: Digital-Investment-Analytics/<ver>`.
- Built-in minimal delay `time.sleep(0.25)` to avoid burst limits.
- Examples implemented:
  - `get_chart(symbol, start_date, end_date)` → DataFrame with `date, open, high, low, close, volume, change, changePercent, vwap`.
  - `get_quote(symbol)` → dict.
  - `get_income_statement(symbol, period, limit)` → DataFrame; parses `date` if present.
  - `get_company_profile(symbol)` → dict.

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

## Developer Workflow
- Setup (PowerShell):
  - `python -m venv venv`; `venv\Scripts\activate`
  - `pip install -e .` or `pip install -e ".[ml,dev]"`
  - Create `config/api_keys.txt` with `FMP_API_KEY=your_actual_key_here`
- Tests (live API): `pytest -q` (requires working internet + valid API key).
- Packaging: `pyproject.toml` uses `package-dir = {"" = "src"}` and auto-discovers packages under `src`, exposing `fmp` as the top-level import (`from fmp.client import FMPClient`). No console script is currently wired; use `python -m fmp.tools.fmp_cli` instead.

## Gotchas & House Rules
- Naming mismatch: README/tests reference `get_historical_prices`, but implementation provides `get_chart`. When extending or fixing, prefer aligning names (e.g., add a thin alias calling `get_chart`) and update docs/tests consistently.
- Keep all HTTP interactions in `_make_request` and reuse the shared `Session`.
- Maintain return-type conventions (DataFrame vs dict) and Parquet/JSON persistence patterns when adding new endpoints/CLI commands.
- Tests call real endpoints; design new tests accordingly or mark/network-isolation explicitly if you refactor.

## Quick References
- Files to study first: `src/fmp/config.py`, `src/fmp/client.py`, `src/fmp/tools/fmp_cli.py`, `tests/test_fmp_client.py`.
- Data directories: `data/raw/` for fetched artifacts; `data/processed/` for curated datasets; `models/` for trained artifacts.
