#!/bin/bash

echo "Building and starting Nginx Storage Server..."

# Build the Docker image
echo "Building Docker image..."
docker build -t nginx-storage .

# Stop and remove existing container if it exists
echo "Stopping existing container..."
docker stop nginx-storage-server 2>/dev/null || true
docker rm nginx-storage-server 2>/dev/null || true

# Start the container
echo "Starting Nginx Storage Server..."
docker run -d \
  --name nginx-storage-server \
  -p 8088:8088 \
  -v /mnt/data/hoangpt/report-automation-project/API.FastPy/storage:/mnt/data/hoangpt/report-automation-project/API.FastPy/storage:ro \
  --restart unless-stopped \
  nginx-storage

# Wait a moment for the container to start
sleep 3

# Check if container is running
if docker ps | grep -q nginx-storage-server; then
    echo "✅ Nginx Storage Server is running successfully!"
    echo "🌐 Access your files at: http://localhost:8088/storage"
    echo "🏥 Health check: http://localhost:8088/health"
    echo ""
    echo "Container logs:"
    docker logs nginx-storage-server
else
    echo "❌ Failed to start Nginx Storage Server"
    docker logs nginx-storage-server
    exit 1
fi
