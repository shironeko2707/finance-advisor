# Qlib Advisor & Predictor Service Architecture

## Overview

The Qlib Advisor & Predictor service is a new microservice that integrates Microsoft Qlib quantitative investment platform into the Khengleong finance automation system. It sits between AI data extraction and report generation, providing predictive analytics, risk assessment, and investment recommendations.

## Service Position in Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐     ┌────────────┐     ┌─────────────┐
│   Frontend  │────▶│  API.FastPy │────▶│   ai_api (AI     │────▶│   Qlib     │────▶│   Report    │
│  (React)    │     │  (FastAPI)  │     │   Extraction)    │     │  Service   │     │  Generation │
└─────────────┘     └─────────────┘     └──────────────────┘     └────────────┘     └─────────────┘
                           │                      │                       │                  │
                           ▼                      ▼                       ▼                  ▼
                    ┌─────────────┐     ┌─────────────────┐     ┌────────────────┐ ┌──────────────┐
                    │  PostgreSQL │     │   Azure AI      │     │   Qlib DB      │ │  PostgreSQL  │
                    │  (Main DB)  │     │   Services      │     │ (Market Data)  │ │ (Predictions)│
                    └─────────────┘     └─────────────────┘     └────────────────┘ └──────────────┘
                           │                      │                       │                  │
                           └──────────────────────┴───────────────────────┴──────────────────┘
                                                   │
                                            ┌──────▼──────┐
                                            │  RabbitMQ   │
                                            │   Queues    │
                                            └─────────────┘
```

## Service Architecture

### Component Structure

```
qlib_service/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py              # Environment configuration
│   │   └── qlib_config.py           # Qlib-specific configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py               # Pydantic models for API
│   │   └── database.py              # SQLAlchemy models for predictions
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_adapter.py          # AI data → Qlib format conversion
│   │   ├── forecasting.py           # Stock price prediction
│   │   ├── portfolio_analysis.py    # Risk & portfolio analysis
│   │   ├── recommendation.py        # Buy/Sell/Hold signals
│   │   └── qlib_manager.py          # Qlib initialization & management
│   ├── messaging/
│   │   ├── __init__.py
│   │   ├── consumer.py              # RabbitMQ consumer (AI extraction)
│   │   └── publisher.py             # RabbitMQ publisher (predictions)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                # REST API endpoints
│   │   └── dependencies.py          # FastAPI dependencies
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                # Logging configuration
│       └── helpers.py               # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_data_adapter.py
│   ├── test_forecasting.py
│   └── test_integration.py
├── qlib_data/                       # Qlib market data storage
├── models/                          # Trained ML models
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## Technology Stack

### Core Dependencies

- **FastAPI** (0.104.1): Web framework for REST API
- **Qlib** (pyqlib): Microsoft quantitative investment library
- **SQLAlchemy** (2.0.23): ORM for prediction persistence
- **RabbitMQ** (aio-pika 1.3.2): Async message queue client
- **PostgreSQL**: Predictions and recommendations storage
- **Pydantic** (2.0+): Data validation

### Qlib-Specific Dependencies

- **pandas** (1.5+): Data manipulation
- **numpy** (1.24+): Numerical computing
- **lightgbm** (4.0+): Gradient boosting models
- **torch** (2.0+): Deep learning models (LSTM, Transformer)
- **scikit-learn** (1.3+): ML utilities

## Data Flow Architecture

### Message Flow

```
1. User uploads PDF/Excel
   ↓
2. API.FastPy validates and stores files
   ↓
3. API.FastPy publishes to RabbitMQ: "report_requests"
   ↓
4. AI Service consumes, extracts data from documents
   ↓
5. AI Service publishes to RabbitMQ: "ai_extraction_complete" ✨ NEW
   ↓
6. Qlib Service consumes extracted data ✨ NEW
   ↓
7. Qlib Service performs:
   - Stock price forecasting
   - Portfolio risk analysis
   - Investment recommendations
   ↓
8. Qlib Service publishes to RabbitMQ: "qlib_predictions_ready" ✨ NEW
   ↓
9. Report Module consumes predictions + extracted data
   ↓
10. Report Module generates enriched Excel report
    ↓
11. API.FastPy returns report to user
```

## Key Features

### 1. Stock Price Forecasting

- **Input**: Historical price data, financial indicators
- **Models**: LightGBM (default), LSTM, GRU, Transformer
- **Output**: Predicted price movements, confidence scores
- **Horizon**: 1-day, 5-day, 30-day forecasts

### 2. Portfolio Analysis

- **Metrics**:
  - Sharpe Ratio
  - Maximum Drawdown
  - Value at Risk (VaR)
  - Beta, Alpha
  - Volatility measures
- **Output**: Risk assessment scores, diversification analysis

### 3. Recommendation Engine

- **Signals**: Buy, Hold, Sell with confidence levels
- **Factors**:
  - Predicted returns
  - Risk-adjusted performance
  - Market regime detection
  - Sector rotation signals
