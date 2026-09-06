"""
Configuration module for SectorAI.
Defines sector mapping, tickers, paths, and application settings.
"""

from pathlib import Path
from typing import Dict, List

# Base Directories
APP_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = APP_DIR.parent
STORAGE_DIR = APP_DIR / "data" / "storage"
ARTIFACTS_DIR = APP_DIR / "models" / "artifacts"

STORAGE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# Fixed Sector Definitions and Tickers (yfinance only)
# 8 In-scope NSE Sectors
SECTORS: Dict[str, Dict[str, str]] = {
    "IT": {
        "name": "NIFTY IT",
        "ticker": "^CNXIT",
        "display_name": "Information Technology",
        "description": "Software, tech services, and digital transformation leaders."
    },
    "BANK": {
        "name": "NIFTY BANK",
        "ticker": "^NSEBANK",
        "display_name": "Banking & Financials",
        "description": "Private and PSU commercial banks across India."
    },
    "AUTO": {
        "name": "NIFTY AUTO",
        "ticker": "^CNXAUTO",
        "display_name": "Automobile",
        "description": "Passenger vehicles, commercial vehicles, and auto components."
    },
    "PHARMA": {
        "name": "NIFTY PHARMA",
        "ticker": "^CNXPHARMA",
        "display_name": "Pharmaceuticals & Healthcare",
        "description": "Generic formulations, APIs, drug discovery, and healthcare providers."
    },
    "FMCG": {
        "name": "NIFTY FMCG",
        "ticker": "^CNXFMCG",
        "display_name": "Fast Moving Consumer Goods",
        "description": "Consumer staples, household goods, and personal care."
    },
    "METAL": {
        "name": "NIFTY METAL",
        "ticker": "^CNXMETAL",
        "display_name": "Metals & Mining",
        "description": "Steel producers, aluminum, zinc, and mining enterprises."
    },
    "ENERGY": {
        "name": "NIFTY ENERGY",
        "ticker": "^CNXENERGY",
        "display_name": "Energy & Power",
        "description": "Oil & gas, refining, renewable energy, and power utilities."
    },
    "REALTY": {
        "name": "NIFTY REALTY",
        "ticker": "^CNXREALTY",
        "display_name": "Real Estate",
        "description": "Residential, commercial real estate developers, and construction."
    }
}

# Benchmark Definition
BENCHMARK: Dict[str, str] = {
    "key": "NIFTY50",
    "name": "NIFTY 50",
    "ticker": "^NSEI",
    "display_name": "NIFTY 50 Benchmark"
}

# All tracked tickers
ALL_TICKERS: Dict[str, str] = {
    **{k: v["ticker"] for k, v in SECTORS.items()},
    BENCHMARK["key"]: BENCHMARK["ticker"]
}

SECTOR_KEYS: List[str] = list(SECTORS.keys())

# Categorical Health Labels in order (Strictly NO raw scores)
HEALTH_LABELS = [
    "Strong Buy",
    "Buy",
    "Neutral",
    "Avoid",
    "Strong Avoid"
]

# Lookback and Forecasting parameters
DEFAULT_LOOKBACK_YEARS = 7
FORECAST_HORIZON_DAYS = 5
LABEL_FORWARD_DAYS = 20
