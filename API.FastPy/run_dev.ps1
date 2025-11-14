#!/usr/bin/env pwsh
# Development script for Windows - Lengkeng API

Write-Host "===== Lengkeng API Development Setup (Windows) =====" -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Blue
} catch {
    Write-Host "Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again."
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment!" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Check if activation was successful
if ($env:VIRTUAL_ENV) {
    Write-Host "Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "Failed to activate virtual environment!" -ForegroundColor Red
    exit 1
}

# Install/upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
pip install -r requirements-windows.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

# Create storage directory structure if it doesn't exist
$storageDirectories = @("storage", "storage\uploads", "storage\templates", "storage\generated", "storage\exports", "storage\cache", "storage\logs")

foreach ($dir in $storageDirectories) {
    if (-not (Test-Path $dir)) {
        Write-Host "Creating directory: $dir" -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Function to expand variables in string (like Docker does)
function Expand-Variables {
    param([string]$inputString, [hashtable]$envVars)
    
    $result = $inputString
    $pattern = '\$\{([^}]+)\}'
    
    while ($result -match $pattern) {
        $varName = $matches[1]
        $varValue = $envVars[$varName]
        if ($null -eq $varValue) {
            $varValue = ""
        }
        $result = $result -replace "\`$\{$varName\}", $varValue
    }
    return $result
}

# Load environment variables from .env.local file
if (Test-Path ".env.local") {
    Write-Host "Loading environment variables from .env.local file..." -ForegroundColor Yellow

    # First pass: collect all variables
    $envVars = @{}
    Get-Content ".env.local" | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]*)\s*=\s*(.*)\s*$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            $envVars[$name] = $value
        }
    }
    
    # Second pass: expand variables and set environment
    foreach ($kvp in $envVars.GetEnumerator()) {
        $expandedValue = Expand-Variables $kvp.Value $envVars
        Set-Item -Path "env:$($kvp.Key)" -Value $expandedValue
        Write-Host "  $($kvp.Key) = $expandedValue" -ForegroundColor Gray
    }
} else {
    Write-Host "Warning: .env.local file not found. Using default values." -ForegroundColor Yellow
    # Override CORS for local development
    $env:ALLOW_CORS_LOCAL = "true"
    $env:IS_PRODUCTION = "false"
}

Write-Host ""
Write-Host "===== Starting Lengkeng API =====" -ForegroundColor Green
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the application
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

