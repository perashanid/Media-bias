#!/usr/bin/env python3
"""Test MongoDB Atlas connection"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

def test_connection():
    # Load environment variables
    load_dotenv()
    
    mongo_uri = os.getenv('MONGODB_URI')
    database_name = os.getenv('DATABASE_NAME')
    
    print(f"MongoDB URI: {mongo_uri}")
    print(f"Database Name: {database_name}")
    
    if not mongo_uri or mongo_uri == 'mongodb://localhost:27017/':
        print("ERROR: MongoDB URI not loaded from .env file")
        return False
    
    try:
        # For MongoDB Atlas, append database name to URI if not present
        if 'mongodb+srv://' in mongo_uri and not mongo_uri.endswith('/'):
            full_uri = f"{mongo_uri}{database_name}"
        else:
            full_uri = mongo_uri
            
        print(f"Full URI: {full_uri}")
        
        # Create MongoDB client
        client = MongoClient(full_uri, serverSelectionTimeoutMS=10000)
        
        # Test connection
        client.admin.command('ping')
        print("✓ MongoDB Atlas connection successful!")
        
        # Test database access
        db = client[database_name]
        collections = db.list_collection_names()
        print(f"✓ Database '{database_name}' accessible")
        print(f"✓ Collections: {collections}")
        
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()