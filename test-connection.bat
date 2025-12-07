@echo off
echo Testing Backend Connection...
echo.

curl http://localhost:8080/health

echo.
echo.
echo If you see "status":"healthy", backend is running!
echo.
pause
