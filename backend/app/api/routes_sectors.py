"""
Sector Routes for MarketPulse AI API.
Serves sector leaderboard and detailed historical series with indicator overlays.
"""

from typing import List
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Path, Query

from backend.app.core.config import ALL_TICKERS, BENCHMARK, SECTORS
from backend.app.core.logging import logger
from backend.app.features.engineer import load_feature_store
from backend.app.models.explain import explain_prediction
from backend.app.models.predict import (
    get_all_sectors_leaderboard,
    predict_forecast_for_row,
    predict_health_for_row,
)
from backend.app.models.train_classifier import load_classifier_model
from backend.app.models.train_forecast import load_forecast_model
from backend.app.schemas.models import (
    HistoricalDataPoint,
    SectorDetailResponse,
    SectorListResponse,
    SectorSummary,
)

router = APIRouter(tags=["Sectors"])


@router.get("/sectors", response_model=SectorListResponse)
def get_sectors():
    """
    Returns full leaderboard of all 8 sectors sorted by health classification label and momentum.
    """
    try:
        leaderboard = get_all_sectors_leaderboard()
        if not leaderboard:
            raise HTTPException(status_code=503, detail="No sector data available.")

        return {
            "as_of_date": leaderboard[0]["as_of_date"],
            "total_sectors": len(leaderboard),
            "sectors": leaderboard
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving /sectors: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Failed to generate sector leaderboard: {str(e)}")


@router.get("/sectors/{sector}", response_model=SectorDetailResponse)
def get_sector_detail(
    sector: str = Path(..., description="Sector key, e.g. IT, BANK, AUTO, PHARMA, FMCG, METAL, ENERGY, REALTY"),
    lookback_days: int = Query(250, description="Number of historical trading sessions to return (default 250 ~ 1 year)")
):
    """
    Returns full sector detail view:
    - Latest health label and top SHAP feature drivers
    - 5-day regression forecast and confidence interval
    - Historical price series with EMA 20, SMA 50, RSI, MACD, and historical health labels
    """
    sector_key = sector.upper().strip()
    if sector_key not in SECTORS:
        valid_keys = ", ".join(SECTORS.keys())
        raise HTTPException(status_code=400, detail=f"Invalid sector '{sector}'. Allowed sectors: {valid_keys}")

    try:
        df = load_feature_store()
        sec_df = df[df["Sector"] == sector_key].sort_values("Date").reset_index(drop=True)

        if sec_df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for sector '{sector_key}'")

        forecast_model = load_forecast_model()
        classifier_model = load_classifier_model()

        latest_row = sec_df.iloc[-1]
        forecast = predict_forecast_for_row(latest_row, forecast_model)
        health = predict_health_for_row(latest_row, classifier_model, include_shap=True)

        # Build historical series
        hist_slice = sec_df.tail(lookback_days).copy()
        
        # Precompute historical health labels for historical points (if not in target_label)
        X_hist = hist_slice[forecast_model.feature_names_in_ if hasattr(forecast_model, "feature_names_in_") else classifier_model.feature_names_in_]
        hist_labels = classifier_model.predict(X_hist)

        history_points = []
        for idx, (_, row) in enumerate(hist_slice.iterrows()):
            history_points.append({
                "date": row["Date"].strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2) if pd.notna(row["Open"]) else round(float(row["Close"]), 2),
                "high": round(float(row["High"]), 2) if pd.notna(row["High"]) else round(float(row["Close"]), 2),
                "low": round(float(row["Low"]), 2) if pd.notna(row["Low"]) else round(float(row["Close"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": float(row["Volume"]) if pd.notna(row["Volume"]) else 0.0,
                "ema_20": round(float(row["ema_20"]), 2) if pd.notna(row["ema_20"]) else None,
                "sma_50": round(float(row["sma_50"]), 2) if pd.notna(row["sma_50"]) else None,
                "rsi_14": round(float(row["rsi_14"]), 1) if pd.notna(row["rsi_14"]) else None,
                "macd": round(float(row["macd"]), 2) if pd.notna(row["macd"]) else None,
                "macd_signal": round(float(row["macd_signal"]), 2) if pd.notna(row["macd_signal"]) else None,
                "macd_hist": round(float(row["macd_hist"]), 2) if pd.notna(row["macd_hist"]) else None,
                "health_label": str(hist_labels[idx])
            })

        sec_meta = SECTORS[sector_key]

        return {
            "sector": sector_key,
            "sector_name": sec_meta["name"],
            "display_name": sec_meta["display_name"],
            "description": sec_meta["description"],
            "as_of_date": latest_row["Date"].strftime("%Y-%m-%d"),
            "latest_close": round(float(latest_row["Close"]), 2),
            "change_20d_pct": round(float(latest_row["return_20d"]) * 100, 2) if pd.notna(latest_row["return_20d"]) else 0.0,
            "health_label": health["health_label"],
            "forecast": {
                "sector": sector_key,
                "sector_name": sec_meta["name"],
                "display_name": sec_meta["display_name"],
                "as_of_date": latest_row["Date"].strftime("%Y-%m-%d"),
                "predicted_return_5d": forecast["predicted_return_5d"],
                "predicted_return_pct": forecast["predicted_return_pct"],
                "confidence_lower_pct": forecast["confidence_lower_pct"],
                "confidence_upper_pct": forecast["confidence_upper_pct"],
                "direction": forecast["direction"],
                "horizon_days": 5
            },
            "top_drivers": health["top_drivers"],
            "price_history": history_points
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving /sectors/{sector}: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch detail for sector '{sector}': {str(e)}")
