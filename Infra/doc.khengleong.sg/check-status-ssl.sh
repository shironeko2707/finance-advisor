#!/bin/bash

# Script kiểm tra trạng thái setup

DOMAIN="lengkeng-doc.hocai.fun"

echo "=== Kiểm tra trạng thái Lengkeng Docs ==="

echo ""
echo "1. Docker Container Status:"
docker compose ps

echo ""
echo "2. Nginx Host Configuration:"
if [ -f "/etc/nginx/sites-enabled/lengkeng-doc.hocai.fun.conf" ]; then
    echo "✅ Nginx config exists"
    sudo nginx -t && echo "✅ Nginx config is valid" || echo "❌ Nginx config has errors"
else
    echo "❌ Nginx config not found"
fi

echo ""
echo "3. SSL Certificate:"
if sudo test -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem"; then
    echo "✅ SSL certificate exists"
    sudo certbot certificates | grep -A5 "$DOMAIN"
else
    echo "❌ SSL certificate not found"
fi

echo ""
echo "4. Basic Auth File:"
if sudo test -f "/etc/nginx/htpasswd/lengkeng-doc.htpasswd"; then
    echo "✅ htpasswd file exists"
    echo "Users:"
    sudo cat /etc/nginx/htpasswd/lengkeng-doc.htpasswd | cut -d: -f1
else
    echo "❌ htpasswd file not found"
fi

echo ""
echo "5. Port Status:"
if netstat -tuln | grep -q ":8000"; then
    echo "✅ Docker container port 8000 is listening"
else
    echo "❌ Docker container port 8000 not listening"
fi

if netstat -tuln | grep -q ":80"; then
    echo "✅ Nginx port 80 is listening"
else
    echo "❌ Nginx port 80 not listening"
fi

if netstat -tuln | grep -q ":443"; then
    echo "✅ Nginx port 443 is listening"
else
    echo "❌ Nginx port 443 not listening"
fi

echo ""
echo "6. Connection Test:"
echo "Testing HTTP->HTTPS redirect:"
curl -I -s http://$DOMAIN | head -1

echo ""
echo "Testing HTTPS (without auth):"
curl -I -k -s https://$DOMAIN | head -1

echo ""
echo "7. Logs (last 5 lines):"
if [ -f "/var/log/nginx/lengkeng-doc.access.log" ]; then
    echo "Access log:"
    sudo tail -5 /var/log/nginx/lengkeng-doc.access.log 2>/dev/null || echo "No access log entries yet"
fi

if [ -f "/var/log/nginx/lengkeng-doc.error.log" ]; then
    echo "Error log:"
    sudo tail -5 /var/log/nginx/lengkeng-doc.error.log 2>/dev/null || echo "No error log entries"
fi

echo ""
echo "=== Summary ==="
echo "🌐 Website: https://$DOMAIN"
echo "📊 MkDocs container: http://localhost:8000"
echo "📁 Nginx config: /etc/nginx/sites-available/lengkeng-doc.hocai.fun.conf"
echo "🔐 htpasswd file: /etc/nginx/htpasswd/lengkeng-doc.htpasswd"
