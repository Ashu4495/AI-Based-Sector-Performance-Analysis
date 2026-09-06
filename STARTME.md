# Start SectorAI

Follow these steps to run the complete SectorAI application locally.

## 1. Start the Backend API (FastAPI)
Open a terminal in the root directory of the project and run the following command to start the backend server on port 8000:

```powershell
.venv\Scripts\uvicorn backend.app.main:app --port 8000 --reload
```

## 2. Start the Frontend Application (React/Vite)
Open a **new** terminal in the root directory of the project, navigate to the `frontend` folder, and start the Vite development server:

```powershell
cd frontend
npm run dev
```

Once the Vite server starts, it will display a local URL (usually `http://localhost:5173/` or `http://localhost:5174/`). Open that URL in your browser to view the dashboard!

> **Note:** If you encounter a `[WinError 10013]` or a "port is in use" error when starting the backend, make sure you don't have another instance of the server running in the background holding onto port 8000.



## 3. (Optional) Re-run Data Ingestion or Model Retraining
If you ever want to refresh data or retrain models:

```powershell
# Ingest fresh data
.venv\Scripts\python -m backend.app.data.clean
# Compute features
.venv\Scripts\python -m backend.app.features.engineer
# Retrain models
.venv\Scripts\python -m backend.app.models.train_forecast
.venv\Scripts\python -m backend.app.models.train_classifier
# Re-run rotation backtest
.venv\Scripts\python -m backend.app.backtest.rotation_strategy
```

## 4. (Optional) Run All Tests
```powershell
.venv\Scripts\pytest -v
```
