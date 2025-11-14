#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Lengkeng UI Development Setup and Launch Script (PowerShell)

.DESCRIPTION
    This script installs dependencies and starts the Lengkeng UI development server.
    It also displays environment variable information and validates configuration.

.EXAMPLE
    .\start-dev.ps1
#>

# Color functions for better output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-ColorOutput Yellow "================================================"
    Write-ColorOutput Yellow "  $Message"
    Write-ColorOutput Yellow "================================================"
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput Green "[SUCCESS] $Message"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput Yellow "[WARN] $Message"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput Red "[ERROR] $Message"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput Cyan "[INFO] $Message"
}

# Main script execution
try {
    Write-Header "LENGKENG UI - DEVELOPMENT SETUP"
    
    # Check if we're in the correct directory
    if (-not (Test-Path "package.json")) {
        Write-Error "package.json not found. Please run this script from the lengkeng_ui directory."
        exit 1
    }
    
    # Display environment file status
    Write-Header "ENVIRONMENT CONFIGURATION"
    
    $envFile = ".env.local"
    $envExampleFile = ".env.example"
    
    if (Test-Path $envFile) {
        Write-Success "Environment file found: $envFile"
        Write-Info "Loading environment variables from $envFile"
        
        # Read and display environment variables
        Write-Host ""
        Write-ColorOutput Magenta "Environment Variables:"
        Write-ColorOutput Magenta "====================="
        
        Get-Content $envFile | ForEach-Object {
            if ($_ -match "^[^#].*=" -and $_ -ne "") {
                $parts = $_ -split "=", 2
                $key = $parts[0].Trim()
                $value = $parts[1].Trim()
                
                # Mask sensitive information
                if ($key -match "(PASSWORD|SECRET|TOKEN|KEY)") {
                    $maskedValue = "*" * $value.Length
                    Write-ColorOutput White "  $key = $maskedValue"
                } else {
                    Write-ColorOutput White "  $key = $value"
                }
            }
        }
        Write-Host ""
    } else {
        Write-Info "Environment file $envFile not found - using default values from config.ts"
        
        $envExampleFile = ".env.example"
        if (Test-Path $envExampleFile) {
            Write-Info "[HINT] To customize environment variables:"
            Write-ColorOutput Cyan "   Copy $envExampleFile to $envFile (or .env.local)"
            Write-ColorOutput Cyan "   Example: Copy-Item $envExampleFile $envFile"
        } else {
            Write-Warning "$envExampleFile not found!"
        }
        
        Write-Host ""
        Write-ColorOutput Magenta "Using Default Configuration:"
        Write-ColorOutput Magenta "=========================="
        Write-ColorOutput White "  API_BASE_URL = http://lengkeng-dev.hocai.fun (from config.ts)"
        Write-ColorOutput White "  IS_DEVELOPMENT = true"
        Write-ColorOutput White "  ENABLE_DEBUG_PANEL = true"
        Write-Host ""
    }
    
    # Check Node.js version
    Write-Header "SYSTEM REQUIREMENTS CHECK"
    
    try {
        $nodeVersion = node --version
        Write-Success "Node.js version: $nodeVersion"
    } catch {
        Write-Error "Node.js is not installed or not in PATH"
        Write-Info "Please install Node.js from https://nodejs.org/"
        exit 1
    }
    
    try {
        $npmVersion = npm --version
        Write-Success "npm version: $npmVersion"
    } catch {
        Write-Error "npm is not available"
        exit 1
    }
    
    # Install dependencies
    Write-Header "INSTALLING DEPENDENCIES"
    
    Write-Info "Checking if node_modules exists..."
    if (-not (Test-Path "node_modules")) {
        Write-Info "node_modules not found. Installing dependencies..."
        npm install
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Dependencies installed successfully"
        } else {
            Write-Error "Failed to install dependencies"
            exit 1
        }
    } else {
        Write-Info "node_modules exists. Checking for updates..."
        npm install
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Dependencies up to date"
        } else {
            Write-Warning "Some dependency issues detected, but continuing..."
        }
    }
    
    # Display available scripts
    Write-Header "AVAILABLE SCRIPTS"
    
    Write-Info "npm run dev     - Start development server"
    Write-Info "npm run build   - Build for production"
    Write-Info "npm run lint    - Run ESLint"
    Write-Info "npm run preview - Preview production build"
    Write-Host ""
    
    # Start development server
    Write-Header "STARTING DEVELOPMENT SERVER"
    
    Write-Info "Starting Vite development server..."
    Write-Info "Application will be available at: http://localhost:5173"
    Write-Info "Press Ctrl+C to stop the server"
    Write-Host ""
    
    # Run the development server
    npm run dev
    
} catch {
    Write-Error "An error occurred: $($_.Exception.Message)"
    exit 1
}
