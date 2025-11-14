#!/bin/bash

# Script để chạy MkDocs development server

echo "🚀 Khởi động MkDocs development server..."

# Kiểm tra xem virtual environment có tồn tại không
if [ ! -d "venv" ]; then
    echo "📦 Tạo virtual environment..."
    python3 -m venv venv
fi

# Kích hoạt virtual environment
echo "🔧 Kích hoạt virtual environment..."
source venv/bin/activate

# Cài đặt dependencies
echo "📚 Cài đặt dependencies..."
pip install -r requirements.txt

# Chạy server
echo "🌐 Khởi động server tại http://localhost:8000"
mkdocs serve --dev-addr=0.0.0.0:8000