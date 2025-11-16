"""
Pydantic models for data validation and serialization.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal


# ===========================
# AI Extraction Message Models
# ===========================

class PriceData(BaseModel):
    """Stock price data for a single date."""
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: Optional[float] = None

    class Config:
        from_attributes = True


class FinancialMetrics(BaseModel):
    """Financial metrics for a stock."""
    pe_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None


class Fundamentals(BaseModel):
    """Fundamental financial data."""
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    cash_flow: Optional[float] = None


class StockData(BaseModel):
    """Complete stock data including prices and fundamentals."""
    ticker: str
    name: str
    prices: List[PriceData]
    financial_metrics: Optional[FinancialMetrics] = None
    fundamentals: Optional[Fundamentals] = None


class PortfolioPosition(BaseModel):
    """Single position in a portfolio."""
    ticker: str
    shares: int
    avg_cost: float
    current_value: float
    weight: float


class Portfolio(BaseModel):
    """Portfolio holdings data."""
    total_value: float
    positions: List[PortfolioPosition]


class MarketContext(BaseModel):
    """Market and benchmark context."""
    region: str = "US"
    sector: Optional[str] = None
    benchmark_index: str = "SPY"
    risk_free_rate: float = 0.045


class DocumentMetadata(BaseModel):
    """Metadata about source documents."""
    source_files: List[str]
    extraction_method: str
    confidence_score: float


class ExtractedData(BaseModel):
    """All extracted data from AI service."""
    stocks: List[StockData]
    portfolio: Optional[Portfolio] = None
    market_context: MarketContext


class AIExtractionCompleteMessage(BaseModel):
    """Message published when AI extraction completes."""
    request_id: str
    report_id: str
    timestamp: datetime
    extraction_status: str  # "success", "partial", "failed"
    extracted_data: ExtractedData
    document_metadata: DocumentMetadata


# ===========================
# Prediction Result Models
# ===========================

class PredictionInterval(BaseModel):
    """Confidence interval for predictions."""
    lower: float
    upper: float


class StockForecast(BaseModel):
    """Single forecast for a specific time horizon."""
    horizon_days: int
    predicted_price: float
    predicted_return: float
    confidence_score: float
    prediction_interval: PredictionInterval


class StockPrediction(BaseModel):
    """All predictions for a single stock."""
    ticker: str
    current_price: float
    forecasts: List[StockForecast]
    trend: str  # "bullish", "bearish", "neutral"
    volatility_forecast: float


class RiskMetrics(BaseModel):
    """Portfolio risk metrics."""
    sharpe_ratio: float
    max_drawdown: float
    volatility: float
    value_at_risk_95: float
    beta: float
    alpha: float


class PerformanceForecast(BaseModel):
    """Expected portfolio performance."""
    expected_return_1d: float
    expected_return_5d: float
    expected_return_30d: float


class PortfolioAnalysis(BaseModel):
    """Complete portfolio analysis results."""
    risk_metrics: RiskMetrics
    performance_forecast: PerformanceForecast
    diversification_score: float
    risk_level: str  # "low", "moderate", "high"


class RecommendationFactors(BaseModel):
    """Factor scores for recommendations."""
    technical_score: float
    fundamental_score: float
    sentiment_score: float


class Recommendation(BaseModel):
    """Investment recommendation for a stock."""
    ticker: str
    action: str  # "buy", "sell", "hold"
    strength: str  # "strong", "moderate", "weak"
    confidence: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    rationale: str
    factors: RecommendationFactors


class MarketRegime(BaseModel):
    """Current market regime detection."""
    regime: str  # "trending_up", "trending_down", "volatile", "sideways"
    confidence: float
    description: str


class PredictionData(BaseModel):
    """All prediction results."""
    stock_forecasts: List[StockPrediction]
    portfolio_analysis: Optional[PortfolioAnalysis] = None
    recommendations: List[Recommendation]
    market_regime: MarketRegime


class ModelMetadata(BaseModel):
    """Metadata about the prediction model."""
    primary_model: str
    model_version: str
    training_date: date
    feature_set: str
    processing_time_seconds: float


class QlibPredictionsReadyMessage(BaseModel):
    """Message published when Qlib predictions are ready."""
    request_id: str
    report_id: str
    timestamp: datetime
    prediction_status: str  # "success", "partial_success", "failed"
    predictions: Optional[PredictionData] = None
    model_metadata: ModelMetadata
    error_message: Optional[str] = None


# ===========================
# API Request/Response Models
# ===========================

class StockPredictionRequest(BaseModel):
    """Request for stock price prediction."""
    ticker: str
    price_history: List[PriceData]
    forecast_horizons: List[int] = [1, 5, 30]
    model: str = "lightgbm"


class StockPredictionResponse(BaseModel):
    """Response with stock predictions."""
    ticker: str
    predictions: List[StockForecast]
    status: str


class PortfolioAnalysisRequest(BaseModel):
    """Request for portfolio analysis."""
    portfolio: Portfolio
    stocks_data: List[StockData]
    benchmark_index: str = "SPY"
    risk_free_rate: float = 0.045


class PortfolioAnalysisResponse(BaseModel):
    """Response with portfolio analysis."""
    analysis: PortfolioAnalysis
    status: str


class RecommendationRequest(BaseModel):
    """Request for investment recommendations."""
    stocks: List[str]  # tickers
    stocks_data: List[StockData]
    risk_tolerance: str = "moderate"
    investment_horizon: int = 30


class RecommendationResponse(BaseModel):
    """Response with recommendations."""
    recommendations: List[Recommendation]
    market_regime: MarketRegime
    status: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    timestamp: datetime
    qlib_initialized: bool
    database_connected: bool
    rabbitmq_connected: bool


class StatusResponse(BaseModel):
    """Detailed status response."""
    service_name: str
    version: str
    uptime_seconds: float
    models_loaded: List[str]
    qlib_data_available: bool
    queue_stats: Dict[str, Any]
