@echo off
echo =====================================
echo TradeBerg Chat Test Script
echo =====================================
echo.

echo [1/4] Checking if backend is running on port 8080...
netstat -ano | findstr :8080 > nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Backend is NOT running on port 8080
    echo.
    echo To start backend:
    echo   cd backend
    echo   .\.runvenv\Scripts\activate
    echo   python -m uvicorn app:app --reload --host 0.0.0.0 --port 8080
    echo.
    goto :check_frontend
) else (
    echo ✅ Backend is running on port 8080
)
echo.

:check_frontend
echo [2/4] Checking if frontend is running on port 3000...
netstat -ano | findstr :3000 > nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Frontend is NOT running on port 3000
    echo.
    echo To start frontend:
    echo   cd frontend
    echo   npm run dev
    echo.
    goto :check_api_key
) else (
    echo ✅ Frontend is running on port 3000
)
echo.

:check_api_key
echo [3/4] Checking Gemini API key configuration...
findstr /C:"GEMINI_API_KEY" backend\env > nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ GEMINI_API_KEY not found in backend\env
    echo.
    echo Please add your Gemini API key to backend\env file
    goto :end
) else (
    echo ✅ GEMINI_API_KEY is configured
)
echo.

echo [4/4] Testing backend health endpoint...
curl -s http://localhost:8080/health 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Cannot reach backend health endpoint
    echo Make sure backend is running!
    goto :end
)
echo.
echo ✅ Backend health check passed
echo.

echo =====================================
echo 🎉 All checks passed!
echo =====================================
echo.
echo Next steps:
echo 1. Open http://localhost:3000 in your browser
echo 2. Try sending a chat message
echo 3. You should see an AI response streaming in real-time
echo.
echo If chat still doesn't work:
echo - Check browser console (F12) for errors
echo - Check backend terminal for error messages
echo - Review the chat_fix_guide.md for detailed troubleshooting
echo.

:end
pause
