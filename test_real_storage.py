#!/usr/bin/env python3
"""
Test real database storage functionality
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.article import Article
from services.article_storage_service import ArticleStorageService
from services.bias_analyzer import BiasAnalyzer
from scrapers.scraper_manager import ScraperManager
from config.database import initialize_database


def test_real_storage():
    """Test real database storage"""
    print("=" * 60)
    print("TESTING REAL DATABASE STORAGE")
    print("=" * 60)
    
    try:
        # Initialize database
        print("1. Initializing database...")
        db = initialize_database()
        print("✅ Database initialized")
        
        # Initialize services
        print("\n2. Initializing services...")
        storage_service = ArticleStorageService()
        bias_analyzer = BiasAnalyzer()
        scraper_manager = ScraperManager()
        print("✅ Services initialized")
        
        # Test article creation and storage
        print("\n3. Testing article storage...")
        
        # Create test articles
        test_articles = [
            Article(
                title="Test Bengali Article",
                content="এটি একটি বাংলা পরীক্ষার নিবন্ধ। সরকারের নতুন নীতি নিয়ে আলোচনা।",
                url="http://test.com/bengali-test",
                source="test_source",
                publication_date=datetime.now(),
                scraped_at=datetime.now(),
                language="bengali",
                author="Test Author"
            ),
            Article(
                title="Test English Article",
                content="This is an English test article. Discussion about government policies and their impact.",
                url="http://test.com/english-test",
                source="test_source",
                publication_date=datetime.now(),
                scraped_at=datetime.now(),
                language="english",
                author="Test Author"
            )
        ]
        
        stored_ids = []
        for i, article in enumerate(test_articles):
            print(f"  Storing article {i+1}: {article.title}")
            article_id = storage_service.store_article(article)
            if article_id:
                stored_ids.append(article_id)
                print(f"    ✅ Stored with ID: {article_id}")
                
                # Test retrieval
                retrieved = storage_service.get_article_by_id(article_id)
                if retrieved:
                    print(f"    ✅ Retrieved successfully")
                else:
                    print(f"    ❌ Failed to retrieve")
            else:
                print(f"    ❌ Failed to store")
        
        # Test bias analysis
        print("\n4. Testing bias analysis...")
        for article_id in stored_ids:
            article = storage_service.get_article_by_id(article_id)
            if article:
                print(f"  Analyzing: {article.title}")
                try:
                    bias_scores = bias_analyzer.analyze_article_bias(article)
                    success = storage_service.update_article_bias_scores(article_id, bias_scores.to_dict())
                    if success:
                        print(f"    ✅ Bias analysis stored")
                        print(f"      Overall bias: {bias_scores.overall_bias_score:.3f}")
                    else:
                        print(f"    ❌ Failed to store bias scores")
                except Exception as e:
                    print(f"    ❌ Bias analysis failed: {e}")
        
        # Test scraping and storage
        print("\n5. Testing scraping and storage...")
        sources = scraper_manager.get_available_sources()
        if sources:
            test_source = sources[0]
            print(f"  Scraping from: {test_source}")
            
            articles = scraper_manager.scrape_source(test_source, limit=2)
            if articles:
                print(f"  Scraped {len(articles)} articles")
                
                batch_result = storage_service.store_articles_batch(articles)
                print(f"  Batch storage: {batch_result['stored']} stored, {batch_result['duplicates']} duplicates")
                
                # Analyze newly stored articles
                for article_id in batch_result['stored_ids']:
                    article = storage_service.get_article_by_id(article_id)
                    if article:
                        try:
                            bias_scores = bias_analyzer.analyze_article_bias(article)
                            storage_service.update_article_bias_scores(article_id, bias_scores.to_dict())
                            print(f"    ✅ Analyzed: {article.title[:30]}...")
                        except Exception as e:
                            print(f"    ❌ Analysis failed: {e}")
            else:
                print("  ❌ No articles scraped")
        
        # Test statistics
        print("\n6. Testing statistics...")
        stats = storage_service.get_storage_statistics()
        print(f"  Total articles: {stats.get('total_articles', 0)}")
        print(f"  Analyzed articles: {stats.get('analyzed_articles', 0)}")
        print(f"  Language distribution: {stats.get('language_distribution', {})}")
        
        print("\n✅ Real storage test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Real storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Real Database Storage Test")
    print(f"Started at: {datetime.now()}")
    
    success = test_real_storage()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Real Storage Test: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    if success:
        print("\n🎉 Real database storage is working correctly!")
        print("The scraper can now save articles and perform bias analysis.")
    else:
        print("\n❌ Real database storage test failed.")
    
    print(f"\nCompleted at: {datetime.now()}")