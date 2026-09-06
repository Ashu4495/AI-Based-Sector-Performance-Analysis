"""
Phase 0 Verification Script:
Validates that yfinance can cleanly fetch historical OHLCV data for all 8 sector tickers and the NIFTY 50 benchmark.
"""

import sys
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from backend.app.core.config import ALL_TICKERS, SECTORS, BENCHMARK
from backend.app.core.logging import logger

def verify_tickers():
    logger.info("Starting Phase 0 ticker verification...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365) # 1 year test pull
    
    results = {}
    all_passed = True
    
    for key, ticker in ALL_TICKERS.items():
        name = SECTORS[key]["name"] if key in SECTORS else BENCHMARK["name"]
        logger.info(f"Testing ticker {ticker} ({name})...")
        try:
            data = yf.download(ticker, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"), progress=False)
            if data is None or data.empty:
                logger.error(f"[FAIL] No data returned for {ticker} ({name})")
                results[key] = {"status": "FAILED", "rows": 0, "ticker": ticker, "name": name}
                all_passed = False
            else:
                rows = len(data)
                close_val = data['Close'].iloc[-1].values[0] if isinstance(data['Close'], pd.DataFrame) else data['Close'].iloc[-1]
                logger.info(f"[OK] {ticker} returned {rows} rows. Latest Close: {close_val:.2f}")
                results[key] = {"status": "SUCCESS", "rows": rows, "ticker": ticker, "name": name}
        except Exception as e:
            logger.error(f"[ERROR] fetching {ticker} ({name}): {str(e)}")
            results[key] = {"status": "ERROR", "error": str(e), "ticker": ticker, "name": name}
            all_passed = False

    print("\n--- PHASE 0 TICKER VERIFICATION SUMMARY ---")
    for key, res in results.items():
        print(f"[{res['status']}] {key:10} | {res['name']:25} | Ticker: {res['ticker']:12} | Rows: {res.get('rows', 0)}")
    
    if all_passed:
        logger.info("[SUCCESS] All 9 tickers successfully verified with yfinance!")
        return 0
    else:
        logger.error("[ERROR] Some tickers failed verification.")
        return 1

if __name__ == "__main__":
    sys.exit(verify_tickers())
