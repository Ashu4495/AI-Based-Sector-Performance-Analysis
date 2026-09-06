"""
Inference & Prediction Utilities for MarketPulse AI.
Loads saved model artifacts (Ridge Forecast & RandomForest Health Classifier)
and exposes real-time inference functions for individual sectors and the full leaderboard.
"""

from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from backend.app.core.config import HEALTH_LABELS, SECTORS
from backend.app.core.logging import logger
from backend.app.features.engineer import ALL_FEATURE_COLUMNS, load_feature_store
from backend.app.models.explain import explain_prediction
from backend.app.models.train_classifier import load_classifier_model
from backend.app.models.train_forecast import load_forecast_model

# Rank ordering for leaderboard sorting (Strictly categorical rank, no raw score shown)
LABEL_RANK = {
    "Strong Buy": 5,
    "Buy": 4,
    "Neutral": 3,
    "Avoid": 2,
    "Strong Avoid": 1
}


def get_latest_sector_row(sector_key: str, df: Optional[pd.DataFrame] = None) -> Optional[pd.Series]:
    """Retrieves the latest available feature row for a given sector."""
    if df is None:
        df = load_feature_store()
    
    sec_df = df[df["Sector"] == sector_key].sort_values("Date")
    if sec_df.empty:
        return None
    return sec_df.iloc[-1]


def predict_forecast_for_row(feature_row: pd.Series, forecast_pipeline=None) -> Dict[str, any]:
    """
    Predicts 5-day return with confidence intervals and direction for a feature row.
    """
    if forecast_pipeline is None:
        forecast_pipeline = load_forecast_model()

    X_single = pd.DataFrame([feature_row[ALL_FEATURE_COLUMNS]])
    pred_return = float(forecast_pipeline.predict(X_single)[0])

    # 1-sigma standard error band (approx 68% confidence)
    # Default standard error ~ 2.5% based on cross-validation residual std
    std_err = 0.025
    lower_bound = pred_return - 1.0 * std_err
    upper_bound = pred_return + 1.0 * std_err

    if pred_return >= 0.015:
        direction = "Bullish"
    elif pred_return <= -0.015:
        direction = "Bearish"
    else:
        direction = "Neutral"

    return {
        "predicted_return_5d": round(pred_return, 4),
        "predicted_return_pct": round(pred_return * 100, 2),
        "confidence_lower_pct": round(lower_bound * 100, 2),
        "confidence_upper_pct": round(upper_bound * 100, 2),
        "direction": direction,
        "horizon_days": 5
    }


def predict_health_for_row(feature_row: pd.Series, classifier_model=None, include_shap: bool = True) -> Dict[str, any]:
    """
    Predicts health classification label (Strong Buy -> Strong Avoid) and extracts SHAP drivers.
    Strictly outputs categorical label, never raw numeric probabilities.
    """
    if classifier_model is None:
        classifier_model = load_classifier_model()

    X_single = pd.DataFrame([feature_row[ALL_FEATURE_COLUMNS]])
    label = str(classifier_model.predict(X_single)[0])

    drivers = []
    if include_shap:
        try:
            drivers = explain_prediction(feature_row, predicted_label=label, top_n=4)
        except Exception as e:
            logger.warning(f"Could not calculate SHAP explanation: {str(e)}")

    return {
        "health_label": label,
        "rank": LABEL_RANK.get(label, 3),
        "top_drivers": drivers
    }


def get_sector_prediction(sector_key: str) -> Optional[Dict[str, any]]:
    """
    Returns full prediction bundle (health label + forecast + SHAP) for a sector.
    """
    if sector_key not in SECTORS:
        raise ValueError(f"Unknown sector key '{sector_key}'")

    row = get_latest_sector_row(sector_key)
    if row is None:
        return None

    forecast_model = load_forecast_model()
    classifier_model = load_classifier_model()

    forecast = predict_forecast_for_row(row, forecast_model)
    health = predict_health_for_row(row, classifier_model, include_shap=True)

    return {
        "sector": sector_key,
        "sector_name": SECTORS[sector_key]["name"],
        "display_name": SECTORS[sector_key]["display_name"],
        "as_of_date": row["Date"].strftime("%Y-%m-%d"),
        "latest_close": float(row["Close"]),
        "change_20d_pct": round(float(row["return_20d"]) * 100, 2) if pd.notna(row["return_20d"]) else 0.0,
        "health_label": health["health_label"],
        "forecast": forecast,
        "top_drivers": health["top_drivers"],
    }


def get_all_sectors_leaderboard() -> List[Dict[str, any]]:
    """
    Generates leaderboard for all 8 sectors sorted by health label and return momentum.
    """
    df = load_feature_store()
    forecast_model = load_forecast_model()
    classifier_model = load_classifier_model()

    results = []
    for sec_key, sec_meta in SECTORS.items():
        row = get_latest_sector_row(sec_key, df)
        if row is None:
            continue

        forecast = predict_forecast_for_row(row, forecast_model)
        health = predict_health_for_row(row, classifier_model, include_shap=False)

        results.append({
            "sector": sec_key,
            "sector_name": sec_meta["name"],
            "display_name": sec_meta["display_name"],
            "as_of_date": row["Date"].strftime("%Y-%m-%d"),
            "latest_close": round(float(row["Close"]), 2),
            "return_1d_pct": round(float(row["return_1d"]) * 100, 2) if pd.notna(row["return_1d"]) else 0.0,
            "return_5d_pct": round(float(row["return_5d"]) * 100, 2) if pd.notna(row["return_5d"]) else 0.0,
            "return_20d_pct": round(float(row["return_20d"]) * 100, 2) if pd.notna(row["return_20d"]) else 0.0,
            "rel_return_20d_pct": round(float(row["rel_return_20d"]) * 100, 2) if pd.notna(row["rel_return_20d"]) else 0.0,
            "rsi_14": round(float(row["rsi_14"]), 1) if pd.notna(row["rsi_14"]) else 50.0,
            "health_label": health["health_label"],
            "rank": health["rank"],
            "predicted_return_5d_pct": forecast["predicted_return_pct"],
            "direction": forecast["direction"],
        })

    # Sort primarily by health label rank (Strong Buy at top), secondarily by 20-day momentum
    results = sorted(results, key=lambda x: (x["rank"], x["return_20d_pct"]), reverse=True)
    return results


if __name__ == "__main__":
    leaderboard = get_all_sectors_leaderboard()
    print("\n--- SECTORAI LEADERBOARD ---")
    for item in leaderboard:
        print(f"[{item['health_label']:12}] {item['sector']:6} | {item['display_name']:28} | Close: {item['latest_close']:10.2f} | 20d: {item['return_20d_pct']:+5.2f}% | Fwd 5d: {item['predicted_return_5d_pct']:+5.2f}% ({item['direction']})")
