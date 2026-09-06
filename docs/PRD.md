# PRD.md — Project Requirements Document

## Project Name
**SectorAI** — AI-Driven NSE Sector Performance & Health Classification Dashboard

## 1. Aim

Build an end-to-end AI system that analyzes NSE sectoral indices and:
1. **Forecasts** near-term sector direction/returns using historical price and technical data.
2. **Classifies each sector's current health** into a clear label — **Strong Buy, Buy, Neutral, Avoid, Strong Avoid** — with no numeric scoring.

The system should read as a professional-grade "sector rotation" analysis tool, similar in spirit to what an equity research analyst would use to decide which sectors to overweight or underweight.

This is a **portfolio project** intended to demonstrate applied ML, financial data engineering, and full-stack product delivery to future employers/recruiters.

## 2. What to Build

- A data pipeline that pulls historical OHLCV data for a fixed set of NSE sectoral indices via `yfinance`.
- A feature engineering layer that computes technical indicators and relative-strength metrics per sector.
- Two ML models:
  - A **forecasting model** (regression) predicting near-term sector return/direction.
  - A **health classification model** mapping engineered features to a **Strong Buy → Strong Avoid** label.
- A backtest module simulating a simple "rotate into the top-labeled sector" strategy vs. the NIFTY 50 benchmark.
- A **React-based web dashboard** (landing page + interactive analysis views) that presents forecasts, health labels, and backtest results.

## 3. Targeted Users

- **Primary**: Recruiters/interviewers evaluating this as a portfolio project (data science / ML / fintech roles).
- **Secondary (illustrative persona)**: A retail investor or finance student who wants a quick, explainable read on "which NSE sectors look strong right now."

The product should be usable and understandable by someone with basic market knowledge — it should not require the viewer to understand ML internals to get value from the dashboard.

## 4. In-Scope Sectors (MVP)

NIFTY IT, NIFTY BANK, NIFTY AUTO, NIFTY PHARMA, NIFTY FMCG, NIFTY METAL, NIFTY ENERGY, NIFTY REALTY — benchmarked against **NIFTY 50**.

Data source: **`yfinance` only** (NSE sectoral index tickers, e.g. `^CNXIT`, `^NSEBANK`, `^CNXAUTO`, etc.). No ETF cross-referencing, no macro data (RBI/FRED), no news/sentiment sources in this version.

## 5. Core Features

### 5.1 Sector Health Classification
- Input: engineered features per sector per day.
- Output: one of **Strong Buy / Buy / Neutral / Avoid / Strong Avoid**.
- Explainability: SHAP values shown per prediction (top contributing features) so the label isn't a black box.

### 5.2 Sector Forecasting
- Input: lagged technical features per sector.
- Output: predicted next-N-day return (continuous) or up/down trend direction.
- Displayed alongside the health label as a "supporting signal," not a competing output.

### 5.3 Sector Leaderboard
- Ranks all sectors by current health label (Strong Buy at top) with underlying key metrics visible (momentum, relative strength, volatility) on demand.

### 5.4 Backtest / Strategy Simulation
- Historical simulation: "if you had rotated monthly into the top-labeled sector, how would that have performed vs. NIFTY 50?"
- Output: cumulative return chart, comparison table (strategy vs. benchmark).

### 5.5 Sector Detail View
- Price chart with overlaid indicators.
- Forecast line vs. actual.
- Health label history over time (how the label has evolved).

## 6. Feature Engineering

Computed per sector, per trading day, using OHLCV data only:

| Category | Features |
|---|---|
| **Returns** | 1-day, 5-day, 20-day rolling returns |
| **Momentum** | RSI, MACD, MACD signal, rate of change (ROC) |
| **Volatility** | Rolling standard deviation (5/20-day), ATR |
| **Relative Strength** | Sector return − NIFTY 50 return (spread), sector/NIFTY 50 price ratio trend |
| **Volume** | Volume % change, On-Balance Volume (OBV) |
| **Trend** | Simple/Exponential moving averages (20, 50-day), price vs. moving average position |

All features are derived solely from `yfinance` OHLCV data — no external data sources.

## 7. Explicit Non-Goals (v1)

- No numeric health score — labels only.
- No ETF data cross-referencing.
- No macroeconomic indicators (interest rates, inflation, USD-INR).
- No news/sentiment/NLP component.
- No live/real-time trading or brokerage integration.
- No Streamlit — the frontend is a custom React application (see `design.md`).

## 8. Success Criteria

- Pipeline reliably pulls and updates data for all 8 sectors + benchmark.
- Both models trained, evaluated, and produce sensible, explainable outputs.
- Backtest shows a clear, honestly-reported comparison (even if the strategy underperforms — that's a valid and defensible portfolio finding).
- Dashboard deployed and publicly accessible via a link shareable on a resume/LinkedIn.
