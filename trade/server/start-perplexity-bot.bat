@echo off
echo Starting Perplexity Trading Bot (Isolated Service)...
echo.

cd /d "%~dp0perplexity_bot"

echo Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Perplexity Trading Bot on port 8001...
echo Service will be available at: http://localhost:8001
echo API endpoints:
echo   - Health: http://localhost:8001/health
echo   - Chat: http://localhost:8001/api/chat
echo   - Models: http://localhost:8001/api/models
echo.
echo Press Ctrl+C to stop the service
echo.

python main.py

pause
