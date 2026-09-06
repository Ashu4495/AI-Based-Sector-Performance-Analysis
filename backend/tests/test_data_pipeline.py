"""
Unit tests for SectorAI Data Pipeline (fetch and clean modules).
"""

from datetime import datetime
import numpy as np
import pandas as pd
import pytest

from backend.app.core.config import ALL_TICKERS, BENCHMARK, SECTORS, STORAGE_DIR
from backend.app.data.clean import clean_and_align_sectors
from backend.app.data.fetch import fetch_all_sectors, fetch_ticker_data


def test_fetch_single_ticker():
    """Test fetching historical data for NIFTY IT (^CNXIT)."""
    df = fetch_ticker_data("^CNXIT", "IT", "2024-01-01", "2024-06-01")
    assert df is not None, "Failed to fetch data for ^CNXIT"
    assert not df.empty, "Returned DataFrame is empty"
    assert "Date" in df.columns
    assert "Close" in df.columns
    assert "Sector" in df.columns
    assert (df["Close"] > 0).all(), "Found non-positive close prices"
    assert (df["Sector"] == "IT").all(), "Sector column mismatch"


def test_clean_and_align_logic():
    """Test cleaning and master calendar alignment with synthetic gap data."""
    dates = pd.date_range("2024-01-01", periods=10, freq="B")
    
    # Create synthetic benchmark data (complete)
    bm_df = pd.DataFrame({
        "Date": dates,
        "Open": 100.0,
        "High": 105.0,
        "Low": 95.0,
        "Close": 102.0,
        "Volume": 1000.0,
        "Sector": BENCHMARK["key"],
        "Ticker": BENCHMARK["ticker"]
    })
    
    # Create sector data with a 1-day gap (should fill) and a 4-day gap (should not fill)
    # Day 0, 1, 3 (day 2 missing -> gap=1 <= 2, fills)
    # Day 8, 9 (days 4, 5, 6, 7 missing -> gap=4 > 2, does not fill)
    sec_dates = [dates[0], dates[1], dates[3], dates[8], dates[9]]
    sec_df = pd.DataFrame({
        "Date": sec_dates,
        "Open": 50.0,
        "High": 55.0,
        "Low": 48.0,
        "Close": 52.0,
        "Volume": 500.0,
        "Sector": "IT",
        "Ticker": "^CNXIT"
    })
    
    raw_combined = pd.concat([bm_df, sec_df], ignore_index=True)
    clean_df, stats = clean_and_align_sectors(raw_combined)
    
    assert not clean_df.empty
    assert stats["master_trading_days"] == 10
    
    sec_clean = clean_df[clean_df["Sector"] == "IT"].sort_values("Date").reset_index(drop=True)
    
    # Day 2 should be filled
    day_2_row = sec_clean[sec_clean["Date"] == dates[2]]
    assert len(day_2_row) == 1, "Short gap (day 2) was not filled"
    assert day_2_row["Close"].iloc[0] == 52.0, "Forward-filled close mismatch"
    
    # Days 4, 5, 6, 7 should NOT be present
    for d in [dates[4], dates[5], dates[6], dates[7]]:
        assert len(sec_clean[sec_clean["Date"] == d]) == 0, f"Long gap date {d} should not have been filled"


def test_full_data_pipeline():
    """Runs fetch and clean for all 8 sectors + benchmark and checks storage output."""
    raw_df, fetch_meta = fetch_all_sectors(lookback_years=5)
    assert not raw_df.empty, "Raw sector DataFrame is empty"
    assert len(fetch_meta["sectors_fetched"]) >= 9, "Not all sectors were fetched"
    
    clean_df, stats = clean_and_align_sectors(raw_df)
    assert not clean_df.empty, "Clean sector DataFrame is empty"
    
    # Verify all 8 sectors + benchmark exist
    sectors_present = set(clean_df["Sector"].unique())
    for s in SECTORS.keys():
        assert s in sectors_present, f"Sector {s} missing from cleaned dataset"
    assert BENCHMARK["key"] in sectors_present, "Benchmark missing from cleaned dataset"
    
    # Verify no zero or negative prices
    assert (clean_df["Close"] > 0).all(), "Found non-positive close price in clean data"
    assert (clean_df["High"] >= clean_df["Low"]).all(), "High < Low found in clean data"
    
    # Verify files exist in storage
    assert (STORAGE_DIR / "clean_sectors.parquet").exists()
    assert (STORAGE_DIR / "clean_sectors.csv").exists()
