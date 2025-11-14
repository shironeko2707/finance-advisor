@echo off
echo Starting Lengkeng API Development Environment...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Build the development Docker image
echo Building development Docker image...
docker build -f Dockerfile -t lengkeng-api:dev .

REM Stop and remove existing container if running
echo Stopping existing container...
docker stop lengkeng-api-dev 2>nul
docker rm lengkeng-api-dev 2>nul

REM Start the main application container with mounted source code
echo Starting Lengkeng API container...
docker run -d ^
    --name lengkeng-api-dev ^
    -p 8080:8080 ^
    -v "%cd%":/app ^
    --env-file .env.local ^
    --restart unless-stopped ^
    lengkeng-api:dev

REM Show container status
echo.
echo =================================
echo   Development Environment Ready
echo =================================
echo.
echo API Server: http://localhost:8000
echo Container Status:
docker ps --filter "name=lengkeng" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
echo To view logs: docker logs -f lengkeng-api-dev
echo To stop all: docker stop lengkeng-api-dev
echo.
pause
