#!/usr/bin/env python3
"""
Database setup script for Media Bias Detector
"""

import os
import sys
from pathlib import Path

def setup_mongodb_atlas():
    """Guide user through MongoDB Atlas setup"""
    print("🔧 MongoDB Atlas Setup Guide")
    print("=" * 50)
    print()
    print("To use this application, you need a MongoDB database.")
    print("Here are your options:")
    print()
    print("1. 🌐 MongoDB Atlas (Cloud - Recommended)")
    print("   - Free tier available")
    print("   - No local installation required")
    print("   - Accessible from anywhere")
    print()
    print("2. 🏠 Local MongoDB Installation")
    print("   - Install MongoDB Community Server")
    print("   - Runs on your local machine")
    print()
    
    choice = input("Choose option (1 for Atlas, 2 for Local): ").strip()
    
    if choice == "1":
        setup_atlas()
    elif choice == "2":
        setup_local()
    else:
        print("Invalid choice. Please run the script again.")

def setup_atlas():
    """Setup MongoDB Atlas"""
    print("\n🌐 MongoDB Atlas Setup")
    print("-" * 30)
    print()
    print("1. Go to https://www.mongodb.com/atlas")
    print("2. Create a free account")
    print("3. Create a new cluster (choose the free tier)")
    print("4. Create a database user:")
    print("   - Username: your_username")
    print("   - Password: your_password")
    print("5. Add your IP address to the IP Access List")
    print("6. Get your connection string:")
    print("   - Click 'Connect' on your cluster")
    print("   - Choose 'Connect your application'")
    print("   - Copy the connection string")
    print()
    
    connection_string = input("Enter your MongoDB Atlas connection string: ").strip()
    
    if connection_string:
        # Update .env file
        env_path = Path(__file__).parent / ".env"
        
        env_content = f"""# Database Configuration - MongoDB Atlas
MONGODB_URI={connection_string}
DATABASE_NAME=media_bias_detector

# Flask Configuration
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=False

# Logging Configuration
LOG_LEVEL=INFO
"""
        
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Configuration saved to {env_path}")
        print()
        test_connection()
    else:
        print("❌ No connection string provided.")

def setup_local():
    """Setup local MongoDB"""
    print("\n🏠 Local MongoDB Setup")
    print("-" * 25)
    print()
    print("1. Download MongoDB Community Server:")
    print("   https://www.mongodb.com/try/download/community")
    print("2. Install MongoDB on your system")
    print("3. Start the MongoDB service")
    print("4. MongoDB will be available at: mongodb://localhost:27017/")
    print()
    
    # Update .env file for local MongoDB
    env_path = Path(__file__).parent / ".env"
    
    env_content = f"""# Database Configuration - Local MongoDB
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=media_bias_detector

# Flask Configuration
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=False

# Logging Configuration
LOG_LEVEL=INFO
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Configuration saved to {env_path}")
    print()
    test_connection()

def test_connection():
    """Test the database connection"""
    print("🔧 Testing database connection...")
    
    try:
        # Add project root to Python path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from config.database import initialize_database
        
        db = initialize_database()
        print("✅ Database connection successful!")
        print()
        print("🎉 Setup complete! You can now run:")
        print("   npm run dev")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print()
        print("Please check your configuration and try again.")
        print("Common issues:")
        print("- Incorrect connection string")
        print("- Network connectivity issues")
        print("- Database user permissions")

def main():
    """Main setup function"""
    print("🎯 Media Bias Detector - Database Setup")
    print("=" * 50)
    
    # Check if .env already exists
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        print("⚠️  .env file already exists.")
        overwrite = input("Do you want to reconfigure? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    setup_mongodb_atlas()

if __name__ == "__main__":
    main()