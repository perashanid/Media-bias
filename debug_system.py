#!/usr/bin/env python3
"""
Debug the entire system to identify issues
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
import requests
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database():
    """Test database connection"""
    try:
        from config.database import initialize_database
        from services.article_storage_service import ArticleStorageService
        
        print("🔧 Testing database connection...")
        db = initialize_database()
        
        storage_service = ArticleStorageService()
        stats = storage_service.get_storage_statistics()
        print(f"✅ Database working. Stats: {stats}")
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_scrapers():
    """Test scraper functionality"""
    try:
        from scrapers.scraper_manager import ScraperManager
        
        print("🔧 Testing scrapers...")
        scraper_manager = ScraperManager()
        sources = scraper_manager.get_available_sources()
        print(f"✅ Scrapers working. Sources: {sources}")
        return True
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False

def test_bias_analyzer():
    """Test bias analyzer"""
    try:
        from services.bias_analyzer import BiasAnalyzer
        from models.article import Article
        from datetime import datetime
        
        print("🔧 Testing bias analyzer...")
        analyzer = BiasAnalyzer()
        
        # Create a test article
        test_article = Article(
            url="http://test.com",
            title="Test Article",
            content="This is a test article content for bias analysis.",
            author="Test Author",
            publication_date=datetime.now(),
            source="Test Source",
            scraped_at=datetime.now(),
            language="en"
        )
        
        bias_scores = analyzer.analyze_article_bias(test_article)
        print(f"✅ Bias analyzer working. Scores: {bias_scores.to_dict()}")
        return True
    except Exception as e:
        print(f"❌ Bias analyzer test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    base_url = "http://localhost:5000"
    
    endpoints = [
        "/health",
        "/api/statistics/overview",
        "/api/articles",
        "/api/scrape/sources"
    ]
    
    print("🔧 Testing API endpoints...")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def main():
    """Run all tests"""
    print("🎯 System Debug - Testing All Components")
    print("=" * 50)
    
    # Test components
    db_ok = test_database()
    scrapers_ok = test_scrapers()
    analyzer_ok = test_bias_analyzer()
    
    print("\n🌐 Testing API endpoints (make sure backend is running)...")
    test_api_endpoints()
    
    print("\n📋 Summary:")
    print(f"Database: {'✅' if db_ok else '❌'}")
    print(f"Scrapers: {'✅' if scrapers_ok else '❌'}")
    print(f"Bias Analyzer: {'✅' if analyzer_ok else '❌'}")
    
    if all([db_ok, scrapers_ok, analyzer_ok]):
        print("\n🎉 All core components are working!")
    else:
        print("\n⚠️  Some components have issues. Check the logs above.")

if __name__ == "__main__":
    main()