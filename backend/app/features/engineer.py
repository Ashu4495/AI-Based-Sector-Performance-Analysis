"""
Feature Engineering Module for MarketPulse AI.
Transforms cleaned OHLCV data into a structured feature store with:
- Technical indicators (RSI, MACD, ROC, ATR, OBV, Moving Averages)
- Benchmark-relative strength metrics vs. NIFTY 50
- Forward targets for forecasting (5-day return) and classification (20-day return & health label)
Strictly avoids lookahead bias in all feature calculations.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import pandas_ta as ta

from backend.app.core.config import (
    BENCHMARK,
    FORECAST_HORIZON_DAYS,
    HEALTH_LABELS,
    LABEL_FORWARD_DAYS,
    SECTORS,
    STORAGE_DIR,
)
from backend.app.core.logging import logger

FEATURES_PARQUET_PATH = STORAGE_DIR / "features.parquet"
FEATURES_CSV_PATH = STORAGE_DIR / "features.csv"

# Feature column definitions for model consumption
MOMENTUM_FEATURES = ["rsi_14", "macd", "macd_signal", "macd_hist", "roc_10", "roc_20"]
VOLATILITY_FEATURES = ["volatility_5d", "volatility_20d", "atr_14", "atr_ratio"]
RETURN_FEATURES = ["return_1d", "return_5d", "return_20d"]
TREND_FEATURES = ["price_to_ema20", "price_to_sma50", "ema20_to_sma50"]
RELATIVE_STRENGTH_FEATURES = ["rel_return_5d", "rel_return_20d", "ratio_to_benchmark", "ratio_trend_20d"]
VOLUME_FEATURES = ["volume_pct_change_5d", "volume_ratio_20d"]

ALL_FEATURE_COLUMNS = (
    RETURN_FEATURES
    + MOMENTUM_FEATURES
    + VOLATILITY_FEATURES
    + TREND_FEATURES
    + RELATIVE_STRENGTH_FEATURES
    + VOLUME_FEATURES
)

# Friendly human-readable names for SHAP explanations
FEATURE_DISPLAY_NAMES = {
    "return_1d": "1-Day Price Return",
    "return_5d": "5-Day Rolling Return",
    "return_20d": "20-Day Rolling Return (1 Month)",
    "rsi_14": "14-Day Relative Strength Index (RSI)",
    "macd": "MACD Fast Line",
    "macd_signal": "MACD Signal Line",
    "macd_hist": "MACD Histogram (Momentum Divergence)",
    "roc_10": "10-Day Rate of Change (ROC)",
    "roc_20": "20-Day Rate of Change (ROC)",
    "volatility_5d": "5-Day Short-Term Volatility",
    "volatility_20d": "20-Day Monthly Volatility",
    "atr_14": "14-Day Average True Range (ATR)",
    "atr_ratio": "ATR as % of Price",
    "price_to_ema20": "Price vs. 20-Day EMA Distance",
    "price_to_sma50": "Price vs. 50-Day SMA Distance",
    "ema20_to_sma50": "20-Day EMA vs. 50-Day SMA Spread",
    "rel_return_5d": "5-Day Relative Return vs. NIFTY 50",
    "rel_return_20d": "20-Day Relative Return vs. NIFTY 50",
    "ratio_to_benchmark": "Price Ratio vs. NIFTY 50",
    "ratio_trend_20d": "20-Day Relative Strength Ratio Trend",
    "volume_pct_change_5d": "5-Day Volume Growth",
    "volume_ratio_20d": "Volume vs. 20-Day Average"
}


def compute_sector_technical_features(df_sector: pd.DataFrame) -> pd.DataFrame:
    """
    Computes single-sector technical indicators using only historical data up to t (no future data).
    """
    df = df_sector.copy().sort_values("Date").reset_index(drop=True)

    # 1. Rolling Returns
    df["return_1d"] = df["Close"].pct_change(1)
    df["return_5d"] = df["Close"].pct_change(5)
    df["return_20d"] = df["Close"].pct_change(20)

    # 2. Momentum Indicators
    df["rsi_14"] = ta.rsi(df["Close"], length=14)

    macd_df = ta.macd(df["Close"], fast=12, slow=26, signal=9)
    if macd_df is not None and not macd_df.empty:
        df["macd"] = macd_df.iloc[:, 0]
        df["macd_hist"] = macd_df.iloc[:, 1]
        df["macd_signal"] = macd_df.iloc[:, 2]
    else:
        ema12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema26 = df["Close"].ewm(span=26, adjust=False).mean()
        df["macd"] = ema12 - ema26
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df["macd_hist"] = df["macd"] - df["macd_signal"]

    df["roc_10"] = ta.roc(df["Close"], length=10)
    if df["roc_10"] is None or df["roc_10"].isna().all():
        df["roc_10"] = df["Close"].pct_change(10) * 100

    df["roc_20"] = ta.roc(df["Close"], length=20)
    if df["roc_20"] is None or df["roc_20"].isna().all():
        df["roc_20"] = df["Close"].pct_change(20) * 100

    # 3. Volatility Indicators
    df["volatility_5d"] = df["return_1d"].rolling(window=5).std() * np.sqrt(252)
    df["volatility_20d"] = df["return_1d"].rolling(window=20).std() * np.sqrt(252)
    
    atr = ta.atr(df["High"], df["Low"], df["Close"], length=14)
    if atr is not None:
        df["atr_14"] = atr
    else:
        tr = np.maximum(
            df["High"] - df["Low"],
            np.maximum(
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs()
            )
        )
        df["atr_14"] = tr.rolling(window=14).mean()

    df["atr_ratio"] = df["atr_14"] / df["Close"]

    # 4. Trend & Moving Averages
    df["ema_20"] = ta.ema(df["Close"], length=20)
    df["sma_50"] = ta.sma(df["Close"], length=50)

    # Relative distances
    df["price_to_ema20"] = (df["Close"] - df["ema_20"]) / df["ema_20"]
    df["price_to_sma50"] = (df["Close"] - df["sma_50"]) / df["sma_50"]
    df["ema20_to_sma50"] = (df["ema_20"] - df["sma_50"]) / df["sma_50"]

    # 5. Volume Indicators
    vol = df["Volume"].replace(0, np.nan).ffill().fillna(1.0)
    df["volume_pct_change_5d"] = vol.pct_change(5).fillna(0.0)
    vol_sma20 = vol.rolling(window=20).mean()
    df["volume_ratio_20d"] = (vol / vol_sma20).fillna(1.0)

    return df


def compute_relative_strength_features(
    sector_features: pd.DataFrame,
    benchmark_features: pd.DataFrame
) -> pd.DataFrame:
    """
    Computes relative strength metrics for a sector against the NIFTY 50 benchmark.
    """
    bm = benchmark_features[["Date", "Close", "return_5d", "return_20d"]].rename(
        columns={
            "Close": "bm_close",
            "return_5d": "bm_return_5d",
            "return_20d": "bm_return_20d"
        }
    )

    merged = pd.merge(sector_features, bm, on="Date", how="inner").sort_values("Date").reset_index(drop=True)

    # 1. Relative Return Spreads
    merged["rel_return_5d"] = merged["return_5d"] - merged["bm_return_5d"]
    merged["rel_return_20d"] = merged["return_20d"] - merged["bm_return_20d"]

    # 2. Sector / Benchmark Price Ratio
    merged["ratio_to_benchmark"] = merged["Close"] / merged["bm_close"]
    ratio_sma20 = merged["ratio_to_benchmark"].rolling(window=20).mean()
    merged["ratio_trend_20d"] = (merged["ratio_to_benchmark"] - ratio_sma20) / ratio_sma20

    # Drop intermediate benchmark columns
    merged = merged.drop(columns=["bm_close", "bm_return_5d", "bm_return_20d"])

    return merged


def generate_forward_targets(df_sector: pd.DataFrame) -> pd.DataFrame:
    """
    Generates forward target returns and health classification labels.
    - target_forward_return_5d: Return from Close[t] to Close[t+5] (for forecasting)
    - target_forward_return_20d: Return from Close[t] to Close[t+20] (for classification)
    - target_label: Categorical health label based on 20-day forward return:
        Strong Buy   (>= 4.0% forward return)
        Buy          (1.0% to 4.0% forward return)
        Neutral      (-1.0% to +1.0% forward return)
        Avoid        (-4.0% to -1.0% forward return)
        Strong Avoid (< -4.0% forward return)
    """
    df = df_sector.copy().sort_values("Date").reset_index(drop=True)

    # Forward returns
    df["target_forward_return_5d"] = (df["Close"].shift(-FORECAST_HORIZON_DAYS) / df["Close"]) - 1.0
    df["target_forward_return_20d"] = (df["Close"].shift(-LABEL_FORWARD_DAYS) / df["Close"]) - 1.0

    labels = pd.Series(index=df.index, dtype=object)
    fwd = df["target_forward_return_20d"]
    valid_mask = fwd.notna()

    labels[valid_mask & (fwd >= 0.04)] = "Strong Buy"
    labels[valid_mask & (fwd >= 0.01) & (fwd < 0.04)] = "Buy"
    labels[valid_mask & (fwd >= -0.01) & (fwd < 0.01)] = "Neutral"
    labels[valid_mask & (fwd >= -0.04) & (fwd < -0.01)] = "Avoid"
    labels[valid_mask & (fwd < -0.04)] = "Strong Avoid"

    df["target_label"] = labels
    return df


def build_full_feature_store(clean_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, any]]:
    """
    Processes all sectors and benchmark through feature engineering, relative strength,
    and target generation pipelines.
    """
    logger.info("Starting feature engineering pipeline...")
    benchmark_key = BENCHMARK["key"]

    # Step 1: Compute single-sector technical indicators for all sectors and benchmark
    sector_dfs = {}
    for sector_name, group in clean_df.groupby("Sector"):
        sector_dfs[sector_name] = compute_sector_technical_features(group)

    if benchmark_key not in sector_dfs:
        raise ValueError(f"Benchmark {benchmark_key} not found in cleaned dataset.")

    benchmark_features = sector_dfs[benchmark_key]

    # Step 2: Compute relative strength and targets for all sectors
    all_processed_sectors = []
    meta = {"sectors": {}, "total_feature_rows": 0, "feature_columns": ALL_FEATURE_COLUMNS}

    for sector_name, df_sec in sector_dfs.items():
        df_with_rel = compute_relative_strength_features(df_sec, benchmark_features)
        df_with_targets = generate_forward_targets(df_with_rel)
        
        # Filter out rows with NaNs in feature columns (first ~50 warm-up days)
        valid_features_df = df_with_targets.dropna(subset=ALL_FEATURE_COLUMNS).reset_index(drop=True)

        if len(valid_features_df) > 0:
            meta["sectors"][sector_name] = {
                "total_rows": len(valid_features_df),
                "labeled_rows": int(valid_features_df["target_label"].dropna().count()),
                "latest_date": valid_features_df["Date"].dropna().max().strftime("%Y-%m-%d"),
                "earliest_date": valid_features_df["Date"].dropna().min().strftime("%Y-%m-%d"),
            }
            all_processed_sectors.append(valid_features_df)

    feature_store_df = pd.concat(all_processed_sectors, ignore_index=True)
    feature_store_df = feature_store_df.sort_values(["Sector", "Date"]).reset_index(drop=True)
    meta["total_feature_rows"] = len(feature_store_df)

    # Persist feature store
    try:
        feature_store_df.to_parquet(FEATURES_PARQUET_PATH, index=False)
        feature_store_df.to_csv(FEATURES_CSV_PATH, index=False)
        logger.info(f"Successfully saved feature store ({len(feature_store_df)} rows) to {FEATURES_PARQUET_PATH}")
    except Exception as e:
        logger.error(f"Failed to persist feature store: {str(e)}")

    return feature_store_df, meta


def load_feature_store() -> pd.DataFrame:
    """Loads feature store from storage."""
    if not FEATURES_PARQUET_PATH.exists():
        raise FileNotFoundError(f"Feature store not found at {FEATURES_PARQUET_PATH}. Run engineer pipeline first.")
    return pd.read_parquet(FEATURES_PARQUET_PATH)


if __name__ == "__main__":
    from backend.app.data.clean import load_clean_data
    clean_df = load_clean_data()
    features_df, meta = build_full_feature_store(clean_df)
    print("\n--- FEATURE ENGINEERING SUMMARY ---")
    print(f"Total Features Table Rows: {meta['total_feature_rows']}")
    print(f"Feature Columns ({len(ALL_FEATURE_COLUMNS)}): {ALL_FEATURE_COLUMNS}")
    for sec, info in meta["sectors"].items():
        print(f"{sec:10} | Rows: {info['total_rows']:5} | Labeled: {info['labeled_rows']:5} | Span: {info['earliest_date']} -> {info['latest_date']}")
