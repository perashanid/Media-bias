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
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]
        self.max_retries = 3
        self.base_delay = 2.0  # Increased from 1.0
        self.max_delay = 15.0  # Increased from 10.0
        
    def _get_random_user_agent(self) -> str:
        """Get a random user agent for requests"""
        return random.choice(self.user_agents)
    
    def _handle_rate_limiting(self, attempt: int = 0):
        """Implement exponential backoff for rate limiting"""
        if attempt > 0:
            delay = min(self.base_delay * (2 ** attempt) + random.uniform(0, 2), self.max_delay)
            logger.info(f"Rate limiting detected, waiting {delay:.2f} seconds")
            time.sleep(delay)
        else:
            # Base delay between requests - increased significantly
            time.sleep(random.uniform(2.0, 4.0))
    
    def _make_request(self, url: str, attempt: int = 0) -> Optional[requests.Response]:
        """Make HTTP request with retry logic and rate limiting"""
        try:
            self._handle_rate_limiting(attempt)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(url, headers=headers, timeout=45)  # Increased timeout
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
        """Scrape articles from the news source with enhanced monitoring"""
        start_time = time.time()
        articles = []
        
        try:
            logger.info(f"🚀 Starting to scrape articles from {self.source_name} (max: {max_articles})")
            
            # Get article URLs from the main page or category pages
            url_start_time = time.time()
            article_urls = self._get_article_urls(max_articles)
            url_extraction_time = time.time() - url_start_time
            
            logger.info(f"📋 Found {len(article_urls)} article URLs in {url_extraction_time:.2f}s")
            
            if not article_urls:
                logger.warning(f"⚠️ No article URLs found for {self.source_name}")
                return []
            
            successful_scrapes = 0
            failed_scrapes = 0
            
            for i, url in enumerate(article_urls):
                try:
                    article_start_time = time.time()
                    article = self._scrape_single_article(url)
                    article_time = time.time() - article_start_time
                    
                    if article:
                        articles.append(article)
                        successful_scrapes += 1
                        logger.debug(f"✅ [{i+1}/{len(article_urls)}] Scraped: {article.title[:50]}... ({article_time:.2f}s)")
                    else:
                        failed_scrapes += 1
                        logger.debug(f"❌ [{i+1}/{len(article_urls)}] Failed to extract content from {url}")
                    
                except Exception as e:
                    failed_scrapes += 1
                    logger.error(f"❌ [{i+1}/{len(article_urls)}] Error scraping {url}: {e}")
                    continue
            
            total_time = time.time() - start_time
            success_rate = (successful_scrapes / len(article_urls) * 100) if article_urls else 0
            
            logger.info(f"🎯 {self.source_name} completed: {successful_scrapes}/{len(article_urls)} articles ({success_rate:.1f}%) in {total_time:.2f}s")
            
            if failed_scrapes > 0:
                logger.warning(f"⚠️ {self.source_name}: {failed_scrapes} articles failed to scrape")
            
            return articles
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"❌ Failed to scrape articles from {self.source_name} after {total_time:.2f}s: {e}")
            return articles  # Return any articles we managed to scrape
    
    def _scrape_single_article(self, url: str) -> Optional[Article]:
        """Scrape a single article from its URL"""
        response = self._make_request(url)
        if not response:
            return None
        
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
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
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
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
            title_selectors = [
                'h1', 'title', '.title', '.headline', '.article-title',
                '.news-title', '.story-title', '.post-title', '.entry-title'
            ]
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem and title_elem.get_text().strip():
                    title = self._clean_text(title_elem.get_text())
                    # Remove site name from title if present
                    if ' - ' in title:
                        title = title.split(' - ')[0].strip()
                    if ' | ' in title:
                        title = title.split(' | ')[0].strip()
                    if len(title) > 10:  # Ensure meaningful title
                        break
            
            if not title or len(title) < 10:
                # Try meta title
                meta_title = soup.find('meta', {'property': 'og:title'})
                if meta_title and meta_title.get('content'):
                    title = self._clean_text(meta_title.get('content'))
                else:
                    title = "Untitled Article"
            
            # Try to find content
            content = ""
            content_selectors = [
                '.article-content', '.content', '.post-content', 
                '.entry-content', 'article', '.article-body',
                '.news-content', '.story-content', '.main-content',
                '.content-body', '.news-details', '.description'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove unwanted elements
                    for unwanted in content_elem.select('script, style, .advertisement, .ad, .social-share, .related-news, .comments, .sidebar, nav, header, footer'):
                        unwanted.decompose()
                    content = self._clean_text(content_elem.get_text())
                    if len(content) > 200:  # Higher minimum content length
                        break
            
            # If no content found, try paragraphs
            if len(content) < 200:
                paragraphs = soup.find_all('p')
                content_parts = []
                for p in paragraphs:
                    p_text = self._clean_text(p.get_text())
                    if len(p_text) > 30:  # Skip very short paragraphs
                        content_parts.append(p_text)
                content = ' '.join(content_parts)
            
            # Final fallback - try meta description
            if len(content) < 100:
                meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
                if meta_desc and meta_desc.get('content'):
                    content = self._clean_text(meta_desc.get('content'))
            
            if len(content) < 50:
                logger.warning(f"Insufficient content extracted from {url}")
                return None
            
            # Try to detect source from URL
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            source = parsed_url.netloc.replace('www.', '')
            
            # Try to extract author
            author = None
            author_selectors = ['.author', '.byline', '.author-name', '.writer', '.reporter']
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = self._clean_text(author_elem.get_text())
                    if len(author) > 2 and len(author) < 100:
                        break
            
            # Try to extract publication date
            publication_date = None
            date_selectors = ['time[datetime]', '.date', '.publish-date', '.news-date']
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date_str = date_elem.get('datetime') or date_elem.get_text()
                    publication_date = self._parse_date(date_str)
                    if publication_date:
                        break
            
            if not publication_date:
                publication_date = datetime.now()
            
            # Detect language
            language = self._detect_language(f"{title} {content}")
            
            return Article(
                title=title,
                content=content,
                url=url,
                source=source,
                publication_date=publication_date,
                scraped_at=datetime.now(),
                language=language,
                author=author
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
        
        # Remove common unwanted patterns (both English and Bengali)
        unwanted_patterns = [
            'Advertisement', 'বিজ্ঞাপন',
            'Click here to', 'এখানে ক্লিক করুন',
            'Read more:', 'আরও পড়ুন:',
            'Subscribe to', 'সাবস্ক্রাইব করুন',
            'Follow us on', 'আমাদের ফলো করুন',
            'Share this:', 'শেয়ার করুন:',
            'Loading...', 'লোড হচ্ছে...',
            'Comments', 'মন্তব্য',
            'Related News', 'সংশ্লিষ্ট সংবাদ',
            'More News', 'আরও সংবাদ',
            'Breaking News', 'জরুরি সংবাদ',
            'Live Updates', 'সরাসরি আপডেট'
        ]
        
        for pattern in unwanted_patterns:
            text = text.replace(pattern, '')
        
        # Remove URLs
        import re
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        return text.strip()
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        # Clean the date string
        date_str = date_str.strip()
        
        # Handle ISO format with timezone
        try:
            from dateutil import parser
            return parser.parse(date_str)
        except:
            pass
        
        # Common date formats to try
        date_formats = [
            '%Y-%m-%dT%H:%M:%S%z',  # ISO format with timezone
            '%Y-%m-%dT%H:%M:%S',    # ISO format without timezone
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%B %d, %Y',
            '%d %B %Y',
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.debug(f"Could not parse date: {date_str}")
        return datetime.now()  # Fallback to current time