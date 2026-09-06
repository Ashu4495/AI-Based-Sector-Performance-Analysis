"""
Unit tests for Feature Engineering module (backend/app/features/engineer.py).
Tests feature calculation, lookahead bias absence, and target label generation.
"""

import numpy as np
import pandas as pd
import pytest

from backend.app.core.config import HEALTH_LABELS, SECTORS
from backend.app.data.clean import load_clean_data
from backend.app.features.engineer import (
    ALL_FEATURE_COLUMNS,
    build_full_feature_store,
    compute_sector_technical_features,
    generate_forward_targets,
)


def test_no_lookahead_bias():
    """
    Asserts strictly that features computed at time t depend ONLY on data at or before time t.
    Modifying price data at t+10 must NOT change any feature value at index t.
    """
    # Create synthetic series
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=100, freq="B")
    prices = 100 + np.cumsum(np.random.randn(100) * 2)
    highs = prices + np.abs(np.random.randn(100))
    lows = prices - np.abs(np.random.randn(100))
    volumes = np.random.randint(1000, 5000, size=100).astype(float)

    df_orig = pd.DataFrame({
        "Date": dates,
        "Open": prices,
        "High": highs,
        "Low": lows,
        "Close": prices,
        "Volume": volumes,
        "Sector": "IT",
        "Ticker": "^CNXIT"
    })

    # Compute features on original data
    features_orig = compute_sector_technical_features(df_orig)

    # Modify future data starting at index 70
    df_perturbed = df_orig.copy()
    df_perturbed.loc[70:, "Close"] = df_perturbed.loc[70:, "Close"] * 2.5
    df_perturbed.loc[70:, "High"] = df_perturbed.loc[70:, "High"] * 2.5
    df_perturbed.loc[70:, "Low"] = df_perturbed.loc[70:, "Low"] * 2.5

    features_perturbed = compute_sector_technical_features(df_perturbed)

    # Features at index <= 69 must be EXACTLY identical
    for col in ALL_FEATURE_COLUMNS:
        if col in features_orig.columns:
            orig_vals = features_orig.loc[:69, col].dropna()
            pert_vals = features_perturbed.loc[:69, col].dropna()
            assert np.allclose(orig_vals.values, pert_vals.values, equal_nan=True), (
                f"Lookahead bias detected in feature '{col}'!"
            )


def test_forward_target_generation():
    """Tests forward return calculations and health label categorical mappings."""
    dates = pd.date_range("2023-01-01", periods=30, freq="B")
    # Monotonically increasing close prices
    close = [100.0 * (1.002 ** i) for i in range(30)]
    df = pd.DataFrame({
        "Date": dates,
        "Close": close,
        "Sector": "IT",
        "Ticker": "^CNXIT"
    })

    df_targets = generate_forward_targets(df)

    # Verify 5-day forward return at t=0
    expected_5d = (close[5] / close[0]) - 1.0
    actual_5d = df_targets.loc[0, "target_forward_return_5d"]
    assert np.isclose(actual_5d, expected_5d), f"5d forward return mismatch: {actual_5d} vs {expected_5d}"

    # Verify target labels belong strictly to HEALTH_LABELS or NaN
    labels = df_targets["target_label"].dropna().unique()
    for lbl in labels:
        assert lbl in HEALTH_LABELS, f"Invalid label '{lbl}' found!"


def test_full_feature_pipeline():
    """Tests full feature extraction on cleaned data."""
    clean_df = load_clean_data()
    features_df, meta = build_full_feature_store(clean_df)

    assert not features_df.empty
    assert meta["total_feature_rows"] > 5000

    # Ensure all required features are present and finite
    for col in ALL_FEATURE_COLUMNS:
        assert col in features_df.columns, f"Feature {col} missing from features table"
        assert not np.isinf(features_df[col]).any(), f"Infinite values found in feature {col}"
        assert not features_df[col].isna().any(), f"NaN values found in feature {col}"

    # Ensure all sectors + benchmark are represented
    sectors = features_df["Sector"].unique()
    for s in SECTORS.keys():
        assert s in sectors, f"Sector {s} missing from feature store"
