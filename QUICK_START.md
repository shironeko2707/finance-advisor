# 🚀 Quick Start Guide - KhengLeong Report Automation

## 📋 Chọn Phương Thức Chạy

Bạn có **2 cách** để chạy hệ thống:

### 🐳 Option 1: Docker (Khuyên dùng - Đơn giản nhất)

✅ **Ưu điểm:**
- Cài đặt tự động
- Không cần cấu hình môi trường Python
- Dễ dàng start/stop
- Phù hợp cho cả development và production

❌ **Yêu cầu:**
- Docker Desktop đã cài đặt

### 💻 Option 2: Local Development (Cho developers)

✅ **Ưu điểm:**
- Hot reload nhanh hơn
- Debug dễ dàng
- Kiểm soát chi tiết

❌ **Yêu cầu:**
- Python 3.9+
- Node.js 16+
- RabbitMQ
- Cấu hình thủ công

---

## 🐳 CÁCH 1: DOCKER (5 PHÚT)

### Bước 1: Cài Docker Desktop

**macOS:**
```bash
brew install --cask docker
# Hoặc tải từ: https://www.docker.com/products/docker-desktop
```

**Windows:**
- Tải Docker Desktop: https://www.docker.com/products/docker-desktop
- Chạy installer và restart máy

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### Bước 2: Khởi động Docker Desktop

- Mở Docker Desktop application
- Đợi cho đến khi thấy "Docker Desktop is running"

### Bước 3: Start Hệ Thống

```bash
# Di chuyển vào thư mục project
cd /path/to/report-automation-project-ai_code_for_review

# Start tất cả services
./docker-start.sh
```

**⏱ Lần đầu tiên sẽ mất 5-10 phút để download và build images.**

### Bước 4: Truy Cập

Sau khi script hoàn tất, truy cập:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Qlib Service**: http://localhost:8386/docs
- **RabbitMQ**: http://localhost:15672

**Đăng nhập với:**
- Username: `admin`
- Password: `admin123`

### Bước 5: Stop Hệ Thống

```bash
# Stop tất cả services (giữ data)
./docker-stop.sh

# Stop và xóa data
./docker-stop.sh --volumes

# Full cleanup (xóa images + data)
./docker-stop.sh --full-clean
```

---

## 💻 CÁCH 2: LOCAL DEVELOPMENT (15 PHÚT)

### Bước 1: Cài Prerequisites

```bash
# Python 3.9+
python3 --version

# Node.js 16+
node --version

# RabbitMQ (macOS)
brew install rabbitmq
brew services start rabbitmq
```

### Bước 2: Setup Backend (API.FastPy)

```bash
# Terminal 1
cd API.FastPy

# Tạo virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# hoặc: .venv\Scripts\activate  # Windows

# Cài dependencies
pip install -r requirements.txt

# Chạy server
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend sẽ chạy tại: http://localhost:8000**

### Bước 3: Setup Qlib Service

```bash
# Terminal 2
cd qlib_service

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt

# Chạy service
python3 -m uvicorn main:app --host 0.0.0.0 --port 8386 --reload
```

**Qlib Service sẽ chạy tại: http://localhost:8386**

### Bước 4: Setup AI API

```bash
# Terminal 3
cd ai_api

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt

# Chạy consumer
python3 main.py
```

### Bước 5: Setup Frontend (UI.ReactJS)

```bash
# Terminal 4
cd UI.ReactJS

# Cài dependencies (chỉ lần đầu)
npm install

# Chạy dev server
npm run dev
```

**Frontend sẽ chạy tại: http://localhost:3000**

### Bước 6: Stop Services

Bấm **Ctrl+C** trong mỗi terminal để stop từng service.

**Hoặc dùng script:**
```bash
./stop-all-services.sh
```

---

## 🎯 Kiểm Tra Hệ Thống

### 1. Test Backend API

```bash
# Health check
curl http://localhost:8000/

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. Test Qlib Service

```bash
# Health check
curl http://localhost:8386/health

# Status
curl http://localhost:8386/status
```

### 3. Test RabbitMQ

- Truy cập: http://localhost:15672
- Login: `rabbitmq` / `rabbitmq`
- Kiểm tra Queues tab để xem các queues được tạo

### 4. Test Frontend

- Mở browser: http://localhost:3000
- Login với `admin` / `admin123`
- Thử upload file và tạo report

---

## 📊 So Sánh Phương Thức

| Feature | Docker | Local Dev |
|---------|--------|-----------|
| **Setup Time** | 5 phút | 15 phút |
| **Độ khó** | ⭐ Dễ | ⭐⭐⭐ Khó |
| **Hot Reload** | Có | Có |
| **Debug** | Khó hơn | Dễ |
| **Production Ready** | ✅ | ❌ |
| **Isolation** | ✅ Tốt | ❌ Ảnh hưởng system |
| **Resource Usage** | Cao hơn | Thấp hơn |

---

## 🆘 Troubleshooting

### Vấn đề: Không đăng nhập được

**Docker:**
```bash
# Tạo admin user
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
"
```

**Local:**
```bash
cd API.FastPy
IS_PRODUCTION=false python3 -c "
import os
os.environ['IS_PRODUCTION']='false'
os.environ['DATABASE_URL']='sqlite:///./storage/lengkeng.db'
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
"
```

### Vấn đề: Port đã được sử dụng

```bash
# Tìm process đang dùng port
lsof -ti:8000

# Kill process
kill -9 <PID>

# Hoặc kill tất cả
lsof -ti:3000,8000,8386,5672 | xargs kill -9
```

### Vấn đề: RabbitMQ không chạy

```bash
# macOS
brew services restart rabbitmq

# Linux
sudo systemctl restart rabbitmq-server

# Docker
docker restart kl-rabbitmq
```

### Vấn đề: Frontend không connect được Backend

Kiểm tra file `UI.ReactJS/.env.local`:
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_AUTH_BASE_URL=http://localhost:8000
VITE_USE_MOCK_AUTH=false
```

---

## 📚 Tài Liệu Chi Tiết

- **Docker Setup**: Xem [DOCKER_SETUP.md](DOCKER_SETUP.md)
- **API Documentation**: http://localhost:8000/docs
- **Qlib Documentation**: http://localhost:8386/docs
- **Architecture**: Xem [README.md](README.md)

---

## 🎉 Chúc Mừng!

Bạn đã setup thành công hệ thống KhengLeong Report Automation!

**Next Steps:**
1. Explore API documentation
2. Upload test documents
3. Generate reports
4. Check RabbitMQ message flow
5. Review logs for debugging

**Need Help?**
- Check logs: `docker-compose logs -f` (Docker) hoặc xem terminal outputs (Local)
- Review [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed troubleshooting

---

**Happy Coding! 🚀**
