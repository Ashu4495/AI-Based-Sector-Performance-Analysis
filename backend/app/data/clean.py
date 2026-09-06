"""
Data Cleaning & Alignment Module for SectorAI.
Cleans raw OHLCV sector data, aligns trading dates across all 8 sectors and NIFTY 50,
handles short-gap forward fills (<=2 days), filters out invalid values, and validates integrity.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from backend.app.core.config import ALL_TICKERS, BENCHMARK, SECTORS, STORAGE_DIR
from backend.app.core.logging import logger

CLEAN_DATA_PATH = STORAGE_DIR / "clean_sectors.parquet"
CLEAN_DATA_CSV_PATH = STORAGE_DIR / "clean_sectors.csv"


def clean_and_align_sectors(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, any]]:
    """
    Cleans raw OHLCV sector data and aligns all sectors against the benchmark trading calendar.
    
    Rules applied:
    1. Removes any rows with non-positive price values (<= 0).
    2. Drops exact duplicates on (Sector, Date).
    3. Aligns all sectors to the master trading calendar (dates on which NIFTY 50 traded).
    4. Identifies date gaps per sector:
       - If gap <= 2 trading days: forward-fill Close price and set Volume = 0.
       - If gap > 2 trading days: leave as NaN (so downstream logic will exclude sector rather than extrapolate).
    5. Recomputes Open/High/Low for forward-filled rows to match filled Close.
    6. Ensures chronological ordering.
    """
    logger.info("Starting data cleaning and alignment pipeline...")

    df = raw_df.copy()
    df["Date"] = pd.to_datetime(df["Date"]).dt.normalize()

    # Drop duplicate records
    df = df.drop_duplicates(subset=["Sector", "Date"]).sort_values(["Sector", "Date"]).reset_index(drop=True)

    # Filter out invalid prices
    invalid_mask = (df["Close"] <= 0) | (df["High"] <= 0) | (df["Low"] <= 0) | (df["Open"] <= 0)
    if invalid_mask.any():
        logger.warning(f"Removing {invalid_mask.sum()} rows with non-positive prices.")
        df = df[~invalid_mask].copy()

    # Get Master Trading Calendar from Benchmark (NIFTY50)
    benchmark_key = BENCHMARK["key"]
    benchmark_data = df[df["Sector"] == benchmark_key].sort_values("Date")
    
    if benchmark_data.empty:
        # If benchmark missing, use sorted union of all sector dates
        logger.warning("Benchmark data missing for master calendar. Using union of all sector dates.")
        master_dates = pd.DatetimeIndex(sorted(df["Date"].unique()))
    else:
        master_dates = pd.DatetimeIndex(sorted(benchmark_data["Date"].unique()))

    logger.info(f"Master trading calendar established: {len(master_dates)} trading sessions from {master_dates.min().strftime('%Y-%m-%d')} to {master_dates.max().strftime('%Y-%m-%d')}")

    cleaned_sector_dfs = []
    stats = {
        "master_trading_days": len(master_dates),
        "date_range_start": master_dates.min().strftime("%Y-%m-%d"),
        "date_range_end": master_dates.max().strftime("%Y-%m-%d"),
        "sectors": {}
    }

    all_sectors = list(ALL_TICKERS.keys())

    for sector in all_sectors:
        sector_df = df[df["Sector"] == sector].copy()
        ticker = ALL_TICKERS[sector]

        if sector_df.empty:
            logger.warning(f"No records found for sector '{sector}'. Skipping.")
            stats["sectors"][sector] = {"status": "EMPTY", "rows": 0}
            continue

        # Reindex to master trading calendar
        sector_df = sector_df.set_index("Date").reindex(master_dates)
        sector_df["Sector"] = sector
        sector_df["Ticker"] = ticker

        # Identify missing blocks
        is_missing = sector_df["Close"].isna()
        
        # Calculate consecutive missing days in each missing block
        missing_groups = (~is_missing).cumsum()
        missing_block_lengths = is_missing.groupby(missing_groups).transform("sum")

        # Forward fill ONLY if the entire missing block is <= 2 trading days
        valid_fill_mask = is_missing & (missing_block_lengths <= 2)
        unfilled_mask = is_missing & (missing_block_lengths > 2)

        filled_count = valid_fill_mask.sum()
        unfilled_count = unfilled_mask.sum()

        if filled_count > 0:
            logger.info(f"Sector '{sector}': Forward-filling {filled_count} short-gap rows (<=2 days).")
            ffilled_close = sector_df["Close"].ffill()
            sector_df.loc[valid_fill_mask, "Close"] = ffilled_close[valid_fill_mask]
            sector_df.loc[valid_fill_mask, "Open"] = sector_df.loc[valid_fill_mask, "Close"]
            sector_df.loc[valid_fill_mask, "High"] = sector_df.loc[valid_fill_mask, "Close"]
            sector_df.loc[valid_fill_mask, "Low"] = sector_df.loc[valid_fill_mask, "Close"]
            sector_df.loc[valid_fill_mask, "Volume"] = 0.0

        # For existing valid rows, replace any NaN volume with 0
        sector_df["Volume"] = sector_df["Volume"].fillna(0.0)

        # Reset index to Date column
        sector_df = sector_df.reset_index().rename(columns={"index": "Date"})

        # Drop any remaining NaN rows (long gaps or dates before sector inception)
        sector_df = sector_df.dropna(subset=["Close"]).reset_index(drop=True)

        stats["sectors"][sector] = {
            "status": "CLEAN",
            "rows": len(sector_df),
            "filled_short_gaps": int(filled_count),
            "unfilled_long_gaps": int(unfilled_count),
            "first_date": sector_df["Date"].min().strftime("%Y-%m-%d"),
            "last_date": sector_df["Date"].max().strftime("%Y-%m-%d")
        }

        cleaned_sector_dfs.append(sector_df)

    if not cleaned_sector_dfs:
        raise RuntimeError("No sector data could be cleaned.")

    clean_df = pd.concat(cleaned_sector_dfs, ignore_index=True)
    clean_df = clean_df.sort_values(["Sector", "Date"]).reset_index(drop=True)

    # Persist clean dataset
    try:
        clean_df.to_parquet(CLEAN_DATA_PATH, index=False)
        clean_df.to_csv(CLEAN_DATA_CSV_PATH, index=False)
        logger.info(f"Successfully saved clean sector dataset ({len(clean_df)} rows) to {CLEAN_DATA_PATH}")
    except Exception as e:
        logger.error(f"Failed to persist clean sector dataset: {str(e)}")

    return clean_df, stats


def load_clean_data() -> pd.DataFrame:
    """Loads clean sector data from storage."""
    if not CLEAN_DATA_PATH.exists():
        raise FileNotFoundError(f"Clean data file not found at {CLEAN_DATA_PATH}. Run fetch and clean first.")
    return pd.read_parquet(CLEAN_DATA_PATH)


if __name__ == "__main__":
    from backend.app.data.fetch import fetch_all_sectors
    raw_df, _ = fetch_all_sectors()
    clean_df, stats = clean_and_align_sectors(raw_df)
    print("\n--- DATA CLEANING SUMMARY ---")
    print(f"Master Trading Days: {stats['master_trading_days']} ({stats['date_range_start']} to {stats['date_range_end']})")
    for sec, info in stats["sectors"].items():
        print(f"{sec:10} | Rows: {info['rows']:5} | Filled Gaps: {info['filled_short_gaps']} | Span: {info['first_date']} -> {info['last_date']}")
