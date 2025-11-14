@echo off
chcp 65001 >nul

REM Script để chạy MkDocs development server

echo 🚀 Khởi động MkDocs development server...

REM Kiểm tra xem virtual environment có tồn tại không
if not exist "venv" (
    echo 📦 Tạo virtual environment...
    python -m venv venv
)

REM Kích hoạt virtual environment
echo 🔧 Kích hoạt virtual environment...
call venv\Scripts\activate.bat

REM Cài đặt dependencies
echo 📚 Cài đặt dependencies...
pip install -r requirements.txt

REM Chạy server
echo 🌐 Khởi động server tại http://localhost:8000
mkdocs serve --dev-addr=0.0.0.0:8000