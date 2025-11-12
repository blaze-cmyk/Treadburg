# TradeBerg Startup Script
# Handles memory issues and provides easy startup

param(
    [Parameter()]
    [ValidateSet('backend', 'frontend', 'both', 'build', 'test')]
    [string]$Mode = 'menu'
)

function Show-Menu {
    Clear-Host
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "   TRADEBERG STARTUP MANAGER" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "[1] Start Backend Only (Port 8080)" -ForegroundColor Yellow
    Write-Host "[2] Start Frontend Dev Server (Port 5173)" -ForegroundColor Yellow
    Write-Host "[3] Start Both (Backend + Frontend)" -ForegroundColor Yellow
    Write-Host "[4] Build Frontend for Production" -ForegroundColor Yellow
    Write-Host "[5] Test Backend Health" -ForegroundColor Yellow
    Write-Host "[6] Fix Memory Issues" -ForegroundColor Yellow
    Write-Host "[7] Exit" -ForegroundColor Yellow
    Write-Host ""
}

function Start-Backend {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   STARTING BACKEND" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    Set-Location backend
    
    # Activate virtual environment
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
        
        Write-Host "Starting Open WebUI backend..." -ForegroundColor Cyan
        python -m open_webui serve --port 8080
    } else {
        Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
        Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    }
}

function Start-Frontend {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   STARTING FRONTEND DEV SERVER" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    # Set Node.js memory to 8GB
    $env:NODE_OPTIONS = "--max-old-space-size=8192"
    Write-Host "✓ Node.js memory set to 8GB" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Starting Vite dev server..." -ForegroundColor Cyan
    npm run dev -- --host
}

function Start-Both {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   STARTING BOTH SERVICES" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    # Start Backend in new window
    Write-Host "Starting Backend in new window..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\venv\Scripts\Activate.ps1; python -m open_webui serve --port 8080"
    
    # Wait for backend to start
    Write-Host "Waiting 5 seconds for backend to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Start Frontend in new window
    Write-Host "Starting Frontend in new window..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:NODE_OPTIONS='--max-old-space-size=8192'; cd '$PWD'; npm run dev -- --host"
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   BOTH SERVICES STARTED!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Backend:  http://localhost:8080" -ForegroundColor Cyan
    Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press any key to return to menu..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Build-Frontend {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   BUILDING FRONTEND FOR PRODUCTION" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    # Set Node.js memory to 8GB
    $env:NODE_OPTIONS = "--max-old-space-size=8192"
    Write-Host "✓ Node.js memory set to 8GB" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Building... (this may take a few minutes)" -ForegroundColor Cyan
    npm run build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "   BUILD SUCCESSFUL!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Frontend built successfully." -ForegroundColor Green
        Write-Host "Access the app at: http://localhost:8080" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "   BUILD FAILED!" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please check the error messages above." -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Press any key to return to menu..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Test-BackendHealth {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   TESTING BACKEND HEALTH" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    try {
        Write-Host "Testing http://localhost:8080/api/tradeberg/metrics" -ForegroundColor Cyan
        Write-Host ""
        
        $response = Invoke-RestMethod -Uri "http://localhost:8080/api/tradeberg/metrics" -Method Get -TimeoutSec 5
        
        Write-Host "Backend is responding!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Health Status:" -ForegroundColor Cyan
        $response | ConvertTo-Json -Depth 3
        
    } catch {
        Write-Host "Backend is not responding." -ForegroundColor Red
        Write-Host "Make sure the backend is running." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Press any key to return to menu..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Fix-MemoryIssues {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   FIXING MEMORY ISSUES" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Applying fixes..." -ForegroundColor Cyan
    Write-Host ""
    
    # Set Node.js memory globally
    [System.Environment]::SetEnvironmentVariable('NODE_OPTIONS', '--max-old-space-size=8192', 'User')
    Write-Host "✓ Set NODE_OPTIONS globally to 8GB" -ForegroundColor Green
    
    # Clear npm cache
    Write-Host ""
    Write-Host "Clearing npm cache..." -ForegroundColor Cyan
    npm cache clean --force
    Write-Host "✓ npm cache cleared" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   FIXES APPLIED!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Please restart your terminal for changes to take effect." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to return to menu..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Main execution
if ($Mode -eq 'menu') {
    while ($true) {
        Show-Menu
        $choice = Read-Host "Enter your choice (1-7)"
        
        switch ($choice) {
            '1' { Start-Backend; break }
            '2' { Start-Frontend; break }
            '3' { Start-Both; continue }
            '4' { Build-Frontend; continue }
            '5' { Test-BackendHealth; continue }
            '6' { Fix-MemoryIssues; continue }
            '7' { Write-Host "Goodbye!"; exit }
            default { Write-Host "Invalid choice. Please try again." -ForegroundColor Red; Start-Sleep -Seconds 2 }
        }
    }
} else {
    switch ($Mode) {
        'backend' { Start-Backend }
        'frontend' { Start-Frontend }
        'both' { Start-Both }
        'build' { Build-Frontend }
        'test' { Test-BackendHealth }
    }
}
