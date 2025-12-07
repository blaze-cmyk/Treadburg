@echo off
echo ========================================
echo Starting TradeBerg Backend API
echo ========================================
echo.

cd backend

echo Activating virtual environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting FastAPI server on http://localhost:8080
echo.
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8080

pause
