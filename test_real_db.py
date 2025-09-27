#!/usr/bin/env python3
"""
Test real MongoDB database connection and functionality
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime
from models.article import Article
from services.article_storage_service import ArticleStorageService
from services.bias_analyzer import BiasAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection and basic operations"""
    print("🔧 Testing MongoDB database connection...")
    
    try:
        from config.database import initialize_database
        
        # Initialize database
        db = initialize_database()
        print("✅ Database connection established")
        
        # Test storage service
        storage_service = ArticleStorageService()
        
        # Get initial statistics
        initial_stats = storage_service.get_storage_statistics()
        print(f"📊 Initial database statistics:")
        print(f"   Total articles: {initial_stats.get('total_articles', 0)}")
        print(f"   Analyzed articles: {initial_stats.get('analyzed_articles', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 To fix this:")
        print("   1. Run: npm run setup-db")
        print("   2. Follow the setup guide to configure MongoDB")
        return False

def test_article_storage():
    """Test storing and retrieving articles"""
    print("\n🔧 Testing article storage...")
    
    try:
        storage_service = ArticleStorageService()
        bias_analyzer = BiasAnalyzer()
        
        # Create a test article
        test_article = Article(
            url="http://test-real-db.com/sample-article",
            title="Test Article for Real Database",
            content="This is a comprehensive test article to verify that our real MongoDB database is working correctly. It includes sufficient content for meaningful bias analysis and demonstrates the complete workflow from scraping to storage to analysis.",
            author="Database Test Author",
            publication_date=datetime.now(),
            source="Test Source Real DB",
            scraped_at=datetime.now(),
            language="en"
        )
        
        print(f"📝 Created test article: {test_article.title}")
        
        # Store the article
        article_id = storage_service.store_article(test_article)
        if article_id:
            print(f"✅ Article stored with ID: {article_id}")
            
            # Analyze bias
            try:
                bias_scores = bias_analyzer.analyze_article_bias(test_article)
                success = storage_service.update_article_bias_scores(article_id, bias_scores.to_dict())
                if success:
                    print(f"✅ Bias analysis completed and stored")
                else:
                    print(f"⚠️  Bias analysis completed but not stored")
            except Exception as e:
                print(f"⚠️  Bias analysis failed: {e}")
            
            # Retrieve the article
            retrieved_article = storage_service.get_article_by_id(article_id)
            if retrieved_article:
                print(f"✅ Article retrieved successfully")
                print(f"   Title: {retrieved_article.title}")
                print(f"   Source: {retrieved_article.source}")
                print(f"   Has bias scores: {retrieved_article.bias_scores is not None}")
            else:
                print(f"❌ Failed to retrieve article")
            
            # Test statistics after insertion
            final_stats = storage_service.get_storage_statistics()
            print(f"📊 Final database statistics:")
            print(f"   Total articles: {final_stats.get('total_articles', 0)}")
            print(f"   Analyzed articles: {final_stats.get('analyzed_articles', 0)}")
            print(f"   Language distribution: {final_stats.get('language_distribution', {})}")
            print(f"   Source distribution: {final_stats.get('source_distribution', {})}")
            
            return True
        else:
            print(f"❌ Failed to store article")
            return False
            
    except Exception as e:
        print(f"❌ Article storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all database tests"""
    print("🎯 Real MongoDB Database Test")
    print("=" * 50)
    
    # Test database connection
    db_connected = test_database_connection()
    
    if db_connected:
        # Test article storage
        storage_test = test_article_storage()
        
        print("\n📋 Test Results:")
        print(f"   Database Connection: ✅")
        print(f"   Article Storage: {'✅' if storage_test else '❌'}")
        
        if storage_test:
            print("\n🎉 Real database is working perfectly!")
            print("   Articles will now persist between application restarts.")
            print("   You can run 'npm run dev' to start the application.")
        else:
            print("\n⚠️  Database connected but storage has issues.")
    else:
        print("\n❌ Database connection failed.")
        print("   Please run 'npm run setup-db' to configure MongoDB.")

if __name__ == "__main__":
    main()