@echo off
echo ========================================
echo Starting TradeBerg Frontend (React/Next.js)
echo ========================================
echo.

cd frontend

echo Checking for node_modules...
if not exist node_modules (
    echo Installing dependencies...
    npm install
)

echo.
echo Starting Next.js development server on http://localhost:3000
echo.
npm run dev

pause
