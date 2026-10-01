#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
export IS_PRODUCTION=false
export APP_MODE=development
export SWAGGER_URL=/swagger
export ALLOW_CORS_LOCAL=true
export DATABASE_URL=sqlite:///./storage/lengkeng.db
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
