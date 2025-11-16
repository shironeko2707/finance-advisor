# Qlib Service Data Schemas

## Overview

This document defines all data schemas used by the Qlib Advisor & Predictor service, including RabbitMQ message formats, API request/response models, and database schemas.

## RabbitMQ Message Schemas

### 1. AI Extraction Complete Message

**Queue**: `ai_extraction_complete`
**Publisher**: AI Service
**Consumer**: Qlib Service

```json
{
  "request_id": "req_1234567890",
  "report_id": "rpt_abcdefgh",
  "timestamp": "2025-11-16T10:30:00Z",
  "extraction_status": "success",
  "extracted_data": {
    "stocks": [
      {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "prices": [
          {
            "date": "2025-11-01",
            "open": 150.25,
            "high": 152.10,
            "low": 149.80,
            "close": 151.50,
            "volume": 85000000,
            "adj_close": 151.50
          }
        ],
        "financial_metrics": {
          "pe_ratio": 28.5,
          "market_cap": 2450000000000,
          "eps": 5.31,
          "dividend_yield": 0.52,
          "beta": 1.21
        },
        "fundamentals": {
          "revenue": 385000000000,
          "net_income": 95000000000,
          "total_assets": 350000000000,
          "total_liabilities": 280000000000,
          "cash_flow": 105000000000
        }
      }
    ],
    "portfolio": {
      "total_value": 1000000,
      "positions": [
        {
          "ticker": "AAPL",
          "shares": 1000,
          "avg_cost": 145.50,
          "current_value": 151500,
          "weight": 0.15
        }
      ]
    },
    "market_context": {
      "region": "US",
      "sector": "Technology",
      "benchmark_index": "SPY",
      "risk_free_rate": 0.045
    }
  },
  "document_metadata": {
    "source_files": ["report_q4_2024.pdf", "portfolio_holdings.xlsx"],
    "extraction_method": "azure_document_intelligence",
    "confidence_score": 0.92
  }
}
```

#### Schema Definition (Pydantic)

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date

