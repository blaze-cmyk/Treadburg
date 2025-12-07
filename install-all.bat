@echo off
echo ========================================
echo TradeBerg - Complete Installation Script
echo ========================================
echo.

echo [1/4] Installing Backend Dependencies...
echo.
cd backend

echo Creating virtual environment...
python -m venv .runvenv
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call .runvenv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing backend requirements...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Backend dependencies installed successfully!
echo.

cd ..

echo [3/4] Installing Frontend Dependencies...
echo.
cd frontend

echo Installing npm packages...
npm install
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)

echo.
echo [4/4] Frontend dependencies installed successfully!
echo.

cd ..

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Configure your .env files (see .env.example)
echo 2. Run 'start-all.bat' to start the application
echo.
pause
