"""
Exploratory Data Analysis (EDA) Script for SectorAI.
Generates summary statistics, correlation matrices, volatility profiles,
and relative performance rankings across all 8 NSE sectors vs NIFTY 50.
"""

from pathlib import Path
import pandas as pd
import numpy as np

from backend.app.core.config import SECTORS, BENCHMARK
from backend.app.features.engineer import load_feature_store, ALL_FEATURE_COLUMNS


def run_eda():
    print("=== SECTORAI EXPLORATORY DATA ANALYSIS ===")
    df = load_feature_store()
    
    print(f"\n1. Feature Store Overview:")
    print(f"Total Rows: {len(df)}")
    print(f"Sectors: {df['Sector'].unique()}")
    print(f"Date Span: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
    
    print("\n2. Sector Volatility and Return Comparison (Annualized):")
    stats = []
    for sector in df["Sector"].unique():
        sec_df = df[df["Sector"] == sector]
        ann_vol = sec_df["volatility_20d"].mean() * 100
        avg_1m_ret = sec_df["return_20d"].mean() * 100
        max_1m_ret = sec_df["return_20d"].max() * 100
        min_1m_ret = sec_df["return_20d"].min() * 100
        stats.append({
            "Sector": sector,
            "Name": SECTORS.get(sector, {}).get("name", sector),
            "Avg Ann Volatility (%)": round(ann_vol, 2),
            "Avg 20d Return (%)": round(avg_1m_ret, 2),
            "Max 20d Return (%)": round(max_1m_ret, 2),
            "Min 20d Return (%)": round(min_1m_ret, 2),
        })
    stats_df = pd.DataFrame(stats)
    print(stats_df.to_string(index=False))

    print("\n3. Health Label Distribution across Sectors:")
    label_dist = df[df["Sector"] != "NIFTY50"]["target_label"].value_counts(dropna=False)
    for label, count in label_dist.items():
        pct = (count / len(df[df["Sector"] != "NIFTY50"])) * 100
        print(f"  {str(label):15}: {count:5} rows ({pct:5.2f}%)")

    print("\n4. Feature Correlation with 5-Day Forward Return:")
    corrs = {}
    valid_target_df = df.dropna(subset=["target_forward_return_5d"])
    for col in ALL_FEATURE_COLUMNS:
        corr = valid_target_df[col].corr(valid_target_df["target_forward_return_5d"])
        corrs[col] = corr
    sorted_corrs = sorted(corrs.items(), key=lambda x: abs(x[1]), reverse=True)
    for col, corr in sorted_corrs[:10]:
        print(f"  {col:25}: {corr:+.4f}")

    print("\n=== EDA Complete ===")


if __name__ == "__main__":
    run_eda()
