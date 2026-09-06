# phases.md — Build Phases

Target: 1 week MVP. Phases are sequential but can overlap slightly where noted.

## Phase 0 — Setup 
- Initialize Git repo, folder structure (per `Architecture.md`).
- Set up Python virtual environment (backend) and Vite React project (frontend).
- Define the fixed sector list + ticker map (8 sectors + NIFTY 50) in `core/config.py`.
- Confirm `yfinance` pulls clean data for all 9 tickers before building anything else on top.

**Exit criteria**: repo scaffolded, one successful end-to-end data pull for all tickers, committed.

## Phase 1 — Data Pipeline 
- Build `fetch.py`: pull historical OHLCV (5–10 years) for all sectors.
- Build `clean.py`: handle missing days, align trading calendars across indices, validate no gaps > threshold.
- Persist processed raw data to `data/storage/`.

**Exit criteria**: a single clean, aligned OHLCV dataset for all 9 tickers, versioned in storage.

## Phase 2 — Feature Engineering
- Implement indicators via `pandas-ta`: RSI, MACD, ROC, ATR, OBV, moving averages.
- Implement relative-strength features (sector vs. NIFTY 50).
- Produce one unified features table (sector, date, all engineered columns).
- Quick EDA notebook: correlation heatmap, sector volatility comparison, seasonality check — useful later for README visuals.

**Exit criteria**: features table ready, sanity-checked (no lookahead bias, no leakage from future rows).

## Phase 3 — Modeling 
- **Forecasting**: train Linear/Ridge Regression on lagged features to predict next-N-day return. Evaluate with RMSE/MAE via time-series train/test split (no random shuffling — respect chronology).
- **Classification**: define label-generation logic (forward-return-based rule for Strong Buy → Strong Avoid), train `RandomForestClassifier`, evaluate with accuracy/F1 per class.
- Wire up `shap` for per-prediction feature attribution on the classifier.
- Save both models as `.joblib` artifacts.

**Exit criteria**: both models trained and evaluated, metrics documented, SHAP explanations working on sample predictions.

## Phase 4 — Backtest Engine 
- Implement monthly "rotate into current top-labeled sector" simulation using historical labels.
- Compare cumulative returns vs. NIFTY 50 buy-and-hold.
- Store backtest results in a format the API can serve directly.

**Exit criteria**: backtest runs end-to-end on full historical data, produces a clear comparison output.

## Phase 5 — Backend API 
- Build FastAPI app with the 5 endpoints from `Architecture.md` §5.
- Load model artifacts at startup, wire feature/backtest data through the endpoints.
- Add error handling per `Rules.md` §5.

**Exit criteria**: all endpoints return valid JSON, tested via Swagger UI (`/docs`) or Postman.

## Phase 6 — Frontend
- Landing page (per `design.md`).
- Dashboard: sector leaderboard with health labels.
- Sector detail page: price chart, forecast overlay, SHAP explanation panel.
- Backtest page: strategy vs. benchmark chart.
- Light/dark theme toggle.

**Exit criteria**: frontend fully wired to live backend, all pages functional and responsive.

