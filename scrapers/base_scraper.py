import time
import random
import requests
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from bs4 import BeautifulSoup
from models.article import Article

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for news website scrapers"""
    
    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        self.max_retries = 3
        self.base_delay = 1.0
        self.max_delay = 10.0
        
    def _get_random_user_agent(self) -> str:
        """Get a random user agent for requests"""
        return random.choice(self.user_agents)
    
    def _handle_rate_limiting(self, attempt: int = 0):
        """Implement exponential backoff for rate limiting"""
        if attempt > 0:
            delay = min(self.base_delay * (2 ** attempt) + random.uniform(0, 1), self.max_delay)
            logger.info(f"Rate limiting detected, waiting {delay:.2f} seconds")
            time.sleep(delay)
        else:
            # Base delay between requests
            time.sleep(random.uniform(0.5, 1.5))
    
    def _make_request(self, url: str, attempt: int = 0) -> Optional[requests.Response]:
        """Make HTTP request with retry logic and rate limiting"""
        try:
            self._handle_rate_limiting(attempt)
            
            headers = {
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed for {url}: {e}")
            
            if attempt < self.max_retries:
                logger.info(f"Retrying request (attempt {attempt + 1}/{self.max_retries})")
                return self._make_request(url, attempt + 1)
            else:
                logger.error(f"Max retries exceeded for {url}")
                return None
    
    def scrape_articles(self, max_articles: int = 50) -> List[Article]:
        """Scrape articles from the news source"""
        try:
            logger.info(f"Starting to scrape articles from {self.source_name}")
            
            # Get article URLs from the main page or category pages
            article_urls = self._get_article_urls(max_articles)
            
            articles = []
            for url in article_urls:
                try:
                    article = self._scrape_single_article(url)
                    if article:
                        articles.append(article)
                        logger.debug(f"Successfully scraped article: {article.title[:50]}...")
                    
                except Exception as e:
                    logger.error(f"Failed to scrape article {url}: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(articles)} articles from {self.source_name}")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to scrape articles from {self.source_name}: {e}")
            return []
    
    def _scrape_single_article(self, url: str) -> Optional[Article]:
        """Scrape a single article from its URL"""
        response = self._make_request(url)
        if not response:
            return None
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._extract_article_content(soup, url)
            
        except Exception as e:
            logger.error(f"Failed to parse article content from {url}: {e}")
            return None
    
    def scrape_single_url(self, url: str) -> Optional[Article]:
        """Scrape a single article from any URL (public method)"""
        try:
            response = self._make_request(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to extract content using generic methods
            return self._extract_generic_article_content(soup, url)
            
        except Exception as e:
            logger.error(f"Failed to scrape single URL {url}: {e}")
            return None
    
    def _extract_generic_article_content(self, soup: BeautifulSoup, url: str) -> Optional[Article]:
        """Extract article content using generic selectors"""
        try:
            # Try to find title
            title = None
            title_selectors = ['h1', 'title', '.title', '.headline', '.article-title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem and title_elem.get_text().strip():
                    title = self._clean_text(title_elem.get_text())
                    break
            
            if not title:
                title = "Untitled Article"
            
            # Try to find content
            content = ""
            content_selectors = [
                '.article-content', '.content', '.post-content', 
                '.entry-content', 'article', '.article-body',
                'main', '.main-content'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove script and style elements
                    for script in content_elem(["script", "style"]):
                        script.decompose()
                    content = self._clean_text(content_elem.get_text())
                    if len(content) > 100:  # Minimum content length
                        break
            
            # If no content found, try paragraphs
            if len(content) < 100:
                paragraphs = soup.find_all('p')
                content = ' '.join([self._clean_text(p.get_text()) for p in paragraphs])
            
            if len(content) < 50:
                logger.warning(f"Insufficient content extracted from {url}")
                return None
            
            # Try to detect source from URL
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            source = parsed_url.netloc.replace('www.', '')
            
            # Detect language
            language = self._detect_language(content)
            
            return Article(
                title=title,
                content=content,
                url=url,
                source=source,
                publication_date=datetime.now(),  # Default to now since we can't reliably extract date
                scraped_at=datetime.now(),
                language=language,
                author=None  # Default to None for generic scraping
            )
            
        except Exception as e:
            logger.error(f"Failed to extract generic article content: {e}")
            return None
    
    @abstractmethod
    def _get_article_urls(self, max_articles: int) -> List[str]:
        """Get list of article URLs to scrape (implemented by subclasses)"""
        pass
    
    @abstractmethod
    def _extract_article_content(self, soup: BeautifulSoup, url: str) -> Optional[Article]:
        """Extract article content from BeautifulSoup object (implemented by subclasses)"""
        pass
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection for Bengali vs English"""
        # Count Bengali characters (Unicode range for Bengali)
        bengali_chars = sum(1 for char in text if '\u0980' <= char <= '\u09FF')
        total_chars = len([char for char in text if char.isalpha()])
        
        if total_chars == 0:
            return 'unknown'
        
        bengali_ratio = bengali_chars / total_chars
        # Use full language names for compatibility
        return 'bengali' if bengali_ratio > 0.3 else 'english'
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            'Advertisement',
            'Click here to',
            'Read more:',
            'Subscribe to',
            'Follow us on',
            'Share this:',
        ]
        
        for pattern in unwanted_patterns:
            text = text.replace(pattern, '')
        
        return text.strip()
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        # Common date formats to try
        date_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%B %d, %Y',
            '%d %B %Y',
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return datetime.now()  # Fallback to current time