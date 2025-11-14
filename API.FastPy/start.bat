@echo off
echo Starting FastAPI server...

REM Check if port 8000 is in use
echo Checking if port 8000 is available...
netstat -ano | findstr :8000 > nul
if %errorlevel% == 0 (
    echo.
    echo ERROR: Port 8000 is already in use!
    echo.
    echo Current processes using port 8000:
    netstat -ano | findstr :8000
    echo.
    echo Please stop the process using port 8000 or use a different port.
    echo You can kill the process using: taskkill /PID [PID_NUMBER] /F
    echo.
    pause
    exit /b 1
)
echo Port 8000 is available.
echo.

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using system Python...
)

REM Check if .env.local exists
if exist .env.local (
    echo Found .env.local file, loading environment variables...
    echo.
    echo Contents of .env.local:
    echo ========================
    type .env.local
    echo ========================
    echo.
    REM Set environment variables from .env.local
    for /f "usebackq tokens=1,2 delims==" %%a in (.env.local) do (
        if not "%%a"=="" if not "%%a:~0,1%%"=="#" set "%%a=%%b"
    )
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
) else (
    echo .env.local file not found, starting without loading environment variables...
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
)
