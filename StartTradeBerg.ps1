# TradeBerg Simple Startup Script
# Fixed version without syntax errors

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   TRADEBERG STARTUP MANAGER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[1] Start Backend Only" -ForegroundColor Yellow
Write-Host "[2] Start Frontend Only" -ForegroundColor Yellow
Write-Host "[3] Start Both Services" -ForegroundColor Yellow
Write-Host "[4] Build Frontend" -ForegroundColor Yellow
Write-Host "[5] Test Backend" -ForegroundColor Yellow
Write-Host "[6] Exit" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "Enter your choice (1-6)"

switch ($choice) {
    '1' {
        Write-Host ""
        Write-Host "Starting Backend..." -ForegroundColor Green
        Set-Location backend
        & "venv\Scripts\Activate.ps1"
        python -m open_webui serve --port 8080
    }
    
    '2' {
        Write-Host ""
        Write-Host "Starting Frontend..." -ForegroundColor Green
        $env:NODE_OPTIONS = "--max-old-space-size=8192"
        Write-Host "Node memory set to 8GB" -ForegroundColor Cyan
        npm run dev -- --host
    }
    
    '3' {
        Write-Host ""
        Write-Host "Starting Both Services..." -ForegroundColor Green
        Write-Host ""
        
        # Start Backend
        Write-Host "Starting Backend in new window..." -ForegroundColor Cyan
        $backendPath = Join-Path $PWD "backend"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; .\venv\Scripts\Activate.ps1; python -m open_webui serve --port 8080"
        
        Start-Sleep -Seconds 3
        
        # Start Frontend
        Write-Host "Starting Frontend in new window..." -ForegroundColor Cyan
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; `$env:NODE_OPTIONS='--max-old-space-size=8192'; npm run dev -- --host"
        
        Write-Host ""
        Write-Host "Both services started!" -ForegroundColor Green
        Write-Host "Backend:  http://localhost:8080" -ForegroundColor Cyan
        Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
    }
    
    '4' {
        Write-Host ""
        Write-Host "Building Frontend..." -ForegroundColor Green
        $env:NODE_OPTIONS = "--max-old-space-size=8192"
        npm run build
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "Build successful!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "Build failed!" -ForegroundColor Red
        }
    }
    
    '5' {
        Write-Host ""
        Write-Host "Testing Backend..." -ForegroundColor Green
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8080/api/tradeberg/metrics" -Method Get -TimeoutSec 5
            Write-Host "Backend is responding!" -ForegroundColor Green
            $response | ConvertTo-Json
        } catch {
            Write-Host "Backend is not responding." -ForegroundColor Red
            Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    
    '6' {
        Write-Host "Goodbye!" -ForegroundColor Cyan
        exit
    }
    
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
