# Perplexity Trading Bot Startup Script
Write-Host "Starting Perplexity Trading Bot (Isolated Service)..." -ForegroundColor Green
Write-Host ""

# Change to the perplexity_bot directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$botPath = Join-Path $scriptPath "perplexity_bot"
Set-Location $botPath

Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow

# Check Python
Write-Host "Checking Python environment..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found! Please install Python 3.8+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install dependencies!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Starting Perplexity Trading Bot on port 8001..." -ForegroundColor Green
Write-Host "Service will be available at: http://localhost:8001" -ForegroundColor Yellow
Write-Host "API endpoints:" -ForegroundColor Yellow
Write-Host "  - Health: http://localhost:8001/health" -ForegroundColor White
Write-Host "  - Chat: http://localhost:8001/api/chat" -ForegroundColor White
Write-Host "  - Models: http://localhost:8001/api/models" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Magenta
Write-Host ""

# Start the service
python main.py
