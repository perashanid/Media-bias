#!/usr/bin/env python3
"""
Initialize and test database connection
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.database import initialize_database, get_articles_collection
from services.article_storage_service import ArticleStorageService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize database and test basic operations"""
    try:
        print("🔧 Initializing database connection...")
        
        # Initialize database
        db = initialize_database()
        print("✅ Database connection established")
        
        # Test articles collection
        articles_collection = get_articles_collection()
        count = articles_collection.count_documents({})
        print(f"📊 Current articles in database: {count}")
        
        # Test storage service
        storage_service = ArticleStorageService()
        stats = storage_service.get_storage_statistics()
        print(f"📈 Storage statistics: {stats}")
        
        print("✅ Database initialization complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        print("⚠️  Database initialization failed, please check MongoDB connection")
        return False

if __name__ == "__main__":
    main()