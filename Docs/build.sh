#!/bin/bash

# Script để build static site

echo "🏗️  Build MkDocs static site..."

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

# Build site
echo "🔨 Build static site..."
mkdocs build

echo "✅ Build hoàn thành! Site được tạo trong thư mục 'site/'"
echo "📁 Bạn có thể deploy thư mục 'site/' lên hosting"