#!/bin/bash

# Script setup SSL certificate cho domain lengkeng-doc.hocai.fun
# Dành cho nginx chạy trên host machine

set -e

DOMAIN="lengkeng-doc.hocai.fun"
EMAIL="pthoang2@cmcglobal.vn"  # Thay đổi email của bạn

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}=== Setup SSL cho $DOMAIN ===${NC}"

# Kiểm tra quyền sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Script này cần chạy với sudo${NC}"
    echo "Chạy: sudo $0"
    exit 1
fi

# Kiểm tra email
if [[ "$EMAIL" == "your-email@example.com" ]]; then
    echo -e "${RED}Lỗi: Vui lòng thay đổi EMAIL trong script này${NC}"
    echo "Sửa biến EMAIL trong file setup-host-ssl.sh"
    exit 1
fi

echo -e "${YELLOW}1. Kiểm tra nginx configuration...${NC}"

# Copy nginx config
if [ -f "nginx-host-config/lengkeng-doc.hocai.fun.conf" ]; then
    cp nginx-host-config/lengkeng-doc.hocai.fun.conf /etc/nginx/sites-available/
    echo "✅ Đã copy nginx config"
else
    echo -e "${RED}❌ Không tìm thấy file nginx-host-config/lengkeng-doc.hocai.fun.conf${NC}"
    exit 1
fi

# Enable site (tạm thời disable SSL lines)
echo -e "${YELLOW}2. Tạo cấu hình tạm thời (chưa có SSL)...${NC}"
sed -e '/ssl_certificate/s/^/#/' \
    -e '/ssl_certificate_key/s/^/#/' \
    -e '/listen 443/s/^/#/' \
    -e '/ssl_/s/^/#/' \
    /etc/nginx/sites-available/lengkeng-doc.hocai.fun.conf > /tmp/lengkeng-doc-temp.conf

cp /tmp/lengkeng-doc-temp.conf /etc/nginx/sites-available/lengkeng-doc.hocai.fun.conf

# Enable site
ln -sf /etc/nginx/sites-available/lengkeng-doc.hocai.fun.conf /etc/nginx/sites-enabled/

# Test nginx config
echo -e "${YELLOW}3. Test nginx configuration...${NC}"
nginx -t

# Reload nginx
echo -e "${YELLOW}4. Reload nginx...${NC}"
systemctl reload nginx

echo -e "${YELLOW}5. Tạo SSL certificate với Certbot...${NC}"

# Install certbot if not exists
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

# Create certificate
certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --no-eff-email --force-renewal

echo -e "${YELLOW}6. Restore full nginx configuration...${NC}"
cp nginx-host-config/lengkeng-doc.hocai.fun.conf /etc/nginx/sites-available/

# Test final config
nginx -t && systemctl reload nginx

echo -e "${GREEN}✅ SSL đã được cài đặt thành công!${NC}"
echo -e "${GREEN}🌐 Website: https://$DOMAIN${NC}"
echo -e "${GREEN}🔒 SSL Certificate: Let's Encrypt${NC}"

echo -e "${BLUE}"
echo "=== Thông tin SSL Certificate ==="
certbot certificates
echo -e "${NC}"

echo -e "${YELLOW}=== Auto-renewal Setup ===${NC}"
echo "SSL certificate sẽ tự động gia hạn qua systemd timer của certbot"
systemctl status certbot.timer --no-pager

echo ""
echo -e "${YELLOW}=== Các bước tiếp theo ===${NC}"
echo "1. Tạo user/password: sudo ./create-host-htpasswd.sh admin"
echo "2. Start Docker container: docker compose up -d"
echo "3. Truy cập: https://$DOMAIN"
