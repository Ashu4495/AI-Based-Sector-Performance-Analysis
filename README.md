# MarketPulse AI — AI-Driven NSE Sector Performance & Health Classification Dashboard

MarketPulse AI is an end-to-end AI-driven NSE sectoral index analysis, forecasting, and health classification dashboard with explainability and backtested sector rotation strategies.

## Overview
- **Data Source**: `yfinance` exclusively for 8 NSE sectors + NIFTY 50 benchmark.
- **Forecasting Model**: Linear / Ridge Regression on lagged technical features predicting near-term return.
- **Health Classification Model**: `RandomForestClassifier` with TreeSHAP explainability mapping sectors to discrete labels: `Strong Buy`, `Buy`, `Neutral`, `Avoid`, `Strong Avoid`.
- **Strategy Backtest**: Monthly sector-rotation simulation benchmarked against NIFTY 50 buy-and-hold.
- **Frontend**: Custom React (Vite + Tailwind CSS) with light & dark analyst desk themes, dynamic ticker strip, interactive charts, and SHAP attribution panel.
- **Backend API**: High-performance FastAPI application serving structured JSON responses with comprehensive error handling.

## Running Locally

### 1. Start the Backend API
```bash
# From the root directory:
python -m venv .venv
.venv\Scripts\activate  # (or source .venv/bin/activate on Mac/Linux)
pip install -r requirements.txt
uvicorn backend.app.main:app --port 8000 --reload
```

### 2. Start the Frontend Application
```bash
# From the root directory:
cd frontend
npm install
npm run dev
```

### 3. (Optional) Re-run Data Ingestion or Model Retraining
```bash
# Ingest fresh data
python -m backend.app.data.clean
# Compute features
python -m backend.app.features.engineer
# Retrain models
python -m backend.app.models.train_forecast
python -m backend.app.models.train_classifier
# Re-run rotation backtest
python -m backend.app.backtest.rotation_strategy
```

## Deployment Options (Free)

### Backend (Render / Railway)
- Use **Render** for a free API hosting (with `requirements.txt` and `Procfile` already configured in this repo).
- Just link this repository to Render as a Web Service. Render will use the `Procfile` to start the FastAPI server.
- The `runtime.txt` will enforce the correct Python version.

### Frontend (Vercel / Netlify / Railway)
- For the frontend, deploy the `/frontend` directory to **Vercel** or **Netlify** (completely free!).
- Add the `VITE_API_URL` environment variable pointing to your deployed backend URL (e.g., `https://your-api.onrender.com`).
- Build command: `npm run build`
- Output directory: `dist`
