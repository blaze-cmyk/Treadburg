@echo off
echo ========================================
echo   Upgrading PyTorch to version 2.1+
echo ========================================
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat

echo Uninstalling old PyTorch...
pip uninstall torch torchvision torchaudio -y

echo.
echo Installing PyTorch 2.1+ (CPU version)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo ========================================
echo   PyTorch Upgrade Complete!
echo ========================================
echo.
echo Verifying installation...
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"

echo.
pause
