# Hướng dẫn sử dụng MkDocs

## Giới thiệu

Dự án này sử dụng MkDocs với theme Material để tạo tài liệu HTML từ các file Markdown. Tài liệu được tổ chức theo cấu trúc:

- `docs/` - Thư mục chứa tất cả file Markdown
- `mkdocs.yml` - File cấu hình MkDocs
- `requirements.txt` - Dependencies cần thiết
- `scripts/` - Scripts tiện ích

## Yêu cầu hệ thống

- Python 3.8 trở lên
- pip (Python package manager)

## Cài đặt và chạy

### 1. Chạy development server (khuyến nghị)

```bash
# Sử dụng script có sẵn
./scripts/serve.sh

# Hoặc thủ công:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Server sẽ chạy tại: http://localhost:8000

### 2. Build static site cho production

```bash
# Sử dụng script có sẵn
./scripts/build.sh

# Hoặc thủ công:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdocs build
```

Kết quả được tạo trong thư mục `site/`

## Cấu trúc navigation

Navigation được định nghĩa trong `mkdocs.yml`:

```yaml
nav:
  - Trang chủ: index.md
  - Yêu cầu:
    - requirements/index.md
    - BRD: requirements/brd.md
  - Luồng người dùng:
    - user-flows/index.md
    - ...
  - Kiến trúc:
    - architecture/index.md
    - ...
```

## Thêm tài liệu mới

1. Tạo file `.md` trong thư mục `docs/`
2. Thêm vào navigation trong `mkdocs.yml`
3. Commit và push

## Features được kích hoạt

- ✅ Theme Material Design
- ✅ Dark/Light mode toggle
- ✅ Tìm kiếm tiếng Việt
- ✅ Code highlighting
- ✅ Navigation tabs
- ✅ Tự động cập nhật ngày sửa đổi
- ✅ Table of contents
- ✅ Responsive design

## Deploy

### GitHub Pages

1. Push code lên GitHub
2. Trong repository settings, bật GitHub Pages
3. Chọn source: GitHub Actions
4. Tạo workflow `.github/workflows/docs.yml`:

```yaml
name: Deploy MkDocs
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: 3.x
    - run: pip install -r requirements.txt
    - run: mkdocs gh-deploy --force
```

### Netlify

1. Connect repository đến Netlify
2. Build command: `pip install -r requirements.txt && mkdocs build`
3. Publish directory: `site`

## Troubleshooting

### Lỗi encoding
Nếu gặp lỗi với tiếng Việt, thêm vào đầu file:
```python
# -*- coding: utf-8 -*-
```

### Port đã được sử dụng
```bash
mkdocs serve -a localhost:8001
```

### Dependencies lỗi
```bash
pip install --upgrade -r requirements.txt
```