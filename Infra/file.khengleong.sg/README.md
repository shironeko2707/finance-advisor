# Nginx Storage Server

Nginx Docker container để serve files từ thư mục `/mnt/data/hoangpt/report-automation-project/API.FastPy/storage` tại port 8088.

## Tính năng

- ✅ Serve files từ thư mục storage tại `/storage` endpoint
- ✅ Auto-index để xem danh sách files
- ✅ Support nhiều loại file (images, documents, videos, audio)
- ✅ Health check endpoint
- ✅ Cache headers cho performance
- ✅ Read-only volume mount

## Cách sử dụng

### Phương pháp 1: Sử dụng script tự động

```bash
chmod +x run-nginx.sh
./run-nginx.sh
```

### Phương pháp 2: Sử dụng Docker Compose

```bash
docker-compose up -d
```

### Phương pháp 3: Build và run thủ công

```bash
# Build image
docker build -t nginx-storage .

# Run container
docker run -d \
  --name nginx-storage-server \
  -p 8088:8088 \
  -v /mnt/data/hoangpt/report-automation-project/API.FastPy/storage:/mnt/data/hoangpt/report-automation-project/API.FastPy/storage:ro \
  --restart unless-stopped \
  nginx-storage
```

## Endpoints

- **Main**: `http://localhost:8088/` - Trang chủ
- **Storage**: `http://localhost:8088/storage` - Truy cập files
- **Health**: `http://localhost:8088/health` - Health check

## Quản lý container

```bash
# Xem logs
docker logs nginx-storage-server

# Stop container
docker stop nginx-storage-server

# Start container
docker start nginx-storage-server

# Restart container
docker restart nginx-storage-server

# Remove container
docker rm -f nginx-storage-server
```

## Cấu hình

File cấu hình Nginx được lưu trong `nginx.conf` với các tính năng:

- Auto-index cho directory listing
- Cache headers cho static files
- Support nhiều MIME types
- Health check endpoint
- Error handling

## Lưu ý

- Thư mục storage được mount với quyền read-only (`:ro`)
- Container sẽ tự động restart nếu bị crash
- Health check chạy mỗi 30 giây
- Port 8088 được expose ra host
