@echo off
echo ========================================
echo    Enhanced TradeBerg System Startup
echo ========================================
echo.
echo Starting backend with enhanced features:
echo - Claude AI for better formatting
echo - Real-time Nansen + Coinalyze data
echo - Structured institutional analysis
echo.

cd backend
call venv\Scripts\activate.bat

echo Checking API keys...
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenAI:', '✓' if os.getenv('OPENAI_API_KEY') and len(os.getenv('OPENAI_API_KEY', '')) > 20 else '✗'); print('Claude:', '✓' if os.getenv('ANTHROPIC_API_KEY') and len(os.getenv('ANTHROPIC_API_KEY', '')) > 20 else '✗'); print('Nansen:', '✓' if os.getenv('NANSEN_API_KEY') else '✗'); print('Coinalyze:', '✓' if os.getenv('COINALYZE_API_KEY') else '✗')"

echo.
echo Starting server on http://localhost:8080
echo TradeBerg Chat: http://localhost:8080/tradeberg-chat
echo Press Ctrl+C to stop
echo.

python -m uvicorn open_webui.main:app --reload --port 8080 --host 0.0.0.0

pause
