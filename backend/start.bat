@echo off
echo ========================================
echo   Starting TradeBerg Backend API
echo ========================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting FastAPI server...
echo Backend will be available at: http://localhost:8080
echo API Documentation: http://localhost:8080/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload

pause