class PriceData(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: float

class FinancialMetrics(BaseModel):
    pe_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None

class Fundamentals(BaseModel):
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    cash_flow: Optional[float] = None

class StockData(BaseModel):
    ticker: str
    name: str
    prices: List[PriceData]
    financial_metrics: Optional[FinancialMetrics] = None
    fundamentals: Optional[Fundamentals] = None

class PortfolioPosition(BaseModel):
    ticker: str
    shares: int
    avg_cost: float
    current_value: float
    weight: float

class Portfolio(BaseModel):
    total_value: float
    positions: List[PortfolioPosition]

class MarketContext(BaseModel):
    region: str = "US"
    sector: Optional[str] = None
    benchmark_index: str = "SPY"
    risk_free_rate: float = 0.045

class DocumentMetadata(BaseModel):
    source_files: List[str]
    extraction_method: str
    confidence_score: float

class ExtractedData(BaseModel):
    stocks: List[StockData]
    portfolio: Optional[Portfolio] = None
    market_context: MarketContext

class AIExtractionCompleteMessage(BaseModel):
    request_id: str
    report_id: str
    timestamp: datetime
    extraction_status: str
    extracted_data: ExtractedData
    document_metadata: DocumentMetadata
```

---

### 2. Qlib Predictions Ready Message

**Queue**: `qlib_predictions_ready`
**Publisher**: Qlib Service
**Consumer**: Report Module

```json
{
  "request_id": "req_1234567890",
  "report_id": "rpt_abcdefgh",
  "timestamp": "2025-11-16T10:32:15Z",
  "prediction_status": "success",
  "predictions": {
    "stock_forecasts": [
      {
        "ticker": "AAPL",
        "current_price": 151.50,
        "forecasts": [
          {
            "horizon_days": 1,
            "predicted_price": 152.30,
            "predicted_return": 0.0053,
            "confidence_score": 0.78,
            "prediction_interval": {
              "lower": 150.80,
              "upper": 153.80
            }
          },
          {
            "horizon_days": 5,
            "predicted_price": 155.20,
            "predicted_return": 0.0244,
            "confidence_score": 0.65,
            "prediction_interval": {
              "lower": 149.50,
              "upper": 160.90
            }
          }
        ],
        "trend": "bullish",
        "volatility_forecast": 0.025
      }
    ],
    "portfolio_analysis": {
      "risk_metrics": {
        "sharpe_ratio": 1.85,
        "max_drawdown": -0.12,
        "volatility": 0.18,
        "value_at_risk_95": -0.035,
        "beta": 1.05,
        "alpha": 0.023
      },
      "performance_forecast": {
        "expected_return_1d": 0.0042,
        "expected_return_5d": 0.0215,
        "expected_return_30d": 0.0890
      },
      "diversification_score": 0.72,
      "risk_level": "moderate"
    },
    "recommendations": [
      {
        "ticker": "AAPL",
        "action": "buy",
        "strength": "strong",
        "confidence": 0.82,
        "target_price": 165.00,
        "stop_loss": 145.00,
        "rationale": "Strong upward trend with positive momentum indicators. Forecasted 8.9% gain over 30 days.",
        "factors": {
          "technical_score": 0.85,
          "fundamental_score": 0.78,
          "sentiment_score": 0.72
        }
      }
    ],
    "market_regime": {
      "regime": "trending_up",
      "confidence": 0.74,
      "description": "Market showing bullish momentum with low volatility"
    }
  },
  "model_metadata": {
    "primary_model": "lightgbm",
    "model_version": "1.2.0",
    "training_date": "2025-11-01",
    "feature_set": "alpha158",
    "processing_time_seconds": 12.5
  },
  "error_message": null
}
```

#### Schema Definition (Pydantic)

```python
class PredictionInterval(BaseModel):
    lower: float
    upper: float

class StockForecast(BaseModel):
    horizon_days: int
    predicted_price: float
    predicted_return: float
    confidence_score: float
    prediction_interval: PredictionInterval

class StockPrediction(BaseModel):
    ticker: str
    current_price: float
    forecasts: List[StockForecast]
    trend: str  # "bullish", "bearish", "neutral"
    volatility_forecast: float

class RiskMetrics(BaseModel):
    sharpe_ratio: float
    max_drawdown: float
    volatility: float
    value_at_risk_95: float
    beta: float
    alpha: float

class PerformanceForecast(BaseModel):
    expected_return_1d: float
    expected_return_5d: float
    expected_return_30d: float

class PortfolioAnalysis(BaseModel):
    risk_metrics: RiskMetrics
    performance_forecast: PerformanceForecast
    diversification_score: float
    risk_level: str  # "low", "moderate", "high"

class RecommendationFactors(BaseModel):
    technical_score: float
    fundamental_score: float
    sentiment_score: float

class Recommendation(BaseModel):
    ticker: str
    action: str  # "buy", "sell", "hold"
    strength: str  # "strong", "moderate", "weak"
    confidence: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    rationale: str
    factors: RecommendationFactors

class MarketRegime(BaseModel):
    regime: str  # "trending_up", "trending_down", "volatile", "sideways"
    confidence: float
    description: str

class PredictionData(BaseModel):
    stock_forecasts: List[StockPrediction]
    portfolio_analysis: Optional[PortfolioAnalysis] = None
    recommendations: List[Recommendation]
    market_regime: MarketRegime

class ModelMetadata(BaseModel):
    primary_model: str
    model_version: str
    training_date: date
    feature_set: str
    processing_time_seconds: float

class QlibPredictionsReadyMessage(BaseModel):
    request_id: str
    report_id: str
    timestamp: datetime
    prediction_status: str  # "success", "partial_success", "failed"
    predictions: Optional[PredictionData] = None
    model_metadata: ModelMetadata
    error_message: Optional[str] = None
```

---

## Database Schemas

### 1. Predictions Table

Stores stock price predictions for audit and historical analysis.

```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255) NOT NULL,
    report_id VARCHAR(255) NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    current_price DECIMAL(12, 4) NOT NULL,
    horizon_days INTEGER NOT NULL,
    predicted_price DECIMAL(12, 4) NOT NULL,
    predicted_return DECIMAL(8, 6) NOT NULL,
    confidence_score DECIMAL(5, 4) NOT NULL,
    prediction_interval_lower DECIMAL(12, 4),
    prediction_interval_upper DECIMAL(12, 4),
    trend VARCHAR(20),
    volatility_forecast DECIMAL(8, 6),
    model_name VARCHAR(50) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_request_id (request_id),
    INDEX idx_report_id (report_id),
    INDEX idx_ticker_created (ticker, created_at)
);
```

#### SQLAlchemy Model

```python
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta

Base = declarative_base()

class Prediction(Base):
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
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))

    __table_args__ = (
        Index('idx_ticker_created', 'ticker', 'created_at'),
    )
