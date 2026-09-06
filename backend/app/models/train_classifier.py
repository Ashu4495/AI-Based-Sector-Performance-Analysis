"""
Health Classification Model Training Module for SectorAI.
Trains a RandomForestClassifier to classify sector health into 5 discrete labels:
Strong Buy, Buy, Neutral, Avoid, Strong Avoid.
Uses time-series validation and evaluates per-class metrics.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score
from sklearn.model_selection import TimeSeriesSplit

from backend.app.core.config import ARTIFACTS_DIR, BENCHMARK, HEALTH_LABELS
from backend.app.core.logging import logger
from backend.app.features.engineer import ALL_FEATURE_COLUMNS, load_feature_store

CLASSIFIER_MODEL_PATH = ARTIFACTS_DIR / "health_classifier.joblib"
CLASSIFIER_METRICS_PATH = ARTIFACTS_DIR / "health_classifier_metrics.json"


def prepare_classification_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Extracts feature matrix X and target y (health label).
    Excludes benchmark and rows where target_label is NaN (last 20 days).
    """
    train_df = df[df["Sector"] != BENCHMARK["key"]].copy()
    valid_mask = train_df["target_label"].notna()
    clean_data = train_df[valid_mask].sort_values("Date").reset_index(drop=True)

    X = clean_data[ALL_FEATURE_COLUMNS].copy()
    y = clean_data["target_label"].copy()

    return X, y, clean_data


def train_and_evaluate_classifier(
    n_estimators: int = 150,
    max_depth: int = 6,
    min_samples_leaf: int = 10,
    n_splits: int = 5
) -> Tuple[RandomForestClassifier, Dict[str, any]]:
    """
    Trains RandomForestClassifier using TimeSeriesSplit cross-validation.
    """
    logger.info("Starting health classification model training (RandomForestClassifier)...")
    df = load_feature_store()
    X, y, clean_data = prepare_classification_dataset(df)

    logger.info(f"Dataset prepared: {len(X)} labeled samples across {len(HEALTH_LABELS)} categories.")

    tscv = TimeSeriesSplit(n_splits=n_splits)
    cv_metrics = []

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        clf = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        )

        clf.fit(X_train, y_train)
        preds = clf.predict(X_test)

        acc = accuracy_score(y_test, preds)
        f1_macro = f1_score(y_test, preds, average="macro", zero_division=0)
        f1_weighted = f1_score(y_test, preds, average="weighted", zero_division=0)

        cv_metrics.append({
            "fold": fold + 1,
            "train_size": len(train_idx),
            "test_size": len(test_idx),
            "accuracy": float(acc),
            "f1_macro": float(f1_macro),
            "f1_weighted": float(f1_weighted),
        })

    # Train final classifier on all labeled data
    final_clf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    final_clf.fit(X, y)

    # Full dataset predictions & report
    all_preds = final_clf.predict(X)
    overall_acc = accuracy_score(y, all_preds)
    overall_f1_macro = f1_score(y, all_preds, average="macro", zero_division=0)
    overall_f1_weighted = f1_score(y, all_preds, average="weighted", zero_division=0)
    report_dict = classification_report(y, all_preds, output_dict=True, zero_division=0)

    # Feature importances (Gini)
    importances = {
        feat: float(imp)
        for feat, imp in zip(ALL_FEATURE_COLUMNS, final_clf.feature_importances_)
    }

    metrics_summary = {
        "model_type": "RandomForestClassifier",
        "hyperparameters": {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "min_samples_leaf": min_samples_leaf,
            "class_weight": "balanced"
        },
        "classes": list(final_clf.classes_),
        "n_samples": len(X),
        "n_features": len(ALL_FEATURE_COLUMNS),
        "feature_names": ALL_FEATURE_COLUMNS,
        "cv_folds": cv_metrics,
        "cv_mean_accuracy": float(np.mean([m["accuracy"] for m in cv_metrics])),
        "cv_mean_f1_macro": float(np.mean([m["f1_macro"] for m in cv_metrics])),
        "overall_accuracy": float(overall_acc),
        "overall_f1_macro": float(overall_f1_macro),
        "overall_f1_weighted": float(overall_f1_weighted),
        "classification_report": report_dict,
        "feature_importances": importances
    }

    # Save artifacts
    try:
        joblib.dump(final_clf, CLASSIFIER_MODEL_PATH)
        with open(CLASSIFIER_METRICS_PATH, "w") as f:
            json.dump(metrics_summary, f, indent=2)
        logger.info(f"Health classifier successfully saved to {CLASSIFIER_MODEL_PATH}")
    except Exception as e:
        logger.error(f"Failed to save health classifier artifact: {str(e)}")

    return final_clf, metrics_summary


def load_classifier_model() -> RandomForestClassifier:
    """Loads saved classifier model artifact."""
    if not CLASSIFIER_MODEL_PATH.exists():
        raise FileNotFoundError(f"Classifier model not found at {CLASSIFIER_MODEL_PATH}. Run train_classifier first.")
    return joblib.load(CLASSIFIER_MODEL_PATH)


if __name__ == "__main__":
    model, metrics = train_and_evaluate_classifier()
    print("\n--- HEALTH CLASSIFIER TRAINING SUMMARY ---")
    print(f"Model: {metrics['model_type']} | Samples: {metrics['n_samples']}")
    print(f"CV Mean Accuracy: {metrics['cv_mean_accuracy']*100:.2f}% | CV Mean F1 (Macro): {metrics['cv_mean_f1_macro']*100:.2f}%")
    print(f"Overall Accuracy: {metrics['overall_accuracy']*100:.2f}% | Overall F1 (Macro): {metrics['overall_f1_macro']*100:.2f}%")
    print("\nPer-Class Performance:")
    for lbl in HEALTH_LABELS:
        if lbl in metrics["classification_report"]:
            rep = metrics["classification_report"][lbl]
            print(f"  {lbl:15} | Precision: {rep['precision']:.2f} | Recall: {rep['recall']:.2f} | F1: {rep['f1-score']:.2f} (Support: {int(rep['support'])})")
    print("\nTop 5 Important Features:")
    sorted_imps = sorted(metrics["feature_importances"].items(), key=lambda x: x[1], reverse=True)
    for feat, imp in sorted_imps[:5]:
        print(f"  {feat:25}: {imp*100:.2f}%")
