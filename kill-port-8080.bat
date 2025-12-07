@echo off
echo Killing all processes on port 8080...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do (
    echo Killing process %%a
    taskkill /F /PID %%a
)
echo Done!
pause
