#!/usr/bin/env python3
"""
Start both frontend and backend for local development
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path
import signal

# Global variables to track processes
backend_process = None
frontend_process = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down services...")
    
    if backend_process:
        backend_process.terminate()
        print("   Backend stopped")
    
    if frontend_process:
        frontend_process.terminate()
        print("   Frontend stopped")
    
    sys.exit(0)

def run_backend():
    """Run the Flask backend using the proper runner"""
    global backend_process
    print("🚀 Starting Flask backend on http://localhost:5000")
    
    try:
        # Use the proper backend runner
        backend_process = subprocess.Popen(
            [sys.executable, "run_backend.py"],
            cwd=Path(__file__).parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Print backend output
        for line in backend_process.stdout:
            print(f"[Backend] {line.strip()}")
            
    except Exception as e:
        print(f"❌ Backend error: {e}")

def run_frontend():
    """Run the React frontend"""
    global frontend_process
    print("🚀 Starting React frontend on http://localhost:3000")
    
    try:
        frontend_dir = Path(__file__).parent / "frontend"
        
        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            install_process = subprocess.run(
                ["npm", "install"], 
                cwd=frontend_dir, 
                check=True,
                capture_output=True,
                text=True
            )
            print("✅ Dependencies installed")
        
        # Start React development server
        frontend_process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Print frontend output
        for line in frontend_process.stdout:
            print(f"[Frontend] {line.strip()}")
            
    except Exception as e:
        print(f"❌ Frontend error: {e}")

def main():
    """Main function to start both services"""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🎯 Media Bias Detector - Local Development Setup")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    print("⏳ Waiting for backend to initialize...")
    time.sleep(5)
    
    # Test backend health
    try:
        import requests
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy and ready")
        else:
            print("⚠️  Backend started but health check failed")
    except:
        print("⚠️  Backend health check failed, but continuing...")
    
    print("\n📱 Starting frontend...")
    print("🌐 Application will be available at: http://localhost:3000")
    print("🔧 API backend available at: http://localhost:5000")
    print("\n💡 Press Ctrl+C to stop both services")
    print("=" * 50)
    
    try:
        # Start frontend (this will block)
        run_frontend()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()