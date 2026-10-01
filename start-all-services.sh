#!/bin/bash

# ============================================================================
# KhengLeong Report Automation - Master Startup Script
# ============================================================================
# This script starts all services in the correct order:
# 1. RabbitMQ (if not running)
# 2. API.FastPy (Backend - Port 8000)
# 3. qlib_service (Financial Analysis - Port 8386)
# 4. ai_api (AI Consumer)
# 5. UI.ReactJS (Frontend - Port 3000)
# ============================================================================

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log file
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/startup_${TIMESTAMP}.log"

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}  KhengLeong Report Automation - Starting All Services${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""
echo -e "${YELLOW}Logs will be saved to: ${LOG_FILE}${NC}"
echo ""

# Function to log messages
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -ti:$port >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is available
    fi
}

# ============================================================================
# Step 1: Check RabbitMQ
# ============================================================================
log "${BLUE}[1/5] Checking RabbitMQ...${NC}"

if check_port 5672; then
    log "${GREEN}✓ RabbitMQ is already running on port 5672${NC}"
else
    log "${YELLOW}⚠ RabbitMQ is not running. Starting...${NC}"
    if command -v brew >/dev/null 2>&1; then
        brew services start rabbitmq
        sleep 3
        log "${GREEN}✓ RabbitMQ started${NC}"
    else
        log "${RED}✗ Homebrew not found. Please start RabbitMQ manually${NC}"
        exit 1
    fi
fi

# Check RabbitMQ Management UI
if check_port 15672; then
    log "${GREEN}✓ RabbitMQ Management UI: http://localhost:15672 (rabbitmq/rabbitmq)${NC}"
fi

echo ""

# ============================================================================
# Step 2: Start API.FastPy (Backend)
# ============================================================================
log "${BLUE}[2/5] Starting API.FastPy (Backend - Port 8000)...${NC}"

cd "$PROJECT_ROOT/API.FastPy"

if check_port 8000; then
    log "${YELLOW}⚠ Port 8000 is already in use. Skipping...${NC}"
else
    # Create virtual environment if not exists
    if [ ! -d ".venv" ]; then
        log "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv .venv
    fi

    # Activate virtual environment and install dependencies
    source .venv/bin/activate

    # Check if requirements need to be installed
    if ! python3 -c "import fastapi" 2>/dev/null; then
        log "${YELLOW}Installing dependencies...${NC}"
        pip install -q -r requirements.txt
    fi

    # Start server in background
    log "${YELLOW}Starting uvicorn server...${NC}"
    export IS_PRODUCTION=false
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload \
        > "$LOG_DIR/api_fastpy_${TIMESTAMP}.log" 2>&1 &

    API_PID=$!
    echo $API_PID > "$LOG_DIR/api_fastpy.pid"

    # Wait for server to start
    sleep 3

    if check_port 8000; then
        log "${GREEN}✓ API.FastPy started successfully (PID: $API_PID)${NC}"
        log "${GREEN}  URL: http://localhost:8000${NC}"
        log "${GREEN}  Docs: http://localhost:8000/docs${NC}"
    else
        log "${RED}✗ Failed to start API.FastPy${NC}"
    fi
fi

cd "$PROJECT_ROOT"
echo ""

# ============================================================================
# Step 3: Start qlib_service
# ============================================================================
log "${BLUE}[3/5] Starting qlib_service (Port 8386)...${NC}"

cd "$PROJECT_ROOT/qlib_service"

if check_port 8386; then
    log "${YELLOW}⚠ Port 8386 is already in use. Skipping...${NC}"
else
    # Create virtual environment if not exists
    if [ ! -d "venv" ]; then
        log "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi

    # Activate virtual environment and install dependencies
    source venv/bin/activate

    # Check if requirements need to be installed
    if ! python3 -c "import fastapi" 2>/dev/null; then
        log "${YELLOW}Installing dependencies...${NC}"
        pip install -q -r requirements.txt
    fi

    # Start server in background
    log "${YELLOW}Starting qlib service...${NC}"
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8386 --reload \
        > "$LOG_DIR/qlib_service_${TIMESTAMP}.log" 2>&1 &

    QLIB_PID=$!
    echo $QLIB_PID > "$LOG_DIR/qlib_service.pid"

    # Wait for server to start
    sleep 3

    if check_port 8386; then
        log "${GREEN}✓ qlib_service started successfully (PID: $QLIB_PID)${NC}"
        log "${GREEN}  URL: http://localhost:8386${NC}"
        log "${GREEN}  Docs: http://localhost:8386/docs${NC}"
    else
        log "${RED}✗ Failed to start qlib_service${NC}"
    fi
