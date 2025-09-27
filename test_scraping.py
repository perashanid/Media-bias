#!/usr/bin/env python3
"""
Test scraping functionality
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapers.scraper_manager import ScraperManager
from services.article_storage_service import ArticleStorageService
from services.bias_analyzer import BiasAnalyzer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scraping():
    """Test the scraping functionality"""
    try:
        print("🔧 Testing scraping functionality...")
        
        # Initialize services
        scraper_manager = ScraperManager()
        storage_service = ArticleStorageService()
        bias_analyzer = BiasAnalyzer()
        
        # Get available sources
        sources = scraper_manager.get_available_sources()
        print(f"📰 Available sources: {sources}")
        
        if not sources:
            print("❌ No sources available")
            return False
        
        # Test scraping from first source
        test_source = sources[0]
        print(f"🔍 Testing scraping from: {test_source}")
        
        articles = scraper_manager.scrape_source(test_source, limit=2)
        print(f"📄 Scraped {len(articles)} articles")
        
        if articles:
            # Test storing articles
            for i, article in enumerate(articles):
                print(f"💾 Storing article {i+1}: {article.title[:50]}...")
                article_id = storage_service.store_article(article)
                if article_id:
                    print(f"✅ Stored with ID: {article_id}")
                    
                    # Test bias analysis
                    try:
                        bias_scores = bias_analyzer.analyze_article_bias(article)
                        storage_service.update_article_bias_scores(article_id, bias_scores.to_dict())
                        print(f"🧠 Bias analysis completed")
                    except Exception as e:
                        print(f"⚠️  Bias analysis failed: {e}")
                else:
                    print(f"❌ Failed to store article")
        
        # Test storage statistics
        stats = storage_service.get_storage_statistics()
        print(f"📊 Storage statistics: {stats}")
        
        print("✅ Scraping test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Scraping test failed: {e}")
        return False

if __name__ == "__main__":
    test_scraping()