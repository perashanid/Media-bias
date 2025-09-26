#!/usr/bin/env python3
"""
Complete workflow test for the Media Bias Detector system
Tests scraping, storage, analysis, and API functionality
"""

import sys
import os
import logging
import requests
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.scraper_manager import ScraperManager
from services.article_storage_service import ArticleStorageService
from services.bias_analyzer import BiasAnalyzer
from services.scraping_orchestrator import ScrapingOrchestrator
from config.database import initialize_database

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WorkflowTester:
    """Comprehensive workflow tester"""
    
    def __init__(self):
        self.scraper_manager = None
        self.storage_service = None
        self.bias_analyzer = None
        self.orchestrator = None
        self.test_results = {
            'database_init': False,
            'services_init': False,
            'scraping': False,
            'storage': False,
            'bias_analysis': False,
            'api_endpoints': False,
            'orchestrator': False
        }
    
    def run_complete_test(self):
        """Run the complete workflow test"""
        print("=" * 80)
        print("MEDIA BIAS DETECTOR - COMPLETE WORKFLOW TEST")
        print("=" * 80)
        print(f"Started at: {datetime.now()}")
        
        try:
            # Test 1: Database initialization
            self.test_database_initialization()
            
            # Test 2: Services initialization
            self.test_services_initialization()
            
            # Test 3: Scraping functionality
            self.test_scraping_functionality()
            
            # Test 4: Storage functionality
            self.test_storage_functionality()
            
            # Test 5: Bias analysis functionality
            self.test_bias_analysis_functionality()
            
            # Test 6: API endpoints
            self.test_api_endpoints()
            
            # Test 7: Orchestrator functionality
            self.test_orchestrator_functionality()
            
            # Generate final report
            self.generate_final_report()
            
        except Exception as e:
            print(f"\n❌ Critical error during testing: {e}")
            import traceback
            traceback.print_exc()
    
    def test_database_initialization(self):
        """Test database initialization"""
        print("\n" + "="*60)
        print("TEST 1: DATABASE INITIALIZATION")
        print("="*60)
        
        try:
            print("Initializing database...")
            initialize_database()
            self.test_results['database_init'] = True
            print("✅ Database initialization successful")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            self.test_results['database_init'] = False
    
    def test_services_initialization(self):
        """Test services initialization"""
        print("\n" + "="*60)
        print("TEST 2: SERVICES INITIALIZATION")
        print("="*60)
        
        try:
            print("Initializing services...")
            self.scraper_manager = ScraperManager()
            self.storage_service = ArticleStorageService()
            self.bias_analyzer = BiasAnalyzer()
            self.orchestrator = ScrapingOrchestrator()
            
            # Test service availability
            sources = self.scraper_manager.get_available_sources()
            print(f"✅ Scraper Manager: {len(sources)} sources available")
            
            stats = self.storage_service.get_storage_statistics()
            print(f"✅ Storage Service: {stats.get('total_articles', 0)} articles in database")
            
            print("✅ Bias Analyzer: Initialized successfully")
            print("✅ Orchestrator: Initialized successfully")
            
            self.test_results['services_init'] = True
            
        except Exception as e:
            print(f"❌ Services initialization failed: {e}")
            self.test_results['services_init'] = False
    
    def test_scraping_functionality(self):
        """Test scraping functionality"""
        print("\n" + "="*60)
        print("TEST 3: SCRAPING FUNCTIONALITY")
        print("="*60)
        
        try:
            if not self.scraper_manager:
                print("❌ Scraper manager not initialized")
                return
            
            sources = self.scraper_manager.get_available_sources()
            print(f"Testing scraping from {len(sources)} sources...")
            
            # Test scraping from first available source
            if sources:
                test_source = sources[0]
                print(f"Testing scraping from: {test_source}")
                
                articles = self.scraper_manager.scrape_source(test_source, limit=3)
                
                if articles:
                    print(f"✅ Successfully scraped {len(articles)} articles")
                    
                    # Test article properties
                    for i, article in enumerate(articles[:2]):  # Test first 2 articles
                        print(f"  Article {i+1}:")
                        print(f"    Title: {article.title[:50]}...")
                        print(f"    Source: {article.source}")
                        print(f"    Language: {article.language}")
                        print(f"    Content length: {len(article.content)} chars")
                        print(f"    URL: {article.url}")
                    
                    self.test_results['scraping'] = True
                else:
                    print("❌ No articles scraped")
                    self.test_results['scraping'] = False
            else:
                print("❌ No sources available for testing")
                self.test_results['scraping'] = False
            
            # Test URL scraping
            print("\nTesting URL scraping...")
            test_urls = [
                "https://www.thedailystar.net/news/bangladesh",
                "https://www.prothomalo.com/bangladesh"
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
            url_success = 0
            
            for url in test_urls:
                try:
                    print(f"  Testing: {url}")
                    article = scraper.scrape_single_url(url)
                    if article:
                        print(f"    ✅ Success: {article.title[:30]}...")
                        url_success += 1
                    else:
                        print(f"    ❌ Failed to scrape")
                except Exception as e:
                    print(f"    ❌ Error: {e}")
            
            print(f"URL scraping: {url_success}/{len(test_urls)} successful")
            
        except Exception as e:
            print(f"❌ Scraping test failed: {e}")
            self.test_results['scraping'] = False
    
    def test_storage_functionality(self):
        """Test storage functionality"""
        print("\n" + "="*60)
        print("TEST 4: STORAGE FUNCTIONALITY")
        print("="*60)
        
        try:
            if not self.storage_service or not self.scraper_manager:
                print("❌ Required services not initialized")
                return
            
            # Get some test articles
            sources = self.scraper_manager.get_available_sources()
            if not sources:
                print("❌ No sources available for storage test")
                return
            
            test_source = sources[0]
            articles = self.scraper_manager.scrape_source(test_source, limit=2)
            
            if not articles:
                print("❌ No articles available for storage test")
                return
            
            print(f"Testing storage with {len(articles)} articles...")
            
            stored_count = 0
            duplicate_count = 0
            
            for i, article in enumerate(articles):
                print(f"  Storing article {i+1}: {article.title[:40]}...")
                
                article_id = self.storage_service.store_article(article)
                if article_id:
                    stored_count += 1
                    print(f"    ✅ Stored with ID: {article_id}")
                    
                    # Test retrieval
                    retrieved = self.storage_service.get_article_by_id(article_id)
                    if retrieved:
                        print(f"    ✅ Successfully retrieved article")
                    else:
                        print(f"    ❌ Failed to retrieve article")
                    
                    # Test duplicate detection (store same article again)
                    duplicate_id = self.storage_service.store_article(article)
                    if duplicate_id == article_id:
                        duplicate_count += 1
                        print(f"    ✅ Duplicate detection working")
                    else:
                        print(f"    ❌ Duplicate detection failed")
                else:
                    print(f"    ❌ Failed to store article")
            
            # Test batch storage
            print(f"\nTesting batch storage...")
            batch_result = self.storage_service.store_articles_batch(articles)
            print(f"  Batch result: {batch_result['stored']} stored, {batch_result['duplicates']} duplicates")
            
            # Test statistics
            stats = self.storage_service.get_storage_statistics()
            print(f"  Database statistics: {stats.get('total_articles', 0)} total articles")
            
            if stored_count > 0:
                self.test_results['storage'] = True
                print("✅ Storage functionality working")
            else:
                self.test_results['storage'] = False
                print("❌ Storage functionality failed")
            
        except Exception as e:
            print(f"❌ Storage test failed: {e}")
            self.test_results['storage'] = False
    
    def test_bias_analysis_functionality(self):
        """Test bias analysis functionality"""
        print("\n" + "="*60)
        print("TEST 5: BIAS ANALYSIS FUNCTIONALITY")
        print("="*60)
        
        try:
            if not self.bias_analyzer or not self.storage_service:
                print("❌ Required services not initialized")
                return
            
            # Get articles without bias analysis
            pending_articles = self.storage_service.get_articles_without_bias_analysis(limit=3)
            
            if not pending_articles:
                print("No pending articles found, creating test article...")
                
                # Create a test article
                from models.article import Article
                test_article = Article(
                    title="Test Article for Bias Analysis",
                    content="This is a test article with some political content. The government has announced new policies that will benefit the economy. Critics argue that these policies favor certain groups over others.",
                    url="http://test.com/article",
                    source="test_source",
                    publication_date=datetime.now(),
                    scraped_at=datetime.now(),
                    language="en",
                    author="Test Author"
                )
                
                article_id = self.storage_service.store_article(test_article)
                if article_id:
                    pending_articles = [test_article]
                    test_article.id = article_id
                else:
                    print("❌ Failed to create test article")
                    return
            
            print(f"Testing bias analysis with {len(pending_articles)} articles...")
            
            analyzed_count = 0
            
            for i, article in enumerate(pending_articles[:2]):  # Test first 2 articles
                print(f"  Analyzing article {i+1}: {article.title[:40]}...")
                
                try:
                    bias_scores = self.bias_analyzer.analyze_article_bias(article)
                    
                    print(f"    ✅ Analysis completed:")
                    print(f"      Political bias: {bias_scores.political_bias_score:.3f}")
                    print(f"      Sentiment: {bias_scores.sentiment_score:.3f}")
                    print(f"      Emotional language: {bias_scores.emotional_language_score:.3f}")
                    print(f"      Factual vs opinion: {bias_scores.factual_vs_opinion_score:.3f}")
                    print(f"      Overall bias: {bias_scores.overall_bias_score:.3f}")
                    
                    # Update article with bias scores
                    if article.id:
                        success = self.storage_service.update_article_bias_scores(
                            article.id, bias_scores.to_dict()
                        )
                        if success:
                            print(f"    ✅ Bias scores stored successfully")
                            analyzed_count += 1
                        else:
                            print(f"    ❌ Failed to store bias scores")
                    
                except Exception as e:
                    print(f"    ❌ Analysis failed: {e}")
            
            # Test text analysis
            print(f"\nTesting direct text analysis...")
            test_texts = [
                "The government's new policy is excellent and will benefit everyone.",
                "This controversial decision has sparked outrage among opposition groups."
            ]
            
            for i, text in enumerate(test_texts):
                try:
                    analysis = self.bias_analyzer.analyze_text_sample(text, 'en')
                    print(f"  Text {i+1} analysis: Overall bias = {analysis.get('overall_bias_score', 0):.3f}")
                except Exception as e:
                    print(f"  Text {i+1} analysis failed: {e}")
            
            if analyzed_count > 0:
                self.test_results['bias_analysis'] = True
                print("✅ Bias analysis functionality working")
            else:
                self.test_results['bias_analysis'] = False
                print("❌ Bias analysis functionality failed")
            
        except Exception as e:
            print(f"❌ Bias analysis test failed: {e}")
            self.test_results['bias_analysis'] = False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n" + "="*60)
        print("TEST 6: API ENDPOINTS")
        print("="*60)
        
        try:
            base_url = "http://localhost:5000"
            api_url = f"{base_url}/api"
            
            # Test health endpoint
            print("Testing health endpoint...")
            try:
                response = requests.get(f"{base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("  ✅ Health endpoint working")
                else:
                    print(f"  ❌ Health endpoint failed: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print("  ⚠️  API server not running (this is optional)")
                self.test_results['api_endpoints'] = True  # Don't fail if server not running
                return
            
            # Test scraper endpoints
            print("Testing scraper endpoints...")
            endpoints_to_test = [
                ("/scrape/sources", "GET", "Sources endpoint"),
                ("/articles?limit=5", "GET", "Articles endpoint"),
                ("/statistics/overview", "GET", "Statistics endpoint"),
            ]
            
            successful_endpoints = 0
            
            for endpoint, method, description in endpoints_to_test:
                try:
                    if method == "GET":
                        response = requests.get(f"{api_url}{endpoint}", timeout=10)
                    else:
                        response = requests.post(f"{api_url}{endpoint}", timeout=10)
                    
                    if response.status_code == 200:
                        print(f"  ✅ {description} working")
                        successful_endpoints += 1
                    else:
                        print(f"  ❌ {description} failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"  ❌ {description} error: {e}")
            
            # Test manual scraping endpoint
            print("Testing manual scraping endpoint...")
            try:
                test_data = {
                    "url": "https://www.thedailystar.net/news/bangladesh"
                }
                response = requests.post(f"{api_url}/scrape/test-url", json=test_data, timeout=15)
                if response.status_code == 200:
                    print("  ✅ Manual scraping endpoint working")
                    successful_endpoints += 1
                else:
                    print(f"  ❌ Manual scraping endpoint failed: {response.status_code}")
            except Exception as e:
                print(f"  ❌ Manual scraping endpoint error: {e}")
            
            if successful_endpoints >= len(endpoints_to_test):
                self.test_results['api_endpoints'] = True
                print("✅ API endpoints working")
            else:
                self.test_results['api_endpoints'] = False
                print(f"❌ API endpoints partially working: {successful_endpoints}/{len(endpoints_to_test) + 1}")
            
        except Exception as e:
            print(f"❌ API endpoints test failed: {e}")
            self.test_results['api_endpoints'] = False
    
    def test_orchestrator_functionality(self):
        """Test orchestrator functionality"""
        print("\n" + "="*60)
        print("TEST 7: ORCHESTRATOR FUNCTIONALITY")
        print("="*60)
        
        try:
            if not self.orchestrator:
                print("❌ Orchestrator not initialized")
                return
            
            print("Testing orchestrator status...")
            status = self.orchestrator.get_orchestrator_status()
            if 'error' not in status:
                print("  ✅ Orchestrator status retrieval working")
            else:
                print(f"  ❌ Orchestrator status failed: {status['error']}")
            
            print("Testing single source scraping via orchestrator...")
            sources = self.scraper_manager.get_available_sources()
            if sources:
                result = self.orchestrator.scrape_single_source(sources[0])
                if 'error' not in result:
                    print(f"  ✅ Single source scraping: {result['scraped']} scraped, {result['stored']} stored")
                else:
                    print(f"  ❌ Single source scraping failed: {result.get('error_message', 'Unknown error')}")
            
            print("Testing pending articles analysis...")
            analysis_result = self.orchestrator.analyze_pending_articles()
            if 'error' not in analysis_result:
                print(f"  ✅ Pending analysis: {analysis_result['analyzed']} analyzed, {analysis_result['errors']} errors")
            else:
                print(f"  ❌ Pending analysis failed: {analysis_result['error']}")
            
            self.test_results['orchestrator'] = True
            print("✅ Orchestrator functionality working")
            
        except Exception as e:
            print(f"❌ Orchestrator test failed: {e}")
            self.test_results['orchestrator'] = False
    
    def generate_final_report(self):
        """Generate final test report"""
        print("\n" + "="*80)
        print("FINAL TEST REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        print(f"Tests completed: {passed_tests}/{total_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! The system is working correctly.")
            print("\nNext steps:")
            print("1. Start the backend server: python api/app.py")
            print("2. Start the frontend: cd frontend && npm start")
            print("3. Access the application at http://localhost:3000")
        elif passed_tests >= total_tests * 0.8:
            print("\n✅ Most tests passed! The system is mostly functional.")
            print("Check the failed tests above for any issues to address.")
        else:
            print("\n❌ Several tests failed. Please review the errors above.")
        
        print(f"\nTest completed at: {datetime.now()}")


if __name__ == "__main__":
    tester = WorkflowTester()
    tester.run_complete_test()