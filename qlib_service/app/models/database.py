"""
SQLAlchemy database models for persistence.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Index, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta

Base = declarative_base()


class Prediction(Base):
    """Stock price predictions table."""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(255), nullable=False, index=True)
    report_id = Column(String(255), nullable=False, index=True)
    ticker = Column(String(20), nullable=False)
    current_price = Column(Numeric(12, 4), nullable=False)
    horizon_days = Column(Integer, nullable=False)
    predicted_price = Column(Numeric(12, 4), nullable=False)
    predicted_return = Column(Numeric(8, 6), nullable=False)
    confidence_score = Column(Numeric(5, 4), nullable=False)
    prediction_interval_lower = Column(Numeric(12, 4))
    prediction_interval_upper = Column(Numeric(12, 4))
    trend = Column(String(20))
    volatility_forecast = Column(Numeric(8, 6))
    model_name = Column(String(50), nullable=False)
    model_version = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(
        DateTime,
        default=lambda: datetime.utcnow() + timedelta(days=30),
        nullable=False
    )

    __table_args__ = (
        Index('idx_ticker_created', 'ticker', 'created_at'),
        Index('idx_request_ticker', 'request_id', 'ticker'),
    )

    def __repr__(self):
        return f"<Prediction(ticker={self.ticker}, horizon={self.horizon_days})>"


class RecommendationRecord(Base):
    """Investment recommendations table."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(255), nullable=False, index=True)
    report_id = Column(String(255), nullable=False, index=True)
    ticker = Column(String(20), nullable=False)
    action = Column(String(10), nullable=False)  # buy, sell, hold
    strength = Column(String(20), nullable=False)  # strong, moderate, weak
    confidence = Column(Numeric(5, 4), nullable=False)
    target_price = Column(Numeric(12, 4))
    stop_loss = Column(Numeric(12, 4))
    rationale = Column(Text, nullable=False)
    technical_score = Column(Numeric(5, 4))
    fundamental_score = Column(Numeric(5, 4))
    sentiment_score = Column(Numeric(5, 4))
    model_name = Column(String(50), nullable=False)
    model_version = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_ticker_action', 'ticker', 'action'),
        Index('idx_request_ticker', 'request_id', 'ticker'),
    )

    def __repr__(self):
        return f"<Recommendation(ticker={self.ticker}, action={self.action})>"


class PortfolioAnalysisRecord(Base):
    """Portfolio analysis results table."""
    __tablename__ = "portfolio_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(255), nullable=False, unique=True, index=True)
    report_id = Column(String(255), nullable=False, index=True)
    sharpe_ratio = Column(Numeric(8, 4))
    max_drawdown = Column(Numeric(8, 6))
    volatility = Column(Numeric(8, 6))
    value_at_risk_95 = Column(Numeric(8, 6))
    beta = Column(Numeric(8, 6))
    alpha = Column(Numeric(8, 6))
    expected_return_1d = Column(Numeric(8, 6))
    expected_return_5d = Column(Numeric(8, 6))
    expected_return_30d = Column(Numeric(8, 6))
    diversification_score = Column(Numeric(5, 4))
    risk_level = Column(String(20))
    market_regime = Column(String(30))
    market_regime_confidence = Column(Numeric(5, 4))
    model_name = Column(String(50), nullable=False)
    model_version = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<PortfolioAnalysis(request_id={self.request_id})>"
