@echo off
echo Restarting TradeBerg Backend...
echo.

cd backend

echo Stopping any running servers...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul

echo.
echo Starting backend server...
python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8080 --reload

pause
