"""
Unit tests for Machine Learning models and SHAP explainability.
Tests Ridge forecasting, RandomForest health classification, and TreeSHAP feature attributions.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from backend.app.core.config import HEALTH_LABELS, SECTORS
from backend.app.features.engineer import load_feature_store
from backend.app.models.explain import explain_prediction
from backend.app.models.predict import (
    get_all_sectors_leaderboard,
    get_sector_prediction,
    predict_forecast_for_row,
    predict_health_for_row,
)
from backend.app.models.train_classifier import (
    load_classifier_model,
    train_and_evaluate_classifier,
)
from backend.app.models.train_forecast import (
    load_forecast_model,
    train_and_evaluate_forecast_model,
)


def test_forecast_model_training_and_inference():
    """Trains Ridge forecasting model and verifies predictions."""
    model, metrics = train_and_evaluate_forecast_model(n_splits=3)

    assert model is not None
    assert metrics["cv_mean_rmse"] > 0
    assert metrics["n_samples"] > 1000

    # Load saved model artifact
    loaded_model = load_forecast_model()
    assert loaded_model is not None

    # Test single row inference
    df = load_feature_store()
    sample_row = df[df["Sector"] == "IT"].iloc[-1]
    res = predict_forecast_for_row(sample_row, loaded_model)

    assert "predicted_return_pct" in res
    assert "direction" in res
    assert res["direction"] in ["Bullish", "Bearish", "Neutral"]
    assert res["confidence_lower_pct"] < res["confidence_upper_pct"]


def test_classifier_training_and_inference():
    """Trains RandomForest classifier and verifies categorical health labels."""
    clf, metrics = train_and_evaluate_classifier(n_splits=3, n_estimators=50)

    assert clf is not None
    assert metrics["cv_mean_accuracy"] > 0
    assert len(metrics["classes"]) == 5

    # Load saved model artifact
    loaded_clf = load_classifier_model()
    assert loaded_clf is not None

    # Test single row inference
    df = load_feature_store()
    sample_row = df[df["Sector"] == "BANK"].iloc[-1]
    res = predict_health_for_row(sample_row, loaded_clf, include_shap=False)

    assert "health_label" in res
    assert res["health_label"] in HEALTH_LABELS, f"Unexpected health label: {res['health_label']}"
    # Verify NO raw numeric score is exposed as health_label
    assert not isinstance(res["health_label"], (int, float))


def test_shap_explainability():
    """Verifies SHAP TreeExplainer feature attributions for health predictions."""
    df = load_feature_store()
    sample_row = df[df["Sector"] == "AUTO"].iloc[-1]
    
    drivers = explain_prediction(sample_row, top_n=4)

    assert len(drivers) == 4
    for driver in drivers:
        assert "feature" in driver
        assert "display_name" in driver
        assert "formatted_value" in driver
        assert "shap_value" in driver
        assert "direction" in driver
        assert driver["direction"] in ["positive", "negative"]
        assert len(driver["description"]) > 10


def test_leaderboard_generation():
    """Verifies leaderboard ranking for all 8 sectors."""
    leaderboard = get_all_sectors_leaderboard()

    assert len(leaderboard) == len(SECTORS)
    sector_keys = [item["sector"] for item in leaderboard]
    for s in SECTORS.keys():
        assert s in sector_keys

    # Check that rank ordering is non-ascending (Strong Buy at top)
    ranks = [item["rank"] for item in leaderboard]
    for i in range(len(ranks) - 1):
        assert ranks[i] >= ranks[i+1], f"Leaderboard not properly sorted by rank: {ranks}"
