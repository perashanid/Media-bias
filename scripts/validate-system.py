#!/usr/bin/env python3
"""
System validation script for Media Bias Detector
Validates all requirements and ensures system integrity
"""

import sys
import os
import logging
import requests
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.article_storage_service import ArticleStorageService
from services.bias_analyzer import BiasAnalyzer
from services.article_comparator import ArticleComparator
from scrapers.scraper_manager import ScraperManager
from models.article import Article

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SystemValidator:
    """System validation utilities"""
    
    def __init__(self):
        self.api_base_url = "http://localhost:5000"
        self.storage_service = ArticleStorageService()
        self.bias_analyzer = BiasAnalyzer()
        self.article_comparator = ArticleComparator()
        self.scraper_manager = ScraperManager()
        
        self.validation_results = {
            'total_checks': 0,
            'passed_checks': 0,
            'failed_checks': 0,
            'warnings': 0,
            'errors': []
        }
    
    def validate_check(self, check_name, check_function, *args, **kwargs):
        """Run a validation check and record results"""
        self.validation_results['total_checks'] += 1
        logger.info(f"🔍 Validating: {check_name}")
        
        try:
            result = check_function(*args, **kwargs)
            if result:
                logger.info(f"✅ PASS: {check_name}")
                self.validation_results['passed_checks'] += 1
                return True
            else:
                logger.error(f"❌ FAIL: {check_name}")
                self.validation_results['failed_checks'] += 1
                self.validation_results['errors'].append(check_name)
                return False
        except Exception as e:
            logger.error(f"❌ ERROR: {check_name} - {e}")
            self.validation_results['failed_checks'] += 1
            self.validation_results['errors'].append(f"{check_name}: {e}")
            return False
    
    def validate_requirement_1_scraping(self):
        """Validate Requirement 1: Multi-source news scraping"""
        logger.info("📰 Validating Requirement 1: Multi-source news scraping")
        
        # 1.1 - 1.5: Check all 5 news sources are available
        sources = self.scraper_manager.get_available_sources()
        expected_sources = ['prothom_alo', 'daily_star', 'bd_pratidin', 'ekattor_tv', 'atn_news']
        
        self.validate_check(
            "1.1-1.5: All 5 news sources available",
            lambda: len(sources) == 5 and all(source in sources for source in expected_sources)
        )
        
        # 1.6: Rate limiting and respectful crawling
        self.validate_check(
            "1.6: Rate limiting implemented",
            lambda: hasattr(self.scraper_manager.scrapers['prothom_alo'], 'base_delay') and
                   self.scraper_manager.scrapers['prothom_alo'].base_delay > 0
        )
        
        # 1.7: User-agent rotation
        scraper = self.scraper_manager.scrapers['prothom_alo']
        agents = [scraper._get_random_user_agent() for _ in range(5)]
        self.validate_check(
            "1.7: User-agent rotation",
            lambda: len(set(agents)) > 1
        )
        
        # 1.8: Error handling and retry mechanisms
        self.validate_check(
            "1.8: Error handling and retry mechanisms",
            lambda: hasattr(scraper, 'max_retries') and scraper.max_retries > 0
        )
    
    def validate_requirement_2_storage(self):
        """Validate Requirement 2: Article storage with deduplication"""
        logger.info("💾 Validating Requirement 2: Article storage with deduplication")
        
        # 2.1: MongoDB storage
        self.validate_check(
            "2.1: MongoDB storage functional",
            lambda: self.storage_service.get_storage_statistics() is not None
        )
        
        # 2.2: Content hashing for deduplication
        test_article = Article(
            url="http://test-validation.com/article1",
            title="Test Article for Validation",
            content="This is test content for validation purposes.",
            source="Test Source",
            publication_date=datetime.now(),
            scraped_at=datetime.now(),
            language="english"
        )
        
        self.validate_check(
            "2.2: Content hashing implemented",
            lambda: hasattr(test_article, 'content_hash') and test_article.content_hash is not None
        )
        
        # 2.3: Duplicate detection
        article_id1 = self.storage_service.store_article(test_article)
        article_id2 = self.storage_service.store_article(test_article)  # Same article
        
        self.validate_check(
            "2.3: Duplicate detection working",
            lambda: article_id1 == article_id2  # Should return same ID for duplicate
        )
        
        # 2.4: Data retention policies
        self.validate_check(
            "2.4: Data retention policies implemented",
            lambda: hasattr(self.storage_service, 'cleanup_old_articles')
        )
    
    def validate_requirement_3_bias_analysis(self):
        """Validate Requirement 3: Comprehensive bias analysis"""
        logger.info("🧠 Validating Requirement 3: Comprehensive bias analysis")
        
        # 3.1: Language detection
        english_text = "This is an English sentence."
        bengali_text = "এটি একটি বাংলা বাক্য।"
        
        self.validate_check(
            "3.1: Language detection for English",
            lambda: self.bias_analyzer.language_detector.detect_language(english_text) == "english"
        )
        
        self.validate_check(
            "3.1: Language detection for Bengali",
            lambda: self.bias_analyzer.language_detector.detect_language(bengali_text) == "bengali"
        )
        
        # 3.2: Sentiment analysis
        positive_text = "This is excellent and wonderful news!"
        negative_text = "This is terrible and awful news!"
        
        pos_sentiment = self.bias_analyzer.sentiment_analyzer.analyze_sentiment(positive_text, "english")
        neg_sentiment = self.bias_analyzer.sentiment_analyzer.analyze_sentiment(negative_text, "english")
        
        self.validate_check(
            "3.2: Positive sentiment detection",
            lambda: pos_sentiment > 0.1
        )
        
        self.validate_check(
            "3.2: Negative sentiment detection",
            lambda: neg_sentiment < -0.1
        )
        
        # 3.3: Political bias detection
        political_text = "The government's excellent policies will benefit everyone greatly."
        political_bias = self.bias_analyzer.political_bias_detector.detect_political_bias(political_text, "english")
        
        self.validate_check(
            "3.3: Political bias detection",
            lambda: isinstance(political_bias, float) and -1.0 <= political_bias <= 1.0
        )
        
        # 3.4: Emotional language detection
        emotional_text = "This is absolutely devastating and completely outrageous!"
        emotional_score = self.bias_analyzer.sentiment_analyzer.detect_emotional_intensity(emotional_text, "english")
        
        self.validate_check(
            "3.4: Emotional language detection",
            lambda: emotional_score > 0.3
        )
        
        # 3.5: Factual vs opinion classification
        factual_text = "According to the report, GDP grew by 3.2% last year."
        opinion_text = "I think this policy is completely wrong."
        
        factual_score = self.bias_analyzer.factual_opinion_classifier.classify_factual_vs_opinion(factual_text, "english")
        opinion_score = self.bias_analyzer.factual_opinion_classifier.classify_factual_vs_opinion(opinion_text, "english")
        
        self.validate_check(
            "3.5: Factual content classification",
            lambda: factual_score > 0.5
        )
        
        self.validate_check(
            "3.5: Opinion content classification",
            lambda: opinion_score < 0.5
        )
        
        # 3.6: Overall bias scoring
        test_article = Article(
            url="http://test-bias.com/article1",
            title="Test Bias Analysis",
            content="This is a test article for bias analysis validation.",
            source="Test Source",
            publication_date=datetime.now(),
            scraped_at=datetime.now(),
            language="english"
        )
        
        bias_scores = self.bias_analyzer.analyze_article_bias(test_article)
        
        self.validate_check(
            "3.6: Overall bias scoring",
            lambda: 0.0 <= bias_scores.overall_bias_score <= 1.0
        )
    
    def validate_requirement_4_api(self):
        """Validate Requirement 4: REST API functionality"""
        logger.info("🌐 Validating Requirement 4: REST API functionality")
        
        # 4.1: API health check
        self.validate_check(
            "4.1: API health endpoint",
            lambda: requests.get(f"{self.api_base_url}/health", timeout=10).status_code == 200
        )
        
        # 4.2: Article retrieval endpoints
        self.validate_check(
            "4.2: Articles endpoint",
            lambda: requests.get(f"{self.api_base_url}/api/articles", timeout=10).status_code == 200
        )
        
        # 4.3: Bias analysis endpoints
        test_data = {"text": "Test text for API validation", "language": "english"}
        self.validate_check(
            "4.3: Bias analysis endpoint",
            lambda: requests.post(f"{self.api_base_url}/api/bias/analyze-text", json=test_data, timeout=30).status_code == 200
        )
        
        # 4.4: Statistics endpoints
        self.validate_check(
            "4.4: Statistics endpoint",
            lambda: requests.get(f"{self.api_base_url}/api/statistics/overview", timeout=10).status_code == 200
        )
    
    def validate_requirement_5_comparison(self):
        """Validate Requirement 5: Article comparison functionality"""
        logger.info("🔍 Validating Requirement 5: Article comparison functionality")
        
        # Create test articles for comparison
        article1 = Article(
            url="http://test-comp1.com/article1",
            title="Test Article 1 About Politics",
            content="This is the first test article about political developments and government policies.",
            source="Source 1",
            publication_date=datetime.now(),
            scraped_at=datetime.now(),
            language="english"
        )
        
        article2 = Article(
            url="http://test-comp2.com/article2",
            title="Test Article 2 About Politics",
            content="This is the second test article about political developments and government policies.",
            source="Source 2",
            publication_date=datetime.now(),
            scraped_at=datetime.now(),
            language="english"
        )
        
        # 5.1: Content similarity calculation
        similarity = self.article_comparator.similarity_matcher.calculate_similarity(article1, article2)
        
        self.validate_check(
            "5.1: Content similarity calculation",
            lambda: 0.0 <= similarity <= 1.0 and similarity > 0.3  # Should be similar
        )
        
        # 5.2: Related article finding
        related_articles = self.article_comparator.find_related_articles(article1, [article2], 0.2)
        
        self.validate_check(
            "5.2: Related article finding",
            lambda: len(related_articles) > 0
        )
        
        # 5.3: Bias difference calculation
        # Add bias scores to articles
        article1.bias_scores = self.bias_analyzer.analyze_article_bias(article1)
        article2.bias_scores = self.bias_analyzer.analyze_article_bias(article2)
        
        bias_differences = self.article_comparator.calculate_bias_differences([article1, article2])
        
        self.validate_check(
            "5.3: Bias difference calculation",
            lambda: len(bias_differences) > 0 and all(isinstance(diff, (int, float)) for diff in bias_differences.values())
        )
        
        # 5.4: Comparison report generation
        comparison_report = self.article_comparator.generate_comparison_report([article1, article2])
        
        self.validate_check(
            "5.4: Comparison report generation",
            lambda: comparison_report is not None and hasattr(comparison_report, 'story_id')
        )
    
    def validate_requirement_6_system(self):
        """Validate Requirement 6: System reliability and monitoring"""
        logger.info("⚙️ Validating Requirement 6: System reliability and monitoring")
        
        # 6.1: Automated scheduling
        from services.scheduler_service import SchedulerService
        scheduler = SchedulerService()
        
        self.validate_check(
            "6.1: Scheduler service functional",
            lambda: hasattr(scheduler, 'add_job') and hasattr(scheduler, 'start')
        )
        
        # 6.2: Error handling and logging
        self.validate_check(
            "6.2: Logging configured",
            lambda: logging.getLogger().handlers is not None and len(logging.getLogger().handlers) > 0
        )
        
        # 6.3: System monitoring
        from services.monitoring_service import MonitoringService
        monitoring = MonitoringService()
        
        self.validate_check(
            "6.3: Monitoring service functional",
            lambda: hasattr(monitoring, 'create_alert') and hasattr(monitoring, 'get_system_health')
        )
        
        # 6.4: Database configuration and deployment
        self.validate_check(
            "6.4: Database connection functional",
            lambda: self.storage_service.get_storage_statistics() is not None
        )
    
    def validate_all_requirements(self):
        """Validate all system requirements"""
        logger.info("🚀 Starting comprehensive system validation...")
        
        start_time = datetime.now()
        
        try:
            # Validate each requirement
            self.validate_requirement_1_scraping()
            self.validate_requirement_2_storage()
            self.validate_requirement_3_bias_analysis()
            self.validate_requirement_4_api()
            self.validate_requirement_5_comparison()
            self.validate_requirement_6_system()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Generate validation report
            self.generate_validation_report(duration)
            
        except Exception as e:
            logger.error(f"❌ System validation failed: {e}")
            raise
    
    def generate_validation_report(self, duration):
        """Generate validation report"""
        results = self.validation_results
        
        report = f"""
=== Media Bias Detector System Validation Report ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration:.1f} seconds

Summary:
- Total checks: {results['total_checks']}
- Passed: {results['passed_checks']} ✅
- Failed: {results['failed_checks']} ❌
- Success rate: {(results['passed_checks'] / results['total_checks'] * 100):.1f}%

"""
        
        if results['failed_checks'] > 0:
            report += "Failed Checks:\n"
            for error in results['errors']:
                report += f"- {error}\n"
            report += "\n"
        
        if results['failed_checks'] == 0:
            report += "🎉 ALL REQUIREMENTS VALIDATED SUCCESSFULLY!\n"
            report += "The system is ready for production deployment.\n"
        else:
            report += "⚠️  Some requirements failed validation.\n"
            report += "Please address the failed checks before deployment.\n"
        
        # Save report
        os.makedirs('reports', exist_ok=True)
        report_file = f"reports/validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"📊 Validation report saved to: {report_file}")
        print(report)
        
        return results['failed_checks'] == 0


def main():
    """Main validation function"""
    print("🔍 Media Bias Detector System Validator")
    print("=" * 50)
    
    validator = SystemValidator()
    
    try:
        success = validator.validate_all_requirements()
        
        if success:
            print("\n🎉 System validation completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ System validation failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Validation error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()