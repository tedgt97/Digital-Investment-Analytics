# Codebase Conventions

## Naming & Imports
- Package namespace = data source name: `fmp`, `fred`, `alphavantage`, `yfinance_`
- Installed imports: `from fmp.client import FMPClient`
- Internal imports: relative (`from .config import config`)

## Client Pattern (follow for every new data source)
- `client.py` — main class with shared `requests.Session`, central `_make_request()`
- `config.py` — loads API key from `config/api_keys.txt`, exposes global `config` instance
- `usage.py` — (if rate-limited) persists daily count, auto-resets on window change
- `tools/<source>_cli.py` — argparse CLI for reproducible data fetches

## Return Types
- Tabular/series data → `pandas.DataFrame`
- Single-entity data → `dict`

## Persistence
- DataFrame → Parquet under `data/raw/<endpoint>/<symbol>/...`
- Dict → pretty-printed JSON under `data/raw/<endpoint>/<symbol>/...`

## Code Markers
- `# --Fixed--` on modified lines
- `# --Added--` on newly added lines
- Retain existing comments/docstrings

## Testing
- Tests call live endpoints (require valid API key + internet)
- Run: `pytest -q` from project root with `.venv` activated
- Temp test scripts go in `test/` folder with `_tmp_*` prefix

## CLI
- Invoked via `python -m <package>.tools.<cli_module>`
- Common `--out` flag defaults to `data/raw`
- No console_scripts entry point yet
