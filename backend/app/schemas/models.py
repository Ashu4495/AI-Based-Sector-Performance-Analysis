"""
Pydantic Schemas for SectorAI REST API.
Defines strict response and data contracts.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SectorSummary(BaseModel):
    sector: str = Field(..., json_schema_extra={"example": "IT"})
    sector_name: str = Field(..., json_schema_extra={"example": "NIFTY IT"})
    display_name: str = Field(..., json_schema_extra={"example": "Information Technology"})
    as_of_date: str = Field(..., json_schema_extra={"example": "2026-09-04"})
    latest_close: float = Field(..., json_schema_extra={"example": 30695.15})
    return_1d_pct: float = Field(..., json_schema_extra={"example": 0.45})
    return_5d_pct: float = Field(..., json_schema_extra={"example": 1.20})
    return_20d_pct: float = Field(..., json_schema_extra={"example": -2.71})
    rel_return_20d_pct: float = Field(..., json_schema_extra={"example": -3.50})
    rsi_14: float = Field(..., json_schema_extra={"example": 48.2})
    health_label: str = Field(..., json_schema_extra={"example": "Strong Buy"})
    rank: int = Field(..., json_schema_extra={"example": 5})
    predicted_return_5d_pct: float = Field(..., json_schema_extra={"example": 0.10})
    direction: str = Field(..., json_schema_extra={"example": "Neutral"})


class SectorListResponse(BaseModel):
    as_of_date: str
    total_sectors: int
    sectors: List[SectorSummary]


class ForecastResponse(BaseModel):
    sector: str
    sector_name: str
    display_name: str
    as_of_date: str
    predicted_return_5d: float
    predicted_return_pct: float
    confidence_lower_pct: float
    confidence_upper_pct: float
    direction: str
    horizon_days: int = 5


class ShapDriver(BaseModel):
    feature: str
    display_name: str
    feature_value: float
    formatted_value: str
    shap_value: float
    direction: str
    description: str


class HealthResponse(BaseModel):
    sector: str
    sector_name: str
    display_name: str
    as_of_date: str
    health_label: str
    rank: int
    top_drivers: List[ShapDriver]


class HistoricalDataPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    ema_20: Optional[float] = None
    sma_50: Optional[float] = None
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    health_label: Optional[str] = None


class SectorDetailResponse(BaseModel):
    sector: str
    sector_name: str
    display_name: str
    description: str
    as_of_date: str
    latest_close: float
    change_20d_pct: float
    health_label: str
    forecast: ForecastResponse
    top_drivers: List[ShapDriver]
    price_history: List[HistoricalDataPoint]


class BacktestMetrics(BaseModel):
    final_equity: float
    cumulative_return_pct: float
    cagr_pct: float
    annualized_volatility_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float


class ComparisonMetrics(BaseModel):
    excess_cagr_pct: float
    excess_total_return_pct: float
    monthly_win_rate_pct: float
    total_rebalances: int


class TradeLog(BaseModel):
    rebalance_date: str
    selected_sector: str
    selected_name: str
    health_label: str
    entry_price: float
    strategy_equity: float
    benchmark_equity: float


class EquityPoint(BaseModel):
    date: str
    strategy: float
    benchmark: float
    strategy_return_pct: float
    benchmark_return_pct: float
    holding: Optional[str] = None


class BacktestResponse(BaseModel):
    strategy_name: str
    benchmark_name: str
    start_date: str
    end_date: str
    total_trading_days: int
    rebalance_frequency: str
    initial_capital: float
    metrics: Dict[str, Dict[str, float]]
    trades_log: List[TradeLog]
    equity_curve: List[EquityPoint]
