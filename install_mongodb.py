#!/usr/bin/env python3
"""
Install MongoDB locally on Windows
"""

import subprocess
import sys
import os
from pathlib import Path

def install_mongodb_windows():
    """Install MongoDB on Windows using chocolatey or direct download"""
    print("🔧 Installing MongoDB locally on Windows...")
    print("=" * 50)
    
    # Check if chocolatey is available
    try:
        subprocess.run(['choco', '--version'], check=True, capture_output=True)
        print("✅ Chocolatey found. Installing MongoDB...")
        
        # Install MongoDB using chocolatey
        result = subprocess.run([
            'choco', 'install', 'mongodb', '-y'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ MongoDB installed successfully via Chocolatey!")
            return True
        else:
            print("❌ Chocolatey installation failed")
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Chocolatey not found. Trying alternative method...")
    
    # Alternative: Download and install manually
    print("\n📥 Manual MongoDB Installation Guide:")
    print("1. Go to: https://www.mongodb.com/try/download/community")
    print("2. Select 'Windows' and download the MSI installer")
    print("3. Run the installer with default settings")
    print("4. MongoDB will be installed as a Windows service")
    print("5. It will be available at: mongodb://localhost:27017/")
    print()
    
    choice = input("Have you installed MongoDB manually? (y/N): ").strip().lower()
    return choice == 'y'

def start_mongodb_service():
    """Start MongoDB service on Windows"""
    print("\n🚀 Starting MongoDB service...")
    
    try:
        # Try to start MongoDB service
        result = subprocess.run([
            'net', 'start', 'MongoDB'
        ], capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print("✅ MongoDB service started successfully!")
            return True
        else:
            print("⚠️  MongoDB service may already be running or needs manual start")
            print("   Try running: net start MongoDB")
            return True
            
    except Exception as e:
        print(f"⚠️  Could not start MongoDB service: {e}")
        print("   MongoDB might already be running")
        return True

def test_local_connection():
    """Test local MongoDB connection"""
    print("\n🔧 Testing local MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        print("✅ Local MongoDB connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Local MongoDB connection failed: {e}")
        return False

def update_env_file():
    """Update .env file to use local MongoDB"""
    print("\n📝 Updating configuration for local MongoDB...")
    
    env_content = """# Database Configuration - Local MongoDB
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=media_bias_detector

# Flask Configuration
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=False

# Logging Configuration
LOG_LEVEL=INFO
"""
    
    env_path = Path(__file__).parent / ".env"
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Configuration updated: {env_path}")

def main():
    """Main installation function"""
    print("🎯 MongoDB Local Installation")
    print("=" * 50)
    
    # Install MongoDB
    installed = install_mongodb_windows()
    
    if installed:
        # Start MongoDB service
        start_mongodb_service()
        
        # Update configuration
        update_env_file()
        
        # Test connection
        if test_local_connection():
            print("\n🎉 MongoDB setup complete!")
            print("   You can now run: npm run dev")
        else:
            print("\n⚠️  MongoDB installed but connection test failed")
            print("   Try restarting your computer and run the test again")
    else:
        print("\n❌ MongoDB installation incomplete")
        print("   Please install MongoDB manually and run this script again")

if __name__ == "__main__":
    main()