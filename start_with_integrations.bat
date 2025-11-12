@echo off
echo ========================================
echo   Starting TradeBerg with Integrations
echo ========================================
echo.

cd backend

echo Loading environment variables...
set /p DUMMY=< .env.mcp
echo ✅ Environment loaded
echo.

echo Starting server on port 8080...
echo.
echo 📊 API Docs: http://localhost:8080/docs
echo 🏥 Health Check: http://localhost:8080/api/integrations/health
echo 💬 Chat: http://localhost:8080/chat
echo.

python -m uvicorn main:app --reload --port 8080
