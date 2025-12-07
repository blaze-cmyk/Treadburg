@echo off
echo ========================================
echo   TradeBerg Stripe Integration Test
echo ========================================
echo.
echo This will start the application and open the pricing page.
echo.
echo Test card: 4242 4242 4242 4242
echo Expiry: 12/25
echo CVC: 123
echo ZIP: 12345
echo.
pause

echo.
echo Starting backend and frontend...
echo.

start "TradeBerg Backend" cmd /k "cd backend && .\.runvenv\Scripts\activate && python -m uvicorn app:app --reload --port 8080"
timeout /t 3 /nobreak > nul

start "TradeBerg Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 5 /nobreak > nul

echo.
echo Waiting for servers to start...
timeout /t 10 /nobreak > nul

echo.
echo Opening pricing page in browser...
start http://localhost:3000/pricing

echo.
echo ========================================
echo   Servers Started!
echo ========================================
echo.
echo Backend: http://localhost:8080
echo Frontend: http://localhost:3000
echo Pricing: http://localhost:3000/pricing
echo Billing: http://localhost:3000/billing
echo.
echo Test the checkout flow:
echo 1. Click "Get Started" on Pro plan
echo 2. Enter test card: 4242 4242 4242 4242
echo 3. Complete checkout
echo 4. Check billing dashboard
echo.
echo Press any key to close this window...
pause > nul
