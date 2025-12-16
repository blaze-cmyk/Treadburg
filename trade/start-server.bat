@echo off
echo ========================================
echo  TradeBerg Backend (Server) Only
echo ========================================
echo.

if not exist "server\.runvenv\" (
    echo Creating Python virtual environment...
    cd server
    python -m venv .runvenv
    call .runvenv\Scripts\activate
    pip install -r requirements.txt
    cd ..
    echo.
)

echo Starting backend on http://localhost:8080
echo.

cd server
call .runvenv\Scripts\activate
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8080
