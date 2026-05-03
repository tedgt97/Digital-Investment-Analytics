# Digital Investment Analytics

Digital Investment Analytics is a multi-asset investment decision system-in-progress that targets medium to long-term horizons.

The end goal is to forecast probabilistic future return scenarios (not point predictions), quantify both return and downside risk, rank assets using a tunable risk–return utility, and construct a small optimal portfolio (Top-K ≤ 5) that is rebalanced monthly.

Developer setup and CLI usage live in README_DEV.md.

IMPORTANT: The forecasting models, scenario engine, and portfolio optimizer described below are the target system design (roadmap). The currently implemented code focuses on data collection + persistence.

## Monthly operating loop (decision clock)

This project is designed around a monthly decision clock over a fixed universe (target: ~80–90 stocks + select ETFs).

At each rebalance date (month-end, or the first trading day after), the system runs:

1. Data refresh: update raw market/fundamental data and persist immutable artifacts
2. Feature build: convert raw data into a monthly modeling table (rolling windows)
3. Forecasting: generate probabilistic return distributions for 1M / 3M / 6M / 12M
4. Scenario metrics: derive expected return and tail-risk metrics from sampled scenarios
5. Decisioning: compute utility scores and rank candidates (long + optional short)
6. Portfolio construction: select Top-K (≤ 5) and optimize weights (cash allowed)
7. Execution output: produce a trade list to rebalance to target weights
8. Risk controls: enforce conservative stop / force-sale rules at monthly boundaries (daily monitoring is a future phase)

## Three-layer architecture (target system)

Layer A — Scenario forecasting (deep learning)
- Input: historical feature windows per asset (e.g., 36–60 months)
- Output: probabilistic future return distributions across horizons (1/3/6/12 months)

Layer B — Scenario → risk/return engine
- Sample many return scenarios from predicted distributions
- Compute scenario-based metrics (mean return, probability of loss, VaR/ES)

Layer C — Decision making & portfolio construction
- Convert metrics into a utility score per asset
- Select Top-K candidates and optimize portfolio weights under constraints

## What exists today

Implemented data collection layers today:

- **FMP** — Python client (`FMPClient`) for price history, quotes, income statements, and company profiles
- **FRED** — Python client (`FREDClient`) for macro series metadata + observations
- CLI-first downloads that persist results locally as Parquet/JSON for downstream modeling
- Live API tests covering both FMP and FRED clients
- Lightweight request-usage tracking to help stay within FMP free-tier limits

Multi-source data architecture for gold trend analysis:

- **FRED** — implemented foundation for core macro data: interest rates, treasury yields, CPI, FX, VIX
- **Alpha Vantage** — planned for gold/silver prices, commodities, GDP (25 free calls/day)
- **yfinance** — planned for gold futures/ETF with volume, equity indices (no API key needed)
- **FMP** — reserved for US stock fundamentals in later expansion

All layers are designed so that downstream ML/optimization can read reproducible artifacts from disk.

## Roadmap (Phases 1–4)

### Phase 1 — Data foundation + baseline signals

Starting with **Gold** as the first asset before expanding to the full stock universe.

- Multi-source data ingestion (FRED, Alpha Vantage, yfinance) and immutable storage
- Gold-focused feature set: price, rates, FX, inflation, VIX, commodities, central bank activity
- Monthly modeling table (rolling features, consistent labels)
- Baseline signals for sanity checks + benchmarking (before deep learning)
- Walk-forward monthly backtest harness (benchmark vs buy-and-hold gold)

### Phase 2 — Deep quantile model + scenario generation

- Multi-horizon quantile regression model (1/3/6/12 months)
- Quantile → empirical distribution conversion and scenario sampling
- Scenario-based metrics (expected return, probability of loss, VaR/ES)
- Calibration and evaluation (pinball loss, backtest comparisons)

### Phase 3 — Portfolio optimization + long/short decision engine

- Utility-based ranking with tunable risk preferences
- Long/short handling with conservative eligibility gates
- Scenario-based portfolio optimization with constraints (gross exposure, cash, concentration penalties)
- Trade list generation with transaction-cost / tax drag assumptions

### Phase 4 — Dynamic stop / force-sale optimization (future)

- Simulate future price paths and evaluate candidate stop levels
- Choose stop levels that maximize expected utility under scenarios
- Upgrade risk controls from monthly checks to daily monitoring

## Short-term to-do list

- [ ] Build Alpha Vantage client (`src/alphavantage/`) — gold price, commodities, GDP
- [ ] Add yfinance wrapper (`src/yfinance_/`) — gold volume, equity indices
- [ ] Initial gold data pull: full history for all gold-relevant series
- [ ] Consolidate raw data into ML-ready panel (`data/processed/`)
- [ ] EDA notebook: gold price vs macro features exploration
- [ ] Feature engineering: rolling windows, returns, regime indicators
- [ ] First deep learning model: gold return forecasting
- [ ] Expand data sources and models to US equities

## For developers

- See README_DEV.md for CLI-first quick start, configuration, data output layout, and testing notes.

## License

MIT

## Author

tedgt97 - https://github.com/tedgt97