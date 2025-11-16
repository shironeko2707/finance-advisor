# Qlib Advisor & Predictor Service

## Overview

The Qlib Advisor & Predictor service is a microservice that integrates **Microsoft Qlib** quantitative investment platform into the Khengleong finance automation system. It provides AI-powered stock price forecasting, portfolio risk analysis, and investment recommendations.

## Architecture

This service sits between the AI data extraction service and the report generation module:

```
AI Service (Extract) → RabbitMQ → Qlib Service (Predict) → RabbitMQ → Report Module (Generate)
```

## Features

### 1. Stock Price Forecasting
- Multi-horizon predictions (1-day, 5-day, 30-day)
- Confidence intervals and scores
- Trend detection (bullish/bearish/neutral)
- Volatility forecasting

### 2. Portfolio Analysis
- Risk metrics (Sharpe ratio, max drawdown, VaR, etc.)
- Performance forecasts
- Diversification scoring
- Risk level classification

### 3. Investment Recommendations
- Buy/Sell/Hold signals
- Confidence-based strength ratings
- Target prices and stop-loss levels
- Multi-factor scoring (technical, fundamental, sentiment)

### 4. Market Regime Detection
- Trend identification
- Volatility regime classification
- Market sentiment analysis

## Technology Stack

- **FastAPI**: Web framework for REST API
- **Qlib**: Microsoft quantitative investment platform
- **LightGBM**: Default forecasting model
- **SQLAlchemy**: Database ORM for PostgreSQL
- **RabbitMQ**: Message queue (aio-pika client)
- **Pandas/NumPy**: Data processing
- **Loguru**: Structured logging

## Directory Structure

```
qlib_service/
├── app/
│   ├── main.py                  # FastAPI app & lifecycle
│   ├── config/
│   │   ├── settings.py          # Environment configuration
│   │   └── __init__.py
│   ├── models/
│   │   ├── schemas.py           # Pydantic models
│   │   ├── database.py          # SQLAlchemy models
│   │   └── __init__.py
│   ├── services/
│   │   ├── data_adapter.py      # AI data → Qlib format
│   │   ├── forecasting.py       # Stock predictions
│   │   ├── portfolio_analysis.py # Risk & portfolio metrics
│   │   ├── recommendation.py    # Investment signals
│   │   ├── qlib_manager.py      # Qlib initialization
│   │   └── __init__.py
│   ├── messaging/
│   │   ├── consumer.py          # RabbitMQ consumer
│   │   ├── publisher.py         # RabbitMQ publisher
│   │   └── __init__.py
│   ├── api/
│   │   ├── endpoints.py         # FastAPI endpoints
│   │   └── __init__.py
│   └── utils/
│       ├── logger.py            # Logging setup
│       ├── helpers.py           # Utilities
│       └── __init__.py
├── tests/                        # Unit & integration tests
├── qlib_data/                    # Qlib market data
├── models_storage/               # Trained ML models
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

## Environment Variables

See `.env.example` for all configuration options. Key variables:

```bash
# Service
QLIB_SERVICE_PORT=8081
DATABASE_URL=postgresql://user:pass@postgres:5432/lengkeng

# RabbitMQ
RABBITMQ_HOST=rabbitmq
QUEUE_AI_EXTRACTION_COMPLETE=ai_extraction_complete
QUEUE_QLIB_PREDICTIONS_READY=qlib_predictions_ready

# Qlib
QLIB_DEFAULT_MODEL=lightgbm
QLIB_FORECAST_HORIZONS=1,5,30
QLIB_FEATURE_SET=alpha158
```

## Installation

### Prerequisites

- Python 3.8-3.12
- PostgreSQL 13+
- RabbitMQ 3.9+

### Local Development

**Option 1: Using the run script (recommended)**

```bash
# Make script executable (first time only)
chmod +x run-dev.sh

# Run the service
./run-dev.sh
```

**Option 2: Manual setup**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run the service
python -m app.main
```

