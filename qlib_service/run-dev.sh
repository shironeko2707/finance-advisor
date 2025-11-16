#!/bin/bash
#
# Development run script for Qlib Advisor & Predictor Service
#
# Usage:
#   ./run-dev.sh
#

set -e

echo "================================================"
echo "  Qlib Advisor & Predictor Service - Dev Mode"
echo "================================================"
echo ""

# Check if .env exists, if not copy from .env.example
if [ ! -f .env ]; then
    echo "⚠ .env file not found, copying from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo "⚠ Please update .env with your configuration"
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Run the service
echo "Starting Qlib service in development mode..."
echo "Service will be available at: http://localhost:8081"
echo "API Documentation: http://localhost:8081/docs"
echo ""
echo "Press Ctrl+C to stop"
echo "================================================"
echo ""

# Run with reload enabled for development
python -m app.main
