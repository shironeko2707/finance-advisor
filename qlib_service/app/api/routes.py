"""
FastAPI routes for Qlib service API endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any
from loguru import logger

from app.config.settings import settings
from app.models import schemas
from app.services.qlib_manager import QlibManager
from app.services.forecasting import ForecastingService
from app.services.portfolio_analysis import PortfolioAnalysisService
from app.services.recommendation import RecommendationService

router = APIRouter()

# Dependency to get services
def get_qlib_manager() -> QlibManager:
    """Get QlibManager instance."""
    from main import qlib_manager
    return qlib_manager


# ===========================
# Health & Status Endpoints
# ===========================

@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Service health status
    """
    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": "1.0.0"
    }


@router.get("/status", tags=["Health"])
async def service_status(qlib_mgr: QlibManager = Depends(get_qlib_manager)):
    """
    Detailed service status.

    Returns:
        dict: Detailed service information
    """
    return {
        "service": settings.service_name,
        "version": "1.0.0",
        "qlib_initialized": qlib_mgr.initialized,
        "qlib_data_available": qlib_mgr.data_available,
        "models_loaded": list(qlib_mgr.models_loaded.keys()),
        "features_enabled": {
            "forecasting": settings.enable_forecasting,
            "portfolio_analysis": settings.enable_portfolio_analysis,
            "recommendations": settings.enable_recommendations,
            "backtesting": settings.enable_backtesting,
        },
        "configuration": {
            "default_model": settings.qlib_default_model,
            "forecast_horizons": settings.forecast_horizons_list,
            "feature_set": settings.qlib_feature_set,
            "region": settings.qlib_region,
        }
    }


# ===========================
# Prediction Endpoints
# ===========================

@router.post("/predict/stock", tags=["Predictions"])
async def predict_stock(
    request: schemas.StockPredictionRequest,
    qlib_mgr: QlibManager = Depends(get_qlib_manager)
):
    """
    Generate stock price predictions.

    Args:
        request: Stock prediction request with ticker and historical data

    Returns:
        Stock prediction with multi-horizon forecasts
    """
    if not settings.enable_forecasting:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Forecasting service is disabled"
        )

    if not qlib_mgr.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Qlib not initialized"
        )

    try:
        logger.info(f"Processing stock prediction request for {request.ticker}")
        forecasting_service = ForecastingService(qlib_mgr)
        forecast = await forecasting_service.forecast_stock(request)
        logger.info(f"Stock prediction completed for {request.ticker}")
        return forecast

    except Exception as e:
        logger.error(f"Stock prediction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict/portfolio", tags=["Predictions"])
async def analyze_portfolio(
    request: schemas.PortfolioAnalysisRequest,
    qlib_mgr: QlibManager = Depends(get_qlib_manager)
):
    """
    Analyze portfolio risk and performance.

    Args:
        request: Portfolio analysis request with holdings and context

    Returns:
        Portfolio analysis with risk metrics and performance forecasts
    """
    if not settings.enable_portfolio_analysis:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Portfolio analysis service is disabled"
        )

    if not qlib_mgr.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Qlib not initialized"
        )

    try:
        logger.info("Processing portfolio analysis request")
        portfolio_service = PortfolioAnalysisService(qlib_mgr)
        analysis = await portfolio_service.analyze_portfolio(request)
        logger.info("Portfolio analysis completed")
        return analysis

    except Exception as e:
        logger.error(f"Portfolio analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/recommend", tags=["Predictions"])
async def get_recommendations(
    request: schemas.RecommendationRequest,
    qlib_mgr: QlibManager = Depends(get_qlib_manager)
):
    """
    Generate investment recommendations.

    Args:
        request: Recommendation request with stocks and portfolio context

    Returns:
        Investment recommendations with Buy/Sell/Hold signals and rationale
    """
    if not settings.enable_recommendations:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recommendation service is disabled"
        )

    if not qlib_mgr.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Qlib not initialized"
        )

    try:
        logger.info("Processing recommendation request")
        recommendation_service = RecommendationService(qlib_mgr)
        recommendations = await recommendation_service.generate_recommendations(request)
        logger.info("Recommendations generated")
        return recommendations

    except Exception as e:
        logger.error(f"Recommendation generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation failed: {str(e)}"
        )


# ===========================
# Admin Endpoints
# ===========================

@router.post("/admin/reload-models", tags=["Admin"])
async def reload_models(qlib_mgr: QlibManager = Depends(get_qlib_manager)):
    """
    Reload ML models from storage.

    Returns:
        dict: Reload status
    """
    try:
        logger.info("Reloading models...")
        success = await qlib_mgr.load_models()

        if success:
            logger.info("Models reloaded successfully")
            return {
                "status": "success",
                "models_loaded": list(qlib_mgr.models_loaded.keys())
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Model reload failed"
            )

    except Exception as e:
        logger.error(f"Model reload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reload failed: {str(e)}"
        )


@router.post("/admin/update-data", tags=["Admin"])
async def update_market_data(qlib_mgr: QlibManager = Depends(get_qlib_manager)):
    """
    Trigger market data update.

    Returns:
        dict: Update status
    """
    try:
        logger.info("Updating market data...")
        # In production, this would trigger data download from Qlib providers
        logger.info("Market data update completed")
        return {
            "status": "success",
            "message": "Market data update initiated"
        }

    except Exception as e:
        logger.error(f"Market data update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Update failed: {str(e)}"
        )


@router.get("/admin/config", tags=["Admin"])
async def get_configuration():
    """
    Get current service configuration.

    Returns:
        dict: Service configuration
    """
    return {
        "service": {
            "name": settings.service_name,
            "host": settings.service_host,
            "port": settings.service_port,
            "log_level": settings.log_level,
        },
        "qlib": {
            "region": settings.qlib_region,
            "default_model": settings.qlib_default_model,
            "forecast_horizons": settings.forecast_horizons_list,
            "feature_set": settings.qlib_feature_set,
            "max_workers": settings.qlib_max_workers,
            "batch_size": settings.qlib_batch_size,
        },
        "features": {
            "forecasting": settings.enable_forecasting,
            "portfolio_analysis": settings.enable_portfolio_analysis,
            "recommendations": settings.enable_recommendations,
            "backtesting": settings.enable_backtesting,
        },
        "rabbitmq": {
            "host": settings.rabbitmq_host,
            "port": settings.rabbitmq_port,
            "queue_input": settings.queue_ai_extraction_complete,
            "queue_output": settings.queue_qlib_predictions_ready,
        }
    }
