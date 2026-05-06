# Digital Investment Analytics — Development Guide

This document is for developers.

- Investor/vision overview + roadmap: see README.md
- Deep-learning architecture/spec: documented here as a target design (roadmap). A dedicated architecture doc can be added later if needed.

## Current status (implemented vs roadmap)

Implemented today:
- FMP client (`FMPClient`) for prices + fundamentals
- FRED client (`FREDClient`) for macro series metadata + observations
- CLI-first data downloads to local disk (Parquet for tabular, JSON for single-entity)
- Basic request usage tracking persisted to `config/fmp_usage.json` for FMP
- Live-API tests for both FMP and FRED clients
- Current FRED starter macro collection is sufficient to begin Alpha Vantage gold-price ingestion and the first baseline model build

Roadmap (high-level):
- Phase 1: data foundation + baseline signals
- Phase 2: quantile model + scenario generation
- Phase 3: portfolio optimization + long/short
- Phase 4: dynamic stop optimization

Immediate next milestone:
- Alpha Vantage gold-series ingestion -> daily as-of processed dataset -> first gold baseline deep learning model

IMPORTANT: The sections below under "Target design" are not implemented yet. They define the development specification so we can implement consistently.

## Project structure

```
Digital-Investment-Analytics/
├── src/
│   ├── fmp/                    # FMP integration package
│   │   ├── __init__.py         # Exports: config, FMPClient
│   │   ├── config.py           # API key loading from config/api_keys.txt
│   │   ├── client.py           # FMPClient — HTTP client for FMP stable API
│   │   ├── usage.py            # Daily request-usage tracker (resets 3 PM ET)
│   │   └── tools/
│   │       └── fmp_cli.py      # CLI: quote, chart, income, profile
│   └── fred/                   # FRED integration package
│       ├── __init__.py         # Exports: config, FREDClient
│       ├── config.py           # FRED API key loading from config/api_keys.txt
│       ├── client.py           # FREDClient — macro series metadata + observations
│       └── tools/
│           └── fred_cli.py     # CLI: series, observations
├── tests/
│   ├── test_fmp_client.py      # Live-API tests for FMPClient methods
│   ├── test_fred_client.py     # Live-API tests for FREDClient methods
│   └── test_setup.py           # Quick setup verification script
├── notebooks/
│   └── 01_FMPClient.ipynb      # Interactive exploration of FMPClient
├── data/
│   ├── raw/                    # Immutable CLI outputs (Parquet/JSON)
│   ├── processed/              # Cleaned / feature-engineered tables
│   └── plans/                  # Project planning docs
├── models/                     # Saved ML model artifacts (empty for now)
├── config/
│   ├── api_keys.txt            # YOUR key here (git-ignored)
│   ├── api_keys.example.txt    # Safe-to-commit template
│   └── fmp_usage.json          # Persisted daily request count
├── .github/
│   └── copilot-instructions.md # AI agent orientation for this repo
├── pyproject.toml              # Package metadata + optional extras
├── README.md                   # Investor-facing overview + roadmap
└── README_DEV.md               # This file — developer guide + target spec
```

## Setup

### 1) Create and activate a virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install

Editable install (recommended):

```bash
pip install -e .
```

Optional extras:

```bash
pip install -e ".[dev]"         # notebooks, pytest, formatters
pip install -e ".[storage]"     # pyarrow/h5py for Parquet/HDF
pip install -e ".[ml,dev,storage]"
```

## API key configuration (file-based)

The project loads API keys from a file at:

- `config/api_keys.txt`

Format:

```text
FMP_API_KEY=your_actual_key_here
FRED_API_KEY=your_actual_key_here
ALPHA_VANTAGE_API_KEY=your_actual_key_here
```

Notes:
- Do not commit your real key. The repo is configured to ignore `config/api_keys.txt` via `.gitignore`.
- A safe template is provided as `config/api_keys.example.txt`.

## CLI-first quick start

The CLI is the recommended entrypoint for reproducible data artifacts.

From the project root:

```bash
python -m fmp.tools.fmp_cli quote --symbol AAPL
python -m fmp.tools.fmp_cli profile --symbol AAPL
python -m fmp.tools.fmp_cli chart --symbol AAPL --from 2024-01-01 --to 2024-01-31
python -m fmp.tools.fmp_cli income --symbol AAPL --period annual --limit 5
python -m fred.tools.fred_cli series --id FEDFUNDS
python -m fred.tools.fred_cli observations --id FEDFUNDS --from 2024-01-01 --to 2024-12-31  # optional --to
```

