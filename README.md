# Digital Investment Analytics

Digital Investment Analytics is a multi-asset investment decision system-in-progress that targets short to medium-term horizons first, with longer-horizon extensions planned later.

The end goal is to forecast probabilistic future return scenarios (not point predictions), quantify both return and downside risk, rank assets using a tunable risk-return utility, refresh those rankings as new data arrives, and eventually construct a small optimal portfolio (Top-K ≤ 5).

Developer setup and CLI usage live in README_DEV.md.

IMPORTANT: The forecasting models, scenario engine, and portfolio optimizer described below are the target system design (roadmap). The currently implemented code focuses on data collection + persistence.

## Refreshable operating loop (decision clock)

This project is being refocused around a refreshable decision clock for short/medium-horizon predictions. The main operational modeling layer will likely be a daily as-of dataset, while monthly tables remain useful for research and slower backtests.

At each scheduled or event-driven refresh date, the system runs:

1. Data refresh: update newly available raw market, macro, and later semantic data and persist immutable artifacts
2. Feature build: convert raw data into an as-of modeling table using the latest known values at that timestamp
3. Forecasting: generate probabilistic future return distributions for 1W / 2W / 1M / 3M
4. Scenario metrics: derive expected return and tail-risk metrics from sampled scenarios
5. Decisioning: compute utility scores, rank candidates, and compare the new output with the prior saved prediction snapshot
6. Portfolio construction: select Top-K (≤ 5) and optimize weights when portfolio construction becomes active
7. Execution output: produce a reproducible decision bundle for buy / sell / hold review
8. Risk controls: keep conservative overlays and later expand toward richer intraperiod monitoring

## Three-layer architecture (target system)

Layer A — Scenario forecasting (deep learning)
- Input: historical feature windows per asset (e.g., 36–60 months)
- Output: probabilistic future return distributions across short/medium horizons (1W / 2W / 1M / 3M first; longer-term later)

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

- **FRED** — implemented starter macro foundation for core gold features: rates, treasury yields, CPI, FX, VIX
- **Alpha Vantage** — planned for gold/silver prices, commodities, GDP (25 free calls/day)
- **yfinance** — planned for gold futures/ETF with volume, equity indices (no API key needed)
- **FMP** — reserved for US stock fundamentals in later expansion

The current FRED macro starter set is treated as sufficient to begin the next phase: Alpha Vantage gold-series ingestion and the first baseline deep learning model.

All layers are designed so that downstream ML/optimization can read reproducible artifacts from disk.

## Roadmap (Phases 1–4)

### Phase 1 — Data foundation + first gold model

Starting with **Gold** as the first asset before expanding to the full stock universe.

- Use the current FRED macro starter set as the baseline macro foundation
- Add Alpha Vantage gold/silver/commodity series and later yfinance market context
- Build a daily as-of processed dataset plus an optional monthly research table
- Define first gold labels for 1W / 2W / 1M / 3M horizons
- Train an initial supervised deep learning baseline before adding more asset classes
- Save prediction snapshots so refreshed runs can be compared over time

### Phase 2 — Deep quantile model + scenario generation

- Multi-horizon quantile regression model (1W / 2W / 1M / 3M first)
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

## Later research directions

- Add semantic/news features after the numeric gold baseline is stable
- Expand to stocks after the gold pipeline and first baseline model are working
- Explore reinforcement learning for adaptive signal weighting or policy optimization only after the supervised baseline is reliable

## Short-term to-do list

- [ ] Build Alpha Vantage client (`src/alphavantage/`) for gold and related commodity series
- [ ] Pull full-history gold series and persist raw artifacts alongside the current FRED starter macro set
- [ ] Build the first processed as-of dataset in `data/processed/`
- [ ] Define the first target labels for 1W / 2W / 1M / 3M prediction horizons
- [ ] Train the first deep learning baseline for gold
- [ ] Save prediction snapshots and evaluation outputs for rerun comparison
- [ ] Add yfinance market-context features if the first baseline needs more support
- [ ] Expand to stocks after the gold baseline is stable
- [ ] Add semantic/news data after the numeric baseline is stable

## For developers

- See README_DEV.md for CLI-first quick start, configuration, data output layout, and testing notes.

## License

MIT

## Author

tedgt97 - https://github.com/tedgt97