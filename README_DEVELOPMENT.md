# Digital Investment Analytics — Development Guide

This document is for developers.

- Investor/vision overview + roadmap: see README.md
- Deep-learning architecture/spec: documented here as a target design (roadmap). A dedicated architecture doc can be added later if needed.

## Current status (implemented vs roadmap)

Implemented today:
- FMP client (`FMPClient`) for prices + fundamentals
- CLI-first data downloads to local disk (Parquet for tabular, JSON for single-entity)
- Basic request usage tracking persisted to `config/fmp_usage.json`

Roadmap (high-level):
- Phase 1: data foundation + baseline signals
- Phase 2: quantile model + scenario generation
- Phase 3: portfolio optimization + long/short
- Phase 4: dynamic stop optimization

IMPORTANT: The sections below under "Target design" are not implemented yet. They define the development specification so we can implement consistently.

## Setup

### 1) Create and activate a virtual environment

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
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

The project loads the FMP API key from a file at:

- `config/api_keys.txt`

Format:

```text
FMP_API_KEY=your_actual_key_here
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
```

### Output layout

Default output root: `data/raw`

- Quote (JSON): `data/raw/quote/<SYMBOL>/<timestamp>.json`
- Profile (JSON): `data/raw/profile/<SYMBOL>/<timestamp>.json`
- Chart (Parquet): `data/raw/chart/<SYMBOL>/<from>_<to>.parquet`
- Income statement (Parquet): `data/raw/income-statement/<SYMBOL>/<period>_<timestamp>.parquet`

### Accumulating data by rebalance date (recommended convention)

For monthly rebalances, prefer saving outputs under a rebalance run “as-of” date so you can:
- re-run without overwriting prior artifacts
- reproduce model training inputs
- compare revisions (re-downloads) over time

A simple convention:

- `data/raw/<endpoint>/<SYMBOL>/asof=YYYY-MM-DD/<files...>`

You can implement this by passing `--out` to the CLI and choosing a dated folder.

## Target design (roadmap): monthly decision clock

The target system runs on a monthly schedule over a fixed universe (target: ~80–90 tickers).

At each rebalance date (month-end or first trading day after), run:

1. Update raw data (EOD prices + selected fundamentals)
2. Build features into a monthly modeling table (rolling window)
3. Forecast return distributions for horizons $H \in \{1,3,6,12\}$ months
4. Sample $M$ scenarios per asset/horizon and compute risk metrics
5. Compute asset utilities, rank candidates, and select Top-K (≤ 5)
6. Optimize weights under constraints (cash allowed, gross exposure capped)
7. Produce trade list + a reproducible run bundle (artifacts)

## Target design (roadmap): three-layer architecture

### Layer A — Scenario forecasting (deep learning)

Objective: forecast probabilistic distributions of future returns (not a single return).

Inputs (MVP):
- Monthly historical features per asset (rolling window, e.g., 36–60 months)
- Candidate features: returns (1M/3M/6M/12M), rolling volatility, momentum, drawdown metrics, optional beta

Outputs (two compatible approaches):

Option A1 — Parametric distributional model (Student-t)
- Predict parameters $(\mu_{i,H}, \sigma_{i,H}, \nu_{i,H})$ for a heavy-tailed Student-t return distribution

Option A2 — Quantile model (recommended MVP)
- Predict non-parametric quantiles $q_{i,t,H}(\alpha)$ for:
	- $\alpha \in \{0.05, 0.25, 0.50, 0.75, 0.95\}$
- Train separate heads per horizon (1/3/6/12 months) to avoid compounding errors from recursive forecasting

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
- Daily OHLCV (adjusted when available)
- Stored immutably as Parquet/JSON artifacts

Processed tables:
- Daily adjusted returns
- Monthly resampled feature table (primary modeling dataset)

Labels:
- Forward returns for horizons $H \in \{1,3,6,12\}$ months:

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

## Known limitations (current)

- The project is still in the data-collection stage; forecasting/models/portfolio code is roadmap work.
- Free-tier symbols may be restricted by FMP plan.
