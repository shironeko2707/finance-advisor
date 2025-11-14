#!/bin/bash
# Development script for Linux/macOS - Lengkeng API

set -e  # Exit on any error

echo "===== Lengkeng API Development Setup (Linux/macOS) ====="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if Python is installed
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${BLUE}Found Python: $(python3 --version)${NC}"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo -e "${BLUE}Found Python: $(python --version)${NC}"
else
    echo -e "${RED}Python is not installed or not in PATH!${NC}"
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "${BLUE}Python version: $PYTHON_VERSION${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv .venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if activation was successful
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${GREEN}Virtual environment activated: $VIRTUAL_ENV${NC}"
else
    echo -e "${RED}Failed to activate virtual environment!${NC}"
    exit 1
fi

# Install/upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
python -m pip install --upgrade pip

# Install dependencies (including platform-specific ones)
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install dependencies!${NC}"
    exit 1
fi

# Install Linux-specific dependencies
echo -e "${YELLOW}Installing Linux-specific dependencies...${NC}"
pip install -r requirements-linux.txt
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Warning: Failed to install Linux-specific dependencies. Some features may not work.${NC}"
fi

# Create storage directory structure if it doesn't exist
storage_dirs=("storage" "storage/uploads" "storage/templates" "storage/generated" "storage/exports" "storage/cache" "storage/logs")

for dir in "${storage_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo -e "${YELLOW}Creating directory: $dir${NC}"
        mkdir -p "$dir"
    fi
done

# Function to expand variables in string (like Docker does)
expand_variables() {
    local input="$1"
    local result="$input"
    
    # Find all ${VAR} patterns and replace them
    while [[ "$result" =~ \$\{([A-Za-z_][A-Za-z0-9_]*)\} ]]; do
        local var_name="${BASH_REMATCH[1]}"
        local var_value="${!var_name}"
        result="${result//\$\{$var_name\}/$var_value}"
    done
    
    echo "$result"
}

# Load environment variables from .env.local file
if [ -f ".env.local" ]; then
    echo -e "${YELLOW}Loading environment variables from .env.local file...${NC}"
    
    # First pass: read all variables into an associative array
    declare -A env_vars
    while IFS= read -r line || [ -n "$line" ]; do
        # Remove carriage return if present (Windows line endings)
        line=${line%$'\r'}
        
        # Skip empty lines and comments
        if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
            # Check if line contains = and is a valid variable assignment
            if [[ "$line" =~ ^([A-Za-z0-9_][A-Za-z0-9_]*)=(.*)$ ]]; then
                var_name="${BASH_REMATCH[1]}"
                var_value="${BASH_REMATCH[2]}"
                env_vars["$var_name"]="$var_value"
            fi
        fi
    done < .env.local
    
    # Second pass: expand variables and export
    for var_name in "${!env_vars[@]}"; do
        var_value="${env_vars[$var_name]}"
        
        # Set the variable first so it's available for expansion
        export "$var_name"="$var_value"
        
        # Expand variables in the value
        expanded_value=$(expand_variables "$var_value")
        
        # Export the expanded value
        export "$var_name"="$expanded_value"
        echo -e "  ${NC}$var_name = $expanded_value"
    done
else
    echo -e "${YELLOW}Warning: .env file not found. Using default values.${NC}"
    export ALLOW_CORS_LOCAL="true"
    export IS_PRODUCTION="false"
fi

echo ""
echo -e "${GREEN}===== Starting Lengkeng API =====${NC}"
echo -e "${CYAN}API will be available at: http://localhost:8000${NC}"
echo -e "${CYAN}API Documentation: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start the application
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
