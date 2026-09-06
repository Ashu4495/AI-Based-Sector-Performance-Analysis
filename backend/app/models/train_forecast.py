"""
Forecasting Model Training Module for MarketPulse AI.
Trains a Ridge Regression model on historical technical and relative-strength features
to predict near-term 5-day sector returns.
Uses strict time-series chronological cross-validation (no random shuffling).
"""

from pathlib import Path
from typing import Dict, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from backend.app.core.config import ARTIFACTS_DIR, BENCHMARK
from backend.app.core.logging import logger
from backend.app.features.engineer import ALL_FEATURE_COLUMNS, load_feature_store

FORECAST_MODEL_PATH = ARTIFACTS_DIR / "forecast_model.joblib"
FORECAST_METRICS_PATH = ARTIFACTS_DIR / "forecast_metrics.json"


def prepare_forecast_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Extracts feature matrix X and target y (5-day forward return).
    Excludes rows where target is NaN (the most recent 5 days).
    """
    # Filter out benchmark from training data if training sector-specific models or keep all sector rows
    train_df = df[df["Sector"] != BENCHMARK["key"]].copy()
    
    # Drop rows with NaN in target
    valid_mask = train_df["target_forward_return_5d"].notna()
    clean_data = train_df[valid_mask].sort_values("Date").reset_index(drop=True)

    X = clean_data[ALL_FEATURE_COLUMNS].copy()
    y = clean_data["target_forward_return_5d"].copy()

    return X, y, clean_data


def train_and_evaluate_forecast_model(
    alpha: float = 10.0,
    n_splits: int = 5
) -> Tuple[Pipeline, Dict[str, any]]:
    """
    Trains Ridge Regression model using TimeSeriesSplit cross-validation.
    """
    logger.info("Starting forecasting model training (Ridge Regression)...")
    df = load_feature_store()
    X, y, clean_data = prepare_forecast_dataset(df)

    logger.info(f"Dataset prepared: {len(X)} samples across {len(ALL_FEATURE_COLUMNS)} features.")

    # Time-series split evaluation
    tscv = TimeSeriesSplit(n_splits=n_splits)
    cv_metrics = []

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("regressor", Ridge(alpha=alpha, random_state=42))
        ])

        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)

        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        # Directional accuracy: sign(actual) == sign(predicted)
        dir_acc = np.mean(np.sign(y_test) == np.sign(preds))

        cv_metrics.append({
            "fold": fold + 1,
            "train_size": len(train_idx),
            "test_size": len(test_idx),
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2),
            "directional_accuracy": float(dir_acc)
        })

    # Train final model on full dataset
    final_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("regressor", Ridge(alpha=alpha, random_state=42))
    ])
    final_pipeline.fit(X, y)

    # Compute in-sample & CV summary metrics
    all_preds = final_pipeline.predict(X)
    overall_mae = mean_absolute_error(y, all_preds)
    overall_rmse = np.sqrt(mean_squared_error(y, all_preds))
    overall_dir_acc = np.mean(np.sign(y) == np.sign(all_preds))

    # Calculate residual standard deviation for confidence interval calculation
    residuals = y - all_preds
    residual_std = float(np.std(residuals))

    metrics_summary = {
        "model_type": "Ridge Regression",
        "alpha": alpha,
        "n_samples": len(X),
        "n_features": len(ALL_FEATURE_COLUMNS),
        "feature_names": ALL_FEATURE_COLUMNS,
        "cv_folds": cv_metrics,
        "cv_mean_mae": float(np.mean([m["mae"] for m in cv_metrics])),
        "cv_mean_rmse": float(np.mean([m["rmse"] for m in cv_metrics])),
        "cv_mean_directional_accuracy": float(np.mean([m["directional_accuracy"] for m in cv_metrics])),
        "overall_mae": float(overall_mae),
        "overall_rmse": float(overall_rmse),
        "overall_directional_accuracy": float(overall_dir_acc),
        "residual_std": residual_std,
        "feature_coefficients": {
            feat: float(coef)
            for feat, coef in zip(ALL_FEATURE_COLUMNS, final_pipeline.named_steps["regressor"].coef_)
        }
    }

    # Save artifact
    try:
        joblib.dump(final_pipeline, FORECAST_MODEL_PATH)
        import json
        with open(FORECAST_METRICS_PATH, "w") as f:
            json.dump(metrics_summary, f, indent=2)
        logger.info(f"Forecast model successfully saved to {FORECAST_MODEL_PATH}")
    except Exception as e:
        logger.error(f"Failed to save forecast model artifact: {str(e)}")

    return final_pipeline, metrics_summary


def load_forecast_model() -> Pipeline:
    """Loads saved forecasting pipeline artifact."""
    if not FORECAST_MODEL_PATH.exists():
        raise FileNotFoundError(f"Forecast model not found at {FORECAST_MODEL_PATH}. Run train_forecast first.")
    return joblib.load(FORECAST_MODEL_PATH)


if __name__ == "__main__":
    model, metrics = train_and_evaluate_forecast_model()
    print("\n--- FORECAST MODEL TRAINING SUMMARY ---")
    print(f"Model: {metrics['model_type']} (alpha={metrics['alpha']})")
    print(f"Samples: {metrics['n_samples']} | Features: {metrics['n_features']}")
    print(f"CV Mean MAE: {metrics['cv_mean_mae']*100:.2f}% | CV Mean RMSE: {metrics['cv_mean_rmse']*100:.2f}%")
    print(f"CV Mean Directional Accuracy: {metrics['cv_mean_directional_accuracy']*100:.2f}%")
    print(f"Overall Directional Accuracy: {metrics['overall_directional_accuracy']*100:.2f}%")
    print("\nTop Positive Coefficients:")
    sorted_coefs = sorted(metrics['feature_coefficients'].items(), key=lambda x: x[1], reverse=True)
    for feat, val in sorted_coefs[:5]:
        print(f"  {feat:25}: {val:+.6f}")
    print("\nTop Negative Coefficients:")
    for feat, val in sorted_coefs[-5:]:
        print(f"  {feat:25}: {val:+.6f}")