- **Output**: Ranked recommendations with rationale

### 4. Alpha Factor Analysis

- **Built-in**: Alpha158 feature set (158 technical indicators)
- **Custom**: User-defined factors from extracted data
- **Output**: Factor importance scores, contribution analysis

## Scalability & Performance

### Async Processing

- Non-blocking RabbitMQ consumers
- Async database operations
- Parallel model inference for multiple stocks

### Caching Strategy

- Cache trained models in memory
- Cache market data with TTL
- Redis integration (future enhancement)

### Model Management

- Pre-trained models loaded on startup
- Online model updates without downtime
- Version control for model artifacts

## Error Handling & Resilience

### Retry Logic

- RabbitMQ connection: 5 retries with exponential backoff
- Database operations: 3 retries
- External API calls: Configurable retries

### Fallback Mechanisms

- If Qlib prediction fails → Use historical averages
- If specific model fails → Fall back to simpler model (LightGBM)
- If entire service fails → Report generation continues without predictions

### Health Checks

- `/health` endpoint for container orchestration
- Database connectivity check
- RabbitMQ connectivity check
- Qlib data availability check

## Security Considerations

### Data Privacy

- Extracted financial data encrypted at rest
- No persistent storage of sensitive document content
- Predictions stored with TTL (30 days default)

### Access Control

- JWT authentication for REST API (inherited from API.FastPy)
- Internal-only RabbitMQ queues (not exposed externally)

## Monitoring & Observability

### Logging

- Structured logging with Loguru
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log aggregation ready (JSON format)

### Metrics (Future)

- Prediction accuracy over time
- Processing latency (p50, p95, p99)
- Model performance metrics
- Queue depth monitoring

## Configuration

### Environment Variables

```bash
# Service Configuration
QLIB_SERVICE_HOST=0.0.0.0
QLIB_SERVICE_PORT=8081

# Database Configuration
DATABASE_URL=postgresql://user:pass@postgres:5432/lengkeng
QLIB_DB_PATH=/app/qlib_data/cn_data

# RabbitMQ Configuration
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=rabbitmq
RABBITMQ_PASSWORD=rabbitmq
QUEUE_AI_EXTRACTION_COMPLETE=ai_extraction_complete
QUEUE_QLIB_PREDICTIONS_READY=qlib_predictions_ready

# Qlib Configuration
QLIB_REGION=cn  # cn, us, etc.
QLIB_DEFAULT_MODEL=lightgbm
QLIB_FORECAST_HORIZON=5  # days
QLIB_CACHE_MODELS=true

# Performance Tuning
QLIB_MAX_WORKERS=4
QLIB_BATCH_SIZE=10
QLIB_PREDICTION_TIMEOUT=300  # seconds
```

## Deployment

### Docker Deployment

- Standalone container with Qlib pre-installed
- Volume mounts for model and data persistence
- Health checks for orchestration

### Resource Requirements

- **CPU**: 2+ cores (model inference)
- **Memory**: 4GB minimum, 8GB recommended
- **Storage**: 10GB for market data + models

### Networking

- **Port 8081**: REST API (internal)
- **Port 5672**: RabbitMQ connection (internal)
- **Port 5432**: PostgreSQL connection (internal)

## API Endpoints

### Health & Status

- `GET /health` - Service health check
- `GET /status` - Detailed status (Qlib data, models loaded)

### Predictions (Internal)

- `POST /predict/stock` - Single stock prediction
- `POST /predict/portfolio` - Portfolio analysis
- `POST /recommend` - Investment recommendations

### Admin (Internal)

- `POST /admin/reload-models` - Reload ML models
- `POST /admin/update-data` - Update market data
- `GET /admin/metrics` - Service metrics

## Integration Points

### Upstream (AI Service)

- **Input**: Extracted financial data via RabbitMQ
- **Format**: JSON with stock prices, indicators, metadata
- **Queue**: `ai_extraction_complete`

### Downstream (Report Module)

- **Output**: Predictions and recommendations via RabbitMQ
- **Format**: JSON with forecasts, risk metrics, signals
- **Queue**: `qlib_predictions_ready`

### Database (PostgreSQL)

- **Tables**: `predictions`, `recommendations`, `forecast_scores`
- **Access**: Read/Write via SQLAlchemy ORM

## Future Enhancements

1. **Real-time Market Data**: Integration with live market feeds
2. **Reinforcement Learning**: RL-based trading strategies
3. **Multi-Asset Support**: Bonds, commodities, forex
4. **Ensemble Models**: Combine multiple models for better accuracy
5. **Explainable AI**: SHAP values for prediction explanations
6. **Backtesting API**: Historical performance simulation
7. **Model Retraining**: Automated periodic retraining pipeline

## References

- [Qlib Official Documentation](https://qlib.readthedocs.io/)
- [Qlib GitHub Repository](https://github.com/microsoft/qlib)
- [Qlib Research Paper](https://arxiv.org/abs/2009.11189)
