@echo off
echo Starting TradeBerg Backend...
echo.

cd backend
call venv\Scripts\activate.bat
python -m open_webui serve --port 8080

pause
