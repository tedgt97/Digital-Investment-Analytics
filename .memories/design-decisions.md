# Design Decisions

## Architecture
- **Monthly decision clock** over fixed universe (~80-90 tickers) — rebalance at month-end
- **3-layer architecture**: Layer A (forecasting) → Layer B (scenario metrics) → Layer C (portfolio construction)
- **Quantile regression** (Option A2) chosen as MVP over parametric Student-t
- Horizons: 1M / 3M / 6M / 12M with separate heads per horizon

## Gold Pivot (ver.0.2.2)
- Gold is the **first asset** before expanding to US stock universe
- Multi-source data strategy:
  - FRED: macro/rates/FX/VIX (~25 series, unlimited) — docs: https://fred.stlouisfed.org/docs/api/fred/
  - Alpha Vantage: gold/silver/commodities/GDP (25 calls/day) — docs: https://www.alphavantage.co/documentation/
  - yfinance: gold futures/ETF volume, equity indices (no key)
  - FMP: reserved for US stock fundamentals later

## Gold Macro Feature Priorities
- Highest-priority FRED blocks for gold: **real yields**, **inflation expectations**, **nominal yields/policy rate**, **USD strength**, and **risk stress**
- Secondary FRED blocks: **realized inflation**, **liquidity / central bank balance sheet**, and **growth / labor market activity**
- Recommended first FRED core set for gold modeling:
  - `DFII10`, `T10YIE`, `FEDFUNDS`, `DGS10`, `DTWEXBGS`, `VIXCLS`, `CPIAUCSL`, `WALCL`, `INDPRO`, `UNRATE`
- Pull raw observations through the CLI and persist tabular data as **Parquet**; keep metadata as **JSON**
- For monthly deep-learning modeling, prefer **15+ years** of overlapping history, with **20+ years** preferred where available; 5 years is acceptable only for quick baseline exploration, not the main deep model

## Data Conventions
- Raw data stored immutably as Parquet (tabular) / JSON (single-entity) in `data/raw/`
- New clients follow `src/fmp/` pattern: `client.py`, `config.py`, CLI, Parquet/JSON persistence
- All HTTP calls go through a central `_make_request` method per client
- Return types: DataFrame for series data, dict for single-entity

## API Key Management
- File-based: `config/api_keys.txt` with `KEY_NAME=value` lines
- NOT env vars at runtime — loaded from file by Config class
- Template at `config/api_keys.example.txt` (committed); real keys git-ignored

## Package Structure
- `src/` layout with `package-dir = {"" = "src"}` in pyproject.toml
- Top-level import namespace per data source: `fmp`, `fred`, `alphavantage`, `yfinance_`
- Installed-package imports: `from fmp.client import FMPClient`
- Internal: relative imports (`from .config import config`)
