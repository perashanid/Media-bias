#!/bin/bash

# Development startup script

echo "Starting Media Bias Detector in development mode..."

# Install frontend dependencies if needed
if [ ! -d "/app/frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd /app/frontend && npm install
fi

# Start React development server in background
echo "Starting React development server..."
cd /app/frontend && npm start &

# Wait a moment for React to start
sleep 5

# Start Flask development server
echo "Starting Flask development server..."
cd /app && python api/app.py