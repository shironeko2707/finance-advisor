#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Function to show help
show_help() {
    echo -e "${GREEN}Usage: ./run_docker.sh [OPTIONS]${NC}"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo -e "  --alone       Run only the main application (uses existing PostgreSQL/RabbitMQ)"
    echo -e "  --down        Stop all containers"
    echo -e "  --logs        Show logs"
    echo -e "  --no-update   Skip Git update check"
    echo -e "  --help        Show this help"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  ${GRAY}./run_docker.sh                 # Pull latest code, build and run all services${NC}"
    echo -e "  ${GRAY}./run_docker.sh --alone         # Pull latest code, build main app only (use existing DB/MQ)${NC}"
    echo -e "  ${GRAY}./run_docker.sh --no-update     # Skip Git update, build and run all services${NC}"
    echo -e "  ${GRAY}./run_docker.sh --down          # Stop all services${NC}"
}

# Function to check for Git updates
check_git_update() {
    if [ "$NO_UPDATE" != "true" ]; then
        echo -e "${YELLOW}Checking for code updates...${NC}"

        # Check Git status
        echo -e "${GRAY}Current Git status:${NC}"
        git status --porcelain

        # Fetch latest changes from remote
        echo -e "${GRAY}Fetching latest changes from remote...${NC}"
        git fetch origin

        # Check if there are updates available
        LOCAL_COMMIT=$(git rev-parse HEAD)
        REMOTE_COMMIT=$(git rev-parse origin/main 2>/dev/null)

        if [ -z "$REMOTE_COMMIT" ]; then
            REMOTE_COMMIT=$(git rev-parse origin/master 2>/dev/null)
        fi

        if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
            echo -e "${GREEN}New code updates found! Pulling changes...${NC}"
            git pull origin main 2>/dev/null || git pull origin master 2>/dev/null

            if [ $? -eq 0 ]; then
                echo -e "${GREEN}Code updated successfully!${NC}"
            else
                echo -e "${RED}Error pulling updates. Please check for conflicts.${NC}"
                exit 1
            fi
        else
            echo -e "${CYAN}No new updates found. Using current code.${NC}"
        fi
    fi
}

# Function to check Docker Compose availability
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    elif docker compose version &> /dev/null; then
        echo "docker compose"
    else
        echo -e "${RED}Error: Docker Compose is not available. Please install Docker and Docker Compose.${NC}"
        exit 1
    fi
}

# Parse command line arguments
ALONE=false
DOWN=false
LOGS=false
HELP=false
NO_UPDATE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --alone)
            ALONE=true
            shift
            ;;
        --down)
            DOWN=true
            shift
            ;;
        --logs)
            LOGS=true
            shift
            ;;
        --help)
            HELP=true
            shift
            ;;
        --no-update)
            NO_UPDATE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Show help if requested
if [ "$HELP" = true ]; then
    show_help
    exit 0
fi

# Create storage directories if they don't exist
STORAGE_DIRS=("storage" "storage/uploads" "storage/templates" "storage/generated" "storage/exports" "storage/cache" "storage/logs")
for dir in "${STORAGE_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo -e "${YELLOW}Creating directory: $dir${NC}"
        mkdir -p "$dir"
    fi
done

# Check for Git updates (unless --no-update is specified)
check_git_update

# Get Docker Compose command
COMPOSE_CMD=$(check_docker_compose)

# Handle down option
if [ "$DOWN" = true ]; then
    echo -e "${YELLOW}Stopping containers...${NC}"
    $COMPOSE_CMD down -v --remove-orphans
    exit $?
fi

# Handle logs option
if [ "$LOGS" = true ]; then
    echo -e "${YELLOW}Showing logs...${NC}"
    $COMPOSE_CMD logs -f
    exit $?
fi

# Determine mode and compose file
if [ "$ALONE" = true ]; then
    echo -e "${CYAN}Running in ALONE mode - using existing PostgreSQL and RabbitMQ instances${NC}"
    echo -e "${YELLOW}Only starting the main application...${NC}"
    COMPOSE_FILE="docker-compose.alone.yml"
    COMPOSE_ARGS="-f $COMPOSE_FILE up -d --build"
else
    echo -e "${GREEN}Running in FULL mode - all services${NC}"
    COMPOSE_ARGS="up -d --build"
fi

# Execute docker-compose command
echo -e "${GRAY}Executing: $COMPOSE_CMD $COMPOSE_ARGS${NC}"
$COMPOSE_CMD $COMPOSE_ARGS

# Check result and show status
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}===== Services started successfully! =====${NC}"

    if [ "$ALONE" = true ]; then
        echo -e "${GREEN}✓ Main Application: http://localhost:8080${NC}"
        echo -e "${CYAN}✓ PostgreSQL: Using existing instance (localhost:5432)${NC}"
        echo -e "${CYAN}✓ RabbitMQ: Using existing instance (localhost:5672)${NC}"
    else
        echo -e "${GREEN}✓ Main Application: http://localhost:8080${NC}"
        echo -e "${GREEN}✓ PostgreSQL: localhost:5432${NC}"
        echo -e "${GREEN}✓ RabbitMQ Management: http://localhost:15672${NC}"
        echo -e "${GREEN}✓ RabbitMQ AMQP: localhost:5672${NC}"
    fi

    echo ""
    echo -e "${CYAN}API Documentation: http://localhost:8080/docs${NC}"
    echo ""
    echo -e "${YELLOW}Useful commands:${NC}"
    echo -e "  ${GRAY}View logs: ./run_docker.sh --logs${NC}"
    echo -e "  ${GRAY}Stop services: ./run_docker.sh --down${NC}"
else
    echo -e "${RED}Failed to start services${NC}"
    exit 1
fi
