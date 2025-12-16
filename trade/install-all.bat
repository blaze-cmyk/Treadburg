@echo off
echo ========================================
echo  TradeBerg - Install All Dependencies
echo ========================================
echo.

echo [1/4] Installing root dependencies...
call npm install
echo.

echo [2/4] Installing client dependencies...
cd client
call npm install
cd ..
echo.

echo [3/4] Creating Python virtual environment...
cd server
if exist ".runvenv\" (
    echo Virtual environment already exists, skipping creation...
) else (
    python -m venv .runvenv
)
echo.

echo [4/4] Installing server dependencies...
call .runvenv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..
echo.

echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo To start development servers, run:
echo   start-dev.bat
echo.
echo Or start them separately:
echo   start-client.bat  (Frontend only)
echo   start-server.bat  (Backend only)
echo.
pause
