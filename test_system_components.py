#!/usr/bin/env python3
"""
Test system components without requiring server
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, '.')

def test_database_connection():
    """Test database connection"""
    try:
        from config.database import initialize_database
        db = initialize_database()
        print("+ Database connection successful (using mock)")
        return True
    except Exception as e:
        print(f"- Database connection failed: {e}")
        return False

def test_article_model():
    """Test article model"""
    try:
        from models.article import Article, BiasScore
        
        # Create test article
        article = Article(
            url="http://test.com/article1",
            title="Test Article",
            content="This is test content for the article.",
            author="Test Author",
            publication_date=datetime.now(),
            source="Test Source",
            scraped_at=datetime.now(),
            language="english"
        )
        
        # Test serialization
        article_dict = article.to_dict()
        article_restored = Article.from_dict(article_dict)
        
        print("+ Article model working correctly")
        return True
    except Exception as e:
        print(f"- Article model failed: {e}")
        return False

def test_bias_analyzer():
    """Test bias analyzer"""
    try:
        from services.bias_analyzer import BiasAnalyzer
        
        analyzer = BiasAnalyzer()
        
        # Test text analysis
        result = analyzer.analyze_text_sample(
            "This is an excellent government policy that will benefit everyone greatly.",
            "english"
        )
        
        # Check required fields
        required_fields = ['sentiment_score', 'political_bias_score', 'overall_bias_score']
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing field: {field}")
        
        print(f"+ Bias analyzer working correctly (bias score: {result['overall_bias_score']:.3f})")
        return True
    except Exception as e:
        print(f"- Bias analyzer failed: {e}")
        return False

def test_scrapers():
    """Test scraper components"""
    try:
        from scrapers.prothom_alo_scraper import ProthomAloScraper
        from scrapers.daily_star_scraper import DailyStarScraper
        
        # Initialize scrapers
        prothom_alo = ProthomAloScraper()
        daily_star = DailyStarScraper()
        
        print(f"+ Scrapers initialized: {prothom_alo.source_name}, {daily_star.source_name}")
        return True
    except Exception as e:
        print(f"- Scrapers failed: {e}")
        return False

def test_text_processing():
    """Test text processing components"""
    try:
        from services.sentiment_analyzer import SentimentAnalyzer
        from services.language_detector import LanguageDetector
        from services.text_preprocessor import BengaliTextPreprocessor, EnglishTextPreprocessor
        
        # Test sentiment analyzer
        sentiment_analyzer = SentimentAnalyzer()
        sentiment_score = sentiment_analyzer.analyze_sentiment("This is great news!", "english")
        
        # Test language detector
        language_detector = LanguageDetector()
        detected_lang = language_detector.detect_language("This is an English sentence.")
        
        # Test text preprocessors
        bengali_preprocessor = BengaliTextPreprocessor()
        english_preprocessor = EnglishTextPreprocessor()
        
        bengali_tokens = bengali_preprocessor.tokenize_bengali("এটি একটি বাংলা বাক্য।")
        english_tokens = english_preprocessor.tokenize_english("This is an English sentence.")
        
        print(f"+ Text processing working (sentiment: {sentiment_score:.3f}, lang: {detected_lang})")
        return True
    except Exception as e:
        print(f"- Text processing failed: {e}")
        return False

def test_article_storage():
    """Test article storage service"""
    try:
        from services.article_storage_service import ArticleStorageService
        from models.article import Article
        
        storage = ArticleStorageService()
        
        # Test with mock database
        test_article = Article(
            url="http://test.com/storage-test",
            title="Storage Test Article",
            content="This is a test article for storage.",
            author="Test Author",
            publication_date=datetime.now(),
            source="Test Source",
            scraped_at=datetime.now(),
            language="english"
        )
        
        # This will work with mock database
        result = storage.store_article(test_article)
        
        print("+ Article storage service working (with mock database)")
        return True
    except Exception as e:
        print(f"- Article storage failed: {e}")
        return False

def test_flask_app_creation():
    """Test Flask app creation"""
    try:
        from api.app import app
        
        # Test app configuration
        assert app is not None
        assert app.config is not None
        
        print("+ Flask app created successfully")
        return True
    except Exception as e:
        print(f"- Flask app creation failed: {e}")
        return False

def main():
    """Run all component tests"""
    print("Testing Media Bias Detection System Components")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Article Model", test_article_model),
        ("Bias Analyzer", test_bias_analyzer),
        ("Scrapers", test_scrapers),
        ("Text Processing", test_text_processing),
        ("Article Storage", test_article_storage),
        ("Flask App", test_flask_app_creation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"- {test_name} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    
    for i, (test_name, _) in enumerate(tests):
        status = "+ PASS" if results[i] else "- FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All component tests passed!")
        return True
    else:
        print("ERROR: Some component tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)