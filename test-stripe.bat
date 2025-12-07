@echo off
echo ========================================
echo Stripe Integration Testing Guide
echo ========================================
echo.

echo This script will help you test the Stripe integration.
echo.
echo Prerequisites:
echo 1. Backend dependencies installed (pip install -r requirements.txt)
echo 2. Frontend dependencies installed (npm install)
echo 3. Stripe API keys configured in backend/.env
echo.

:MENU
echo ========================================
echo Select Test Option:
echo ========================================
echo.
echo 1. Test Backend API Endpoints
echo 2. Start Backend + Frontend (for manual testing)
echo 3. Run Stripe CLI Webhook Forwarding
echo 4. View Test Card Numbers
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto TEST_API
if "%choice%"=="2" goto START_SERVERS
if "%choice%"=="3" goto STRIPE_CLI
if "%choice%"=="4" goto TEST_CARDS
if "%choice%"=="5" goto END

echo Invalid choice. Please try again.
goto MENU

:TEST_API
echo.
echo ========================================
echo Testing Backend API Endpoints
echo ========================================
echo.
echo Make sure backend is running on http://localhost:8080
echo.
pause

cd backend
python test_stripe_integration.py
pause
goto MENU

:START_SERVERS
echo.
echo ========================================
echo Starting Backend and Frontend
echo ========================================
echo.
echo This will open 2 terminal windows:
echo - Backend: http://localhost:8080
echo - Frontend: http://localhost:3000
echo.
pause

start "TradeBerg Backend" cmd /k "cd backend && .runvenv\Scripts\activate && python -m uvicorn app:app --reload --port 8080"
timeout /t 3 /nobreak > nul
start "TradeBerg Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Servers starting...
echo - Backend: http://localhost:8080
echo - Frontend: http://localhost:3000
echo - API Docs: http://localhost:8080/docs
echo.
echo Press any key to return to menu...
pause > nul
goto MENU

:STRIPE_CLI
echo.
echo ========================================
echo Stripe CLI Webhook Forwarding
echo ========================================
echo.
echo This requires Stripe CLI to be installed.
echo Download from: https://stripe.com/docs/stripe-cli
echo.
echo Command to run:
echo stripe listen --forward-to localhost:8080/api/billing/webhook
echo.
echo This will give you a webhook signing secret (whsec_...)
echo Add it to your backend/.env file as STRIPE_WEBHOOK_SECRET
echo.
pause
goto MENU

:TEST_CARDS
echo.
echo ========================================
echo Stripe Test Card Numbers
echo ========================================
echo.
echo Use these test cards in Stripe Checkout:
echo.
echo SUCCESS CARDS:
echo   4242 4242 4242 4242 - Visa (always succeeds)
echo   5555 5555 5555 4444 - Mastercard
echo   3782 822463 10005   - American Express
echo.
echo FAILURE CARDS:
echo   4000 0000 0000 0002 - Card declined
echo   4000 0000 0000 9995 - Insufficient funds
echo.
echo EXPIRY: Any future date (e.g., 12/34)
echo CVC: Any 3 digits (e.g., 123)
echo ZIP: Any 5 digits (e.g., 12345)
echo.
echo More test cards: https://stripe.com/docs/testing
echo.
pause
goto MENU

:END
echo.
echo Exiting...
exit /b 0
