# Architecture.md — System Architecture

## 1. High-Level App Flow

```
┌──────────────┐     ┌───────────────────┐     ┌────────────────────┐
│  yfinance    │────▶│  Data Pipeline     │────▶│  Feature Store      │
│  (NSE index  │     │  (fetch, clean,    │     │  (processed CSV/    │
│   OHLCV)     │     │   validate)        │     │   parquet files)    │
└──────────────┘     └───────────────────┘     └─────────┬───────────┘
                                                            │
                                                            ▼
                                                ┌────────────────────────┐
                                                │  Feature Engineering    │
                                                │  (indicators, relative  │
                                                │   strength, volatility) │
                                                └─────────┬──────────────┘
                                                            │
                              ┌─────────────────────────────┴───────────────────────────┐
                              ▼                                                          ▼
                ┌───────────────────────────┐                          ┌───────────────────────────────┐
                │  Forecasting Model         │                          │  Health Classification Model   │
                │  (Linear/Ridge Regression)  │                          │  (RandomForestClassifier)      │
                └─────────────┬──────────────┘                          └───────────────┬────────────────┘
                              │                                                          │
                              └───────────────────────┬──────────────────────────────────┘
                                                        ▼
                                          ┌───────────────────────────┐
                                          │  Backtest Engine            │
                                          │  (sector rotation vs NIFTY) │
                                          └─────────────┬──────────────┘
                                                        ▼
                                          ┌───────────────────────────┐
                                          │  FastAPI Backend (REST API) │
                                          └─────────────┬──────────────┘
                                                        ▼
                                          ┌───────────────────────────┐
                                          │  React Frontend (Dashboard) │
                                          └───────────────────────────┘
```

## 2. Component Responsibilities

- **Data Pipeline**: scheduled/manual script pulling OHLCV via `yfinance` for all 8 sectors + NIFTY 50, validating for missing days/nulls, storing as versioned local files.
- **Feature Engineering**: pure-function transforms producing a single features table (one row per sector per day).
- **Forecasting Model**: Linear or Ridge Regression on engineered features, predicting next-N-day return. Deliberately kept simple and interpretable — no LSTM, no Prophet.
- **Health Classification Model**: `RandomForestClassifier` predicting the Strong Buy → Strong Avoid label, with **SHAP** used to explain individual predictions (top feature contributions per sector per day).
- **Backtest Engine**: replays historical labels/forecasts to simulate a monthly sector-rotation strategy vs. NIFTY 50 buy-and-hold.
- **Backend (FastAPI)**: exposes REST endpoints serving model outputs, leaderboard data, and backtest results to the frontend. Keeps the model layer decoupled from the UI.
- **Frontend (React)**: landing page + dashboard views consuming the API; no Streamlit.

## 3. Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Data source | `yfinance` | Only data source used in v1 |
| Data handling | `pandas`, `numpy` | Core data manipulation |
| Technical indicators | `pandas-ta` | RSI, MACD, ATR, OBV, etc. |
| Forecasting model | `scikit-learn` — **Linear Regression / Ridge Regression only** | No LSTM, no Prophet, no deep learning |
| Classification model | `scikit-learn` — `RandomForestClassifier` | Predicts health label |
| Explainability | `shap` | Per-prediction feature attribution |
| Backend API | `FastAPI` + `uvicorn` | Serves processed data & model outputs as JSON |
| Frontend | `React` (Vite), `Tailwind CSS`, `Recharts` or `Chart.js` for charts | No Streamlit |
| Model persistence | `joblib` | Save/load trained models |
| Backtesting | Custom Python module using `pandas` | No external backtest library needed at this scope |
| Version control | Git + GitHub | Clean commit history, README |
| Deployment | Backend: Render/Railway free tier · Frontend: Vercel/Netlify | Public link for resume |

## 4. Folder & File Structure

```
sectorai/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entrypoint
│   │   ├── api/
│   │   │   ├── routes_sectors.py   # /sectors, /sectors/{id}
│   │   │   ├── routes_forecast.py  # /forecast/{sector}
│   │   │   ├── routes_health.py    # /health/{sector}
│   │   │   └── routes_backtest.py  # /backtest
│   │   ├── core/
│   │   │   ├── config.py           # settings, sector ticker map
│   │   │   └── logging.py
│   │   ├── data/
│   │   │   ├── fetch.py            # yfinance pull logic
│   │   │   ├── clean.py            # validation, missing-data handling
│   │   │   └── storage/            # cached raw + processed data files
│   │   ├── features/
│   │   │   └── engineer.py         # indicator + relative strength calc
│   │   ├── models/
│   │   │   ├── train_forecast.py   # Ridge/Linear regression training
│   │   │   ├── train_classifier.py # RandomForestClassifier training
│   │   │   ├── explain.py          # SHAP wiring
│   │   │   ├── predict.py          # inference helpers
│   │   │   └── artifacts/          # saved .joblib model files
│   │   ├── backtest/
│   │   │   └── rotation_strategy.py
│   │   └── schemas/
│   │       └── models.py           # Pydantic response schemas
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── SectorDetail.jsx
│   │   │   └── Backtest.jsx
│   │   ├── components/
│   │   │   ├── Leaderboard.jsx
│   │   │   ├── HealthBadge.jsx
│   │   │   ├── PriceChart.jsx
│   │   │   ├── ForecastChart.jsx
│   │   │   └── ThemeToggle.jsx
│   │   ├── api/
│   │   │   └── client.js           # fetch wrapper for backend API
│   │   ├── context/
│   │   │   └── ThemeContext.jsx    # light/dark mode
│   │   ├── styles/
│   │   │   └── tokens.css          # color/type tokens
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   ├── package.json
│   └── README.md
│
├── notebooks/
│   └── eda.ipynb                   # exploratory analysis, used for README visuals
│
├── docs/
│   ├── PRD.md
│   ├── Architecture.md
│   ├── Rules.md
│   ├── phases.md
│   └── design.md
│
└── README.md                       # top-level project overview
```

## 5. API Endpoints (v1)

| Endpoint | Method | Returns |
|---|---|---|
| `/sectors` | GET | List of sectors with current health label |
| `/sectors/{sector}` | GET | Detail: price history, indicators, forecast, label history |
| `/forecast/{sector}` | GET | Latest forecast value + confidence range |
| `/health/{sector}` | GET | Current label + top SHAP feature contributions |
| `/backtest` | GET | Rotation strategy vs. NIFTY 50 cumulative returns |

## 6. Data Flow Between Layers

1. Data pipeline runs (manually or on schedule) → writes processed feature table to `backend/app/data/storage/`.
2. Model training scripts read the feature table → produce `.joblib` artifacts in `models/artifacts/`.
3. FastAPI loads artifacts at startup → serves predictions/labels via REST.
4. React frontend calls the API on load and on user interaction (sector selection, backtest view) → renders charts and labels.
