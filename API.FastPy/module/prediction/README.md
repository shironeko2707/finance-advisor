# Prediction Module

## Overview

The Prediction module handles the integration of Qlib quantitative investment predictions into the KhengLeong Smart Report Generator API. It processes prediction results from the Qlib service and stores them in the database for retrieval and inclusion in generated reports.

## Architecture

```
Qlib Service → [qlib_predictions_ready] → RabbitMQ Consumer →
  Prediction Service → Database → API Endpoints → Frontend/Reports
```

## Components

### 1. Database Models (`PredictionModel.py`)

- **PredictionRequest**: Master table tracking prediction requests
- **StockPrediction**: Stock price forecasts for multiple horizons
- **PortfolioAnalysis**: Portfolio risk metrics and performance
- **Recommendation**: Investment recommendations (Buy/Sell/Hold)
- **MarketRegime**: Market trend detection

### 2. Data Transfer Objects (`PredictionDTO.py`)

Pydantic models for API request/response validation and serialization.

### 3. Repository (`prediction_repository.py`)

Database access layer with methods for CRUD operations on predictions.

### 4. Service (`prediction_service.py`)

Business logic for processing Qlib prediction messages and storing results.

### 5. Consumer (`prediction_consumer.py`)

RabbitMQ consumer that listens to `qlib_predictions_ready` queue and processes predictions.

### 6. Controller (`prediction_controller.py`)

FastAPI endpoints for retrieving predictions via REST API.

## API Endpoints

### GET /predictions/
Get all prediction requests with pagination.

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum records to return (default: 100)

**Response:**
```json
{
  "total": 10,
  "requests": [...]
}
```

### GET /predictions/request/{request_id}
Get complete prediction results by request ID.

**Response:**
```json
{
  "request": {...},
  "stock_predictions": [...],
  "portfolio_analysis": {...},
  "recommendations": [...],
  "market_regime": {...}
}
```

### GET /predictions/report/{report_id}
Get predictions for a specific report.

### GET /predictions/status/{request_id}
Get prediction request status.

**Response:**
```json
{
  "request_id": "req_123",
  "status": "success",
  "prediction_status": "success",
  "created_at": "2025-01-16T...",
  "updated_at": "2025-01-16T...",
  "processing_time_seconds": 12.5,
  "stocks_count": 5,
  "recommendations_count": 5,
  "has_portfolio_analysis": true,
  "has_market_regime": true
}
```

### GET /predictions/stocks/{ticker}
Get recent predictions for a specific stock ticker.

**Query Parameters:**
- `limit` (int): Maximum predictions to return (default: 10)

## Database Schema

### prediction_requests
- `id` (PK)
- `request_id` (unique string)
- `report_id` (FK to generated_reports)
- `status` (pending, processing, success, failed)
- `prediction_status` (success, partial_success, failed)
- `model_name`, `model_version`, `feature_set`
- `processing_time_seconds`
- `error_message`
- Timestamps

### stock_predictions
- `id` (PK)
- `prediction_request_id` (FK)
- `ticker`, `current_price`, `trend`
- `volatility_forecast`
- `forecasts` (JSON array of forecast objects)

### portfolio_analysis
- `id` (PK)
- `prediction_request_id` (FK, unique)
- Risk metrics (sharpe_ratio, max_drawdown, volatility, VaR, beta, alpha)
- Performance forecasts (1d, 5d, 30d expected returns)
- `diversification_score`, `risk_level`

### recommendations
- `id` (PK)
- `prediction_request_id` (FK)
- `ticker`, `action`, `strength`, `confidence`
- `target_price`, `stop_loss`, `rationale`
- Factor scores (technical, fundamental, sentiment)

### market_regimes
- `id` (PK)
- `prediction_request_id` (FK, unique)
- `regime`, `confidence`, `description`

## Message Flow

### Input Message (from Qlib Service)

Queue: `qlib_predictions_ready`

```json
{
  "request_id": "req_123",
  "report_id": "rpt_456",
  "timestamp": "2025-01-16T...",
  "prediction_status": "success",
  "predictions": {
    "stock_forecasts": [...],
    "portfolio_analysis": {...},
    "recommendations": [...],
    "market_regime": {...}
  },
  "model_metadata": {
    "primary_model": "lightgbm",
    "model_version": "1.0.0",
    "feature_set": "alpha158",
    "processing_time_seconds": 12.5
  }
}
```

### Consumer Processing

1. Parse message from RabbitMQ
2. Create/update `PredictionRequest` record
3. Store stock forecasts
4. Store portfolio analysis (if present)
5. Store recommendations
6. Store market regime
7. Update request status
8. Acknowledge message

## Configuration

### Environment Variables

Add to `.env` file:

```bash
# Qlib Prediction Queue Configuration
QUEUE_QLIB_PREDICTIONS_READY=qlib_predictions_ready
EXCHANGE_NAME=khengleong.direct

# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_DEFAULT_USER=rabbitmq
RABBITMQ_DEFAULT_PASS=rabbitmq
RABBITMQ_VHOST=/
```

## Usage

### Starting the Consumer

The consumer is automatically started when the FastAPI application starts (via lifespan manager in `main.py`).

### Retrieving Predictions

```python
from module.prediction.prediction_service import PredictionService
from config.database import get_db

db = next(get_db())
service = PredictionService(db)

# Get results by request ID
results = service.get_prediction_results("req_123")

# Get results by report ID
results = service.get_prediction_results_by_report(456)
```

### Via API

```bash
# Get all predictions
curl http://localhost:8080/predictions/

# Get specific prediction
curl http://localhost:8080/predictions/request/req_123

# Get predictions for a report
curl http://localhost:8080/predictions/report/456

# Get status
curl http://localhost:8080/predictions/status/req_123

# Get ticker predictions
curl http://localhost:8080/predictions/stocks/AAPL
```

## Error Handling

- Invalid JSON messages are rejected without requeue
- Processing errors are logged and request status is set to "failed"
- Failed messages are not requeued (send to DLQ if configured)
- Consumer continues running even if individual message processing fails

## Integration with Reports

Predictions can be included in generated reports by:

1. Querying predictions by `report_id`
2. Formatting prediction data for Excel templates
3. Including forecasts, analysis, and recommendations in report sections

## Testing

```bash
# Run tests
pytest tests/test_prediction_module.py

# Test consumer
python -m module.prediction.prediction_consumer

# Test API endpoints
curl http://localhost:8080/docs
```

## Monitoring

- Check consumer status: Consumer logs on startup/shutdown
- Check queue status: RabbitMQ Management UI (http://localhost:15672)
- Check prediction statistics: `/predictions/` endpoint
- Check processing errors: Query `prediction_requests` table for failed statuses

## Future Enhancements

- [ ] Add prediction expiration/cleanup
- [ ] Add prediction caching
- [ ] Add webhook notifications for prediction completion
- [ ] Add batch prediction retrieval
- [ ] Add prediction comparison/historical tracking
- [ ] Add prediction accuracy metrics
