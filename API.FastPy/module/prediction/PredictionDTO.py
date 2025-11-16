"""
Data Transfer Objects (DTOs) for Prediction API endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ===========================
# Forecast Models
# ===========================

class PredictionIntervalDTO(BaseModel):
    """Confidence interval for predictions."""
    lower: float
    upper: float


class StockForecastDTO(BaseModel):
    """Individual forecast for a specific time horizon."""
    horizon_days: int
    predicted_price: float
    predicted_return: float
    confidence_score: float
    prediction_interval: PredictionIntervalDTO


class StockPredictionDTO(BaseModel):
    """Stock predictions with all forecasts."""
    id: int
    ticker: str
    current_price: float
    trend: str
    volatility_forecast: float
    forecasts: List[StockForecastDTO]
    created_at: datetime

    class Config:
        from_attributes = True


# ===========================
# Portfolio Analysis Models
# ===========================

class RiskMetricsDTO(BaseModel):
    """Portfolio risk metrics."""
    sharpe_ratio: float
    max_drawdown: float
    volatility: float
    value_at_risk_95: float
    beta: float
    alpha: float


class PerformanceForecastDTO(BaseModel):
    """Expected portfolio performance."""
    expected_return_1d: float
    expected_return_5d: float
    expected_return_30d: float


class PortfolioAnalysisDTO(BaseModel):
    """Complete portfolio analysis."""
    id: int
    risk_metrics: RiskMetricsDTO
    performance_forecast: PerformanceForecastDTO
    diversification_score: float
    risk_level: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===========================
# Recommendation Models
# ===========================

class RecommendationFactorsDTO(BaseModel):
    """Factor scores for recommendations."""
    technical_score: float
    fundamental_score: float
    sentiment_score: float


class RecommendationDTO(BaseModel):
    """Investment recommendation."""
    id: int
    ticker: str
    action: str
    strength: str
    confidence: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    rationale: str
    factors: RecommendationFactorsDTO
    created_at: datetime

    class Config:
        from_attributes = True


# ===========================
# Market Regime Models
# ===========================

class MarketRegimeDTO(BaseModel):
    """Market regime detection."""
    id: int
    regime: str
    confidence: float
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===========================
# Prediction Request Models
# ===========================

class PredictionRequestDTO(BaseModel):
    """Prediction request summary."""
    id: int
    request_id: str
    report_id: Optional[int]
    status: str
    prediction_status: Optional[str]
    model_name: Optional[str]
    model_version: Optional[str]
    feature_set: Optional[str]
    processing_time_seconds: Optional[float]
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str]

    class Config:
        from_attributes = True


class PredictionResultsDTO(BaseModel):
    """Complete prediction results."""
    request: PredictionRequestDTO
    stock_predictions: List[StockPredictionDTO]
    portfolio_analysis: Optional[PortfolioAnalysisDTO]
    recommendations: List[RecommendationDTO]
    market_regime: Optional[MarketRegimeDTO]


# ===========================
# List Response Models
# ===========================

class PredictionRequestListDTO(BaseModel):
    """List response for prediction requests."""
    total: int
    requests: List[PredictionRequestDTO]


# ===========================
# Status Response Models
# ===========================

class PredictionStatusDTO(BaseModel):
    """Status of a prediction request."""
    request_id: str
    status: str
    prediction_status: Optional[str]
    created_at: datetime
    updated_at: datetime
    processing_time_seconds: Optional[float]
    stocks_count: int
    recommendations_count: int
    has_portfolio_analysis: bool
    has_market_regime: bool
