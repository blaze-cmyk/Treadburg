@echo off
echo Starting TradeBerg Frontend...
echo.

set NODE_OPTIONS=--max-old-space-size=8192
echo Node memory set to 8GB
echo.

npm run dev -- --host

pause
