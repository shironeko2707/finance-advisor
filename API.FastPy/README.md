# Khengleong API

A comprehensive FastAPI-based system for managing users, templates, file uploads, and AI-generated content for smart report generation.

## Features

- **🔐 JWT Authentication**: Secure login with 8-hour token expiration
- **👑 Role-Based Access Control**: Admin role required for management operations
- **� User Management**: Complete CRUD operations for user accounts
- **📋 Template Management**: Create and manage report templates
- **📁 File Upload System**: Handle various file formats for processing
- **🚀 RabbitMQ Integration**: Message queue for file upload notifications and processing workflows
- **🤖 AI Integration**: Generate reports and content using AI
- **🗃️ Multi-Database Support**: PostgreSQL for production, SQLite for development
- **🔍 Search & Filter**: Advanced search functionality across entities
- **✅ Data Validation**: Comprehensive validation and error handling
- **📖 API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **🐳 Docker Support**: Full containerization with docker-compose
- **📁 Stateful Storage**: Persistent storage for database, uploads, and generated files

## Quick Start

### Development Setup

#### Windows
```powershell
# Run with virtual environment
.\run_dev.ps1
```

#### Linux/macOS
```bash
# Make script executable and run
chmod +x run_dev.sh
./run_dev.sh
```

### Production Setup with Docker

#### Windows
```powershell
# Run with Docker
.\run_docker.ps1
```

#### Linux/macOS
```bash
# Make script executable and run
chmod +x run_docker.sh
./run_docker.sh
```

## Manual Installation

### Prerequisites
- Python 3.8+
- Docker (for containerized deployment)

### Cross-Platform Installation

The application supports both Windows and Linux/macOS environments with platform-specific dependencies.

#### Windows Installation
```powershell
pip install -r requirements.txt
pip install -r requirements-windows.txt
```

#### Linux/macOS Installation
```bash
# Install system dependencies first
# Ubuntu/Debian:
sudo apt-get update && sudo apt-get install -y libmagic1

# RHEL/CentOS:
sudo yum install -y file-libs

# Fedora:
sudo dnf install -y file-libs

# macOS:
brew install libmagic

# Then install Python dependencies
pip install -r requirements.txt
pip install -r requirements-linux.txt
```

### Development Setup

1. Clone the repository
2. Install dependencies using the appropriate method above for your platform

3. Create the initial admin user:
   ```bash
   python scripts/create_admin.py
   ```
   Default admin credentials: `admin` / `admin123`

4. Set up database (optional - uses SQLite by default):
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/lengkeng_db"
   ```

5. Run the application:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

The API will be available at `http://localhost:8000`

## Docker Deployment

### Development Environment (with CORS enabled)
```bash
# Using development compose file
docker compose up --build -d
```

### Production Environment (with CORS disabled)
```bash
# Using production compose file with PostgreSQL
docker compose -f docker-compose.prod.yml up --build -d
```

### Using Plain Docker
```bash
# Build image
docker build -t lengkeng-api .

# Run container with development settings: CORS enabled, mount source and storage
docker run -d --name lengkeng-api -p 8000:8000 \
  -e ENABLE_CORS=true \
  -e CORS_ORIGINS="http://localhost:3000,http://localhost:3001" \
  -v ./storage:/app/storage lengkeng-api

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## Database Configuration

### Development (SQLite)
Default configuration uses SQLite database stored in `storage/lengkeng.db`

### Production (PostgreSQL)
Set the `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="postgresql://username:password@host:port/database_name"
```
## Environment Variables

- `DATABASE_URL`: Database connection string (default: `sqlite:///./storage/lengkeng.db`)
- `UPLOAD_DIR`: Directory for uploaded files (default: `storage/uploads`)
- `TEMPLATE_DIR`: Directory for template files (default: `storage/templates`)
- `GENERATED_DIR`: Directory for generated content (default: `storage/generated`)
- `EXPORT_DIR`: Directory for exported reports (default: `storage/exports`)
- `LOG_DIR`: Directory for application logs (default: `storage/logs`)
- `JWT_SECRET_KEY`: Secret key for JWT token encryption
- `AI_API_KEY`: API key for AI service integration

### CORS Configuration
- `ALLOW_CORS_LOCAL`: Enable/disable CORS middleware (default: `false`)
- `CORS_ORIGINS`: Allowed origins, comma-separated (default: `*`)
- `CORS_CREDENTIALS`: Allow credentials (default: `false`)
- `CORS_METHODS`: Allowed HTTP methods, comma-separated (default: `*`)
- `CORS_HEADERS`: Allowed headers, comma-separated (default: `*`)

**Note**: In production with API Gateway, set `ALLOW_CORS_LOCAL=false` or remove this as CORS headers should be handled by the gateway.

## RabbitMQ Configuration

The application integrates with RabbitMQ for file upload notifications and processing workflows. Configure RabbitMQ connection using environment variables:

```bash
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=rabbitmq
RABBITMQ_PASSWORD=rabbitmq
RABBITMQ_VHOST=/
```

### RabbitMQ Setup

#### Using Docker:
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=rabbitmq \
  -e RABBITMQ_DEFAULT_PASS=rabbitmq \
  rabbitmq:3-management
```

#### Access Management UI:
http://localhost:15672 (rabbitmq/rabbitmq)

For detailed RabbitMQ integration documentation, see [docs/RABBITMQ_INTEGRATION.md](docs/RABBITMQ_INTEGRATION.md)

## Available Scripts

- `run_dev.ps1` / `run_dev.sh`: Development server with virtual environment
- `run_docker.ps1` / `run_docker.sh`: Production deployment with Docker
- `scripts/create_admin.py`: Create initial admin user
- `python run_tests.py`: Run test suite