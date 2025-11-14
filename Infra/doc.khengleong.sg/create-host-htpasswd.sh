#!/bin/bash

# Script tạo htpasswd file cho nginx trên host machine
# Usage: ./create-host-htpasswd.sh username

if [ -z "$1" ]; then
    echo "Usage: $0 <username>"
    echo "Example: $0 admin"
    exit 1
fi

USERNAME=$1
HTPASSWD_DIR="/etc/nginx/htpasswd"
HTPASSWD_FILE="$HTPASSWD_DIR/lengkeng-doc.htpasswd"

echo "=== Tạo htpasswd cho nginx host ==="

# Kiểm tra quyền sudo
if [ "$EUID" -ne 0 ]; then
    echo "Script này cần chạy với sudo để tạo file trong /etc/nginx/"
    echo "Chạy: sudo $0 $1"
    exit 1
fi

# Tạo thư mục nếu chưa có
mkdir -p $HTPASSWD_DIR

echo "Tạo mật khẩu cho user: $USERNAME"
echo "Nhập mật khẩu:"
read -s PASSWORD

# Tạo hash bcrypt
HASH=$(openssl passwd -6 "$PASSWORD")

# Thêm user vào file .htpasswd
echo "$USERNAME:$HASH" >> $HTPASSWD_FILE

# Set permissions
chown root:www-data $HTPASSWD_FILE
chmod 640 $HTPASSWD_FILE

echo "✅ Đã tạo user $USERNAME trong file $HTPASSWD_FILE"
echo "📁 Permissions: $(ls -la $HTPASSWD_FILE)"
echo ""
echo "Để xem nội dung file: sudo cat $HTPASSWD_FILE"
