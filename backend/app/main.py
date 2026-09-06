"""
MarketPulse AI FastAPI Application Entrypoint.
Exposes REST API endpoints serving sector leaderboard, details, forecasts, health classifications, and backtests.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.routes_backtest import router as backtest_router
from backend.app.api.routes_forecast import router as forecast_router
from backend.app.api.routes_health import router as health_router
from backend.app.api.routes_sectors import router as sectors_router
from backend.app.core.logging import logger
from backend.app.models.explain import get_tree_explainer
from backend.app.models.train_classifier import load_classifier_model
from backend.app.models.train_forecast import load_forecast_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Preloads model artifacts on application startup for fast response times."""
    logger.info("Starting MarketPulse AI API server...")
    try:
        logger.info("Pre-loading ML model artifacts into memory...")
        load_forecast_model()
        load_classifier_model()
        get_tree_explainer()
        logger.info("All model artifacts preloaded successfully.")
    except Exception as e:
        logger.warning(f"Note on startup artifact pre-loading: {str(e)}")
    yield
    logger.info("Shutting down MarketPulse AI API server...")


app = FastAPI(
    title="MarketPulse AI API",
    description="AI-Driven NSE Sector Performance Analysis & Health Classification API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for local frontend dev & production deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred while processing market analysis data."}
    )


# Health check endpoint
@app.get("/healthcheck", tags=["System"])
def healthcheck():
    return {"status": "healthy", "service": "MarketPulse AI Backend API"}


# Include Routers
app.include_router(sectors_router)
app.include_router(forecast_router)
app.include_router(health_router)
app.include_router(backtest_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
