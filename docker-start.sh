#!/bin/bash

# ============================================================================
# KhengLeong Report Automation - Docker Start Script
# ============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}  KhengLeong Report Automation - Docker Deployment${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed. Please install Docker first.${NC}"
    echo -e "${YELLOW}  Visit: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Use docker compose or docker-compose based on availability
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo -e "${GREEN}✓ Docker is installed${NC}"
echo -e "${GREEN}✓ Docker Compose is installed${NC}"
echo ""

# Check if .env file exists, if not create from .env.example
if [ ! -f "ai_api/.env" ]; then
    echo -e "${YELLOW}⚠ ai_api/.env not found. Creating from defaults...${NC}"
    cat > ai_api/.env << 'EOF'
# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=rabbitmq
RABBITMQ_PASSWORD=rabbitmq
RABBITMQ_VHOST=/

# Azure Services (optional - configure if needed)
DOCUMENT_INTELLIGENT_ENDPOINT=
DOCUMENT_INTELLIGENT_API_KEY=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
OPENAI_API_VERSION=2024-02-15-preview
AZURE_LLM_DEPLOYMENT=
AZURE_EMBEDDING_DEPLOYMENT=
AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_API_KEY=
AZURE_STORAGE_CONNECTION_STRING=

# MySQL (optional)
MYSQL_USER=root
MYSQL_PASSWORD=123456a
MYSQL_HOST=localhost
MYSQL_PORT=3307
MYSQL_DB=testdb
EOF
    echo -e "${GREEN}✓ Created ai_api/.env${NC}"
fi

# Create necessary directories
echo -e "${CYAN}Creating necessary directories...${NC}"
mkdir -p API.FastPy/storage/{uploads,templates,generated,exports,logs,cache}
mkdir -p qlib_service/{storage,qlib_data,models_storage,logs}
mkdir -p logs
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Stop any running containers
echo -e "${CYAN}Stopping any existing containers...${NC}"
$DOCKER_COMPOSE down 2>/dev/null || true
echo ""

# Build and start services
echo -e "${BLUE}============================================================================${NC}"
echo -e "${CYAN}Building Docker images... (this may take a few minutes)${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

$DOCKER_COMPOSE build

echo ""
echo -e "${BLUE}============================================================================${NC}"
echo -e "${CYAN}Starting all services...${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

$DOCKER_COMPOSE up -d

echo ""
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check service health
echo ""
echo -e "${BLUE}============================================================================${NC}"
echo -e "${CYAN}Checking service status...${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=0

    echo -n -e "${YELLOW}Checking $service_name...${NC} "

    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Running${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    echo -e "${RED}✗ Not responding${NC}"
    return 1
}

# Check each service
check_service "RabbitMQ Management" "http://localhost:15672" || true
check_service "Backend API" "http://localhost:8000/" || true
check_service "Qlib Service" "http://localhost:8386/health" || true
check_service "Frontend UI" "http://localhost:3000" || true

# Show running containers
echo ""
echo -e "${BLUE}============================================================================${NC}"
echo -e "${CYAN}Running Containers:${NC}"
echo -e "${BLUE}============================================================================${NC}"
$DOCKER_COMPOSE ps

echo ""
echo -e "${BLUE}============================================================================${NC}"
echo -e "${GREEN}🚀 All services are starting up!${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""
echo -e "${CYAN}Service URLs:${NC}"
echo -e "  ${GREEN}Frontend UI:        http://localhost:3000${NC}"
echo -e "  ${GREEN}Backend API Docs:   http://localhost:8000/docs${NC}"
echo -e "  ${GREEN}Qlib Service Docs:  http://localhost:8386/docs${NC}"
echo -e "  ${GREEN}RabbitMQ Management:http://localhost:15672${NC}"
echo -e "    ${YELLOW}Username: rabbitmq${NC}"
echo -e "    ${YELLOW}Password: rabbitmq${NC}"
echo ""
echo -e "${CYAN}Default Admin Login:${NC}"
echo -e "  ${GREEN}Username: admin${NC}"
echo -e "  ${GREEN}Password: admin123${NC}"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo -e "  View logs:           ${GREEN}docker-compose logs -f${NC}"
echo -e "  View specific logs:  ${GREEN}docker-compose logs -f [service-name]${NC}"
echo -e "  Stop all services:   ${GREEN}./docker-stop.sh${NC}"
echo -e "  Restart services:    ${GREEN}docker-compose restart${NC}"
echo ""
echo -e "${YELLOW}Service Names:${NC}"
echo -e "  - ${CYAN}rabbitmq${NC}      (Message broker)"
echo -e "  - ${CYAN}api-backend${NC}   (Main API)"
echo -e "  - ${CYAN}qlib-service${NC}  (Financial analysis)"
echo -e "  - ${CYAN}ai-api${NC}        (AI processing)"
echo -e "  - ${CYAN}ui-frontend${NC}   (Web interface)"
echo ""
echo -e "${BLUE}============================================================================${NC}"
echo ""
echo -e "${GREEN}📝 Note:${NC} If you see connection errors initially, wait 30-60 seconds"
echo -e "         for all services to fully initialize."
echo ""
