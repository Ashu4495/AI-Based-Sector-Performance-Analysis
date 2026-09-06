# Rules.md — Development Guardrails

Purpose: keep the project scope tight for a 2–3 week MVP and avoid common scope-creep traps in ML side projects.

## 1. Data Sources

**Use:**
- `yfinance` — the only data source for OHLCV data (sector indices + NIFTY 50).

**Avoid:**
- No ETF data (Nippon/ICICI sector ETFs) — cross-referencing was explicitly cancelled for v1.
- No macroeconomic data (RBI rates, FRED, inflation, USD-INR).
- No news/sentiment APIs (NewsAPI, RSS feeds, FinBERT, or any NLP sentiment source).
- No alternative/paid data vendors (Bloomberg, Refinitiv, etc.) — not needed at this scope and adds cost/complexity.

If a feature idea requires a data source outside `yfinance`, it belongs in a "Future Work" note, not in v1 code.

## 2. Modeling Libraries

**Use:**
- `scikit-learn` for both models:
  - Forecasting → `LinearRegression` or `Ridge` only.
  - Classification → `RandomForestClassifier` only.
- `shap` for explainability on the classifier.
- `pandas-ta` for technical indicators.

**Avoid:**
- No deep learning for forecasting (no LSTM, GRU, Transformer-based models).
- No `Prophet` or other specialized time-series libraries.
- No AutoML frameworks (they obscure the modeling decisions you want to be able to explain in an interview).
- No ensembling forecasting models with the classifier — keep the two models' responsibilities separate and legible.

Rationale: the goal is a system you can fully explain, feature-by-feature and decision-by-decision, in a job interview. Simpler, interpretable models that you understand deeply are more valuable here than complex models you can't defend under questioning.

## 3. Output Format Rules

- The health output is a **categorical label only**: `Strong Buy`, `Buy`, `Neutral`, `Avoid`, `Strong Avoid`.
- Never surface a raw numeric health score in the UI or API response — if the classifier internally uses `predict_proba`, use it only to pick the label/order the leaderboard, not to display a number to the user.
- Forecast output may be numeric (predicted return %) since that's a distinct, clearly-labeled output from the health classification.

## 4. Frontend

**Use:**
- React (Vite) + Tailwind CSS + a charting library (Recharts or Chart.js).
- Both light and dark theme support from the start (see `design.md`).

**Avoid:**
- No Streamlit, Dash, or Gradio — the frontend must be a custom React build.
- No UI component kit that fights the custom design direction (avoid default Bootstrap/Material look — see `design.md` for visual direction).

## 5. Error Handling

- **Data fetch failures**: wrap all `yfinance` calls in try/except; on failure, fall back to the last successfully cached dataset and surface a clear "data may be stale as of [date]" notice in the API response — never crash the pipeline on a single failed ticker fetch.
- **Missing/partial data**: forward-fill short gaps (≤2 trading days) only; longer gaps should exclude that sector from that day's leaderboard rather than silently interpolating.
- **Model inference failures**: API endpoints must catch prediction errors and return a structured error response (HTTP 503 with a clear message), never a raw stack trace to the frontend.
- **Frontend API failures**: show an explicit error/empty state per component (e.g., "Couldn't load forecast for this sector — try again"), never a blank or infinitely-loading UI.
- **Logging**: all pipeline and API errors logged with timestamp, sector, and operation — no silent failures anywhere in the pipeline.
- **Input validation**: validate sector identifiers against a fixed allow-list (the 8 sectors + benchmark) at the API layer; reject anything else with HTTP 400.

## 6. Scope Discipline

- Every new feature idea should be checked against `PRD.md` §7 (Non-Goals) before being added.
- If a change would require a new data source, a new model type, or Streamlit, stop and flag it explicitly rather than adding it quietly.
