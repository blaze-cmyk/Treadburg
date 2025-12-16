@echo off
echo ========================================
echo  TradeBerg Development Server Startup
echo ========================================
echo.

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing root dependencies...
    call npm install
    echo.
)

REM Check if client dependencies exist
if not exist "client\node_modules\" (
    echo Installing client dependencies...
    cd client
    call npm install
    cd ..
    echo.
)

REM Check if Python virtual environment exists
if not exist "server\.runvenv\" (
    echo Creating Python virtual environment...
    cd server
    python -m venv .runvenv
    call .runvenv\Scripts\activate
    pip install -r requirements.txt
    cd ..
    echo.
)

echo.
echo Starting development servers...
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8080
echo.
echo Press Ctrl+C to stop both servers
echo.

call npm run dev
