"""
Prediction database models for storing Qlib prediction results.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime


class PredictionRequest(Base):
    """
    Master table for tracking prediction requests and their lifecycle.
    """
    __tablename__ = "prediction_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(100), unique=True, nullable=False, index=True)
    report_id = Column(Integer, ForeignKey("generated_reports.id"), nullable=True)

    # Request metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Processing status
    status = Column(String(50), default="pending")  # pending, processing, success, failed
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)

    # Prediction metadata
    prediction_status = Column(String(50), nullable=True)  # success, partial_success, failed
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    feature_set = Column(String(100), nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)

    # Relationships
    stock_predictions = relationship("StockPrediction", back_populates="prediction_request", cascade="all, delete-orphan")
    portfolio_analysis = relationship("PortfolioAnalysis", back_populates="prediction_request", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="prediction_request", cascade="all, delete-orphan")
    market_regime = relationship("MarketRegime", back_populates="prediction_request", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PredictionRequest(id={self.id}, request_id={self.request_id}, status={self.status})>"


class StockPrediction(Base):
    """
    Stock price predictions for individual tickers.
    """
    __tablename__ = "stock_predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_request_id = Column(Integer, ForeignKey("prediction_requests.id"), nullable=False)

    # Stock information
    ticker = Column(String(20), nullable=False, index=True)
    current_price = Column(Float, nullable=False)
    trend = Column(String(20), nullable=False)  # bullish, bearish, neutral
    volatility_forecast = Column(Float, nullable=False)

    # Forecasts (JSON array of forecast objects)
    forecasts = Column(JSON, nullable=False)  # [{horizon_days, predicted_price, predicted_return, confidence_score, prediction_interval}]

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    prediction_request = relationship("PredictionRequest", back_populates="stock_predictions")

    def __repr__(self):
        return f"<StockPrediction(id={self.id}, ticker={self.ticker}, trend={self.trend})>"


class PortfolioAnalysis(Base):
    """
    Portfolio-level risk and performance analysis.
    """
    __tablename__ = "portfolio_analysis"

    id = Column(Integer, primary_key=True, index=True)
    prediction_request_id = Column(Integer, ForeignKey("prediction_requests.id"), nullable=False, unique=True)

    # Risk metrics
    sharpe_ratio = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    volatility = Column(Float, nullable=False)
    value_at_risk_95 = Column(Float, nullable=False)
    beta = Column(Float, nullable=False)
    alpha = Column(Float, nullable=False)

    # Performance forecasts
    expected_return_1d = Column(Float, nullable=False)
    expected_return_5d = Column(Float, nullable=False)
    expected_return_30d = Column(Float, nullable=False)

    # Overall metrics
    diversification_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # low, moderate, high

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    prediction_request = relationship("PredictionRequest", back_populates="portfolio_analysis")

    def __repr__(self):
        return f"<PortfolioAnalysis(id={self.id}, sharpe_ratio={self.sharpe_ratio}, risk_level={self.risk_level})>"


class Recommendation(Base):
    """
    Investment recommendations for stocks.
    """
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    prediction_request_id = Column(Integer, ForeignKey("prediction_requests.id"), nullable=False)

    # Stock information
    ticker = Column(String(20), nullable=False, index=True)

    # Recommendation details
    action = Column(String(10), nullable=False)  # buy, sell, hold
    strength = Column(String(20), nullable=False)  # strong, moderate, weak
    confidence = Column(Float, nullable=False)
    target_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    rationale = Column(Text, nullable=False)

    # Factor scores
    technical_score = Column(Float, nullable=False)
    fundamental_score = Column(Float, nullable=False)
    sentiment_score = Column(Float, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    prediction_request = relationship("PredictionRequest", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation(id={self.id}, ticker={self.ticker}, action={self.action}, strength={self.strength})>"


class MarketRegime(Base):
    """
    Market regime detection and classification.
    """
    __tablename__ = "market_regimes"

    id = Column(Integer, primary_key=True, index=True)
    prediction_request_id = Column(Integer, ForeignKey("prediction_requests.id"), nullable=False, unique=True)

    # Regime information
    regime = Column(String(50), nullable=False)  # trending_up, trending_down, volatile, sideways
    confidence = Column(Float, nullable=False)
    description = Column(Text, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    prediction_request = relationship("PredictionRequest", back_populates="market_regime")

    def __repr__(self):
        return f"<MarketRegime(id={self.id}, regime={self.regime}, confidence={self.confidence})>"