fi

cd "$PROJECT_ROOT"
echo ""

# ============================================================================
# Step 4: Start ai_api (AI Consumer)
# ============================================================================
log "${BLUE}[4/5] Starting ai_api (AI Consumer)...${NC}"

cd "$PROJECT_ROOT/ai_api"

# Check if ai_api is already running (check for main.py process)
if pgrep -f "python.*ai_api.*main.py" > /dev/null; then
    log "${YELLOW}⚠ ai_api is already running. Skipping...${NC}"
else
    # Create virtual environment if not exists
    if [ ! -d "venv" ]; then
        log "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi

    # Activate virtual environment and install dependencies
    source venv/bin/activate

    # Check if requirements need to be installed
    if ! python3 -c "import aio_pika" 2>/dev/null; then
        log "${YELLOW}Installing dependencies...${NC}"
        pip install -q -r requirements.txt
    fi

    # Start consumer in background
    log "${YELLOW}Starting AI consumer...${NC}"
    nohup python3 -m auto_report.messaging > "$LOG_DIR/ai_api_${TIMESTAMP}.log" 2>&1 &

    AI_PID=$!
    echo $AI_PID > "$LOG_DIR/ai_api.pid"

    # Wait for consumer to start
    sleep 2

    if pgrep -f "python.*auto_report.messaging" > /dev/null; then
        log "${GREEN}✓ ai_api started successfully (PID: $AI_PID)${NC}"
    else
        log "${RED}✗ Failed to start ai_api${NC}"
    fi
fi

cd "$PROJECT_ROOT"
echo ""

# ============================================================================
# Step 5: Start UI.ReactJS (Frontend)
# ============================================================================
log "${BLUE}[5/5] Starting UI.ReactJS (Frontend - Port 3000)...${NC}"

cd "$PROJECT_ROOT/UI.ReactJS"

if check_port 3000; then
    log "${YELLOW}⚠ Port 3000 is already in use. Skipping...${NC}"
else
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log "${YELLOW}Installing npm dependencies...${NC}"
        npm install
    fi

    # Start React app in background
    log "${YELLOW}Starting React development server...${NC}"
    nohup npm run dev > "$LOG_DIR/ui_reactjs_${TIMESTAMP}.log" 2>&1 &

    UI_PID=$!
    echo $UI_PID > "$LOG_DIR/ui_reactjs.pid"

    # Wait for server to start
    sleep 5

    if check_port 3000; then
        log "${GREEN}✓ UI.ReactJS started successfully (PID: $UI_PID)${NC}"
        log "${GREEN}  URL: http://localhost:3000${NC}"
    else
        log "${RED}✗ Failed to start UI.ReactJS${NC}"
    fi
fi

cd "$PROJECT_ROOT"
echo ""

# ============================================================================
# Summary
# ============================================================================
log "${BLUE}============================================================================${NC}"
log "${GREEN}All services have been started!${NC}"
log "${BLUE}============================================================================${NC}"
echo ""
log "${YELLOW}Service URLs:${NC}"
log "  Frontend:    ${GREEN}http://localhost:3000${NC}"
log "  Backend API: ${GREEN}http://localhost:8000/docs${NC}"
log "  Qlib Service:${GREEN}http://localhost:8386/docs${NC}"
log "  RabbitMQ UI: ${GREEN}http://localhost:15672${NC} (rabbitmq/rabbitmq)"
echo ""
log "${YELLOW}Login Credentials:${NC}"
log "  Username: ${GREEN}admin${NC}"
log "  Password: ${GREEN}admin123${NC}"
echo ""
log "${YELLOW}Logs Directory:${NC}"
log "  ${LOG_DIR}"
echo ""
log "${YELLOW}To stop all services, run:${NC}"
log "  ${GREEN}./stop-all-services.sh${NC}"
echo ""
log "${BLUE}============================================================================${NC}"
