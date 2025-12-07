@echo off
echo ========================================
echo Fix Pydantic Dependency Conflict
echo ========================================
echo.
echo This script will:
echo 1. Upgrade pydantic to latest compatible version
echo 2. Reinstall google-genai
echo 3. Test the configuration
echo.
pause

cd backend
call .\.runvenv\Scripts\activate.bat

echo.
echo Step 1: Upgrading pydantic...
pip install --upgrade pydantic

echo.
echo Step 2: Reinstalling google-genai...
pip install --upgrade --force-reinstall google-genai

echo.
echo Step 3: Testing configuration...
python test_gemini_config.py

echo.
echo ========================================
echo Fix Complete!
echo ========================================
echo.
echo If the test passed, restart your backend server:
echo   cd backend
echo   .\.runvenv\Scripts\activate
echo   python -m uvicorn app:app --reload --host 0.0.0.0 --port 8080
echo.
pause
