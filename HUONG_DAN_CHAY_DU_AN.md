# 📚 HƯỚNG DẪN CHẠY DỰ ÁN TỪ A-Z

## KhengLeong Report Automation - Complete Guide

---

## 📋 Mục Lục

1. [Tổng Quan Dự Án](#1-tổng-quan-dự-án)
2. [Yêu Cầu Hệ Thống](#2-yêu-cầu-hệ-thống)
3. [Cấu Trúc Dự Án](#3-cấu-trúc-dự-án)
4. [Phương Thức Chạy](#4-phương-thức-chạy)
5. [Chạy với Docker (Khuyên Dùng)](#5-chạy-với-docker-khuyên-dùng)
6. [Chạy Local Development](#6-chạy-local-development)
7. [Chạy Documentation (MkDocs)](#7-chạy-documentation-mkdocs)
8. [Cấu Hình Environment](#8-cấu-hình-environment)
9. [Kiểm Tra Hệ Thống](#9-kiểm-tra-hệ-thống)
10. [Troubleshooting](#10-troubleshooting)
11. [Thông Tin Đăng Nhập](#11-thông-tin-đăng-nhập)

---

## 1. Tổng Quan Dự Án

Dự án **KhengLeong Report Automation** bao gồm 5 thành phần chính:

| Component | Mô Tả | Port | Công Nghệ |
|-----------|-------|------|-----------|
| **API.FastPy** | Backend REST API | 8000 | FastAPI, Python, SQLAlchemy |
| **UI.ReactJS** | Frontend Web App | 3000 | React 18, TypeScript, Vite, Tailwind |
| **qlib_service** | Financial Analysis Service | 8386 | FastAPI, Microsoft Qlib, LightGBM |
| **ai_api** | AI Document Processing | - | Python, RabbitMQ Consumer |
| **Docs** | Documentation Site | 8000 | MkDocs Material |

### Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network: khengleong-network        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌─────────────┐  │
│  │  UI.ReactJS  │────►│   API.FastPy │────►│   ai_api    │  │
│  │  Port 3000   │     │   Port 8000  │     │  (consumer) │  │
│  └──────────────┘     └──────┬───────┘     └──────┬──────┘  │
│                              │                     │         │
│                              └──────►┌──────────┐◄┘         │
│                                      │ RabbitMQ │            │
│                                      │ Port 5672│            │
│                                      └────┬─────┘            │
│                                           │                  │
│                                           ▼                  │
│                                  ┌─────────────────┐         │
│                                  │  qlib_service   │         │
│                                  │  Port 8386      │         │
│                                  └─────────────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Yêu Cầu Hệ Thống

### 2.1 Phần Cứng

| Đặc tả | Tối thiểu | Khuyến nghị |
|--------|-----------|-------------|
| **RAM** | 8GB | 16GB |
| **CPU** | 2 cores | 4+ cores |
| **Disk** | 10GB | 20GB+ |

### 2.2 Phần Mềm - Docker Method

- **Docker Desktop** (Bao gồm Docker Compose)
  - macOS: [Download](https://docs.docker.com/desktop/install/mac-install/)
  - Windows: [Download](https://docs.docker.com/desktop/install/windows-install/)
  - Linux: [Install Docker Engine](https://docs.docker.com/engine/install/)

### 2.3 Phần Mềm - Local Development Method

| Phần Mềm | Phiên Bản | Ghi Chú |
|----------|-----------|---------|
| **Python** | 3.9+ | Dùng cho API.FastPy, qlib_service, ai_api |
| **Node.js** | 18+ | Dùng cho UI.ReactJS |
| **npm** | 9+ | Đi kèm Node.js |
| **RabbitMQ** | 3.9+ | Message Broker |

#### Cài đặt RabbitMQ:

**macOS:**
```bash
brew install rabbitmq
brew services start rabbitmq
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install rabbitmq-server
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
```

**Linux (RHEL/CentOS):**
```bash
sudo yum install rabbitmq-server
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
```

---

## 3. Cấu Trúc Dự Án

```
report-automation-project/
├── API.FastPy/              # Backend API
│   ├── main.py              # Entry point
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           
│   ├── .env.example         # Environment template
│   ├── config/              # Configuration files
│   ├── module/              # Business logic modules
│   ├── scripts/             # Utility scripts
│   └── storage/             # Database & uploads
│
├── UI.ReactJS/              # Frontend Application
│   ├── src/                 # React source code
│   ├── package.json         
│   ├── Dockerfile           
│   ├── .env.example         
│   └── vite.config.ts       
│
├── qlib_service/            # Financial Analysis
│   ├── main.py              # Entry point
│   ├── app/                 # Application code
│   ├── requirements.txt     
│   ├── Dockerfile           
│   ├── .env.example         
│   └── qlib_data/           # Market data
│
├── ai_api/                  # AI Document Processing
│   ├── main.py              # RabbitMQ consumer entry
│   ├── api.py               # API endpoints
│   ├── auto_report/         # Report generation logic
│   └── requirements.txt     
│
├── Docs/                    # MkDocs Documentation
│   ├── docs/                # Markdown files
│   ├── mkdocs.yml           # MkDocs configuration
│   └── requirements.txt     
│
├── docker-compose.yml       # Docker orchestration
├── docker-start.sh          # Docker startup script
├── docker-stop.sh           # Docker stop script
├── start-all-services.sh    # Local startup script
├── stop-all-services.sh     # Local stop script
├── QUICK_START.md           # Quick start guide
└── DOCKER_SETUP.md          # Docker detailed guide
```

---

## 4. Phương Thức Chạy

### So Sánh 2 Phương Thức

| Feature | 🐳 Docker | 💻 Local Development |
|---------|-----------|---------------------|
| **Thời gian setup** | 5 phút | 15-20 phút |
| **Độ khó** | ⭐ Dễ | ⭐⭐⭐ Trung bình |
| **Hot Reload** | ✅ Có | ✅ Có |
| **Debug** | Khó hơn | Dễ dàng |
| **Isolation** | ✅ Hoàn toàn | ❌ Ảnh hưởng system |
| **Production Ready** | ✅ | ❌ |
| **Resource Usage** | Cao hơn | Thấp hơn |

---

## 5. Chạy với Docker (Khuyên Dùng)

### 5.1 Bước 1: Chuẩn Bị

```bash
# Di chuyển vào thư mục project
cd /path/to/report-automation-project

# Kiểm tra Docker đã cài đặt
docker --version
docker compose version
```

### 5.2 Bước 2: Khởi Động Docker Desktop

- Mở **Docker Desktop** application
- Đợi cho đến khi thấy "Docker Desktop is running" ở thanh trạng thái

### 5.3 Bước 3: Cấp Quyền Thực Thi Scripts

```bash
chmod +x docker-start.sh docker-stop.sh
```

### 5.4 Bước 4: Start Tất Cả Services

```bash
./docker-start.sh
```

> ⏱ **Lưu ý**: Lần đầu tiên chạy sẽ mất 5-10 phút để download và build images.
> 
> **Note cho Mac User (M1/M2/M3)**: Service `qlib_service` sẽ chạy dưới chế độ giả lập `linux/amd64` để tương thích với thư viện `pyqlib`. Việc này có thể làm quá trình build và chạy chậm hơn bình thường.
>
> **Note về AI API**: Đã cập nhật `docker-compose.yml` và `settings.py` để thêm các biến môi trường còn thiếu cho `ai_api` (Google Gemini keys, Azure keys). Các giá trị này đang để là placeholder, bạn cần cập nhật lại trong file `.env` nếu muốn sử dụng tính năng AI thực tế.

Script này sẽ tự động:
- ✅ Build tất cả Docker images
- ✅ Start tất cả containers
- ✅ Initialize databases
- ✅ Setup RabbitMQ queues
- ✅ Check service health

### 5.5 Bước 5: Truy Cập Services

Sau khi khởi động thành công:

| Service | URL | Thông tin |
|---------|-----|-----------|
| **Frontend UI** | http://localhost:3000 | Login: admin/admin123 |
| **Backend API** | http://localhost:8000/docs | Swagger Documentation |
| **Qlib Service** | http://localhost:8386/docs | Financial API Docs |
| **RabbitMQ Management** | http://localhost:15672 | Login: rabbitmq/rabbitmq |

### 5.6 Bước 6: Stop Services

```bash
# Stop tất cả services (giữ lại data)
./docker-stop.sh

# Stop và xóa volumes/data
./docker-stop.sh --volumes

# Full cleanup (xóa images + data)
./docker-stop.sh --full-clean
```

### 5.7 Docker Commands Hữu Ích

```bash
# Xem logs real-time của tất cả services
docker-compose logs -f

# Xem logs của service cụ thể
docker-compose logs -f api-backend
docker-compose logs -f qlib-service
docker-compose logs -f ai-api
docker-compose logs -f ui-frontend

# Restart một service cụ thể
docker-compose restart api-backend

# Rebuild và restart một service
docker-compose up -d --build api-backend

# Vào shell của container
docker exec -it kl-api-backend bash
docker exec -it kl-qlib-service bash

# Xem resource usage
docker stats
```

---

## 6. Chạy Local Development

### 6.1 Phương Thức 1: Sử Dụng Script Tự Động

```bash
# Cấp quyền thực thi
chmod +x start-all-services.sh stop-all-services.sh

# Start tất cả
./start-all-services.sh

# Stop tất cả
./stop-all-services.sh
```

### 6.2 Phương Thức 2: Khởi Động Từng Service Thủ Công

#### 🔧 Bước 1: Khởi Động RabbitMQ

**macOS:**
```bash
brew services start rabbitmq
```

**Linux:**
```bash
sudo systemctl start rabbitmq-server
```

Verify: Truy cập http://localhost:15672 (guest/guest hoặc rabbitmq/rabbitmq)

---

#### 🔧 Bước 2: Khởi Động API.FastPy (Backend)

```bash
# Terminal 1
cd API.FastPy

# Tạo virtual environment (lần đầu)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\activate      # Windows PowerShell

# Cài dependencies (lần đầu)
pip install -r requirements.txt

# macOS: Cài thêm libmagic
brew install libmagic
pip install -r requirements-linux.txt

# Windows:
pip install -r requirements-windows.txt

# Chạy server
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

✅ Backend chạy tại: http://localhost:8000
📖 API Docs: http://localhost:8000/docs

---

#### 🔧 Bước 3: Khởi Động qlib_service

```bash
# Terminal 2
cd qlib_service

# Tạo virtual environment (lần đầu)
python3 -m venv venv

# Activate
source venv/bin/activate

# Cài dependencies (lần đầu)
pip install -r requirements.txt

# Chạy server
python3 -m uvicorn main:app --host 0.0.0.0 --port 8386 --reload
```

✅ Qlib Service chạy tại: http://localhost:8386
📖 API Docs: http://localhost:8386/docs

---

#### 🔧 Bước 4: Khởi Động ai_api (AI Consumer)

```bash
# Terminal 3
cd ai_api

# Tạo virtual environment (lần đầu)
python3 -m venv venv

# Activate
source venv/bin/activate

# Cài dependencies (lần đầu)
pip install -r requirements.txt

# Chạy RabbitMQ consumer
python3 main.py
```

✅ AI API consumer đang lắng nghe RabbitMQ

---

#### 🔧 Bước 5: Khởi Động UI.ReactJS (Frontend)

```bash
# Terminal 4
cd UI.ReactJS

# Cài dependencies (lần đầu)
npm install

# Chạy development server
npm run dev
```

✅ Frontend chạy tại: http://localhost:3000

---

### 6.3 Scripts Có Sẵn Trong Mỗi Component

#### API.FastPy:
```bash
# Windows
.\run_dev.ps1      # Development mode
.\run_docker.ps1   # Docker mode

# macOS/Linux
./run_dev.sh       # Development mode
./run_docker.sh    # Docker mode
```

#### UI.ReactJS:
```bash
# Windows
.\run-dev.ps1      # Development mode
.\run-docker.ps1   # Docker mode

# macOS/Linux
./run-dev.sh       # Development mode
./run-docker.sh    # Docker mode
```

---

## 7. Chạy Documentation (MkDocs)

### 7.1 Development Server

```bash
cd Docs

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt

# Chạy development server
mkdocs serve
```

✅ Documentation chạy tại: http://localhost:8000

### 7.2 Build Static Site

```bash
cd Docs
source venv/bin/activate
mkdocs build
```

Kết quả được tạo trong thư mục `site/`

### 7.3 Sử Dụng Scripts

```bash
# Development
./Docs/serve.sh

# Build
./Docs/build.sh
```

---

## 8. Cấu Hình Environment

### 8.1 API.FastPy (.env.local)

Tạo file `API.FastPy/.env.local` từ template:

```bash
cp API.FastPy/.env.example API.FastPy/.env.local
```

**Các biến quan trọng:**

```bash
# App Mode
IS_PRODUCTION=false
APP_MODE=development

# Database (SQLite cho development)
DATABASE_URL=sqlite:///./storage/lengkeng.db

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_DEFAULT_USER=rabbitmq
RABBITMQ_DEFAULT_PASS=rabbitmq

# CORS
ALLOW_CORS_LOCAL=true
CORS_ORIGINS=*

# Security
JWT_SECRET_KEY=your_secret_key_here

# Azure OpenAI (optional)
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
```

### 8.2 qlib_service (.env.local)

```bash
cp qlib_service/.env.example qlib_service/.env.local
```

**Các biến quan trọng:**

```bash
# Service
QLIB_SERVICE_HOST=0.0.0.0
QLIB_SERVICE_PORT=8386
LOG_LEVEL=INFO
DEBUG=true

# Database
DATABASE_URL=sqlite:///./storage/qlib.db

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=rabbitmq
RABBITMQ_PASSWORD=rabbitmq

# Qlib Settings
QLIB_REGION=us
QLIB_DEFAULT_MODEL=lightgbm
ENABLE_FORECASTING=true
```

### 8.3 UI.ReactJS (.env.local)

```bash
cp UI.ReactJS/.env.example UI.ReactJS/.env.local
```

**Các biến quan trọng:**

```bash
# API URLs
VITE_API_BASE_URL=http://localhost:8000
VITE_AUTH_BASE_URL=http://localhost:8000
VITE_FILE_BASE_URL=http://localhost:8888

# Mode
VITE_MODE=development
VITE_USE_MOCK_AUTH=false
```

### 8.4 ai_api (.env)

Tạo hoặc chỉnh sửa `ai_api/.env`:

```bash
# Azure Services
DOCUMENT_INTELLIGENT_ENDPOINT=your_endpoint
DOCUMENT_INTELLIGENT_API_KEY=your_key
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_LLM_DEPLOYMENT=gpt-4

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=rabbitmq
RABBITMQ_PASSWORD=rabbitmq
```

---

## 9. Kiểm Tra Hệ Thống

### 9.1 Health Checks

```bash
# Backend API
curl http://localhost:8000/

# Qlib Service
curl http://localhost:8386/health
curl http://localhost:8386/status

# RabbitMQ
curl http://localhost:15672/api/healthchecks/node
```

### 9.2 Test Login API

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 9.3 Kiểm Tra RabbitMQ Queues

```bash
# Via Management UI
# Mở browser: http://localhost:15672
# Login: rabbitmq / rabbitmq
# Vào tab Queues để xem các queues

# Via Command Line (Docker)
docker exec kl-rabbitmq rabbitmqctl list_queues
```

### 9.4 Test Frontend

1. Mở browser: http://localhost:3000
2. Đăng nhập với: `admin` / `admin123`
3. Thử upload file và tạo report

---

## 10. Troubleshooting

### 10.1 Port Đã Được Sử Dụng

```bash
# Tìm process sử dụng port
lsof -ti:8000           # Backend
lsof -ti:3000           # Frontend
lsof -ti:8386           # Qlib
lsof -ti:5672           # RabbitMQ

# Kill process
kill -9 <PID>

# Kill tất cả ports liên quan
lsof -ti:3000,8000,8386,5672 | xargs kill -9
```

### 10.2 Không Đăng Nhập Được

**Tạo admin user thủ công:**

**Docker:**
```bash
docker exec -it kl-api-backend python3 -c "
import os
os.environ['IS_PRODUCTION']='false'
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

**Local:**
```bash
cd API.FastPy
source .venv/bin/activate
python3 scripts/create_admin.py
```

### 10.3 RabbitMQ Không Chạy

**macOS:**
```bash
brew services restart rabbitmq
```

**Linux:**
```bash
sudo systemctl restart rabbitmq-server
```

**Docker:**
```bash
docker restart kl-rabbitmq
```

### 10.4 Frontend Không Connect Backend

Kiểm tra file `UI.ReactJS/.env.local`:
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_AUTH_BASE_URL=http://localhost:8000
VITE_USE_MOCK_AUTH=false
```

### 10.5 Database Lỗi

**Reset database:**
```bash
# Local
rm -rf API.FastPy/storage/*.db
rm -rf qlib_service/storage/*.db

# Docker
./docker-stop.sh --volumes
./docker-start.sh
```

### 10.6 Docker: Out of Disk Space

```bash
# Remove unused containers, images, volumes
docker system prune -a --volumes

# Remove only unused images
docker image prune -a
```

### 10.7 Docker: Services Không Communicate

```bash
# Check network
docker network ls
docker network inspect khengleong-network

# Recreate network
docker-compose down
docker network rm khengleong-network
docker-compose up -d
```

---

## 11. Thông Tin Đăng Nhập

### Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| **Frontend/API** | admin | admin123 |
| **RabbitMQ** | rabbitmq | rabbitmq |

### Service URLs Summary

| Service | URL | Notes |
|---------|-----|-------|
| Frontend | http://localhost:3000 | Main Web UI |
| Backend API | http://localhost:8000 | REST API |
| Backend Docs | http://localhost:8000/docs | Swagger UI |
| Qlib Service | http://localhost:8386 | Financial Analysis |
| Qlib Docs | http://localhost:8386/docs | Swagger UI |
| RabbitMQ UI | http://localhost:15672 | Message Queue Management |
| MkDocs | http://localhost:8000 | Documentation (khi chạy standalone) |

---

## 📝 Ghi Chú Cuối

### Logs Location

| Method | Location |
|--------|----------|
| **Docker** | `docker-compose logs -f [service]` |
| **Local** | `./logs/` directory |

### Stop Commands

```bash
# Docker
./docker-stop.sh

# Local (sử dụng script)
./stop-all-services.sh

# Local (manual)
# Nhấn Ctrl+C trong mỗi terminal
```

### Rebuild Commands

```bash
# Docker - rebuild tất cả
docker-compose up -d --build

# Docker - rebuild service cụ thể
docker-compose up -d --build api-backend
```

---

**Chúc bạn thành công! 🚀**

---

## 12. Các Thay Đổi Đã Thực Hiện (Changelog)

Để đảm bảo hệ thống chạy mượt mà, các thay đổi sau đã được áp dụng vào codebase:

### 1. qlib_service
- **Dockerfile**:
  - Hạ version Python xuống **3.9-slim** (do `pyqlib` chưa hỗ trợ tốt Python 3.11/3.12).
  - Thêm flag `--platform=linux/amd64` để hỗ trợ chạy trên chip Apple Silicon (M1/M2/M3) qua cơ chế giả lập (do thiếu wheel ARM64 cho `pyqlib`).
- **requirements.txt**: Nới lỏng điều kiện version `pyqlib>=0.9.6`.

### 2. ai_api
- **Dockerfile**:
  - Cài đặt thêm `curl` để phục vụ Healthcheck.
  - Cập nhật Healthcheck port về **8080** (khớp với port ứng dụng chạy).
- **settings.py**: Bổ sung các trường thiếu (`google_llm_api_key_1`, `google_llm_api_key_2`, v.v.) để tránh lỗi crash khi khởi động.
- **docker-compose.yml**: Thêm các biến môi trường placeholder cho Azure và Google Gemini.

### 3. API.FastPy (Backend)
- **Dockerfile**:
  - Cài đặt thêm `curl` cho Healthcheck.
  - Cập nhật Healthcheck port về **8080**.

### 4. UI.ReactJS (Frontend)
- **Dockerfile**: Cập nhật EXPOSE port từ 80 sang **3000**.
- **nginx.conf**: Cấu hình Nginx listen trên port **3000** để khớp với mapping trong docker-compose.
