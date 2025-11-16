"""
API controller for prediction endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from config.database import get_db
from .prediction_repository import PredictionRepository
from .prediction_service import PredictionService
from .PredictionDTO import (
    PredictionResultsDTO,
    PredictionRequestListDTO,
    PredictionStatusDTO,
    PredictionRequestDTO,
    StockPredictionDTO,
    PortfolioAnalysisDTO,
    RecommendationDTO,
    MarketRegimeDTO,
    PredictionIntervalDTO,
    StockForecastDTO,
    RiskMetricsDTO,
    PerformanceForecastDTO,
    RecommendationFactorsDTO
)

router = APIRouter(prefix="/predictions", tags=["Predictions"])


def _convert_stock_prediction_to_dto(stock_prediction) -> StockPredictionDTO:
    """Convert stock prediction model to DTO."""
    forecasts_dto = [
        StockForecastDTO(
            horizon_days=f["horizon_days"],
            predicted_price=f["predicted_price"],
            predicted_return=f["predicted_return"],
            confidence_score=f["confidence_score"],
            prediction_interval=PredictionIntervalDTO(
                lower=f["prediction_interval"]["lower"],
                upper=f["prediction_interval"]["upper"]
            )
        )
        for f in stock_prediction.forecasts
    ]

    return StockPredictionDTO(
        id=stock_prediction.id,
        ticker=stock_prediction.ticker,
        current_price=stock_prediction.current_price,
        trend=stock_prediction.trend,
        volatility_forecast=stock_prediction.volatility_forecast,
        forecasts=forecasts_dto,
        created_at=stock_prediction.created_at
    )


def _convert_portfolio_to_dto(portfolio) -> Optional[PortfolioAnalysisDTO]:
    """Convert portfolio analysis model to DTO."""
    if not portfolio:
        return None

    return PortfolioAnalysisDTO(
        id=portfolio.id,
        risk_metrics=RiskMetricsDTO(
            sharpe_ratio=portfolio.sharpe_ratio,
            max_drawdown=portfolio.max_drawdown,
            volatility=portfolio.volatility,
            value_at_risk_95=portfolio.value_at_risk_95,
            beta=portfolio.beta,
            alpha=portfolio.alpha
        ),
        performance_forecast=PerformanceForecastDTO(
            expected_return_1d=portfolio.expected_return_1d,
            expected_return_5d=portfolio.expected_return_5d,
            expected_return_30d=portfolio.expected_return_30d
        ),
        diversification_score=portfolio.diversification_score,
        risk_level=portfolio.risk_level,
        created_at=portfolio.created_at
    )


def _convert_recommendation_to_dto(recommendation) -> RecommendationDTO:
    """Convert recommendation model to DTO."""
    return RecommendationDTO(
        id=recommendation.id,
        ticker=recommendation.ticker,
        action=recommendation.action,
        strength=recommendation.strength,
        confidence=recommendation.confidence,
        target_price=recommendation.target_price,
        stop_loss=recommendation.stop_loss,
        rationale=recommendation.rationale,
        factors=RecommendationFactorsDTO(
            technical_score=recommendation.technical_score,
            fundamental_score=recommendation.fundamental_score,
            sentiment_score=recommendation.sentiment_score
        ),
        created_at=recommendation.created_at
    )


def _convert_market_regime_to_dto(market_regime) -> Optional[MarketRegimeDTO]:
    """Convert market regime model to DTO."""
    if not market_regime:
        return None

    return MarketRegimeDTO(
        id=market_regime.id,
        regime=market_regime.regime,
        confidence=market_regime.confidence,
        description=market_regime.description,
        created_at=market_regime.created_at
    )


@router.get("/", response_model=PredictionRequestListDTO)
def get_all_predictions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all prediction requests with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of prediction requests
    """
    repository = PredictionRepository(db)

    requests = repository.get_all_prediction_requests(skip=skip, limit=limit)
    total = repository.count_all_predictions()

    request_dtos = [
        PredictionRequestDTO.from_orm(req) for req in requests
    ]

    return PredictionRequestListDTO(
        total=total,
        requests=request_dtos
    )


