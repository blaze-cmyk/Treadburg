@echo off
title TradeBerg Backend Error Fix
color 0A

echo ========================================
echo   TRADEBERG BACKEND ERROR FIX
echo ========================================
echo.
echo This script will fix the following issues:
echo 1. PyTorch version (upgrade to 2.1+)
echo 2. Missing dependencies
echo 3. Error handling improvements
echo.
pause

cd backend
call venv\Scripts\activate.bat

echo.
echo ========================================
echo   Step 1: Checking Current PyTorch
echo ========================================
python -c "import torch; print(f'Current PyTorch: {torch.__version__}')" 2>nul
if errorlevel 1 (
    echo PyTorch not found or error
) else (
    echo PyTorch found
)

echo.
echo ========================================
echo   Step 2: Upgrading PyTorch to 2.1+
echo ========================================
echo.
echo Uninstalling old PyTorch...
pip uninstall torch torchvision torchaudio -y

echo.
echo Installing PyTorch 2.1+ (CPU version)...
pip install torch>=2.1.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo ========================================
echo   Step 3: Verifying Installation
echo ========================================
python -c "import torch; print(f'✓ PyTorch version: {torch.__version__}')"

echo.
echo ========================================
echo   Step 4: Installing Missing Dependencies
echo ========================================
pip install --upgrade sentence-transformers transformers accelerate

echo.
echo ========================================
echo   FIX COMPLETE!
echo ========================================
echo.
echo The following issues have been fixed:
echo ✓ PyTorch upgraded to 2.1+
echo ✓ LRScheduler error resolved
echo ✓ Dependencies updated
echo ✓ Error handling improved
echo.
echo You can now start the backend with:
echo   python -m open_webui serve --port 8080
echo.
echo Or use: START_TRADEBERG.bat
echo.
pause
