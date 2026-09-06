# SectorAI Backend

FastAPI application, data ingestion, feature engineering, and ML model inference for SectorAI.

## Architecture
- `app/api/`: REST endpoints (`/sectors`, `/sectors/{id}`, `/forecast/{sector}`, `/health/{sector}`, `/backtest`)
- `app/core/`: Configuration, ticker maps, and logging
- `app/data/`: yfinance ingestion (`fetch.py`), cleaning & alignment (`clean.py`), local storage
- `app/features/`: Technical indicators & relative strength engineering (`engineer.py`)
- `app/models/`: Linear/Ridge forecast regression, RandomForest classifier, SHAP explainability
- `app/backtest/`: Sector rotation strategy simulation vs. NIFTY 50

## Running
```bash
# Run API server
uvicorn backend.app.main:app --reload --port 8000
```