### Output layout

Default output root: `data/raw`

- Quote (JSON): `data/raw/quote/<SYMBOL>/<timestamp>.json`
- Profile (JSON): `data/raw/profile/<SYMBOL>/<timestamp>.json`
- Chart (Parquet): `data/raw/chart/<SYMBOL>/<from>_<to>.parquet`
- Income statement (Parquet): `data/raw/income-statement/<SYMBOL>/<period>_<timestamp>.parquet`
- FRED series metadata (JSON): `data/raw/fred-series/<SERIES_ID>/<timestamp>.json`
- FRED observations (Parquet): `data/raw/fred-observations/<SERIES_ID>/<from>_<to>.parquet`

### Accumulating data by prediction date (recommended convention)

For scheduled or event-driven prediction refreshes, prefer saving outputs under an as-of date so you can:
- re-run without overwriting prior artifacts
- reproduce model training inputs
- compare revisions (re-downloads) over time

A simple convention (not yet implemented in the CLI; manual via `--out`):

- `data/raw/<endpoint>/<SYMBOL>/asof=YYYY-MM-DD/<files...>`

You can approximate this today by passing `--out data/raw/<endpoint>/asof=YYYY-MM-DD` to the CLI. Native support is planned for a future CLI update.

## Target design (roadmap): refreshable decision clock

The target system should support scheduled and event-driven reruns over a fixed universe. The main operational modeling layer should be a daily as-of dataset, with monthly tables reserved for research and slower backtests.

At each refresh date (weekly, biweekly, or event-driven), run:

1. Update raw data from whichever sources have changed
2. Build an as-of feature table that carries forward the latest known lower-frequency values
3. Forecast return distributions for horizons $H \in \{1W, 2W, 1M, 3M\}$
4. Sample $M$ scenarios per asset/horizon and compute risk metrics
5. Persist a prediction snapshot and compare it with the prior run
6. Compute asset utilities, rank candidates, and optionally update portfolio weights
7. Produce a reproducible run bundle (artifacts)

## Target design (roadmap): three-layer architecture

### Layer A — Scenario forecasting (deep learning)

Objective: forecast probabilistic distributions of future returns (not a single return).

Inputs (MVP):
- As-of historical feature windows per asset or product (daily rows with latest known macro values)
- Candidate features: gold returns, rates, real yields, inflation, USD, VIX, optional market context; semantic inputs later

Outputs (two compatible approaches):

Option A1 — Parametric distributional model (Student-t)
- Predict parameters $(\mu_{i,H}, \sigma_{i,H}, \nu_{i,H})$ for a heavy-tailed Student-t return distribution

Option A2 — Quantile model (recommended MVP)
- Predict non-parametric quantiles $q_{i,t,H}(\alpha)$ for:
	- $\alpha \in \{0.05, 0.25, 0.50, 0.75, 0.95\}$
- Train separate heads per horizon (1W / 2W / 1M / 3M first; longer-term later) to avoid compounding errors from recursive forecasting

Quantile (pinball) loss:

$$
L_\alpha(y, \hat{q}) =
\begin{cases}
\alpha (y-\hat{q}) & \text{if } y \ge \hat{q} \\
(1-\alpha)(\hat{q}-y) & \text{if } y < \hat{q}
\end{cases}
$$

### Layer B — Scenario generation + metrics

From predicted quantiles (or a parametric distribution), construct an empirical return distribution and sample $M$ scenarios.

Scenario compounding for multi-month returns:

$$
R_{i,H}^m = \prod_{h=1}^{H} (1 + r_{i,t+h}^m) - 1
$$

Key scenario-derived metrics per asset and horizon:
- Expected return: $\mu_{i,H} = \mathbb{E}[R]$
- Probability of loss: $P^-_{i,H} = \mathbb{P}(R < 0)$
- Value-at-Risk (VaR, 5%): $\mathrm{VaR}_{0.05}$
- Expected shortfall (ES, 5%): $\mathrm{ES}_{0.05}$

Note: VaR/ES sign convention is intentionally TBD (loss-positive vs return-negative). Pick one at implementation time and keep it consistent across code, plots, and reporting.

### Layer C — Decision making & portfolio construction

Utility score (one default form):

