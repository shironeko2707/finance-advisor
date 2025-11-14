#!/bin/bash

#
# Lengkeng UI Development Setup and Launch Script (Bash)
# 
# This script installs dependencies and starts the Lengkeng UI development server.
# It also displays environment variable information and validates configuration.
#
# Usage: ./run-dev.sh
#

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo ""
    echo -e "${YELLOW}================================================${NC}"
    echo -e "${YELLOW}  $1${NC}"
    echo -e "${YELLOW}================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Exit on any error
set -e

# Main script execution
main() {
    print_header "LENGKENG UI - DEVELOPMENT SETUP"
    
    # Check if we're in the correct directory
    if [ ! -f "package.json" ]; then
        print_error "package.json not found. Please run this script from the lengkeng_ui directory."
        exit 1
    fi
    
    # Display environment file status
    print_header "ENVIRONMENT CONFIGURATION"
    
    ENV_FILE=".env"
    ENV_EXAMPLE_FILE=".env.example"
    
    if [ -f "$ENV_FILE" ]; then
        print_success "Environment file found: $ENV_FILE"
        print_info "Loading environment variables from $ENV_FILE"
        
        # Read and display environment variables
        echo ""
        echo -e "${MAGENTA}Environment Variables:${NC}"
        echo -e "${MAGENTA}=====================${NC}"
        
        while IFS= read -r line; do
            # Skip comments and empty lines
            if [[ $line =~ ^[^#].*= ]] && [ -n "$line" ]; then
                key=$(echo "$line" | cut -d'=' -f1 | xargs)
                value=$(echo "$line" | cut -d'=' -f2- | xargs)
                
                # Mask sensitive information
                if [[ $key =~ (PASSWORD|SECRET|TOKEN|KEY) ]]; then
                    masked_value=$(printf "%*s" ${#value} | tr ' ' '*')
                    echo -e "${WHITE}  $key = $masked_value${NC}"
                else
                    echo -e "${WHITE}  $key = $value${NC}"
                fi
            fi
        done < "$ENV_FILE"
        echo ""
    else
        print_info "Environment file $ENV_FILE not found - using default values from devConfig.ts"
        
        if [ -f "$ENV_EXAMPLE_FILE" ]; then
            print_info "💡 To customize environment variables:"
            echo -e "${CYAN}   Copy $ENV_EXAMPLE_FILE to $ENV_FILE (or .env.local)${NC}"
            echo -e "${CYAN}   Example: cp $ENV_EXAMPLE_FILE $ENV_FILE${NC}"
        else
            print_warning "⚠️  $ENV_EXAMPLE_FILE not found!"
        fi
        
        echo ""
        echo -e "${MAGENTA}Using Default Configuration:${NC}"
        echo -e "${MAGENTA}==========================${NC}"
        echo -e "${WHITE}  API_BASE_URL = http://lengkeng-dev.hocai.fun (from devConfig.ts)${NC}"
        echo -e "${WHITE}  IS_DEVELOPMENT = true${NC}"
        echo -e "${WHITE}  ENABLE_DEBUG_PANEL = true${NC}"
        echo ""
    fi
    
    # Check Node.js version
    print_header "SYSTEM REQUIREMENTS CHECK"
    
    if command -v node >/dev/null 2>&1; then
        NODE_VERSION=$(node --version)
        print_success "Node.js version: $NODE_VERSION"
    else
        print_error "Node.js is not installed or not in PATH"
        print_info "Please install Node.js from https://nodejs.org/"
        exit 1
    fi
    
    if command -v npm >/dev/null 2>&1; then
        NPM_VERSION=$(npm --version)
        print_success "npm version: $NPM_VERSION"
    else
        print_error "npm is not available"
        exit 1
    fi
    
    # Install dependencies
    print_header "INSTALLING DEPENDENCIES"
    
    print_info "Checking if node_modules exists..."
    if [ ! -d "node_modules" ]; then
        print_info "node_modules not found. Installing dependencies..."
        npm install
        print_success "Dependencies installed successfully"
    else
        print_info "node_modules exists. Checking for updates..."
        npm install
        print_success "Dependencies up to date"
    fi
    
    # Display available scripts
    print_header "AVAILABLE SCRIPTS"
    
    print_info "npm run dev     - Start development server"
    print_info "npm run build   - Build for production"
    print_info "npm run lint    - Run ESLint"
    print_info "npm run preview - Preview production build"
    echo ""
    
    # Start development server
    print_header "STARTING DEVELOPMENT SERVER"
    
    print_info "Starting Vite development server..."
    print_info "Application will be available at: http://localhost:5173"
    print_info "Press Ctrl+C to stop the server"
    echo ""
    
    # Run the development server
    npm run dev
}

# Trap to handle script interruption
trap 'echo -e "\n${YELLOW}Script interrupted by user${NC}"; exit 0' INT TERM

# Run main function
main "$@"
