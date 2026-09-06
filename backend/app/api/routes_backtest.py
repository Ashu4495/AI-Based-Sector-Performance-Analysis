"""
Backtest Routes for MarketPulse AI API.
Serves strategy vs benchmark backtest metrics, rebalancing logs, and equity curves.
"""

from fastapi import APIRouter, HTTPException

from backend.app.backtest.rotation_strategy import load_backtest_results
from backend.app.core.logging import logger
from backend.app.schemas.models import BacktestResponse

router = APIRouter(tags=["Backtest"])


@router.get("/backtest", response_model=BacktestResponse)
def get_backtest():
    """
    Returns the full sector rotation strategy backtest results vs NIFTY 50 benchmark.
    Includes CAGR, Sharpe ratio, Max Drawdown, monthly rotation logs, and downsampled equity curves.
    """
    try:
        results = load_backtest_results()
        if not results:
            raise HTTPException(status_code=503, detail="Backtest results could not be loaded.")
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving /backtest: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Failed to load backtest results: {str(e)}")
