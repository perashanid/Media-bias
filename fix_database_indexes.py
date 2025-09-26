#!/usr/bin/env python3
"""
Script to fix database indexes and resolve language override issues
"""

import sys
import os
import logging
from pymongo import ASCENDING

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import get_database, get_articles_collection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fix_database_indexes():
    """Fix database indexes to resolve language override issues"""
    print("=" * 60)
    print("FIXING DATABASE INDEXES")
    print("=" * 60)
    
    try:
        # Initialize database connection
        print("1. Connecting to database...")
        db = get_database()
        articles_collection = get_articles_collection()
        print("✅ Database connection established")
        
        # List current indexes
        print("\n2. Current indexes:")
        indexes = list(articles_collection.list_indexes())
        for idx in indexes:
            print(f"   - {idx['name']}: {idx.get('key', {})}")
        
        # Drop problematic indexes
        print("\n3. Dropping problematic indexes...")
        try:
            # Drop text index if it exists
            articles_collection.drop_index("title_text_content_text")
            print("   ✅ Dropped text index")
        except Exception as e:
            print(f"   ⚠️  Text index not found or already dropped: {e}")
        
        try:
            # Drop language index if it exists and is causing issues
            articles_collection.drop_index("language_1")
            print("   ✅ Dropped language index")
        except Exception as e:
            print(f"   ⚠️  Language index not found or already dropped: {e}")
        
        # Recreate safe indexes
        print("\n4. Creating safe indexes...")
        
        # Basic indexes without language constraints
        safe_indexes = [
            ([("url", ASCENDING)], {"unique": True, "name": "url_unique"}),
            ([("content_hash", ASCENDING)], {"unique": True, "name": "content_hash_unique"}),
            ([("source", ASCENDING)], {"name": "source_index"}),
            ([("publication_date", ASCENDING)], {"name": "publication_date_index"}),
            ([("scraped_at", ASCENDING)], {"name": "scraped_at_index"}),
        ]
        
        for index_spec, options in safe_indexes:
            try:
                articles_collection.create_index(index_spec, **options)
                print(f"   ✅ Created index: {options['name']}")
            except Exception as e:
                print(f"   ⚠️  Index {options['name']} already exists or failed: {e}")
        
        # Create a simple language index without text search constraints
        try:
            articles_collection.create_index([("language", ASCENDING)], name="language_simple")
            print("   ✅ Created simple language index")
        except Exception as e:
            print(f"   ⚠️  Simple language index failed: {e}")
        
        # List final indexes
        print("\n5. Final indexes:")
        indexes = list(articles_collection.list_indexes())
        for idx in indexes:
            print(f"   - {idx['name']}: {idx.get('key', {})}")
        
        print("\n✅ Database indexes fixed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to fix database indexes: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_article_storage():
    """Test article storage after fixing indexes"""
    print("\n" + "=" * 60)
    print("TESTING ARTICLE STORAGE")
    print("=" * 60)
    
    try:
        from models.article import Article
        from services.article_storage_service import ArticleStorageService
        from datetime import datetime
        
        storage_service = ArticleStorageService()
        
        # Test with Bengali article
        print("1. Testing Bengali article storage...")
        bengali_article = Article(
            title="বাংলা নিবন্ধ পরীক্ষা",
            content="এটি একটি বাংলা নিবন্ধ যা পরীক্ষার জন্য তৈরি করা হয়েছে। এতে রাজনীতি এবং সংবাদ সম্পর্কিত বিষয়বস্তু রয়েছে।",
            url="http://test.com/bengali-article",
            source="test_source",
            publication_date=datetime.now(),
            scraped_at=datetime.now(),
            language="bengali",
            author="Test Author"
        )
        
        article_id = storage_service.store_article(bengali_article)
        if article_id:
            print(f"   ✅ Bengali article stored successfully: {article_id}")
            
            # Test retrieval
            retrieved = storage_service.get_article_by_id(article_id)
            if retrieved:
                print(f"   ✅ Bengali article retrieved successfully")
            else:
                print(f"   ❌ Failed to retrieve Bengali article")
        else:
            print(f"   ❌ Failed to store Bengali article")
        
        # Test with English article
        print("\n2. Testing English article storage...")
        english_article = Article(
            title="English Article Test",
            content="This is an English article created for testing purposes. It contains political and news-related content.",
            url="http://test.com/english-article",
            source="test_source",
            publication_date=datetime.now(),
            scraped_at=datetime.now(),
            language="english",
            author="Test Author"
        )
        
        article_id = storage_service.store_article(english_article)
        if article_id:
            print(f"   ✅ English article stored successfully: {article_id}")
            
            # Test retrieval
            retrieved = storage_service.get_article_by_id(article_id)
            if retrieved:
                print(f"   ✅ English article retrieved successfully")
            else:
                print(f"   ❌ Failed to retrieve English article")
        else:
            print(f"   ❌ Failed to store English article")
        
        # Test statistics
        print("\n3. Testing storage statistics...")
        stats = storage_service.get_storage_statistics()
        print(f"   Total articles: {stats.get('total_articles', 0)}")
        print(f"   Language distribution: {stats.get('language_distribution', {})}")
        
        print("\n✅ Article storage test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Article storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Database Index Fix and Storage Test")
    from datetime import datetime
    print(f"Started at: {datetime.now()}")
    
    # Fix database indexes
    index_fix_success = fix_database_indexes()
    
    # Test article storage
    if index_fix_success:
        storage_test_success = test_article_storage()
    else:
        storage_test_success = False
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Index Fix: {'✅ SUCCESS' if index_fix_success else '❌ FAILED'}")
    print(f"Storage Test: {'✅ SUCCESS' if storage_test_success else '❌ FAILED'}")
    
    if index_fix_success and storage_test_success:
        print("\n🎉 All fixes applied successfully! Storage should now work correctly.")
    else:
        print("\n❌ Some fixes failed. Please check the errors above.")
    
    print(f"\nCompleted at: {datetime.now()}")