### Docker Deployment

**Option 1: Using docker-compose (recommended)**

```bash
# Start all services (Qlib, PostgreSQL, RabbitMQ)
docker-compose up -d

# View logs
docker-compose logs -f qlib-service

# Stop services
docker-compose down
```

**Option 2: Docker standalone**

```bash
# Build image
docker build -t qlib-service:latest .

# Run container
docker run -d \
  -p 8081:8081 \
  -v $(pwd)/qlib_data:/app/qlib_data \
  -v $(pwd)/models_storage:/app/models_storage \
  --env-file .env \
  --name qlib-service \
  qlib-service:latest
```

## API Endpoints

### Health & Status

- `GET /health` - Service health check
- `GET /status` - Detailed service status

### Predictions (Internal Use)

- `POST /predict/stock` - Single stock prediction
- `POST /predict/portfolio` - Portfolio analysis
- `POST /recommend` - Investment recommendations

### Admin

- `POST /admin/reload-models` - Reload ML models
- `POST /admin/update-data` - Update market data

## Message Flow

### Input: AI Extraction Complete

Queue: `ai_extraction_complete`

```json
{
  "request_id": "req_123",
  "report_id": "rpt_456",
  "extracted_data": {
    "stocks": [...],
    "portfolio": {...},
    "market_context": {...}
  }
}
```

### Output: Qlib Predictions Ready

Queue: `qlib_predictions_ready`

```json
{
  "request_id": "req_123",
  "report_id": "rpt_456",
  "predictions": {
    "stock_forecasts": [...],
    "portfolio_analysis": {...},
    "recommendations": [...],
    "market_regime": {...}
  },
  "model_metadata": {...}
}
```

## Database Tables

### predictions
Stores stock price predictions with horizons and confidence scores.

### recommendations
Stores buy/sell/hold recommendations with rationale.

### portfolio_analysis
Stores portfolio-level risk and performance metrics.

## Development Status

### ✅ Completed (Phase 1 & 2 - Partial)

- [x] Service architecture design
- [x] Data schemas definition
- [x] RabbitMQ queue design
- [x] Database schema design
- [x] Directory structure setup
- [x] Configuration files (settings.py, .env.example)
- [x] Pydantic models (schemas.py)
- [x] SQLAlchemy models (database.py)
- [x] Data adapter (AI → Qlib conversion)

### ✅ Phase 2 Completed (100%)

- [x] Stock price forecasting module
- [x] Portfolio analysis module
- [x] Recommendation engine
- [x] FastAPI endpoints (health, predict/stock, predict/portfolio, recommend)
- [x] RabbitMQ consumer/publisher
- [x] Qlib initialization & model loading
- [x] Main FastAPI application with lifecycle management
- [x] Docker support (Dockerfile, docker-compose.yml)
- [x] Development scripts (run-dev.sh)

### ⏳ Pending

- Phase 3: Backend Integration
- Phase 4: Template Enhancement
- Phase 5: Frontend Updates
- Phase 6: Docker & Infrastructure
- Phase 7: Testing
- Phase 8: Documentation
- Phase 9: Deployment

## Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run integration tests
pytest tests/integration/
```

## Documentation

- **Architecture**: `/Docs/docs/architecture/06-qlib-advisor-predictor-service.md`
- **Data Schemas**: `/Docs/docs/architecture/07-qlib-data-schemas.md`
- **RabbitMQ Integration**: `/Docs/docs/architecture/08-rabbitmq-integration.md`

## References

- [Qlib Official Documentation](https://qlib.readthedocs.io/)
- [Qlib GitHub](https://github.com/microsoft/qlib)
- [Qlib Research Paper](https://arxiv.org/abs/2009.11189)

## License

Internal project - Khengleong Finance Automation System

## Contributors

- Development Team
- AI/ML Team

## Support

For issues or questions, please contact the development team.
