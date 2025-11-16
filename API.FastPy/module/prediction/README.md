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

### Report Enhancement Features

The prediction module includes utilities to automatically enhance generated Excel reports with prediction data:

#### Components:

1. **PredictionFormatter** (`prediction_formatter.py`):
   - Formats prediction data for Excel tables
   - Provides summary and detailed views
   - Handles stock forecasts, portfolio analysis, recommendations, and market regime

2. **PredictionReportService** (`prediction_report_service.py`):
   - Enhances existing Excel reports with prediction sheets
   - Adds formatted tables with color coding
   - Creates separate worksheets for each prediction type

### API Endpoints for Report Integration

#### Get Formatted Predictions for Report

```bash
GET /predictions/report/{report_id}/formatted
```

Returns formatted prediction data ready for Excel/PDF inclusion:

```json
{
  "summary": {
    "metadata": {
      "request_id": "req_123",
      "model_name": "lightgbm",
      "processing_time": "12.50s",
      "status": "success"
    },
    "stock_count": 5,
    "has_portfolio_analysis": true,
    "recommendations_count": 5
  },
  "market_regime": {
    "Market Regime": "Trending Up",
    "Confidence": "85.5%",
    "Description": "..."
  },
  "stock_predictions": [...],
  "portfolio_analysis": {...},
  "recommendations": [...]
}
```

#### Enhance Report with Predictions

```bash
POST /predictions/report/{report_id}/enhance
```

Automatically adds prediction sheets to an existing Excel report:
- **Market Regime**: Overview of current market conditions
- **Stock Predictions**: Multi-horizon price forecasts for all stocks
- **Recommendations**: Buy/Sell/Hold signals with rationale
- **Portfolio Analysis**: Risk metrics and performance forecasts

**Response:**
```json
{
  "status": "processing",
  "message": "Report enhancement started for report 123",
  "report_id": 123,
  "prediction_summary": {...}
}
```

### Usage Examples

#### Programmatic Enhancement

```python
from module.prediction.prediction_report_service import PredictionReportService
from config.database import get_db

db = next(get_db())
service = PredictionReportService(db)

# Enhance a report
success, message = service.enhance_excel_report_with_predictions(
    report_file_path="/path/to/report.xlsx",
    report_id=123
)

if success:
    print(f"Report enhanced: {message}")
else:
    print(f"Enhancement failed: {message}")
```

#### Getting Formatted Data

```python
# Get formatted prediction data
prediction_data = service.get_prediction_data_for_report(report_id=123)

if prediction_data:
    # Access formatted sections
    stocks = prediction_data["stock_predictions"]
    portfolio = prediction_data["portfolio_analysis"]
    recommendations = prediction_data["recommendations"]
```

#### Via API

```bash
# Get formatted predictions for a report
curl http://localhost:8080/predictions/report/123/formatted

# Enhance report with predictions (background task)
curl -X POST http://localhost:8080/predictions/report/123/enhance
```

### Excel Report Structure

After enhancement, the Excel report will contain additional sheets:

1. **Market Regime** - Current market trend analysis
2. **Stock Predictions** - Detailed forecasts with:
   - Current prices and trends
   - Multi-horizon predictions (1d, 5d, 30d)
   - Confidence intervals
   - Volatility forecasts

3. **Recommendations** - Investment signals with:
   - Buy/Sell/Hold actions (color-coded)
   - Confidence scores
   - Target prices and stop-loss levels
   - Multi-factor analysis scores
   - Detailed rationale

4. **Portfolio Analysis** - Risk and performance metrics:
   - Sharpe ratio, max drawdown, VaR
   - Beta, alpha, volatility
   - Expected returns (1d, 5d, 30d)
   - Diversification score
   - Risk level classification

### Color Coding

- **Buy** recommendations: Light green background
- **Sell** recommendations: Light red background
- **Hold** recommendations: Light yellow background
- **Positive returns**: Green background
- **Negative returns**: Red background

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
