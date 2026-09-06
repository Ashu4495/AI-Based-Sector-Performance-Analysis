"""
Sector Rotation Backtesting Module for MarketPulse AI.
Simulates a monthly sector rotation strategy based on model health labels
and compares performance against the NIFTY 50 buy-and-hold benchmark.
Computes CAGR, Sharpe Ratio, Max Drawdown, and monthly rebalancing logs.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from backend.app.core.config import (
    BENCHMARK,
    HEALTH_LABELS,
    SECTORS,
    STORAGE_DIR,
)
from backend.app.core.logging import logger
from backend.app.features.engineer import ALL_FEATURE_COLUMNS, load_feature_store
from backend.app.models.predict import LABEL_RANK
from backend.app.models.train_classifier import load_classifier_model

BACKTEST_JSON_PATH = STORAGE_DIR / "backtest_results.json"


def run_sector_rotation_backtest(
    rebalance_freq_days: int = 21,
    initial_capital: float = 100000.0,
    risk_free_rate: float = 0.065 # 6.5% standard Indian 10y yield
) -> Dict[str, any]:
    """
    Simulates monthly sector rotation strategy:
    1. Iterates through historical trading dates at rebalance frequency (every 21 trading days).
    2. Uses RandomForestClassifier on features available at t to predict health labels for all 8 sectors.
    3. Ranks sectors primarily by health label (Strong Buy -> Buy -> Neutral -> Avoid -> Strong Avoid),
       and secondarily by 20-day relative strength momentum.
    4. Rotates 100% of capital into the #1 top-ranked sector for the next 21 trading days.
    5. Tracks daily equity curve for Strategy vs. NIFTY 50 benchmark.
    6. Calculates cumulative return, CAGR, Sharpe ratio, Max Drawdown, and monthly logs.
    """
    logger.info("Starting sector rotation strategy backtest...")
    df = load_feature_store()
    clf = load_classifier_model()

    # Separate benchmark from sectors
    bm_df = df[df["Sector"] == BENCHMARK["key"]].sort_values("Date").reset_index(drop=True)
    sec_df = df[df["Sector"] != BENCHMARK["key"]].copy()

    # Align dates present in benchmark
    unique_dates = sorted(bm_df["Date"].unique())
    logger.info(f"Backtesting over {len(unique_dates)} trading sessions from {unique_dates[0].strftime('%Y-%m-%d')} to {unique_dates[-1].strftime('%Y-%m-%d')}")

    # Rebalance index intervals
    rebalance_indices = list(range(0, len(unique_dates) - 1, rebalance_freq_days))

    trades_log = []
    daily_records = []

    strategy_equity = initial_capital
    benchmark_equity = initial_capital
    
    current_holding_sector = None
    current_entry_price = 0.0

    # Pivot prices table (Date x Sector Close)
    price_pivot = df.pivot(index="Date", columns="Sector", values="Close").ffill()

    for i in range(len(unique_dates)):
        current_date = unique_dates[i]

        # Check if rebalance session
        if i in rebalance_indices:
            # Score each sector at current_date
            sector_scores = []
            for sector in SECTORS.keys():
                sector_rows = sec_df[(sec_df["Sector"] == sector) & (sec_df["Date"] == current_date)]
                if sector_rows.empty:
                    continue
                row = sector_rows.iloc[0]
                X_single = pd.DataFrame([row[ALL_FEATURE_COLUMNS]])
                predicted_label = str(clf.predict(X_single)[0])
                rank = LABEL_RANK.get(predicted_label, 3)
                rel_momentum = float(row["rel_return_20d"]) if pd.notna(row["rel_return_20d"]) else 0.0

                sector_scores.append({
                    "sector": sector,
                    "name": SECTORS[sector]["name"],
                    "health_label": predicted_label,
                    "rank": rank,
                    "rel_momentum": rel_momentum,
                    "price": float(row["Close"])
                })

            if sector_scores:
                # Sort primarily by health label rank, secondarily by 20d relative momentum
                sorted_sectors = sorted(sector_scores, key=lambda x: (x["rank"], x["rel_momentum"]), reverse=True)
                top_sector = sorted_sectors[0]
                new_sector = top_sector["sector"]
                
                # If sector rotated, log trade
                trades_log.append({
                    "rebalance_date": current_date.strftime("%Y-%m-%d"),
                    "selected_sector": new_sector,
                    "selected_name": SECTORS[new_sector]["name"],
                    "health_label": top_sector["health_label"],
                    "entry_price": round(top_sector["price"], 2),
                    "strategy_equity": round(strategy_equity, 2),
                    "benchmark_equity": round(benchmark_equity, 2)
                })

                current_holding_sector = new_sector

        # Daily performance tracking
        if i > 0 and current_holding_sector is not None:
            prev_date = unique_dates[i - 1]
            
            # Holding sector return
            sec_prev = price_pivot.loc[prev_date, current_holding_sector]
            sec_curr = price_pivot.loc[current_date, current_holding_sector]
            sec_daily_ret = (sec_curr / sec_prev) - 1.0 if (pd.notna(sec_prev) and sec_prev > 0) else 0.0

            # Benchmark daily return
            bm_prev = price_pivot.loc[prev_date, BENCHMARK["key"]]
            bm_curr = price_pivot.loc[current_date, BENCHMARK["key"]]
            bm_daily_ret = (bm_curr / bm_prev) - 1.0 if (pd.notna(bm_prev) and bm_prev > 0) else 0.0

            strategy_equity *= (1.0 + sec_daily_ret)
            benchmark_equity *= (1.0 + bm_daily_ret)

        daily_records.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "strategy_equity": round(strategy_equity, 2),
            "benchmark_equity": round(benchmark_equity, 2),
            "holding_sector": current_holding_sector,
            "strategy_cumulative_pct": round(((strategy_equity / initial_capital) - 1.0) * 100, 2),
            "benchmark_cumulative_pct": round(((benchmark_equity / initial_capital) - 1.0) * 100, 2)
        })

    # Convert to DataFrame for analytics
    perf_df = pd.DataFrame(daily_records)
    perf_df["strategy_daily_ret"] = perf_df["strategy_equity"].pct_change().fillna(0.0)
    perf_df["benchmark_daily_ret"] = perf_df["benchmark_equity"].pct_change().fillna(0.0)

    # Performance Metrics Calculation
    total_days = len(perf_df)
    years = total_days / 252.0

    strat_total_return = (strategy_equity / initial_capital) - 1.0
    bm_total_return = (benchmark_equity / initial_capital) - 1.0

    strat_cagr = ((strategy_equity / initial_capital) ** (1.0 / years)) - 1.0 if years > 0 else 0.0
    bm_cagr = ((benchmark_equity / initial_capital) ** (1.0 / years)) - 1.0 if years > 0 else 0.0

    strat_vol = perf_df["strategy_daily_ret"].std() * np.sqrt(252)
    bm_vol = perf_df["benchmark_daily_ret"].std() * np.sqrt(252)

    strat_sharpe = (strat_cagr - risk_free_rate) / strat_vol if strat_vol > 0 else 0.0
    bm_sharpe = (bm_cagr - risk_free_rate) / bm_vol if bm_vol > 0 else 0.0

    # Max Drawdowns
    strat_peaks = perf_df["strategy_equity"].cummax()
    strat_dd = (perf_df["strategy_equity"] - strat_peaks) / strat_peaks
    strat_max_dd = float(strat_dd.min())

    bm_peaks = perf_df["benchmark_equity"].cummax()
    bm_dd = (perf_df["benchmark_equity"] - bm_peaks) / bm_peaks
    bm_max_dd = float(bm_dd.min())

    # Monthly win rate (comparing rebalance period returns)
    rebalance_rets_strat = []
    rebalance_rets_bm = []
    for k in range(len(rebalance_indices) - 1):
        idx_start = rebalance_indices[k]
        idx_end = rebalance_indices[k + 1]
        r_strat = (perf_df.loc[idx_end, "strategy_equity"] / perf_df.loc[idx_start, "strategy_equity"]) - 1.0
        r_bm = (perf_df.loc[idx_end, "benchmark_equity"] / perf_df.loc[idx_start, "benchmark_equity"]) - 1.0
        rebalance_rets_strat.append(r_strat)
        rebalance_rets_bm.append(r_bm)

    wins = sum(1 for s, b in zip(rebalance_rets_strat, rebalance_rets_bm) if s > b)
    win_rate = (wins / len(rebalance_rets_strat)) * 100 if rebalance_rets_strat else 0.0

    # Downsample equity curve for smooth frontend rendering (e.g. 1 point per week)
    sampled_curve = perf_df.iloc[::3].copy()
    if len(sampled_curve) == 0 or sampled_curve.iloc[-1]["date"] != perf_df.iloc[-1]["date"]:
        sampled_curve = pd.concat([sampled_curve, perf_df.iloc[[-1]]], ignore_index=True)

    equity_curve = [
        {
            "date": row["date"],
            "strategy": row["strategy_equity"],
            "benchmark": row["benchmark_equity"],
            "strategy_return_pct": row["strategy_cumulative_pct"],
            "benchmark_return_pct": row["benchmark_cumulative_pct"],
            "holding": row["holding_sector"]
        }
        for _, row in sampled_curve.iterrows()
    ]

    results = {
        "strategy_name": "AI Sector Rotation Strategy (Monthly Top Health)",
        "benchmark_name": "NIFTY 50 Buy-and-Hold",
        "start_date": unique_dates[0].strftime("%Y-%m-%d"),
        "end_date": unique_dates[-1].strftime("%Y-%m-%d"),
        "total_trading_days": total_days,
        "rebalance_frequency": f"Every {rebalance_freq_days} Trading Days (~1 Month)",
        "initial_capital": initial_capital,
        "metrics": {
            "strategy": {
                "final_equity": round(strategy_equity, 2),
                "cumulative_return_pct": round(strat_total_return * 100, 2),
                "cagr_pct": round(strat_cagr * 100, 2),
                "annualized_volatility_pct": round(strat_vol * 100, 2),
                "sharpe_ratio": round(strat_sharpe, 2),
                "max_drawdown_pct": round(strat_max_dd * 100, 2),
            },
            "benchmark": {
                "final_equity": round(benchmark_equity, 2),
                "cumulative_return_pct": round(bm_total_return * 100, 2),
                "cagr_pct": round(bm_cagr * 100, 2),
                "annualized_volatility_pct": round(bm_vol * 100, 2),
                "sharpe_ratio": round(bm_sharpe, 2),
                "max_drawdown_pct": round(bm_max_dd * 100, 2),
            },
            "comparison": {
                "excess_cagr_pct": round((strat_cagr - bm_cagr) * 100, 2),
                "excess_total_return_pct": round((strat_total_return - bm_total_return) * 100, 2),
                "monthly_win_rate_pct": round(win_rate, 2),
                "total_rebalances": len(trades_log)
            }
        },
        "trades_log": trades_log[-12:], # Last 12 monthly rotations
        "equity_curve": equity_curve
    }

    # Save to storage
    try:
        with open(BACKTEST_JSON_PATH, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Backtest results saved successfully to {BACKTEST_JSON_PATH}")
    except Exception as e:
        logger.error(f"Failed to save backtest results: {str(e)}")

    return results


def load_backtest_results() -> Dict[str, any]:
    """Loads backtest results from storage."""
    if not BACKTEST_JSON_PATH.exists():
        return run_sector_rotation_backtest()
    with open(BACKTEST_JSON_PATH, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    res = run_sector_rotation_backtest()
    print("\n--- SECTOR ROTATION BACKTEST SUMMARY ---")
    print(f"Period: {res['start_date']} to {res['end_date']} ({res['total_trading_days']} days)")
    s_m = res["metrics"]["strategy"]
    b_m = res["metrics"]["benchmark"]
    c_m = res["metrics"]["comparison"]
    print(f"Strategy Cumulative Return: {s_m['cumulative_return_pct']:+6.2f}% | Benchmark: {b_m['cumulative_return_pct']:+6.2f}%")
    print(f"Strategy CAGR:              {s_m['cagr_pct']:+6.2f}% | Benchmark: {b_m['cagr_pct']:+6.2f}% (Excess: {c_m['excess_cagr_pct']:+6.2f}%)")
    print(f"Sharpe Ratio:               {s_m['sharpe_ratio']:6.2f}  | Benchmark: {b_m['sharpe_ratio']:6.2f}")
    print(f"Max Drawdown:               {s_m['max_drawdown_pct']:6.2f}% | Benchmark: {b_m['max_drawdown_pct']:6.2f}%")
    print(f"Monthly Win Rate:           {c_m['monthly_win_rate_pct']:.2f}% ({c_m['total_rebalances']} rebalance periods)")
    print("\nRecent 5 Monthly Rotations:")
    for t in res["trades_log"][-5:]:
        print(f"  {t['rebalance_date']}: Rotated into {t['selected_sector']:6} ({t['selected_name']:20}) [{t['health_label']}]")