$$
U_i = \mu_{i,H} - \lambda \cdot (-\mathrm{ES}_{0.05}(i,H)) - \gamma \cdot P^-_{i,H} - \rho \cdot TC_i
$$

Where:
- $\lambda$ controls tail-risk aversion
- $\gamma$ controls frequency-of-loss aversion
- $TC_i$ models transaction cost / tax drag

Shorting eligibility gate (MVP):
- Allow shorts only if $P(R < 0)$ exceeds a threshold (e.g., 65–75%) AND tail risk is controlled

Portfolio optimization (scenarios-based):

Budget constraint:

$$
\sum_i w_i + w_{cash} = 1
$$

Gross exposure cap (MVP):

$$
\sum_i |w_i| \le G \quad \text{with } G = 1.2
$$

Soft concentration caps (recommended):
- Avoid hard max weights; instead apply a penalty when $|w_i|$ exceeds ~35%

## Data engineering notes (target conventions)

Raw data:
- Keep each source at its native frequency and release timestamp
- Stored immutably as Parquet/JSON artifacts

Processed tables:
- Daily as-of feature table (primary modeling dataset)
- Monthly resampled research table (secondary sandbox/backtest dataset)

Labels:
- Forward returns for first baseline horizons $H \in \{1W, 2W, 1M, 3M\}$:

$$
Y_{t,H} = \frac{P_{t+H}}{P_t} - 1
$$

## Rate limits and usage tracking

- The free-tier limit is treated as 250 requests/day.
- A small sleep is applied per request to reduce burst rate.
- Usage is persisted to `config/fmp_usage.json` so repeated runs share a counter.

## Testing

Run:

```bash
pytest -q
```

Notes:
- Tests call live endpoints and require a valid API key + internet.
- Compatibility alias: `get_historical_prices(...)` is supported as an alias of `get_chart(...)`.

## Technology stack

Implemented now:
- Python 3.8+
- requests, pandas, numpy
- Parquet storage (via pyarrow)

Target (roadmap):
- PyTorch (quantile regression model)
- Pandas / Polars (feature engineering)
- NumPy / SciPy (scenario sampling, metrics)
- CVXPY (optional, portfolio weight optimization)
- matplotlib / seaborn (evaluation plots)
- Reinforcement learning or adaptive signal-weighting experiments after the supervised baseline is stable

## Backtesting specification (target)

Method: walk-forward refresh backtest.

Steps per refresh date:
1. Predict return distributions (Layer A)
2. Generate scenarios and compute metrics (Layer B)
3. Compare the current prediction snapshot with the prior snapshot
4. Rank assets and optimize portfolio (Layer C)
5. Apply transaction costs and tax assumptions
6. Record portfolio return for the evaluation window

Evaluation metrics:
- CAGR
- Annualized volatility
- Sharpe ratio / Sortino ratio
- Maximum drawdown
- Portfolio turnover
- Benchmark comparison (SPY buy-and-hold)

## FMP API plan limitations

The current setup assumes the FMP free tier. Symbol coverage depends on your plan:

- **Free**: Limited to ~90 tickers: AAPL, TSLA, AMZN, MSFT, NVDA, GOOGL, META, NFLX, JPM, V, BAC, PYPL, DIS, T, PFE, COST, INTC, KO, TGT, NKE, SPY, BA, BABA, XOM, WMT, GE, CSCO, VZ, JNJ, CVX, PLTR, SQ, SHOP, SBUX, SOFI, HOOD, RBLX, SNAP, AMD, UBER, FDX, ABBV, ETSY, MRNA, LMT, GM, F, LCID, CCL, DAL, UAL, AAL, TSM, SONY, ET, MRO, COIN, RIVN, RIOT, CPRX, VWO, SPYG, NOK, ROKU, VIAC, ATVI, BIDU, DOCU, ZM, PINS, TLRY, WBA, MGM, NIO, C, GS, WFC, ADBE, PEP, UNH, CARR, HCA, TWTR, BILI, SIRI, FUBO, RKT
- **Starter**: US exchanges
- **Premium**: US, UK, and Canada exchanges

## Known limitations (current)

- The project is still in the data-collection stage; forecasting/models/portfolio code is roadmap work.
- Alpha Vantage and yfinance integrations are still pending, and the first gold baseline model is not implemented yet.
- Stocks expansion, semantic/news features, and reinforcement learning are later-stage additions.
- Free-tier symbols may be restricted by FMP plan (see list above).
