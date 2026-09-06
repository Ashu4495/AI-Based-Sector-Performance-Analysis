"""
Unit tests for SectorAI FastAPI endpoints.
Tests all 5 core REST endpoints + input validation and error conditions.
"""

from fastapi.testclient import TestClient
import pytest

from backend.app.core.config import HEALTH_LABELS, SECTORS
from backend.app.main import app

client = TestClient(app)


def test_healthcheck_endpoint():
    """Verifies system healthcheck."""
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_sectors_leaderboard():
    """Verifies /sectors returns complete leaderboard with all 8 sectors."""
    response = client.get("/sectors")
    assert response.status_code == 200
    data = response.json()

    assert "total_sectors" in data
    assert data["total_sectors"] == len(SECTORS)
    assert len(data["sectors"]) == len(SECTORS)

    for item in data["sectors"]:
        assert item["sector"] in SECTORS
        assert item["health_label"] in HEALTH_LABELS
        assert "predicted_return_5d_pct" in item
        assert "direction" in item


def test_get_sector_detail_valid():
    """Verifies /sectors/{sector} returns full detail payload with price history and overlays."""
    response = client.get("/sectors/IT")
    assert response.status_code == 200
    data = response.json()

    assert data["sector"] == "IT"
    assert data["sector_name"] == "NIFTY IT"
    assert data["health_label"] in HEALTH_LABELS
    assert "forecast" in data
    assert "top_drivers" in data
    assert len(data["price_history"]) > 0

    point = data["price_history"][-1]
    assert "close" in point
    assert "ema_20" in point
    assert "rsi_14" in point
    assert "health_label" in point


def test_get_sector_detail_invalid():
    """Verifies /sectors/{sector} returns 400 Bad Request for unknown sector."""
    response = client.get("/sectors/CRYPTO_UNKNOWN")
    assert response.status_code == 400
    assert "Invalid sector" in response.json()["detail"]


def test_get_forecast_endpoint():
    """Verifies /forecast/{sector} endpoint."""
    response = client.get("/forecast/AUTO")
    assert response.status_code == 200
    data = response.json()

    assert data["sector"] == "AUTO"
    assert "predicted_return_pct" in data
    assert "direction" in data
    assert data["direction"] in ["Bullish", "Bearish", "Neutral"]
    assert data["confidence_lower_pct"] < data["confidence_upper_pct"]


def test_get_forecast_invalid():
    """Verifies /forecast/{sector} returns 400 for unknown sector."""
    response = client.get("/forecast/XYZ")
    assert response.status_code == 400


def test_get_health_endpoint():
    """Verifies /health/{sector} returns categorical label and SHAP feature drivers."""
    response = client.get("/health/BANK")
    assert response.status_code == 200
    data = response.json()

    assert data["sector"] == "BANK"
    assert data["health_label"] in HEALTH_LABELS
    assert "top_drivers" in data
    assert len(data["top_drivers"]) == 4

    for driver in data["top_drivers"]:
        assert "feature" in driver
        assert "display_name" in driver
        assert "direction" in driver


def test_get_health_invalid():
    """Verifies /health/{sector} returns 400 for unknown sector."""
    response = client.get("/health/INVALID_SECTOR")
    assert response.status_code == 400


def test_get_backtest_endpoint():
    """Verifies /backtest returns complete strategy vs benchmark analytics."""
    response = client.get("/backtest")
    assert response.status_code == 200
    data = response.json()

    assert "strategy_name" in data
    assert "benchmark_name" in data
    assert "metrics" in data
    assert "strategy" in data["metrics"]
    assert "benchmark" in data["metrics"]
    assert "comparison" in data["metrics"]
    assert len(data["equity_curve"]) > 50
    assert len(data["trades_log"]) > 0
