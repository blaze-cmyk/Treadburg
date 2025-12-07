@echo off
REM Run all tests for TradeBerg project

echo ========================================
echo   TradeBerg - Running All Tests
echo ========================================
echo.

echo [1/2] Running Backend Tests...
echo ----------------------------------------
cd backend
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)
pytest tests\ -v --tb=short
set BACKEND_RESULT=%ERRORLEVEL%
cd ..

echo.
echo [2/2] Frontend Tests...
echo ----------------------------------------
echo Note: Frontend tests require npm packages
echo       Run 'npm install' in frontend/ first
echo.
echo Skipping frontend tests for now...
echo (Uncomment below to enable)
REM cd frontend
REM npm test
REM set FRONTEND_RESULT=%ERRORLEVEL%
REM cd ..

echo.
echo ========================================
if %BACKEND_RESULT% EQU 0 (
    echo ✅ Backend tests passed!
) else (
    echo ❌ Backend tests failed!
)
echo ========================================
pause

