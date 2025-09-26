# Media Bias Detector - Start Both Services

Write-Host "Media Bias Detector - Local Development Setup" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Start backend in a new PowerShell window
Write-Host "Starting Flask backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python run_backend.py"

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend in a new PowerShell window
Write-Host "Starting React frontend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"

Write-Host ""
Write-Host "Both services are starting!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Close both PowerShell windows to stop the services" -ForegroundColor Yellow
Write-Host "Manual scraper available at: http://localhost:3000/scraper" -ForegroundColor Magenta

# Keep this window open
Read-Host "Press Enter to exit this launcher"