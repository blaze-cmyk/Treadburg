@echo off
echo ========================================
echo Starting TradeBerg Complete System
echo ========================================
echo.
echo This will start:
echo 1. Backend API (Port 8080)
echo 2. Frontend (Port 3000)
echo.
echo Press any key to continue...
pause > nul

echo.
echo Starting Backend API...
start "TradeBerg Backend" cmd /k "cd backend && .\.runvenv\Scripts\activate.bat && python -m uvicorn app:app --reload --host 0.0.0.0 --port 8080"

timeout /t 5 /nobreak > nul

echo.
echo Starting Frontend...
start "TradeBerg Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo TradeBerg is starting!
echo ========================================
echo.
echo Backend API: http://localhost:8080
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8080/docs
echo.
echo Both services are running in separate windows.
echo Close those windows to stop the services.
echo.
pause
