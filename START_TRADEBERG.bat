@echo off
title TradeBerg Startup Manager
color 0A

echo.
echo ========================================
echo   TRADEBERG STARTUP MANAGER
echo ========================================
echo.

:menu
echo Choose an option:
echo.
echo [1] Start Backend Only (Port 8080)
echo [2] Start Frontend Dev Server (Port 5173)
echo [3] Start Both (Backend + Frontend)
echo [4] Build Frontend for Production
echo [5] Test Backend Health
echo [6] Exit
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto backend
if "%choice%"=="2" goto frontend
if "%choice%"=="3" goto both
if "%choice%"=="4" goto build
if "%choice%"=="5" goto test
if "%choice%"=="6" goto end

echo Invalid choice. Please try again.
echo.
goto menu

:backend
echo.
echo ========================================
echo   STARTING BACKEND
echo ========================================
echo.
cd backend
call venv\Scripts\activate.bat
python -m open_webui serve --port 8080
goto end

:frontend
echo.
echo ========================================
echo   STARTING FRONTEND DEV SERVER
echo ========================================
echo.
echo Setting Node.js memory to 8GB...
set NODE_OPTIONS=--max-old-space-size=8192
echo.
echo Starting Vite...
npm run dev -- --host
goto end

:both
echo.
echo ========================================
echo   STARTING BOTH SERVICES
echo ========================================
echo.
echo Starting Backend in new window...
start "TradeBerg Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python -m open_webui serve --port 8080"
echo.
echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul
echo.
echo Starting Frontend in new window...
set NODE_OPTIONS=--max-old-space-size=8192
start "TradeBerg Frontend" cmd /k "set NODE_OPTIONS=--max-old-space-size=8192 && npm run dev -- --host"
echo.
echo ========================================
echo   BOTH SERVICES STARTED!
echo ========================================
echo.
echo Backend: http://localhost:8080
echo Frontend: http://localhost:5173
echo.
echo Press any key to return to menu...
pause > nul
goto menu

:build
echo.
echo ========================================
echo   BUILDING FRONTEND FOR PRODUCTION
echo ========================================
echo.
echo Setting Node.js memory to 8GB...
set NODE_OPTIONS=--max-old-space-size=8192
echo.
echo Building... (this may take a few minutes)
npm run build
echo.
if %errorlevel% equ 0 (
    echo ========================================
    echo   BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Frontend built successfully.
    echo You can now access the app at: http://localhost:8080
) else (
    echo ========================================
    echo   BUILD FAILED!
    echo ========================================
    echo.
    echo Please check the error messages above.
)
echo.
echo Press any key to return to menu...
pause > nul
goto menu

:test
echo.
echo ========================================
echo   TESTING BACKEND HEALTH
echo ========================================
echo.
echo Testing http://localhost:8080/api/tradeberg/metrics
echo.
curl -s http://localhost:8080/api/tradeberg/metrics
echo.
echo.
if %errorlevel% equ 0 (
    echo Backend is responding!
) else (
    echo Backend is not responding. Make sure it's running.
)
echo.
echo Press any key to return to menu...
pause > nul
goto menu

:end
echo.
echo Goodbye!
timeout /t 2 /nobreak > nul
exit