```

---

### 2. Recommendations Table

Stores investment recommendations for audit trail.

```sql
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255) NOT NULL,
    report_id VARCHAR(255) NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    action VARCHAR(10) NOT NULL,  -- buy, sell, hold
    strength VARCHAR(20) NOT NULL,  -- strong, moderate, weak
    confidence DECIMAL(5, 4) NOT NULL,
    target_price DECIMAL(12, 4),
    stop_loss DECIMAL(12, 4),
    rationale TEXT NOT NULL,
    technical_score DECIMAL(5, 4),
    fundamental_score DECIMAL(5, 4),
    sentiment_score DECIMAL(5, 4),
    model_name VARCHAR(50) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_request_id (request_id),
    INDEX idx_report_id (report_id),
    INDEX idx_ticker_action (ticker, action)
);
```

#### SQLAlchemy Model

```python
class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(255), nullable=False, index=True)
    report_id = Column(String(255), nullable=False, index=True)
    ticker = Column(String(20), nullable=False)
    action = Column(String(10), nullable=False)
    strength = Column(String(20), nullable=False)
    confidence = Column(Numeric(5, 4), nullable=False)
    target_price = Column(Numeric(12, 4))
    stop_loss = Column(Numeric(12, 4))
    rationale = Column(String)
    technical_score = Column(Numeric(5, 4))
    fundamental_score = Column(Numeric(5, 4))
    sentiment_score = Column(Numeric(5, 4))
    model_name = Column(String(50), nullable=False)
    model_version = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_ticker_action', 'ticker', 'action'),
    )
```

---

### 3. Portfolio Analysis Table

Stores portfolio-level risk and performance metrics.

```sql
CREATE TABLE portfolio_analysis (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255) NOT NULL UNIQUE,
    report_id VARCHAR(255) NOT NULL,
    sharpe_ratio DECIMAL(8, 4),
    max_drawdown DECIMAL(8, 6),
    volatility DECIMAL(8, 6),
    value_at_risk_95 DECIMAL(8, 6),
    beta DECIMAL(8, 6),
    alpha DECIMAL(8, 6),
    expected_return_1d DECIMAL(8, 6),
    expected_return_5d DECIMAL(8, 6),
    expected_return_30d DECIMAL(8, 6),
    diversification_score DECIMAL(5, 4),
    risk_level VARCHAR(20),
    market_regime VARCHAR(30),
    market_regime_confidence DECIMAL(5, 4),
    model_name VARCHAR(50) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_request_id (request_id),
    INDEX idx_report_id (report_id)
);
```

#### SQLAlchemy Model

```python
class PortfolioAnalysisRecord(Base):
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
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## API Request/Response Schemas

### 1. Stock Prediction Request

```python
class StockPredictionRequest(BaseModel):
    ticker: str
    price_history: List[PriceData]
    forecast_horizons: List[int] = [1, 5, 30]  # days
    model: str = "lightgbm"

class StockPredictionResponse(BaseModel):
    ticker: str
    predictions: List[StockForecast]
    status: str
```

### 2. Portfolio Analysis Request

```python
class PortfolioAnalysisRequest(BaseModel):
    portfolio: Portfolio
    stocks_data: List[StockData]
    benchmark_index: str = "SPY"
    risk_free_rate: float = 0.045

class PortfolioAnalysisResponse(BaseModel):
    analysis: PortfolioAnalysis
    status: str
```

### 3. Recommendation Request

```python
class RecommendationRequest(BaseModel):
    stocks: List[str]  # tickers
    stocks_data: List[StockData]
    risk_tolerance: str = "moderate"  # low, moderate, high
    investment_horizon: int = 30  # days

class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation]
    market_regime: MarketRegime
    status: str
```

---

## Data Validation Rules

### Price Data

- `open`, `high`, `low`, `close` must be > 0
- `high` >= `low`
- `volume` >= 0
- `date` in ISO 8601 format

### Confidence Scores

- All confidence scores: 0.0 to 1.0
- Prediction intervals: lower < upper

### Tickers

- Format: 1-10 uppercase alphanumeric characters
- Examples: AAPL, MSFT, BRK.A

### Returns

- Decimal format: -1.0 to +∞
- Example: 0.0244 = 2.44% return

---

## Data Retention Policy

- **Predictions**: 30 days (configurable)
- **Recommendations**: 90 days (audit trail)
- **Portfolio Analysis**: 90 days
- **Cleanup**: Automated daily job to remove expired records

---

## Versioning

- **Message Schema Version**: Included in `model_metadata.schema_version`
- **Backward Compatibility**: Maintain for at least 2 versions
- **Migration Strategy**: Gradual rollout with dual-version support
