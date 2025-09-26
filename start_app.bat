@echo off
echo 🎯 Media Bias Detector - Local Development Setup
echo ==================================================

echo 🚀 Starting Flask backend...
start "Backend" cmd /k "python run_backend.py"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo 🚀 Starting React frontend...
cd frontend
start "Frontend" cmd /k "npm start"
cd ..

echo ✅ Both services are starting!
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend: http://localhost:5000
echo.
echo 💡 Close both command windows to stop the services
pause