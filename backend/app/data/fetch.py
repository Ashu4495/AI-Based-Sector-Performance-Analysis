"""
Data Fetcher Module for MarketPulse AI.
Pulls historical OHLCV data for all 8 NSE sectors and the NIFTY 50 benchmark via yfinance.
Implements robust error handling, caching, and multi-index column flattening.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple
import pandas as pd
import yfinance as yf

from backend.app.core.config import (
    ALL_TICKERS,
    BENCHMARK,
    DEFAULT_LOOKBACK_YEARS,
    SECTORS,
    STORAGE_DIR,
)
from backend.app.core.logging import logger

RAW_DATA_PATH = STORAGE_DIR / "raw_sectors.parquet"
RAW_DATA_CSV_PATH = STORAGE_DIR / "raw_sectors.csv"


def fetch_ticker_data(
    ticker: str,
    sector_key: str,
    start_date: str,
    end_date: str
) -> Optional[pd.DataFrame]:
    """
    Fetches OHLCV data for a single ticker from yfinance.
    Normalizes column names and formats index.
    """
    try:
        logger.info(f"Fetching {ticker} for sector '{sector_key}' from {start_date} to {end_date}...")
        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=False
        )

        if df is None or df.empty:
            logger.warning(f"No data returned for ticker {ticker} ({sector_key})")
            return None

        # If yfinance returned MultiIndex columns (e.g. ('Close', '^CNXIT')), flatten them
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        df = df.reset_index()

        # Normalize Date column
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
        elif "Datetime" in df.columns:
            df["Date"] = pd.to_datetime(df["Datetime"]).dt.tz_localize(None)
            df = df.drop(columns=["Datetime"])
        else:
            df["Date"] = pd.to_datetime(df.index).tz_localize(None)

        # Standardize required columns
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        for col in required_cols:
            if col not in df.columns:
                if col == "Volume":
                    df["Volume"] = 0.0
                else:
                    logger.error(f"Missing required price column '{col}' in {ticker}")
                    return None

        # Select & cast columns
        df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df["Sector"] = sector_key
        df["Ticker"] = ticker
        df = df.dropna(subset=["Close", "Date"])
        df = df.sort_values("Date").reset_index(drop=True)

        logger.info(f"Successfully fetched {len(df)} rows for {ticker} ({sector_key})")
        return df

    except Exception as e:
        logger.error(f"Error fetching data for ticker {ticker} ({sector_key}): {str(e)}")
        return None


def fetch_all_sectors(
    lookback_years: int = DEFAULT_LOOKBACK_YEARS,
    use_cache_on_failure: bool = True
) -> Tuple[pd.DataFrame, Dict[str, any]]:
    """
    Pulls historical data for all 8 sectors + benchmark.
    If a fetch fails and cache exists, falls back gracefully per Rules.md.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_years * 365 + 30)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    data_frames = []
    fetch_meta = {
        "timestamp": datetime.now().isoformat(),
        "lookback_years": lookback_years,
        "start_date": start_str,
        "end_date": end_str,
        "sectors_fetched": [],
        "sectors_failed": [],
        "is_stale_fallback": False
    }

    for sector_key, ticker in ALL_TICKERS.items():
        df = fetch_ticker_data(ticker, sector_key, start_str, end_str)
        if df is not None and not df.empty:
            data_frames.append(df)
            fetch_meta["sectors_fetched"].append(sector_key)
        else:
            fetch_meta["sectors_failed"].append(sector_key)

    # Handle partial or total failure with cache fallback
    if len(fetch_meta["sectors_failed"]) > 0 or len(data_frames) == 0:
        if use_cache_on_failure and RAW_DATA_PATH.exists():
            logger.warning(
                f"Fetch incomplete for {fetch_meta['sectors_failed']}. Loading cached dataset from {RAW_DATA_PATH}..."
            )
            try:
                cached_df = pd.read_parquet(RAW_DATA_PATH)
                fetch_meta["is_stale_fallback"] = True
                fetch_meta["note"] = "Data loaded from cache due to fetch error on one or more tickers."
                return cached_df, fetch_meta
            except Exception as e:
                logger.error(f"Failed to read cache file: {str(e)}")

    if not data_frames:
        raise RuntimeError("Data fetch completely failed and no valid cache is available.")

    combined_df = pd.concat(data_frames, ignore_index=True)
    combined_df = combined_df.sort_values(["Sector", "Date"]).reset_index(drop=True)

    # Save to storage
    try:
        combined_df.to_parquet(RAW_DATA_PATH, index=False)
        combined_df.to_csv(RAW_DATA_CSV_PATH, index=False)
        logger.info(f"Persisted raw sector data ({len(combined_df)} rows) to {RAW_DATA_PATH}")
    except Exception as e:
        logger.error(f"Failed to persist raw sector data: {str(e)}")

    return combined_df, fetch_meta


if __name__ == "__main__":
    df, meta = fetch_all_sectors()
    print(f"Raw data fetched: {len(df)} rows across {df['Sector'].nunique()} sectors.")
    print("Sectors fetched:", meta["sectors_fetched"])
    print("Sectors failed:", meta["sectors_failed"])