@router.get("/request/{request_id}", response_model=PredictionResultsDTO)
def get_prediction_by_request_id(
    request_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete prediction results by request ID.

    Args:
        request_id: Request ID
        db: Database session

    Returns:
        Complete prediction results
    """
    repository = PredictionRepository(db)

    prediction_request = repository.get_prediction_request_by_request_id(request_id)

    if not prediction_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction request not found: {request_id}"
        )

    # Convert to DTOs
    request_dto = PredictionRequestDTO.from_orm(prediction_request)

    stock_predictions_dto = [
        _convert_stock_prediction_to_dto(sp)
        for sp in prediction_request.stock_predictions
    ]

    portfolio_dto = _convert_portfolio_to_dto(prediction_request.portfolio_analysis)

    recommendations_dto = [
        _convert_recommendation_to_dto(rec)
        for rec in prediction_request.recommendations
    ]

    market_regime_dto = _convert_market_regime_to_dto(prediction_request.market_regime)

    return PredictionResultsDTO(
        request=request_dto,
        stock_predictions=stock_predictions_dto,
        portfolio_analysis=portfolio_dto,
        recommendations=recommendations_dto,
        market_regime=market_regime_dto
    )


@router.get("/report/{report_id}", response_model=PredictionResultsDTO)
def get_prediction_by_report_id(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Get prediction results by report ID.

    Args:
        report_id: Report ID
        db: Database session

    Returns:
        Complete prediction results
    """
    repository = PredictionRepository(db)

    prediction_request = repository.get_prediction_request_by_report_id(report_id)

    if not prediction_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No predictions found for report ID: {report_id}"
        )

    # Convert to DTOs (reuse logic from above)
    request_dto = PredictionRequestDTO.from_orm(prediction_request)

    stock_predictions_dto = [
        _convert_stock_prediction_to_dto(sp)
        for sp in prediction_request.stock_predictions
    ]

    portfolio_dto = _convert_portfolio_to_dto(prediction_request.portfolio_analysis)

    recommendations_dto = [
        _convert_recommendation_to_dto(rec)
        for rec in prediction_request.recommendations
    ]

    market_regime_dto = _convert_market_regime_to_dto(prediction_request.market_regime)

    return PredictionResultsDTO(
        request=request_dto,
        stock_predictions=stock_predictions_dto,
        portfolio_analysis=portfolio_dto,
        recommendations=recommendations_dto,
        market_regime=market_regime_dto
    )


@router.get("/status/{request_id}", response_model=PredictionStatusDTO)
def get_prediction_status(
    request_id: str,
    db: Session = Depends(get_db)
):
    """
    Get prediction request status.

    Args:
        request_id: Request ID
        db: Database session

    Returns:
        Prediction request status
    """
    repository = PredictionRepository(db)

    prediction_request = repository.get_prediction_request_by_request_id(request_id)

    if not prediction_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction request not found: {request_id}"
        )

    return PredictionStatusDTO(
        request_id=prediction_request.request_id,
        status=prediction_request.status,
        prediction_status=prediction_request.prediction_status,
        created_at=prediction_request.created_at,
        updated_at=prediction_request.updated_at,
        processing_time_seconds=prediction_request.processing_time_seconds,
        stocks_count=len(prediction_request.stock_predictions),
        recommendations_count=len(prediction_request.recommendations),
        has_portfolio_analysis=prediction_request.portfolio_analysis is not None,
        has_market_regime=prediction_request.market_regime is not None
    )


@router.get("/stocks/{ticker}", response_model=List[StockPredictionDTO])
def get_predictions_by_ticker(
    ticker: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent predictions for a specific stock ticker.

    Args:
        ticker: Stock ticker symbol
        limit: Maximum number of predictions to return
        db: Database session

    Returns:
        List of stock predictions
    """
    # Get recent prediction requests
    repository = PredictionRepository(db)
    recent_requests = repository.get_all_prediction_requests(skip=0, limit=limit)

    # Collect predictions for this ticker
    predictions = []
    for request in recent_requests:
        stock_pred = repository.get_stock_prediction_by_ticker(request.id, ticker)
        if stock_pred:
            predictions.append(_convert_stock_prediction_to_dto(stock_pred))

    if not predictions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No predictions found for ticker: {ticker}"
        )

    return predictions
