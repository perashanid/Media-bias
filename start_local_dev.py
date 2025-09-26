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

def run_backend():
    """Run the Flask backend"""
    print("🚀 Starting Flask backend on http://localhost:5000")
    try:
        # Change to project root directory
        os.chdir(Path(__file__).parent)
        
        # Run Flask app
        subprocess.run([sys.executable, "api/app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped")
    except Exception as e:
        print(f"❌ Backend error: {e}")

def run_frontend():
    """Run the React frontend"""
    print("🚀 Starting React frontend on http://localhost:3000")
    try:
        # Change to frontend directory
        frontend_dir = Path(__file__).parent / "frontend"
        os.chdir(frontend_dir)
        
        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], check=True)
        
        # Start React development server
        subprocess.run(["npm", "start"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

def main():
    """Main function to start both services"""
    print("🎯 Media Bias Detector - Local Development Setup")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(3)
    
    print("\n📱 Frontend will start in a new window...")
    print("🌐 Access the application at: http://localhost:3000")
    print("🔧 API backend available at: http://localhost:5000")
    print("\n💡 Press Ctrl+C to stop both services")
    
    try:
        # Start frontend (this will block)
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")

if __name__ == "__main__":
    main()