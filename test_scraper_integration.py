#!/usr/bin/env python3
"""
Test script to verify scraper integration and article storage
"""

import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.scraper_manager import ScraperManager
from services.article_storage_service import ArticleStorageService
from services.bias_analyzer import BiasAnalyzer
from config.database import initialize_database

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_scraper_integration():
    """Test the complete scraper integration"""
    print("=" * 60)
    print("TESTING SCRAPER INTEGRATION")
    print("=" * 60)
    
    try:
        # Initialize database
        print("\n1. Initializing database...")
        initialize_database()
        print("✓ Database initialized")
        
        # Initialize services
        print("\n2. Initializing services...")
        scraper_manager = ScraperManager()
        storage_service = ArticleStorageService()
        bias_analyzer = BiasAnalyzer()
        print("✓ Services initialized")
        
        # Test available sources
        print("\n3. Testing available sources...")
        sources = scraper_manager.get_available_sources()
        print(f"✓ Available sources: {sources}")
        
        # Test scraping from one source
        print("\n4. Testing source scraping...")
        if sources:
            test_source = sources[0]  # Use first available source
            print(f"Testing scraping from: {test_source}")
            
            articles = scraper_manager.scrape_source(test_source, limit=2)
            print(f"✓ Scraped {len(articles)} articles from {test_source}")
            
            if articles:
                # Test article storage
                print("\n5. Testing article storage...")
                stored_count = 0
                analyzed_count = 0
                
                for i, article in enumerate(articles):
                    print(f"  Processing article {i+1}: {article.title[:50]}...")
                    
                    # Store article
                    article_id = storage_service.store_article(article)
                    if article_id:
                        stored_count += 1
                        print(f"    ✓ Stored with ID: {article_id}")
                        
                        # Analyze bias
                        try:
                            bias_scores = bias_analyzer.analyze_article_bias(article)
                            success = storage_service.update_article_bias_scores(article_id, bias_scores.to_dict())
                            if success:
                                analyzed_count += 1
                                print(f"    ✓ Bias analysis completed")
                                print(f"      - Political bias: {bias_scores.political_bias:.2f}")
                                print(f"      - Sentiment: {bias_scores.sentiment_score:.2f}")
                                print(f"      - Overall bias: {bias_scores.overall_bias_score:.2f}")
                            else:
                                print(f"    ✗ Failed to update bias scores")
                        except Exception as e:
                            print(f"    ✗ Bias analysis failed: {e}")
                    else:
                        print(f"    ✗ Failed to store article")
                
                print(f"\n✓ Storage test complete: {stored_count}/{len(articles)} stored, {analyzed_count} analyzed")
            else:
                print("✗ No articles scraped")
        else:
            print("✗ No sources available")
        
        # Test storage statistics
        print("\n6. Testing storage statistics...")
        stats = storage_service.get_storage_statistics()
        print(f"✓ Total articles in database: {stats.get('total_articles', 0)}")
        print(f"✓ Analyzed articles: {stats.get('analyzed_articles', 0)}")
        print(f"✓ Recent articles: {stats.get('recent_articles', 0)}")
        
        # Test URL scraping
        print("\n7. Testing URL scraping...")
        test_urls = [
            "https://www.thedailystar.net/news/bangladesh",
            "https://www.prothomalo.com/bangladesh",
        ]
        
        from scrapers.base_scraper import BaseScraper
        
        class GenericScraper(BaseScraper):
            def __init__(self):
                super().__init__("generic", "")
            
            def _get_article_urls(self, max_articles: int):
                return []
            
            def _extract_article_content(self, soup, url):
                return None
        
        scraper = GenericScraper()
        
        for url in test_urls:
            try:
                print(f"  Testing URL: {url}")
                article = scraper.scrape_single_url(url)
                if article:
                    print(f"    ✓ Successfully scraped: {article.title[:50]}...")
                    print(f"    ✓ Content length: {len(article.content)} characters")
                    print(f"    ✓ Language: {article.language}")
                else:
                    print(f"    ✗ Failed to scrape URL")
            except Exception as e:
                print(f"    ✗ URL scraping failed: {e}")
        
        print("\n" + "=" * 60)
        print("INTEGRATION TEST COMPLETE")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test API endpoints"""
    print("\n" + "=" * 60)
    print("TESTING API ENDPOINTS")
    print("=" * 60)
    
    try:
        import requests
        
        base_url = "http://localhost:5000/api"
        
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health endpoint working")
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
        
        # Test scraper sources endpoint
        print("\n2. Testing scraper sources endpoint...")
        response = requests.get(f"{base_url}/scrape/sources", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Sources endpoint working: {data.get('sources', [])}")
        else:
            print(f"✗ Sources endpoint failed: {response.status_code}")
        
        # Test articles endpoint
        print("\n3. Testing articles endpoint...")
        response = requests.get(f"{base_url}/articles?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Articles endpoint working: {data.get('count', 0)} articles")
        else:
            print(f"✗ Articles endpoint failed: {response.status_code}")
        
        # Test statistics endpoint
        print("\n4. Testing statistics endpoint...")
        response = requests.get(f"{base_url}/statistics/overview", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Statistics endpoint working: {data.get('total_articles', 0)} total articles")
        else:
            print(f"✗ Statistics endpoint failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to API server. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"✗ API test failed: {e}")
        return False


if __name__ == "__main__":
    print("Media Bias Detector - Scraper Integration Test")
    print(f"Started at: {datetime.now()}")
    
    # Test scraper integration
    integration_success = test_scraper_integration()
    
    # Test API endpoints (optional - only if server is running)
    print("\nWould you like to test API endpoints? (Server must be running)")
    print("Press Enter to skip, or type 'y' to test:")
    user_input = input().strip().lower()
    
    if user_input == 'y':
        api_success = test_api_endpoints()
    else:
        api_success = True
        print("Skipping API tests")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Integration Test: {'✓ PASSED' if integration_success else '✗ FAILED'}")
    if user_input == 'y':
        print(f"API Test: {'✓ PASSED' if api_success else '✗ FAILED'}")
    
    if integration_success and (api_success or user_input != 'y'):
        print("\n🎉 All tests passed! The scraper integration is working correctly.")
        print("\nNext steps:")
        print("1. Start the backend server: python api/app.py")
        print("2. Start the frontend: cd frontend && npm start")
        print("3. Test the manual scraper in the web interface")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    print(f"\nCompleted at: {datetime.now()}")