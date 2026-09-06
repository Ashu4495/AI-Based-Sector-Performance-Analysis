# SectorAI — AI-Driven NSE Sector Performance & Health Classification Dashboard

SectorAI is an end-to-end AI-driven NSE sectoral index analysis, forecasting, and health classification dashboard with explainability and backtested sector rotation strategies.

## Overview
- **Data Source**: `yfinance` exclusively for 8 NSE sectors + NIFTY 50 benchmark.
- **Forecasting Model**: Linear / Ridge Regression on lagged technical features predicting near-term return.
- **Health Classification Model**: `RandomForestClassifier` with TreeSHAP explainability mapping sectors to discrete labels: `Strong Buy`, `Buy`, `Neutral`, `Avoid`, `Strong Avoid`.
- **Strategy Backtest**: Monthly sector-rotation simulation benchmarked against NIFTY 50 buy-and-hold.
- **Frontend**: Custom React (Vite + Tailwind CSS) with light & dark analyst desk themes, dynamic ticker strip, interactive charts, and SHAP attribution panel.
- **Backend API**: High-performance FastAPI application serving structured JSON responses with comprehensive error handling.

## Structure
- `backend/`: FastAPI application, feature engineering, and ML models
- `frontend/`: Custom React application
- `notebooks/`: Exploratory data analysis (EDA)
- `docs/`: Product Requirements Document, Architecture, Design specs, Rules, and Phases
