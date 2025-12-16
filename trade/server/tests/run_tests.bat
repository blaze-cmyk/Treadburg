@echo off
REM Script to run backend tests on Windows

echo 🧪 Running TradeBerg Backend Tests...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run pytest
pytest tests\ -v --tb=short

echo.
echo ✅ Tests completed!
pause

