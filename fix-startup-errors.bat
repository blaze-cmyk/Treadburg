@echo off
echo ========================================
echo Fixing Startup Errors
echo ========================================
echo.

echo [1/2] Installing missing backend dependency...
cd backend
call .runvenv\Scripts\activate.bat
pip install pydantic[email]
echo.

echo [2/2] Generating Prisma client for frontend...
cd ..\frontend
call npx prisma generate
echo.

echo ========================================
echo Fixes Complete!
echo ========================================
echo.
echo Now restart your servers:
echo 1. Stop both servers (Ctrl+C)
echo 2. Run: start-all.bat
echo.
pause
