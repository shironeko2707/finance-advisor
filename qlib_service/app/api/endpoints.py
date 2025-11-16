"""
FastAPI REST API endpoints for Qlib service.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime
from loguru import logger

from app.models.schemas import (
    StockPredictionRequest,
    StockPredictionResponse,
    PortfolioAnalysisRequest,
    PortfolioAnalysisResponse,
    RecommendationRequest,
    RecommendationResponse,
    HealthResponse,
    StatusResponse,
    StockForecast,
)
from app.services.forecasting import ForecastingService
from app.services.portfolio_analysis import PortfolioAnalysisService
from app.services.recommendation import RecommendationService
from app.services.qlib_manager import QlibManager
from app.config.settings import settings


# Create router
router = APIRouter()

# Service instances (will be initialized in main.py)
forecasting_service: ForecastingService = None
portfolio_service: PortfolioAnalysisService = None
recommendation_service: RecommendationService = None
qlib_manager: QlibManager = None


def get_services():
    """Dependency to get service instances."""
    global forecasting_service, portfolio_service, recommendation_service, qlib_manager

    if not forecasting_service:
        forecasting_service = ForecastingService()
    if not portfolio_service:
        portfolio_service = PortfolioAnalysisService()
    if not recommendation_service:
        recommendation_service = RecommendationService()
    if not qlib_manager:
        qlib_manager = QlibManager()

    return {
        "forecasting": forecasting_service,
        "portfolio": portfolio_service,
        "recommendation": recommendation_service,
        "qlib": qlib_manager,
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status of the service
    """
    try:
        services = get_services()

        # Check database connection
        database_connected = True  # TODO: Add actual DB check

        # Check RabbitMQ connection
        from app.messaging.publisher import publisher
        rabbitmq_connected = publisher.connected

        # Check Qlib initialization
        qlib_initialized = services["qlib"].initialized

        return HealthResponse(
            status="healthy" if all([database_connected, rabbitmq_connected, qlib_initialized]) else "degraded",
            service=settings.service_name,
            timestamp=datetime.now(),
            qlib_initialized=qlib_initialized,
            database_connected=database_connected,
            rabbitmq_connected=rabbitmq_connected,
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            service=settings.service_name,
            timestamp=datetime.now(),
            qlib_initialized=False,
            database_connected=False,
            rabbitmq_connected=False,
        )


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Get detailed service status.

    Returns:
        Detailed status information
    """
    try:
        services = get_services()
        qlib = services["qlib"]

        # Calculate uptime (placeholder)
        uptime_seconds = 0.0  # TODO: Track actual uptime

        # Get queue stats (placeholder)
        queue_stats = {
            "messages_processed": 0,
            "messages_failed": 0,
            "current_queue_size": 0,
        }

        return StatusResponse(
            service_name=settings.service_name,
            version="1.0.0",
            uptime_seconds=uptime_seconds,
            models_loaded=list(qlib.models_loaded.keys()) if qlib.models_loaded else [],
            qlib_data_available=qlib.data_available,
            queue_stats=queue_stats,
        )

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )


@router.post("/predict/stock", response_model=StockPredictionResponse)
async def predict_stock(request: StockPredictionRequest):
    """
    Predict stock price for multiple horizons.

    Args:
        request: Stock prediction request with ticker and price history

    Returns:
        Stock price predictions
    """
    try:
        services = get_services()
        forecasting = services["forecasting"]

        logger.info(f"Received stock prediction request for {request.ticker}")

        # Create StockData from request
        from app.models.schemas import StockData

        stock_data = StockData(
            ticker=request.ticker,
            name=request.ticker,  # Name not provided, use ticker
            prices=request.price_history,
            financial_metrics=None,
            fundamentals=None,
        )

        # Generate prediction
        prediction = await forecasting.predict_stock_price(
            stock_data=stock_data,
            horizons=request.forecast_horizons
        )

        return StockPredictionResponse(
            ticker=prediction.ticker,
            predictions=prediction.forecasts,
            status="success"
        )

    except Exception as e:
        logger.error(f"Stock prediction failed for {request.ticker}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stock prediction failed: {str(e)}"
        )


@router.post("/predict/portfolio", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio(request: PortfolioAnalysisRequest):
    """
    Analyze portfolio risk and performance.

    Args:
        request: Portfolio analysis request

    Returns:
        Portfolio analysis results
    """
    try:
        services = get_services()
        portfolio = services["portfolio"]

        logger.info(f"Received portfolio analysis request")

        # Create market context
        from app.models.schemas import MarketContext

        market_context = MarketContext(
            region="US",
            benchmark_index=request.benchmark_index,
            risk_free_rate=request.risk_free_rate,
        )

        # Analyze portfolio
        analysis = await portfolio.analyze_portfolio(
            portfolio=request.portfolio,
            stocks_data=request.stocks_data,
            market_context=market_context
        )

        return PortfolioAnalysisResponse(
            analysis=analysis,
            status="success"
        )

    except Exception as e:
        logger.error(f"Portfolio analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Portfolio analysis failed: {str(e)}"
        )


@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Generate investment recommendations.

    Args:
        request: Recommendation request with stocks and parameters

    Returns:
        Investment recommendations
    """
    try:
        services = get_services()
        recommendation = services["recommendation"]

        logger.info(f"Received recommendation request for {len(request.stocks)} stocks")

        # Create market context
        from app.models.schemas import MarketContext

        market_context = MarketContext(
            region="US",
            risk_free_rate=0.045,
        )

        # Generate recommendations
        recommendations = await recommendation.generate_recommendations(
            stocks_data=request.stocks_data,
            portfolio=None,
            market_context=market_context,
            stock_forecasts=[]
        )

        # Detect market regime
        market_regime = await recommendation.detect_market_regime(
            request.stocks_data
        )

        return RecommendationResponse(
            recommendations=recommendations,
            market_regime=market_regime,
            status="success"
        )

    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation generation failed: {str(e)}"
        )


@router.get("/")
async def root():
    """
    Root endpoint.

    Returns:
        Service information
    """
    return {
        "service": settings.service_name,
        "version": "1.0.0",
        "description": "Qlib Advisor & Predictor Service for quantitative investment analysis",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "predict_stock": "/predict/stock",
            "analyze_portfolio": "/predict/portfolio",
            "recommendations": "/recommend",
        }
    }
