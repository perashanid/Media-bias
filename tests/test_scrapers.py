"""
Unit tests for news scrapers
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scrapers.base_scraper import BaseScraper
from scrapers.scraper_manager import ScraperManager
from scrapers.prothom_alo_scraper import ProthomAloScraper
from scrapers.daily_star_scraper import DailyStarScraper
from models.article import Article


class TestScraper(BaseScraper):
    """Concrete test scraper for testing base functionality"""
    
    def _get_article_urls(self, max_articles: int):
        return ["http://test.com/article1", "http://test.com/article2"]
    
    def _extract_article_content(self, soup, url):
        return Article(
            url=url,
            title="Test Article",
            content="Test content",
            author="Test Author",
            publication_date=datetime.now(),
            source=self.source_name,
            scraped_at=datetime.now(),
            language="english"
        )


class TestBaseScraper:
    """Tests for BaseScraper functionality"""
    
    def test_user_agent_rotation(self):
        """Test user agent rotation"""
        scraper = TestScraper("Test", "http://test.com")
        
        # Get multiple user agents
        agents = [scraper._get_random_user_agent() for _ in range(10)]
        
        # Should have variety (not all the same)
        assert len(set(agents)) > 1
        
        # All should be valid user agent strings
        for agent in agents:
            assert "Mozilla" in agent or "Chrome" in agent
    
    def test_rate_limiting_delay(self):
        """Test rate limiting delay calculation"""
        scraper = TestScraper("Test", "http://test.com")
        
        # Test exponential backoff
        import time
        start_time = time.time()
        scraper._handle_rate_limiting(1)  # First retry
        end_time = time.time()
        
        # Should have some delay
        assert end_time - start_time >= scraper.base_delay
    
    def test_language_detection(self):
        """Test language detection"""
        scraper = TestScraper("Test", "http://test.com")
        
        # Test English text
        english_text = "This is an English article about politics and news."
        assert scraper._detect_language(english_text) == "english"
        
        # Test Bengali text
        bengali_text = "এটি একটি বাংলা নিবন্ধ যা রাজনীতি এবং সংবাদ সম্পর্কে।"
        assert scraper._detect_language(bengali_text) == "bengali"
    
    def test_text_cleaning(self):
        """Test text cleaning functionality"""
        scraper = TestScraper("Test", "http://test.com")
        
        # Test with messy text
        messy_text = "  This   is   a   test   \n\n  with   extra   spaces  "
        cleaned = scraper._clean_text(messy_text)
        
        assert cleaned == "This is a test with extra spaces"
        
        # Test with unwanted patterns
        text_with_ads = "This is content Advertisement Click here to subscribe"
        cleaned = scraper._clean_text(text_with_ads)
        
        assert "Advertisement" not in cleaned
        assert "Click here to" not in cleaned
    
    def test_date_parsing(self):
        """Test date parsing functionality"""
        scraper = TestScraper("Test", "http://test.com")
        
        # Test various date formats
        date_formats = [
            "2023-12-01 15:30:00",
            "2023-12-01",
            "01/12/2023",
            "December 1, 2023"
        ]
        
        for date_str in date_formats:
            parsed_date = scraper._parse_date(date_str)
            assert isinstance(parsed_date, datetime)


class TestScraperManager:
    """Tests for ScraperManager"""
    
    def test_scraper_initialization(self):
        """Test scraper manager initialization"""
        manager = ScraperManager()
        
        # Should have all 5 scrapers
        sources = manager.get_available_sources()
        expected_sources = ['prothom_alo', 'daily_star', 'bd_pratidin', 'ekattor_tv', 'atn_news']
        
        assert len(sources) == 5
        for source in expected_sources:
            assert source in sources
    
    def test_scraper_info(self):
        """Test scraper information retrieval"""
        manager = ScraperManager()
        info = manager.get_scraper_info()
        
        assert isinstance(info, dict)
        assert len(info) == 5
        
        # Check info structure
        for source_name, source_info in info.items():
            assert 'source_name' in source_info
            assert 'base_url' in source_info
            assert 'max_retries' in source_info


class TestProthomAloScraper:
    """Tests for Prothom Alo scraper"""
    
    def test_initialization(self):
        """Test scraper initialization"""
        scraper = ProthomAloScraper()
        
        assert scraper.source_name == "Prothom Alo"
        assert scraper.base_url == "https://www.prothomalo.com"
    
    def test_article_url_validation(self):
        """Test article URL validation"""
        scraper = ProthomAloScraper()
        
        # Valid article URLs
        valid_urls = [
            "https://www.prothomalo.com/bangladesh/article123",
            "https://www.prothomalo.com/politics/news456",
            "https://www.prothomalo.com/international/story789"
        ]
        
        for url in valid_urls:
            assert scraper._is_article_url(url)
        
        # Invalid URLs
        invalid_urls = [
            "https://www.prothomalo.com/live/",
            "https://www.prothomalo.com/video/",
            "https://www.prothomalo.com/photo/gallery",
            "https://www.prothomalo.com/image.jpg"
        ]
        
        for url in invalid_urls:
            assert not scraper._is_article_url(url)
    
    @patch('scrapers.base_scraper.BaseScraper._make_request')
    def test_article_extraction(self, mock_request):
        """Test article content extraction"""
        scraper = ProthomAloScraper()
        
        # Mock HTML response
        mock_html = """
        <html>
            <head><title>Test Article</title></head>
            <body>
                <h1 class="title">Test Article Title</h1>
                <div class="story-content">
                    <p>This is the article content.</p>
                    <p>More content here.</p>
                </div>
                <div class="author-name">Test Author</div>
                <div class="publish-date">2023-12-01</div>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.content = mock_html.encode('utf-8')
        mock_request.return_value = mock_response
        
        # Test extraction
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(mock_html, 'html.parser')
        article = scraper._extract_article_content(soup, "http://test.com/article")
        
        assert article is not None
        assert article.title == "Test Article Title"
        assert "This is the article content" in article.content
        assert article.author == "Test Author"
        assert article.source == "Prothom Alo"


