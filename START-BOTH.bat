@echo off
echo ========================================
echo   STARTING TRADEBERG
echo ========================================
echo.

echo Starting Backend...
start "TradeBerg Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python -m open_webui serve --port 8080"

echo Waiting 3 seconds...
timeout /t 3 /nobreak > nul

echo Starting Frontend...
start "TradeBerg Frontend" cmd /k "set NODE_OPTIONS=--max-old-space-size=8192 && npm run dev -- --host"

echo.
echo ========================================
echo   BOTH SERVICES STARTED!
echo ========================================
echo.
echo Backend:  http://localhost:8080
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit...
pause > nul
