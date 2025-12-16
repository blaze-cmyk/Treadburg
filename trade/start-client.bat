@echo off
echo ========================================
echo  TradeBerg Frontend (Client) Only
echo ========================================
echo.

if not exist "client\node_modules\" (
    echo Installing client dependencies...
    cd client
    call npm install
    cd ..
    echo.
)

echo Starting frontend on http://localhost:3000
echo.

cd client
call npm run dev
