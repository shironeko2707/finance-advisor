#!/bin/bash
cd "$(dirname "$0")"

# Create storage directories
mkdir -p storage qlib_data models_storage

# Load environment variables from .env.local
if [ -f .env.local ]; then
    export $(grep -v '^#' .env.local | grep -v '^$' | xargs)
fi

echo "===== Starting Qlib Advisor & Predictor Service ====="
echo "Service will be available at: http://localhost:8081"
echo "API Documentation: http://localhost:8081/docs"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the service (assumes dependencies are already installed in current environment)
python -m uvicorn main:app --host 0.0.0.0 --port 8386 --reload
