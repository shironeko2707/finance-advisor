#!/bin/bash

# ============================================================================
# KhengLeong Report Automation - Stop All Services Script
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

LOG_DIR="$PROJECT_ROOT/logs"

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}  KhengLeong Report Automation - Stopping All Services${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# Function to kill process by PID file
kill_by_pid_file() {
    local pid_file=$1
    local service_name=$2

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            echo -e "${YELLOW}Stopping $service_name (PID: $pid)...${NC}"
            kill $pid 2>/dev/null || kill -9 $pid 2>/dev/null
            rm -f "$pid_file"
            echo -e "${GREEN}✓ $service_name stopped${NC}"
        else
            echo -e "${YELLOW}⚠ $service_name process (PID: $pid) not found${NC}"
            rm -f "$pid_file"
        fi
    else
        echo -e "${YELLOW}⚠ $service_name PID file not found${NC}"
    fi
}

# Function to kill processes by port
kill_by_port() {
    local port=$1
    local service_name=$2

    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}Stopping $service_name on port $port (PID: $pid)...${NC}"
        kill $pid 2>/dev/null || kill -9 $pid 2>/dev/null
        echo -e "${GREEN}✓ $service_name stopped${NC}"
    else
        echo -e "${YELLOW}⚠ No process found on port $port${NC}"
    fi
}

# Stop services
echo -e "${BLUE}Stopping services...${NC}"
echo ""

# Stop UI.ReactJS
echo -e "${BLUE}[1/4] Stopping UI.ReactJS...${NC}"
kill_by_pid_file "$LOG_DIR/ui_reactjs.pid" "UI.ReactJS"
kill_by_port 3000 "UI.ReactJS (Port 3000)"
echo ""

# Stop ai_api
echo -e "${BLUE}[2/4] Stopping ai_api...${NC}"
kill_by_pid_file "$LOG_DIR/ai_api.pid" "ai_api"
# Also kill by process name
if pgrep -f "python.*ai_api.*main.py" > /dev/null; then
    echo -e "${YELLOW}Stopping ai_api by process name...${NC}"
    pkill -f "python.*ai_api.*main.py" || true
    echo -e "${GREEN}✓ ai_api stopped${NC}"
fi
echo ""

# Stop qlib_service
echo -e "${BLUE}[3/4] Stopping qlib_service...${NC}"
kill_by_pid_file "$LOG_DIR/qlib_service.pid" "qlib_service"
kill_by_port 8386 "qlib_service (Port 8386)"
echo ""

# Stop API.FastPy
echo -e "${BLUE}[4/4] Stopping API.FastPy...${NC}"
kill_by_pid_file "$LOG_DIR/api_fastpy.pid" "API.FastPy"
kill_by_port 8000 "API.FastPy (Port 8000)"
echo ""

# Clean up stale PID files
echo -e "${YELLOW}Cleaning up PID files...${NC}"
rm -f "$LOG_DIR"/*.pid
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo ""

# Optionally stop RabbitMQ
echo -e "${YELLOW}RabbitMQ is still running. To stop it, run:${NC}"
echo -e "  ${GREEN}brew services stop rabbitmq${NC}"
echo ""

echo -e "${BLUE}============================================================================${NC}"
echo -e "${GREEN}All services have been stopped!${NC}"
echo -e "${BLUE}============================================================================${NC}"
