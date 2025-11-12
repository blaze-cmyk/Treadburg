@echo off
echo ========================================
echo   TradeBerg Unified Perplexity System
echo ========================================
echo.

echo Checking environment...
if not exist "backend\.env" (
    echo ERROR: backend\.env file not found!
    echo Please copy backend\.env.example to backend\.env and configure API keys
    pause
    exit /b 1
)

echo.
echo Starting Backend Server...
echo.
start "TradeBerg Backend" cmd /k "cd backend && python -m uvicorn open_webui.main:app --reload --port 8080"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   Backend started on port 8080
echo ========================================
echo.
echo To test the integration:
echo   1. Open another terminal
echo   2. cd backend
echo   3. python test_api_simple.py
echo.
echo To start frontend:
echo   npm run dev
echo.
echo Press any key to exit...
pause >nul
