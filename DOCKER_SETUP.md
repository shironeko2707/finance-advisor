# 🐳 Docker Setup - KhengLeong Report Automation

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

---

## ✅ Prerequisites

### Required Software

1. **Docker Desktop** (recommended) or Docker Engine
   - macOS: [Download Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
   - Windows: [Download Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
   - Linux: [Install Docker Engine](https://docs.docker.com/engine/install/)

2. **Docker Compose**
   - Included with Docker Desktop
   - For Linux: Install separately if needed

### System Requirements

- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: At least 10GB free space
- **CPU**: 4 cores recommended

### Verify Installation

```bash
# Check Docker
docker --version
# Expected output: Docker version 20.x.x or higher

# Check Docker Compose
docker compose version
# Expected output: Docker Compose version v2.x.x or higher
```

---

## 🚀 Quick Start

### 1. Make Scripts Executable

```bash
chmod +x docker-start.sh docker-stop.sh
```

### 2. Start All Services

```bash
./docker-start.sh
```

This will:
- ✅ Build all Docker images
- ✅ Start all containers
- ✅ Initialize databases
- ✅ Setup RabbitMQ queues
- ✅ Check service health

**⏱ First run may take 5-10 minutes to build images.**

### 3. Access Services

After startup completes, access:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend UI** | http://localhost:3000 | admin / admin123 |
| **Backend API** | http://localhost:8000/docs | - |
| **Qlib Service** | http://localhost:8386/docs | - |
| **RabbitMQ Management** | http://localhost:15672 | rabbitmq / rabbitmq |

### 4. Stop All Services

```bash
# Normal stop (preserves data)
./docker-stop.sh

# Stop and remove volumes (deletes all data)
./docker-stop.sh --volumes

# Full cleanup (removes images and volumes)
./docker-stop.sh --full-clean
```

---

## 🏗️ Architecture

### Service Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network: khengleong-network         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐     ┌──────────────┐     ┌─────────────┐ │
│  │  ui-frontend │────►│ api-backend  │────►│  ai-api     │ │
│  │  Port 3000   │     │  Port 8000   │     │  (consumer) │ │
│  └──────────────┘     └──────┬───────┘     └──────┬──────┘ │
│                               │                     │         │
│                               └──────►┌──────────┐◄┘         │
│                                       │ RabbitMQ │           │
│                                       │ Port 5672│           │
│                                       └────┬─────┘           │
│                                            │                  │
│                                            ▼                  │
│                                   ┌─────────────────┐        │
│                                   │  qlib-service   │        │
│                                   │  Port 8386      │        │
│                                   └─────────────────┘        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Containers

| Container | Image | Port(s) | Purpose |
|-----------|-------|---------|---------|
| `kl-ui-frontend` | Built from UI.ReactJS | 3000 | React web interface |
| `kl-api-backend` | Built from API.FastPy | 8000→8080 | Main REST API |
| `kl-qlib-service` | Built from qlib_service | 8386 | Financial analysis |
| `kl-ai-api` | Built from ai_api | - | Document processing |
| `kl-rabbitmq` | rabbitmq:3.12-management | 5672, 15672 | Message broker |

### Volumes

| Volume | Purpose | Location |
|--------|---------|----------|
| `kl-rabbitmq-data` | RabbitMQ persistence | Docker managed |
| `./API.FastPy/storage` | Backend file storage | Host bind mount |
| `./qlib_service/storage` | Qlib data storage | Host bind mount |

---

## ⚙️ Configuration

### Environment Variables

#### Backend API (API.FastPy)

Edit in `docker-compose.yml` under `api-backend` service:

```yaml
environment:
  IS_PRODUCTION: "false"           # Development mode
  DATABASE_URL: "sqlite:///..."    # Database connection
  JWT_SECRET_KEY: "your-secret"    # Change in production!
  CORS_ORIGINS: "*"                # Allowed origins
```

#### Qlib Service

Edit in `docker-compose.yml` under `qlib-service`:

```yaml
environment:
  QLIB_REGION: us                  # Market region
  ENABLE_FORECASTING: "true"       # Enable forecasting
  QLIB_MAX_WORKERS: 4              # Parallel workers
```

#### AI API

Create or edit `ai_api/.env`:

```bash
# Azure credentials (optional)
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint

# RabbitMQ (uses Docker network)
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
```

### Database Configuration

By default, SQLite is used for development:
- Backend: `API.FastPy/storage/lengkeng.db`
- Qlib: `qlib_service/storage/qlib.db`

**For production**, update `DATABASE_URL` to use PostgreSQL:

```yaml
environment:
  DATABASE_URL: "postgresql://user:pass@host:5432/dbname"
```

---

## 📖 Usage

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-backend
docker-compose logs -f qlib-service
docker-compose logs -f ai-api
docker-compose logs -f ui-frontend
```

### Restart a Service

```bash
# Restart specific service
docker-compose restart api-backend

# Rebuild and restart
docker-compose up -d --build api-backend
```

### Access Container Shell

```bash
# Backend shell
docker exec -it kl-api-backend bash

# Qlib service shell
docker exec -it kl-qlib-service bash

# RabbitMQ shell
docker exec -it kl-rabbitmq bash
```

### Database Operations

```bash
# Access backend database
docker exec -it kl-api-backend python3 -c "
from config.database import engine, SessionLocal
from module.user_mgmt.UserModel import User
db = SessionLocal()
users = db.query(User).all()
for u in users:
    print(f'{u.username}: {u.email}')
"

# Backup database
docker cp kl-api-backend:/app/storage/lengkeng.db ./backup_lengkeng.db
```

### Create Admin User

If admin doesn't exist:

```bash
docker exec -it kl-api-backend python3 -c "
import os
os.environ['IS_PRODUCTION'] = 'false'
from config.database import SessionLocal
from module.user_mgmt.UserModel import User, UserRole, UserStatus
from module.user_auth.provider.security import get_password_hash

db = SessionLocal()
admin = User(
    username='admin',
    password=get_password_hash('admin123'),
    email='admin@khengleong.sg',
    role=UserRole.ADMIN,
    status=UserStatus.ACTIVE
)
db.add(admin)
db.commit()
print('Admin created!')
"
```

### Check Service Health

```bash
# Backend health
curl http://localhost:8000/

# Qlib health
curl http://localhost:8386/health

# RabbitMQ health
curl http://localhost:15672/api/healthchecks/node
```

---

## 🔧 Troubleshooting

### Issue: Containers Won't Start

**Check logs:**
```bash
docker-compose logs
```

**Common causes:**
- Port already in use
- Insufficient memory
- Docker daemon not running

**Solution:**
```bash
# Stop other services using ports
lsof -ti:3000,8000,8386,5672 | xargs kill -9

# Restart Docker Desktop
# Or restart docker service on Linux
sudo systemctl restart docker
```

### Issue: "Cannot connect to the Docker daemon"

**Solution:**
```bash
# macOS/Windows: Start Docker Desktop

# Linux: Start Docker service
sudo systemctl start docker
```

### Issue: Port Already in Use

```bash
# Find process using port
lsof -ti:8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8080"  # Change 8000 to 8001
```

### Issue: Out of Disk Space

```bash
# Remove unused containers, images, volumes
docker system prune -a --volumes

# Remove only unused images
docker image prune -a
```

### Issue: Services Can't Communicate

**Check network:**
```bash
docker network ls
docker network inspect khengleong-network
```

**Recreate network:**
```bash
docker-compose down
docker network rm khengleong-network
docker-compose up -d
```

### Issue: Database Not Initialized

**Reset database:**
```bash
# Stop services
./docker-stop.sh

# Remove database files
rm -rf API.FastPy/storage/*.db
rm -rf qlib_service/storage/*.db

# Restart
./docker-start.sh
```

### Issue: RabbitMQ Queues Not Created

**Check RabbitMQ:**
```bash
# Access management UI
open http://localhost:15672

# Or check via command
docker exec kl-rabbitmq rabbitmqctl list_queues
```

**Manually create queue:**
```bash
docker exec kl-rabbitmq rabbitmqadmin declare queue name=ai_extraction_complete durable=true
```

### Issue: Slow Performance

**Increase resources in Docker Desktop:**
- Settings → Resources → Advanced
- Increase CPUs: 4+
- Increase Memory: 8GB+

**Or use production mode:**
```yaml
environment:
  RELOAD: "false"  # Disable auto-reload
```

### Issue: Can't Access Frontend

**Check if running:**
```bash
docker ps | grep ui-frontend
```

**Check logs:**
```bash
docker-compose logs ui-frontend
```

**Rebuild:**
```bash
docker-compose up -d --build ui-frontend
```

---

## 🔍 Debug Mode

### Enable Debug Logging

Edit `docker-compose.yml`:

```yaml
# For backend
environment:
  APP_MODE: development
  LOG_LEVEL: DEBUG

# For qlib
environment:
  DEBUG: "true"
  LOG_LEVEL: DEBUG
```

### Monitor Resource Usage

```bash
# Real-time stats
docker stats

# Specific container
docker stats kl-api-backend
```

---

## 🔒 Production Deployment

### Security Checklist

- [ ] Change `JWT_SECRET_KEY` to a strong random value
- [ ] Set `IS_PRODUCTION: "true"`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure proper CORS origins
- [ ] Enable API key authentication
- [ ] Use HTTPS with reverse proxy (nginx/traefik)
- [ ] Set resource limits for containers
- [ ] Enable container restart policies
- [ ] Configure log rotation
- [ ] Set up monitoring and alerting

### Production Compose File

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api-backend:
    environment:
      IS_PRODUCTION: "true"
      DATABASE_URL: "postgresql://..."
      JWT_SECRET_KEY: "${JWT_SECRET_KEY}"
      CORS_ORIGINS: "https://yourdomain.com"
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    restart: always
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [RabbitMQ Docker Guide](https://www.rabbitmq.com/download.html)

---

## 🆘 Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Review this troubleshooting guide
3. Check container status: `docker ps -a`
4. Verify network: `docker network inspect khengleong-network`
5. Try a fresh start: `./docker-stop.sh --full-clean && ./docker-start.sh`

---

**Last Updated**: 2024-01-11
