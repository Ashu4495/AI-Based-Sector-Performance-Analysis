"""
Health Routes for SectorAI API.
Serves categorical health labels (Strong Buy -> Strong Avoid) and top SHAP feature drivers.
"""

from fastapi import APIRouter, HTTPException, Path

from backend.app.core.config import SECTORS
from backend.app.core.logging import logger
from backend.app.models.predict import get_latest_sector_row, predict_health_for_row
from backend.app.models.train_classifier import load_classifier_model
from backend.app.schemas.models import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health/{sector}", response_model=HealthResponse)
def get_sector_health(
    sector: str = Path(..., description="Sector key, e.g. IT, BANK, AUTO, PHARMA, FMCG, METAL, ENERGY, REALTY")
):
    """
    Returns the latest health classification label and top 4 SHAP feature contributions for a given sector.
    Never exposes raw numeric probabilities.
    """
    sector_key = sector.upper().strip()
    if sector_key not in SECTORS:
        valid_keys = ", ".join(SECTORS.keys())
        raise HTTPException(status_code=400, detail=f"Invalid sector '{sector}'. Allowed sectors: {valid_keys}")

    try:
        row = get_latest_sector_row(sector_key)
        if row is None:
            raise HTTPException(status_code=404, detail=f"No data found for sector '{sector_key}'")

        classifier_model = load_classifier_model()
        health = predict_health_for_row(row, classifier_model, include_shap=True)

        sec_meta = SECTORS[sector_key]

        return {
            "sector": sector_key,
            "sector_name": sec_meta["name"],
            "display_name": sec_meta["display_name"],
            "as_of_date": row["Date"].strftime("%Y-%m-%d"),
            "health_label": health["health_label"],
            "rank": health["rank"],
            "top_drivers": health["top_drivers"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving /health/{sector}: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch health classification for sector '{sector}': {str(e)}")
