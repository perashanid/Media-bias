# Media Bias Detector - Start Both Services

Write-Host "Media Bias Detector - Local Development Setup" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Function to start backend
function Start-Backend {
    Write-Host "Starting Flask backend on http://localhost:5000" -ForegroundColor Green
    try {
        python run_backend.py
    }
    catch {
        Write-Host "Backend error: $_" -ForegroundColor Red
    }
}

# Function to start frontend
function Start-Frontend {
    Write-Host "Starting React frontend on http://localhost:3000" -ForegroundColor Green
    try {
        Set-Location frontend
        
        # Check if node_modules exists
        if (!(Test-Path "node_modules")) {
            Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
            npm install
        }
        
        # Start React development server
        npm start
    }
    catch {
        Write-Host "Frontend error: $_" -ForegroundColor Red
    }
    finally {
        Set-Location ..
    }
}

# Start backend in background job
Write-Host "Starting backend server..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock { 
    Set-Location $using:PWD
    python run_backend.py 
} -Name "Backend"

# Wait for backend to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test backend health
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "Backend is healthy and ready" -ForegroundColor Green
    }
} catch {
    Write-Host "Backend health check failed, but continuing..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting frontend development server..." -ForegroundColor Yellow
Write-Host "Application will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API backend available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both services" -ForegroundColor Yellow
Write-Host "=" * 50 -ForegroundColor Cyan

# Start frontend (this will block and open browser)
try {
    Start-Frontend
} finally {
    # Cleanup
    Write-Host "Shutting down services..." -ForegroundColor Yellow
    Stop-Job -Name "Backend" -ErrorAction SilentlyContinue
    Remove-Job -Name "Backend" -ErrorAction SilentlyContinue
    Write-Host "Services stopped" -ForegroundColor Green
}