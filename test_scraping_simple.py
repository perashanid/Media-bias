#!/usr/bin/env python3
"""
Simple test of scraping functionality without API calls
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
from scrapers.scraper_manager import ScraperManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_scraping():
    """Test scraping directly without API"""
    print("🔧 Testing direct scraping and storage...")
    
    try:
        # Initialize services
        storage_service = ArticleStorageService()
        bias_analyzer = BiasAnalyzer()
        scraper_manager = ScraperManager()
        
        # Create a test article
        test_article = Article(
            url="http://test-article.com/sample",
            title="Test Article for Storage",
            content="This is a test article content to verify that our storage system is working properly. It contains enough text to be meaningful for bias analysis.",
            author="Test Author",
            publication_date=datetime.now(),
            source="Test Source",
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
                print(f"✅ Article retrieved successfully: {retrieved_article.title}")
            else:
                print(f"❌ Failed to retrieve article")
            
            # Test statistics
            stats = storage_service.get_storage_statistics()
            print(f"📊 Storage statistics: {stats}")
            
            return True
        else:
            print(f"❌ Failed to store article")
            return False
            
    except Exception as e:
        print(f"❌ Direct scraping test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_scraping():
    """Test scraping from a real source"""
    print("\n🔧 Testing real source scraping...")
    
    try:
        scraper_manager = ScraperManager()
        storage_service = ArticleStorageService()
        bias_analyzer = BiasAnalyzer()
        
        # Get available sources
        sources = scraper_manager.get_available_sources()
        print(f"📰 Available sources: {sources}")
        
        if not sources:
            print("❌ No sources available")
            return False
        
        # Try to scrape from first source
        test_source = sources[0]
        print(f"🔍 Attempting to scrape from: {test_source}")
        
        articles = scraper_manager.scrape_source(test_source, limit=2)
        print(f"📄 Scraped {len(articles)} articles")
        
        if articles:
            stored_count = 0
            for i, article in enumerate(articles):
                print(f"💾 Storing article {i+1}: {article.title[:50]}...")
                article_id = storage_service.store_article(article)
                if article_id:
                    stored_count += 1
                    print(f"   ✅ Stored with ID: {article_id}")
                    
                    # Try bias analysis
                    try:
                        bias_scores = bias_analyzer.analyze_article_bias(article)
                        storage_service.update_article_bias_scores(article_id, bias_scores.to_dict())
                        print(f"   🧠 Bias analysis completed")
                    except Exception as e:
                        print(f"   ⚠️  Bias analysis failed: {e}")
                else:
                    print(f"   ❌ Failed to store article")
            
            print(f"✅ Successfully stored {stored_count}/{len(articles)} articles")
            
            # Check final statistics
            stats = storage_service.get_storage_statistics()
            print(f"📊 Final statistics: {stats}")
            
            return stored_count > 0
        else:
            print("❌ No articles scraped")
            return False
            
    except Exception as e:
        print(f"❌ Real scraping test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🎯 Simple Scraping Test")
    print("=" * 50)
    
    # Test direct storage
    direct_test = test_direct_scraping()
    
    # Test real scraping
    real_test = test_real_scraping()
    
    print("\n📋 Test Results:")
    print(f"   Direct Storage: {'✅' if direct_test else '❌'}")
    print(f"   Real Scraping: {'✅' if real_test else '❌'}")
    
    if direct_test and real_test:
        print("\n🎉 All tests passed! The scraping and storage system is working.")
    elif direct_test:
        print("\n⚠️  Storage works, but real scraping may have issues.")
    else:
        print("\n❌ Storage system has issues.")

if __name__ == "__main__":
    main()