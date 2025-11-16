# Khengleong Finance Advisor - Complete Setup Guide

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running the Services](#running-the-services)
7. [Testing the Complete Flow](#testing-the-complete-flow)
8. [API Usage Examples](#api-usage-examples)
9. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
10. [Production Deployment](#production-deployment)

---

## Overview

The Khengleong Finance Advisor is an AI-powered financial report automation platform with integrated quantitative investment analysis using Microsoft Qlib. The system consists of 4 microservices working together to generate intelligent financial reports.

### Key Features

- **AI Data Extraction**: Automatically extract data from PDFs and Excel files using Azure AI
- **Quantitative Analysis**: Stock price forecasting, portfolio analysis, and investment recommendations using Qlib
- **Report Generation**: Generate standardized Excel reports from 40+ templates
- **Real-time Processing**: Async message processing with RabbitMQ
- **Prediction Enhancement**: Automatically enhance reports with AI predictions

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Khengleong Finance Advisor                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  UI.ReactJS  │────▶│ API.FastPy   │────▶│  ai_api      │
│  (Port 8800) │     │ (Port 8080)  │     │ (Port 8000)  │
└──────────────┘     └──────┬───────┘     └──────┬───────┘
                            │                     │
                            │                     │
                            ▼                     ▼
                     ┌──────────────┐      ┌──────────────┐
                     │ qlib_service │      │  RabbitMQ    │
                     │ (Port 8081)  │◀─────│  (Port 5672) │
                     └──────────────┘      └──────────────┘
                            │                     │
                            ▼                     ▼
                     ┌──────────────────────────────┐
                     │      PostgreSQL DB           │
                     │      (Port 5432)             │
                     └──────────────────────────────┘
```

### Services Overview

| Service | Port | Purpose |
|---------|------|---------|
| **UI.ReactJS** | 8800 | Frontend web interface |
| **API.FastPy** | 8080 | Main backend API |
| **ai_api** | 8000 | AI extraction service |
| **qlib_service** | 8081 | Qlib prediction service |
| **RabbitMQ** | 5672, 15672 | Message queue |
| **PostgreSQL** | 5432 | Database |

### Data Flow

```
1. File Upload
   User → UI → API → Storage → RabbitMQ

2. AI Extraction
   RabbitMQ → ai_api → Azure AI → Extract Data → RabbitMQ

3. Qlib Prediction
   RabbitMQ → qlib_service → Qlib Analysis → Database → RabbitMQ

4. Report Generation
   API → Template + Data → Excel Report → Storage

5. Report Enhancement
   API → Prediction Data → Enhanced Excel → User Download
```

---

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **RAM**: Minimum 8GB, Recommended 16GB
- **Disk**: 20GB free space
- **CPU**: 4+ cores recommended

### Software Dependencies

#### Required

- **Python**: 3.8 - 3.11 (Qlib requires <3.12)
- **Node.js**: 18+ and npm
- **Docker**: 20.10+ and Docker Compose 2.0+
- **Git**: 2.30+

#### Optional (for local development without Docker)

- **PostgreSQL**: 13+
- **RabbitMQ**: 3.9+

### Cloud Services (for AI features)

- **Azure OpenAI**: GPT-4 access
- **Azure AI Document Intelligence**: For OCR and data extraction

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/shironeko2707/finance-advisor.git
cd finance-advisor
```

### 2. Backend Setup (API.FastPy)

#### 2.1. Create Virtual Environment

```bash
cd API.FastPy
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2.2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2.3. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and configure:

```bash
# Database (for development, use SQLite; for production, use PostgreSQL)
IS_PRODUCTION=false
DATABASE_URL=sqlite:///./storage/lengkeng.db

# For production:
# IS_PRODUCTION=true
# DATABASE_URL=postgresql://lengkeng_user:lengkeng_password@localhost:5432/lengkeng

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_DEFAULT_USER=rabbitmq
RABBITMQ_DEFAULT_PASS=rabbitmq
RABBITMQ_VHOST=/

# Qlib Prediction Queue
QUEUE_QLIB_PREDICTIONS_READY=qlib_predictions_ready
EXCHANGE_NAME=khengleong.direct

# Security
JWT_SECRET_KEY=your_very_secret_key_change_this_in_production

# CORS (for development)
ALLOW_CORS_LOCAL=true
CORS_ORIGINS=http://localhost:8800,http://localhost:3000

# Azure OpenAI (required for AI features)
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
OPENAI_API_VERSION=2024-12-01-preview
AZURE_LLM_DEPLOYMENT=gpt-4.1
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# Email (optional - for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

#### 2.4. Initialize Database

```bash
# Create storage directories
mkdir -p storage/{uploads,templates,generated,exports,logs}

# Run migrations (if using PostgreSQL)
alembic upgrade head

# Or let the app create tables automatically (CODE FIRST approach)
# Tables will be created on first run
```

### 3. Qlib Service Setup

#### 3.1. Navigate to Qlib Service

```bash
cd ../qlib_service
```

#### 3.2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3.3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3.4. Create Environment File

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# Service Configuration
QLIB_SERVICE_HOST=0.0.0.0
QLIB_SERVICE_PORT=8081
SERVICE_NAME=qlib-advisor-predictor
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://lengkeng_user:lengkeng_password@localhost:5432/lengkeng

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_DEFAULT_USER=rabbitmq
RABBITMQ_DEFAULT_PASS=rabbitmq
RABBITMQ_VHOST=/

# Queue Names
QUEUE_AI_EXTRACTION_COMPLETE=ai_extraction_complete
QUEUE_QLIB_PREDICTIONS_READY=qlib_predictions_ready
QUEUE_DLQ=qlib_predictions_dlq
EXCHANGE_NAME=khengleong.direct

# Qlib Configuration
QLIB_DEFAULT_MODEL=lightgbm
QLIB_FORECAST_HORIZONS=1,5,30
QLIB_FEATURE_SET=alpha158

# Feature Flags
ENABLE_FORECASTING=true
ENABLE_PORTFOLIO_ANALYSIS=true
ENABLE_RECOMMENDATIONS=true

# Development
DEBUG=false
RELOAD=false
```

### 4. Frontend Setup (UI.ReactJS)

#### 4.1. Navigate to Frontend

```bash
cd ../UI.ReactJS
```

#### 4.2. Install Dependencies

```bash
npm install
```

#### 4.3. Create Environment File

```bash
cp .env.example .env
```

Edit `.env`:

```bash
VITE_API_URL=http://localhost:8080
VITE_APP_NAME=Khengleong Finance Advisor
```

### 5. Infrastructure Setup (PostgreSQL & RabbitMQ)

#### Option 1: Using Docker (Recommended)

Create `docker-compose.infrastructure.yml` in the root directory:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:17
    container_name: finance-advisor-postgres
    environment:
      POSTGRES_USER: lengkeng_user
      POSTGRES_PASSWORD: lengkeng_password
      POSTGRES_DB: lengkeng
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  rabbitmq:
    image: rabbitmq:4.1-management
    container_name: finance-advisor-rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: rabbitmq
      RABBITMQ_DEFAULT_PASS: rabbitmq
    ports:
      - "5672:5672"   # AMQP
      - "15672:15672" # Management UI
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    restart: unless-stopped

volumes:
  postgres_data:
  rabbitmq_data:
```

Start infrastructure:

```bash
docker-compose -f docker-compose.infrastructure.yml up -d
```

#### Option 2: Local Installation

**PostgreSQL:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql@17
brew services start postgresql@17

# Create database and user
sudo -u postgres psql
CREATE DATABASE lengkeng;
CREATE USER lengkeng_user WITH PASSWORD 'lengkeng_password';
GRANT ALL PRIVILEGES ON DATABASE lengkeng TO lengkeng_user;
\q
```

**RabbitMQ:**

```bash
# Ubuntu/Debian
sudo apt-get install rabbitmq-server
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server

# macOS
brew install rabbitmq
brew services start rabbitmq

# Enable management plugin
sudo rabbitmq-plugins enable rabbitmq_management

# Create user
sudo rabbitmqctl add_user rabbitmq rabbitmq
sudo rabbitmqctl set_permissions -p / rabbitmq ".*" ".*" ".*"
sudo rabbitmqctl set_user_tags rabbitmq administrator
```

---

## Configuration

### 1. RabbitMQ Queue Setup

The queues and exchanges are created automatically by the services, but you can verify:

**Access RabbitMQ Management UI:**
```
http://localhost:15672
Username: rabbitmq
Password: rabbitmq
```

**Expected Queues:**
- `file_upload_notifications` - File upload events
- `ai_extraction_complete` - AI extraction results
- `qlib_predictions_ready` - Qlib predictions
- `qlib_predictions_dlq` - Dead letter queue

**Expected Exchange:**
- `khengleong.direct` - Main exchange (type: direct)

### 2. Database Initialization

The application uses a CODE FIRST approach - tables are created automatically on first run.

**Verify tables were created:**

```bash
psql -U lengkeng_user -d lengkeng -h localhost
\dt
```

**Expected tables:**
- `users` - User management
- `uploaded_files` - File uploads
- `templates` - Report templates
- `generated_reports` - Generated reports
- `report_input_files` - Report relationships
- `prediction_requests` - Prediction tracking
- `stock_predictions` - Stock forecasts
- `portfolio_analysis` - Portfolio metrics
- `recommendations` - Investment signals
- `market_regimes` - Market analysis

### 3. Create Initial Admin User

```bash
cd API.FastPy
source venv/bin/activate

# Create admin user via Python shell
python
```

```python
from module.user_mgmt.user_service import user_service
from config.database import SessionLocal

db = SessionLocal()

admin_data = {
    "username": "admin",
    "email": "admin@khengleong.sg",
    "password": "Admin@123456",  # Change this!
    "first_name": "System",
    "last_name": "Administrator",
    "role": "admin",
    "status": "active"
}

user = user_service.create_user(db, admin_data)
print(f"Admin user created: {user.username}")
db.close()
exit()
```

---

## Running the Services

### Development Mode (Recommended for Testing)

#### 1. Start Infrastructure (if using Docker)

```bash
docker-compose -f docker-compose.infrastructure.yml up -d
```

Wait 10-15 seconds for services to initialize.

#### 2. Start Backend API

```bash
cd API.FastPy
source venv/bin/activate
python main.py
```

**Expected output:**
```
============================================================
Starting up KhengLeong Smart Report Generator API...
============================================================
✓ Qlib prediction consumer started successfully
============================================================
Application started successfully
============================================================
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

**Verify:** http://localhost:8080/ should return `{"message": "ok"}`

#### 3. Start Qlib Service

Open a new terminal:

```bash
cd qlib_service
source venv/bin/activate
chmod +x run-dev.sh
./run-dev.sh
```

**Expected output:**
```
============================================================
Starting qlib-advisor-predictor
============================================================
Step 1/4: Initializing Qlib...
✓ Qlib initialized successfully
Step 2/4: Connecting to RabbitMQ Publisher...
✓ RabbitMQ Publisher connected successfully
Step 3/4: Connecting to RabbitMQ Consumer...
✓ RabbitMQ Consumer connected successfully
Step 4/4: Starting message consumption...
✓ Message consumer started
============================================================
qlib-advisor-predictor started successfully
============================================================
```

**Verify:** http://localhost:8081/health should return health status

#### 4. Start Frontend

Open a new terminal:

```bash
cd UI.ReactJS
npm run dev
```

**Expected output:**
```
VITE v7.0.4  ready in 500 ms

➜  Local:   http://localhost:8800/
➜  Network: use --host to expose
```

**Verify:** http://localhost:8800 should show the login page

### All Services Running Checklist

✅ PostgreSQL: `psql -U lengkeng_user -d lengkeng -h localhost -c "\l"`
✅ RabbitMQ: http://localhost:15672 (Management UI)
✅ API.FastPy: http://localhost:8080/ → `{"message": "ok"}`
✅ Qlib Service: http://localhost:8081/health → health status
✅ Frontend: http://localhost:8800 → Login page

---

## Testing the Complete Flow

### 1. Login to the System

**URL:** http://localhost:8800

**Default Admin:**
- Username: `admin`
- Password: `Admin@123456` (or what you set)

### 2. Upload Files and Generate Report

#### Via UI:

1. Navigate to **Files** → **Upload Files**
2. Upload PDF or Excel files with financial data
3. Navigate to **Reports** → **Create Report**
4. Select uploaded files and a template
5. Click **Generate Report**
6. Wait for processing (AI extraction + Qlib prediction)
7. Download the report

#### Via API:

```bash
# 1. Login and get token
TOKEN=$(curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin@123456"
  }' | jq -r '.access_token')

# 2. Upload files with template
curl -X POST http://localhost:8080/files/upload-with-template \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@sample_data.pdf" \
  -F "template_file=@template.xlsx" \
  -F "report_name=Test Report"

# Response will include report_id
```

### 3. Check Prediction Status

```bash
# Get predictions for a report
curl http://localhost:8080/predictions/report/{report_id} \
  -H "Authorization: Bearer $TOKEN"

# Get formatted predictions (Excel-ready)
curl http://localhost:8080/predictions/report/{report_id}/formatted \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Enhance Report with Predictions

```bash
# Enhance Excel report with prediction sheets
curl -X POST http://localhost:8080/predictions/report/{report_id}/enhance \
  -H "Authorization: Bearer $TOKEN"
```

This adds 4 new sheets to the Excel report:
- Market Regime
- Stock Predictions
- Recommendations
- Portfolio Analysis

### 5. Download Enhanced Report

```bash
curl http://localhost:8080/reports/{report_id}/download \
  -H "Authorization: Bearer $TOKEN" \
  -o enhanced_report.xlsx
```

---

## API Usage Examples

### Authentication

```bash
# Login
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin@123456"
  }'

# Response
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

### File Upload

```bash
# Upload single file
curl -X POST http://localhost:8080/files/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf"

# Upload with template and generate report
curl -X POST http://localhost:8080/files/upload-with-template \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@data1.pdf" \
  -F "files=@data2.xlsx" \
  -F "template_file=@template.xlsx" \
  -F "report_name=Monthly Report"
```

### Predictions

```bash
# Get all predictions
curl http://localhost:8080/predictions/ \
  -H "Authorization: Bearer $TOKEN"

# Get prediction by request ID
curl http://localhost:8080/predictions/request/req_123 \
  -H "Authorization: Bearer $TOKEN"

# Get predictions for a report
curl http://localhost:8080/predictions/report/456 \
  -H "Authorization: Bearer $TOKEN"

# Get prediction status
curl http://localhost:8080/predictions/status/req_123 \
  -H "Authorization: Bearer $TOKEN"

# Get stock predictions
curl http://localhost:8080/predictions/stocks/AAPL \
  -H "Authorization: Bearer $TOKEN"
```

### Reports

```bash
# List all reports
curl http://localhost:8080/reports \
  -H "Authorization: Bearer $TOKEN"

# Get report details
curl http://localhost:8080/reports/{report_id} \
  -H "Authorization: Bearer $TOKEN"

# Download report
curl http://localhost:8080/reports/{report_id}/download \
  -H "Authorization: Bearer $TOKEN" \
  -o report.xlsx

# View report as PDF in browser
curl http://localhost:8080/reports/{report_id}/pdf \
  -H "Authorization: Bearer $TOKEN"

# Enhance report with predictions
curl -X POST http://localhost:8080/predictions/report/{report_id}/enhance \
  -H "Authorization: Bearer $TOKEN"
```

---

## Monitoring & Troubleshooting

### Service Health Checks

```bash
# Backend API
curl http://localhost:8080/

# Qlib Service
curl http://localhost:8081/health
```

### RabbitMQ Monitoring

**Management UI:** http://localhost:15672

**Check queues:**
```bash
# List all queues
sudo rabbitmqctl list_queues

# Check queue messages
sudo rabbitmqctl list_queues name messages
```

### Database Monitoring

```bash
# Connect to database
psql -U lengkeng_user -d lengkeng -h localhost

# Check prediction requests
SELECT id, request_id, status, prediction_status, created_at
FROM prediction_requests
ORDER BY created_at DESC LIMIT 10;

# Check stock predictions
SELECT COUNT(*) FROM stock_predictions;

# Check recommendations
SELECT ticker, action, confidence
FROM recommendations
ORDER BY created_at DESC LIMIT 10;
```

### Log Files

**Backend API:**
```bash
cd API.FastPy
tail -f storage/logs/app.log  # If logging to file

# Or check console output
```

**Qlib Service:**
```bash
cd qlib_service
# Check console output for logs
```

### Common Issues

#### 1. RabbitMQ Connection Failed

**Symptom:** `Failed to connect to RabbitMQ`

**Solution:**
```bash
# Check if RabbitMQ is running
sudo systemctl status rabbitmq-server

# Restart RabbitMQ
sudo systemctl restart rabbitmq-server

# Check logs
sudo journalctl -u rabbitmq-server -n 50
```

#### 2. Database Connection Failed

**Symptom:** `Failed to connect to database`

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Verify connection
psql -U lengkeng_user -d lengkeng -h localhost

# Check DATABASE_URL in .env file
```

#### 3. Prediction Consumer Not Starting

**Symptom:** `⚠ Application will continue without prediction consumer`

**Solution:**
```bash
# Check RabbitMQ is accessible
curl http://localhost:15672

# Verify queue configuration in .env
# Check RabbitMQ logs for connection errors
```

#### 4. Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.8-3.11
```

#### 5. Port Already in Use

**Symptom:** `Address already in use`

**Solution:**
```bash
# Find process using port
lsof -i :8080  # Or 8081, 5432, etc.

# Kill process
kill -9 <PID>

# Or change port in .env file
```

---

## Production Deployment

### Using Docker Compose (Recommended)

#### 1. Full Stack Docker Compose

Create `docker-compose.yml` in the root:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:17
    container_name: finance-postgres
    environment:
      POSTGRES_USER: lengkeng_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: lengkeng
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - finance-network
    restart: unless-stopped

  # RabbitMQ
  rabbitmq:
    image: rabbitmq:4.1-management
    container_name: finance-rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: rabbitmq
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
    ports:
      - "15672:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - finance-network
    restart: unless-stopped

  # Backend API
  api:
    build:
      context: ./API.FastPy
      dockerfile: Dockerfile
    container_name: finance-api
    ports:
      - "8080:8080"
    environment:
      - IS_PRODUCTION=true
      - DATABASE_URL=postgresql://lengkeng_user:${DB_PASSWORD}@postgres:5432/lengkeng
      - RABBITMQ_HOST=rabbitmq
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_KEY}
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
    volumes:
      - api_storage:/app/storage
    depends_on:
      - postgres
      - rabbitmq
    networks:
      - finance-network
    restart: unless-stopped

  # Qlib Service
  qlib:
    build:
      context: ./qlib_service
      dockerfile: Dockerfile
    container_name: finance-qlib
    ports:
      - "8081:8081"
    environment:
      - DATABASE_URL=postgresql://lengkeng_user:${DB_PASSWORD}@postgres:5432/lengkeng
      - RABBITMQ_HOST=rabbitmq
    volumes:
      - qlib_data:/app/qlib_data
      - models_storage:/app/models_storage
    depends_on:
      - postgres
      - rabbitmq
    networks:
      - finance-network
    restart: unless-stopped

  # Frontend
  frontend:
    build:
      context: ./UI.ReactJS
      dockerfile: Dockerfile
    container_name: finance-frontend
    ports:
      - "8800:80"
    environment:
      - VITE_API_URL=http://api:8080
    depends_on:
      - api
    networks:
      - finance-network
    restart: unless-stopped

volumes:
  postgres_data:
  rabbitmq_data:
  api_storage:
  qlib_data:
  models_storage:

networks:
  finance-network:
    driver: bridge
```

#### 2. Create .env for Docker

```bash
# Database
DB_PASSWORD=secure_password_here

# RabbitMQ
RABBITMQ_PASSWORD=secure_password_here

# Azure OpenAI
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
```

#### 3. Deploy

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Production Best Practices

1. **Security:**
   - Change all default passwords
   - Use strong JWT_SECRET_KEY
   - Enable HTTPS with SSL/TLS certificates
   - Configure firewall rules
   - Disable debug mode

2. **Performance:**
   - Use PostgreSQL instead of SQLite
   - Configure connection pooling
   - Enable caching where appropriate
   - Use CDN for frontend assets

3. **Reliability:**
   - Set up automated backups for database
   - Configure monitoring and alerting
   - Implement log aggregation
   - Use load balancers for high availability

4. **Monitoring:**
   - Prometheus + Grafana for metrics
   - ELK stack for log analysis
   - Health check endpoints
   - Alert notifications

---

## Quick Start Summary

**Fastest way to get started (Development):**

```bash
# 1. Clone and setup
git clone https://github.com/shironeko2707/finance-advisor.git
cd finance-advisor

# 2. Start infrastructure
docker-compose -f docker-compose.infrastructure.yml up -d

# 3. Setup and start backend
cd API.FastPy
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python main.py &

# 4. Setup and start Qlib service
cd ../qlib_service
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
chmod +x run-dev.sh
./run-dev.sh &

# 5. Setup and start frontend
cd ../UI.ReactJS
npm install
cp .env.example .env
npm run dev

# 6. Access the application
# Frontend: http://localhost:8800
# API: http://localhost:8080
# RabbitMQ: http://localhost:15672
```

**Production (Docker):**

```bash
# Create .env with production settings
nano .env

# Deploy full stack
docker-compose up -d

# Access
# Frontend: http://your-domain:8800
# API: http://your-domain:8080
```

---

## Support & Documentation

### API Documentation

- **OpenAPI/Swagger**: http://localhost:8080/docs (development mode)
- **ReDoc**: http://localhost:8080/redoc

### Module Documentation

- **Prediction Module**: `API.FastPy/module/prediction/README.md`
- **Qlib Service**: `qlib_service/README.md`
- **Full Documentation**: `Docs/` directory

### Architecture Diagrams

- System Architecture: `Docs/docs/architecture/01-system-architecture.md`
- Database Design: `Docs/docs/architecture/02-database-design.md`
- Qlib Service: `Docs/docs/architecture/06-qlib-advisor-predictor-service.md`

### Support

- **Issues**: https://github.com/shironeko2707/finance-advisor/issues
- **Email**: dev@khengleong.sg

---

## Appendix

### A. Environment Variables Reference

See individual service `.env.example` files for complete reference.

### B. Database Schema

See `Docs/docs/architecture/02-database-design.md`

### C. API Endpoints

See Swagger documentation at http://localhost:8080/docs

### D. Message Queue Structure

See `Docs/docs/architecture/08-rabbitmq-integration.md`

---

**Last Updated:** 2025-01-16
**Version:** 1.0.0
**Status:** Production Ready ✅