class TestDailyStarScraper:
    """Tests for Daily Star scraper"""
    
    def test_initialization(self):
        """Test scraper initialization"""
        scraper = DailyStarScraper()
        
        assert scraper.source_name == "The Daily Star"
        assert scraper.base_url == "https://www.thedailystar.net"
    
    def test_article_url_validation(self):
        """Test article URL validation"""
        scraper = DailyStarScraper()
        
        # Valid article URLs
        valid_urls = [
            "https://www.thedailystar.net/news/bangladesh/article123",
            "https://www.thedailystar.net/business/news456",
            "https://www.thedailystar.net/sports/story789"
        ]
        
        for url in valid_urls:
            assert scraper._is_article_url(url)
        
        # Invalid URLs
        invalid_urls = [
            "https://www.thedailystar.net/live-news/",
            "https://www.thedailystar.net/video/",
            "https://www.thedailystar.net/gallery/",
            "https://www.thedailystar.net/page/2"
        ]
        
        for url in invalid_urls:
            assert not scraper._is_article_url(url)


class TestScrapingWorkflow:
    """Integration tests for scraping workflow"""
    
    @patch('scrapers.base_scraper.BaseScraper._make_request')
    def test_complete_scraping_workflow(self, mock_request):
        """Test complete scraping workflow"""
        # Mock responses for different stages
        
        # Mock category page response
        category_html = """
        <html>
            <body>
                <a href="/bangladesh/article1">Article 1</a>
                <a href="/politics/article2">Article 2</a>
            </body>
        </html>
        """
        
        # Mock article page response
        article_html = """
        <html>
            <body>
                <h1 class="title">Test Article</h1>
                <div class="story-content">Article content here.</div>
                <div class="author-name">Test Author</div>
                <div class="publish-date">2023-12-01</div>
            </body>
        </html>
        """
        
        def mock_request_side_effect(url):
            mock_response = Mock()
            if 'article' in url:
                mock_response.content = article_html.encode('utf-8')
            else:
                mock_response.content = category_html.encode('utf-8')
            return mock_response
        
        mock_request.side_effect = mock_request_side_effect
        
        # Test scraping
        scraper = ProthomAloScraper()
        
        # Mock the _get_article_urls method to return test URLs
        with patch.object(scraper, '_get_article_urls', return_value=['http://test.com/article1']):
            articles = scraper.scrape_articles(max_articles=1)
        
        assert len(articles) <= 1  # Should respect max_articles limit


if __name__ == "__main__":
    pytest.main([__file__, "-v"])