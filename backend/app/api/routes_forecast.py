"""
Forecast Routes for SectorAI API.
Serves 5-day regression forecasts and confidence ranges per sector.
"""

from fastapi import APIRouter, HTTPException, Path

from backend.app.core.config import SECTORS
from backend.app.core.logging import logger
from backend.app.models.predict import get_latest_sector_row, predict_forecast_for_row
from backend.app.models.train_forecast import load_forecast_model
from backend.app.schemas.models import ForecastResponse

router = APIRouter(tags=["Forecast"])


@router.get("/forecast/{sector}", response_model=ForecastResponse)
def get_sector_forecast(
    sector: str = Path(..., description="Sector key, e.g. IT, BANK, AUTO, PHARMA, FMCG, METAL, ENERGY, REALTY")
):
    """
    Returns latest 5-day forward return forecast, direction, and confidence interval for a given sector.
    """
    sector_key = sector.upper().strip()
    if sector_key not in SECTORS:
        valid_keys = ", ".join(SECTORS.keys())
        raise HTTPException(status_code=400, detail=f"Invalid sector '{sector}'. Allowed sectors: {valid_keys}")

    try:
        row = get_latest_sector_row(sector_key)
        if row is None:
            raise HTTPException(status_code=404, detail=f"No data found for sector '{sector_key}'")

        forecast_model = load_forecast_model()
        pred = predict_forecast_for_row(row, forecast_model)

        sec_meta = SECTORS[sector_key]

        return {
            "sector": sector_key,
            "sector_name": sec_meta["name"],
            "display_name": sec_meta["display_name"],
            "as_of_date": row["Date"].strftime("%Y-%m-%d"),
            "predicted_return_5d": pred["predicted_return_5d"],
            "predicted_return_pct": pred["predicted_return_pct"],
            "confidence_lower_pct": pred["confidence_lower_pct"],
            "confidence_upper_pct": pred["confidence_upper_pct"],
            "direction": pred["direction"],
            "horizon_days": pred["horizon_days"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving /forecast/{sector}: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Failed to generate forecast for sector '{sector}': {str(e)}")
