#!/bin/bash

# ============================================================================
# KhengLeong Report Automation - Docker Stop Script
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
echo -e "${BLUE}  KhengLeong Report Automation - Stopping Docker Services${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# Use docker compose or docker-compose based on availability
if docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Parse command line arguments
REMOVE_VOLUMES=false
REMOVE_IMAGES=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--volumes)
            REMOVE_VOLUMES=true
            shift
            ;;
        -i|--images)
            REMOVE_IMAGES=true
            shift
            ;;
        --full-clean)
            REMOVE_VOLUMES=true
            REMOVE_IMAGES=true
            shift
            ;;
        *)
            echo -e "${YELLOW}Unknown option: $1${NC}"
            shift
            ;;
    esac
done

# Stop containers
echo -e "${CYAN}Stopping all containers...${NC}"
$DOCKER_COMPOSE down

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Containers stopped${NC}"
else
    echo -e "${RED}✗ Failed to stop containers${NC}"
    exit 1
fi

# Remove volumes if requested
if [ "$REMOVE_VOLUMES" = true ]; then
    echo ""
    echo -e "${YELLOW}⚠ Removing volumes (this will delete all data)...${NC}"
    $DOCKER_COMPOSE down -v
    echo -e "${GREEN}✓ Volumes removed${NC}"
fi

# Remove images if requested
if [ "$REMOVE_IMAGES" = true ]; then
    echo ""
    echo -e "${YELLOW}⚠ Removing images...${NC}"

    # Remove project images
    docker images | grep "khengleong\|report-automation" | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true

    # Remove dangling images
    docker image prune -f

    echo -e "${GREEN}✓ Images removed${NC}"
fi

echo ""
echo -e "${BLUE}============================================================================${NC}"
echo -e "${GREEN}All services stopped successfully!${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

if [ "$REMOVE_VOLUMES" = false ] && [ "$REMOVE_IMAGES" = false ]; then
    echo -e "${YELLOW}Options:${NC}"
    echo -e "  Remove volumes:      ${GREEN}./docker-stop.sh --volumes${NC}"
    echo -e "  Remove images:       ${GREEN}./docker-stop.sh --images${NC}"
    echo -e "  Full cleanup:        ${GREEN}./docker-stop.sh --full-clean${NC}"
    echo ""
fi

echo -e "${CYAN}To start services again:${NC}"
echo -e "  ${GREEN}./docker-start.sh${NC}"
echo ""
