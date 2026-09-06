"""
Unit tests for MarketPulse AI Backtest Engine (backend/app/backtest/rotation_strategy.py).
Tests sector rotation logic, equity curve tracking, and financial performance metrics.
"""

from pathlib import Path
import json
import pytest

from backend.app.backtest.rotation_strategy import (
    BACKTEST_JSON_PATH,
    load_backtest_results,
    run_sector_rotation_backtest,
)


def test_sector_rotation_backtest_execution():
    """Runs sector rotation backtest and verifies structure of returned results."""
    results = run_sector_rotation_backtest(rebalance_freq_days=21)

    assert "strategy_name" in results
    assert "metrics" in results
    assert "equity_curve" in results
    assert "trades_log" in results

    metrics = results["metrics"]
    assert "strategy" in metrics
    assert "benchmark" in metrics
    assert "comparison" in metrics

    # Strategy metrics
    strat = metrics["strategy"]
    assert "cumulative_return_pct" in strat
    assert "cagr_pct" in strat
    assert "sharpe_ratio" in strat
    assert "max_drawdown_pct" in strat
    assert strat["final_equity"] > 0

    # Benchmark metrics
    bm = metrics["benchmark"]
    assert "cumulative_return_pct" in bm
    assert "cagr_pct" in bm
    assert "sharpe_ratio" in bm
    assert "max_drawdown_pct" in bm
    assert bm["final_equity"] > 0

    # Equity curve validity
    curve = results["equity_curve"]
    assert len(curve) > 50
    assert "strategy" in curve[0]
    assert "benchmark" in curve[0]
    assert "date" in curve[0]

    # File persistence check
    assert BACKTEST_JSON_PATH.exists()
    loaded = load_backtest_results()
    assert loaded["metrics"]["strategy"]["final_equity"] == strat["final_equity"]
