@echo off
echo ========================================
echo RESTARTING SERVER WITH BINANCE INTEGRATION
echo ========================================
echo.

echo Step 1: Stopping any running servers...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Step 2: Starting server with Binance integration...
cd backend
start "TradeBerg Server" cmd /k "python -m uvicorn main:app --reload --port 8080"

echo.
echo Step 3: Waiting for server to start (10 seconds)...
timeout /t 10 /nobreak

echo.
echo Step 4: Testing Binance integration...
cd ..
python test_binance_chat_integration.py

echo.
echo ========================================
echo DONE!
echo ========================================
echo.
echo Server is running at: http://localhost:8080
echo Chat interface: http://localhost:8080/chat
echo.
echo Try asking: "What is BTC price?"
echo You should see the LIVE Binance price!
echo.
pause
