#!/bin/bash

# Script test nhanh MkDocs

echo "🧪 Testing MkDocs setup..."

# Kiểm tra virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment chưa được tạo"
    echo "   Chạy: python3 -m venv venv"
    exit 1
fi

# Kích hoạt virtual environment
source venv/bin/activate

# Kiểm tra dependencies
echo "📦 Kiểm tra dependencies..."
if ! pip list | grep mkdocs > /dev/null; then
    echo "❌ MkDocs chưa được cài đặt"
    echo "   Chạy: pip install -r requirements.txt"
    exit 1
fi

# Test build
echo "🔨 Testing build..."
if mkdocs build --quiet; then
    echo "✅ Build thành công!"
else
    echo "❌ Build thất bại"
    exit 1
fi

# Kiểm tra site directory
if [ -d "site" ]; then
    echo "✅ Site directory được tạo"
    echo "📁 Kích thước: $(du -sh site | cut -f1)"
    echo "📄 Files: $(find site -type f | wc -l) files"
else
    echo "❌ Site directory không tồn tại"
    exit 1
fi

echo ""
echo "🎉 Tất cả tests passed!"
echo ""
echo "Để chạy development server:"
echo "   ./scripts/serve.sh"
echo ""
echo "Để build production site:"
echo "   ./scripts/build.sh"
echo ""
echo "Tài liệu có sẵn tại: ./site/index.html"