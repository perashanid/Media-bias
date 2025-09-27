#!/bin/bash

# Render build script for Modern Media Bias Detector

set -e  # Exit on any error

echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Build frontend
echo "🏗️ Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Verify build
if [ -d "frontend/build" ]; then
    echo "✅ Frontend build successful!"
    echo "📁 Build directory contents:"
    ls -la frontend/build/
else
    echo "❌ Frontend build failed!"
    exit 1
fi

echo "🎉 Build completed successfully!"