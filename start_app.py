#!/usr/bin/env python3
"""
Start both frontend and backend for local development
"""

import subprocess
import sys
import os
import time
import threading
import signal
from pathlib import Path

# Global variables to track processes
backend_process = None
frontend_process = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down services...")
    
    if backend_process:
        backend_process.terminate()
        print("✓ Backend stopped")
    
    if frontend_process:
        frontend_process.terminate()
        print("✓ Frontend stopped")
    
    sys.exit(0)

def run_backend():
    """Run the Flask backend"""
    global backend_process
    
    print("🚀 Starting Flask backend on http://localhost:5000")
    try:
        # Change to project root directory
        project_root = Path(__file__).parent
        os.chdir(project_root)
        
        # Add project root to Python path
        env = os.environ.copy()
        env['PYTHONPATH'] = str(project_root)
        
        # Run Flask app
        backend_process = subprocess.Popen([
            sys.executable, "-c", 
            """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from api.app import app
app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
"""
        ], env=env)
        
        backend_process.wait()
        
    except Exception as e:
        print(f"❌ Backend error: {e}")

def run_frontend():
    """Run the React frontend"""
    global frontend_process
    
    print("🚀 Starting React frontend on http://localhost:3000")
    try:
        # Change to frontend directory
        frontend_dir = Path(__file__).parent / "frontend"
        
        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        
        # Start React development server
        env = os.environ.copy()
        env['BROWSER'] = 'none'  # Don't auto-open browser
        
        frontend_process = subprocess.Popen(
            ["npm", "start"], 
            cwd=frontend_dir,
            env=env
        )
        
        frontend_process.wait()
        
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
    print("⏳ Waiting for backend to start...")
    time.sleep(5)
    
    # Test backend connection
    try:
        import requests
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Backend is running successfully")
        else:
            print("⚠️ Backend may not be fully ready")
    except:
        print("⚠️ Backend connection test failed, but continuing...")
    
    print("\n📱 Starting frontend...")
    print("🌐 Access the application at: http://localhost:3000")
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