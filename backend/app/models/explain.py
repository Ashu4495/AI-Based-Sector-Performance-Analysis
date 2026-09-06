"""
SHAP Explainability Module for SectorAI.
Uses TreeExplainer to compute feature attributions for the RandomForestClassifier predictions.
Maps raw feature names to human-readable descriptions and extracts top positive/negative drivers.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import shap

from backend.app.core.logging import logger
from backend.app.features.engineer import ALL_FEATURE_COLUMNS, FEATURE_DISPLAY_NAMES
from backend.app.models.train_classifier import load_classifier_model

_EXPLAINER = None
_MODEL = None


def get_tree_explainer():
    """Lazily initializes and caches SHAP TreeExplainer."""
    global _EXPLAINER, _MODEL
    if _EXPLAINER is None:
        logger.info("Initializing SHAP TreeExplainer...")
        _MODEL = load_classifier_model()
        _EXPLAINER = shap.TreeExplainer(_MODEL)
    return _EXPLAINER, _MODEL


def explain_prediction(
    feature_row: pd.Series or pd.DataFrame,
    predicted_label: Optional[str] = None,
    top_n: int = 4
) -> List[Dict[str, any]]:
    """
    Computes SHAP values for a single sector prediction row and returns the top N contributing features.
    
    Returns a list of dictionaries with:
    - feature: raw feature name
    - display_name: human-readable feature description
    - feature_value: the actual value of the feature
    - shap_value: the attribution impact on the predicted label
    - direction: 'positive' (supports the label) or 'negative' (pulls away)
    - description: clear explanation sentence
    """
    explainer, model = get_tree_explainer()

    if isinstance(feature_row, pd.Series):
        X_single = pd.DataFrame([feature_row[ALL_FEATURE_COLUMNS]])
    else:
        X_single = feature_row[ALL_FEATURE_COLUMNS].copy()

    # Get class index for predicted label
    classes = list(model.classes_)
    if predicted_label is None or predicted_label not in classes:
        # Predict label if not passed
        predicted_label = model.predict(X_single)[0]

    class_idx = classes.index(predicted_label)

    # Compute SHAP values
    shap_values = explainer.shap_values(X_single)

    # shap_values shape handling:
    # In newer shap versions, shap_values is a list of arrays (one per class) or a 3D array (samples, features, classes)
    if isinstance(shap_values, list):
        class_shaps = shap_values[class_idx][0]
    elif len(shap_values.shape) == 3:
        class_shaps = shap_values[0, :, class_idx]
    else:
        class_shaps = shap_values[0]

    # Combine feature names, values, and shap attribution
    feature_effects = []
    for col_idx, col_name in enumerate(ALL_FEATURE_COLUMNS):
        raw_val = float(X_single[col_name].iloc[0])
        shap_val = float(class_shaps[col_idx])
        disp_name = FEATURE_DISPLAY_NAMES.get(col_name, col_name)

        direction = "positive" if shap_val >= 0 else "negative"
        
        # Format human-friendly description
        if "return" in col_name or "roc" in col_name:
            val_str = f"{raw_val * 100:+.2f}%" if "return" in col_name else f"{raw_val:+.2f}%"
        elif "rsi" in col_name or "volatility" in col_name:
            val_str = f"{raw_val:.1f}" if "rsi" in col_name else f"{raw_val * 100:.1f}% ann."
        else:
            val_str = f"{raw_val:+.4f}" if abs(raw_val) < 1 else f"{raw_val:.2f}"

        desc = f"{disp_name} ({val_str}) {'strongly reinforces' if shap_val > 0.05 else 'supports' if shap_val > 0 else 'dampens'} {predicted_label} signal"

        feature_effects.append({
            "feature": col_name,
            "display_name": disp_name,
            "feature_value": raw_val,
            "formatted_value": val_str,
            "shap_value": round(shap_val, 4),
            "impact_magnitude": abs(shap_val),
            "direction": direction,
            "description": desc
        })

    # Sort by absolute impact magnitude
    feature_effects = sorted(feature_effects, key=lambda x: x["impact_magnitude"], reverse=True)

    return feature_effects[:top_n]


if __name__ == "__main__":
    from backend.app.features.engineer import load_feature_store
    df = load_feature_store()
    sample_row = df[df["Sector"] == "IT"].iloc[-1]
    explanations = explain_prediction(sample_row)
    print(f"\n--- SHAP EXPLANATION FOR SECTOR IT ---")
    print(f"Date: {sample_row['Date'].strftime('%Y-%m-%d')}")
    for exp in explanations:
        print(f"[{exp['direction'].upper()}] {exp['display_name']:40} | Value: {exp['formatted_value']:10} | SHAP: {exp['shap_value']:+.4f}")
        print(f"  -> {exp['description']}")
