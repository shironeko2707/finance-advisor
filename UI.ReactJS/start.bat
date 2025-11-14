@echo off
if exist .env.local (
    echo Found .env.local file, starting development server...
    echo.
    echo Contents of .env.local:
    echo ========================
    type .env.local
    echo ========================
    echo.
    npm run dev
) else (
    echo .env.local file not found. Please create it before running the development server.
    pause
)

