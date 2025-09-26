# Media Bias Detector - Local Development Startup Script

Write-Host "🎯 Media Bias Detector - Local Development Setup" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Function to start backend
function Start-Backend {
    Write-Host "🚀 Starting Flask backend on http://localhost:5000" -ForegroundColor Green
    try {
        python api/app.py
    }
    catch {
        Write-Host "❌ Backend error: $_" -ForegroundColor Red
    }
}

# Function to start frontend
function Start-Frontend {
    Write-Host "🚀 Starting React frontend on http://localhost:3000" -ForegroundColor Green
    try {
        Set-Location frontend
        
        # Check if node_modules exists
        if (!(Test-Path "node_modules")) {
            Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
            npm install
        }
        
        # Start React development server
        npm start
    }
    catch {
        Write-Host "❌ Frontend error: $_" -ForegroundColor Red
    }
    finally {
        Set-Location ..
    }
}

# Start backend in background
Write-Host "🔧 Starting backend server..." -ForegroundColor Yellow
Start-Job -ScriptBlock { 
    Set-Location $using:PWD
    python api/app.py 
} -Name "Backend"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "📱 Starting frontend development server..." -ForegroundColor Yellow
Write-Host "🌐 Access the application at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 API backend available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Press Ctrl+C to stop both services" -ForegroundColor Yellow
Write-Host ""

# Start frontend (this will block and open browser)
Start-Frontend

# Cleanup
Write-Host "🛑 Shutting down services..." -ForegroundColor Yellow
Stop-Job -Name "Backend" -ErrorAction SilentlyContinue
Remove-Job -Name "Backend" -ErrorAction SilentlyContinue