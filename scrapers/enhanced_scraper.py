import time
import random
import requests
from typing import List, Optional, Set
from datetime import datetime
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from models.article import Article
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class EnhancedScraper(BaseScraper):
    """Enhanced scraper that can crawl entire websites by following all links"""
    
    def __init__(self, source_name: str, base_url: str):
        super().__init__(source_name, base_url)
        self.visited_urls: Set[str] = set()
        self.article_urls: Set[str] = set()
        self.max_depth = 3  # Maximum crawling depth
        self.max_pages_per_depth = 50  # Maximum pages to visit per depth level
        
    def crawl_website(self, max_articles: int = 100, max_depth: int = 3) -> List[Article]:
        """Crawl the entire website by following all links"""
        self.max_depth = max_depth
        self.visited_urls.clear()
        self.article_urls.clear()
        
        logger.info(f"Starting comprehensive crawl of {self.source_name} (max_depth={max_depth})")
        
        # Start crawling from the base URL
        self._crawl_recursive(self.base_url, 0, max_articles)
        
        # Now scrape all discovered article URLs
        articles = []
        article_urls_list = list(self.article_urls)[:max_articles]
        
        logger.info(f"Found {len(self.article_urls)} potential article URLs, scraping {len(article_urls_list)}")
        
        for i, url in enumerate(article_urls_list):
            try:
                logger.info(f"Scraping article {i+1}/{len(article_urls_list)}: {url}")
                article = self._scrape_single_article(url)
                if article:
                    articles.append(article)
                    logger.info(f"Successfully scraped: {article.title[:50]}...")
                else:
                    logger.warning(f"Failed to extract content from: {url}")
                    
                # Add delay between requests
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"Failed to scrape article {url}: {e}")
                continue
        
        logger.info(f"Crawling completed. Scraped {len(articles)} articles from {self.source_name}")
        return articles
    
    def _crawl_recursive(self, url: str, depth: int, max_articles: int):
        """Recursively crawl website following all links"""
        if depth > self.max_depth or len(self.article_urls) >= max_articles:
            return
        
        if url in self.visited_urls:
            return
        
        # Check if URL belongs to the same domain
        if not self._is_same_domain(url):
            return
        
        self.visited_urls.add(url)
        logger.debug(f"Crawling (depth {depth}): {url}")
        
        try:
            response = self._make_request(url)
            if not response:
                return
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if this page is an article
            if self._is_article_page(soup, url):
                self.article_urls.add(url)
                logger.info(f"Found article: {url}")
            
            # Find all links on this page
            links = soup.find_all('a', href=True)
            page_links = []
            
            for link in links:
                href = link['href']
                full_url = urljoin(url, href)
                
                # Filter out unwanted URLs
                if self._should_follow_link(full_url):
                    page_links.append(full_url)
            
            logger.info(f"Found {len(page_links)} valid links on {url} (depth {depth})")
            
            # Limit the number of links to follow per page to avoid infinite crawling
            random.shuffle(page_links)
            page_links = page_links[:self.max_pages_per_depth]
            
            # Recursively crawl found links
            for link_url in page_links:
                if len(self.article_urls) >= max_articles:
                    break
                self._crawl_recursive(link_url, depth + 1, max_articles)
                
        except Exception as e:
            logger.error(f"Failed to crawl {url}: {e}")
    
    def _is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain as base_url"""
        try:
            base_domain = urlparse(self.base_url).netloc
            url_domain = urlparse(url).netloc
            return url_domain == base_domain or url_domain == f"www.{base_domain}" or base_domain == f"www.{url_domain}"
        except:
            return False
    
    def _should_follow_link(self, url: str) -> bool:
        """Determine if we should follow this link"""
        if not url or url in self.visited_urls:
            return False
        
        # Skip non-HTTP URLs
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Skip file downloads
        skip_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', 
                          '.zip', '.rar', '.tar', '.gz', '.jpg', '.jpeg', '.png', 
                          '.gif', '.bmp', '.svg', '.mp4', '.avi', '.mov', '.mp3', '.wav']
        
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip certain URL patterns - be more specific to avoid blocking legitimate articles
        skip_patterns = [
            '/search', '/tag/', '/author/', '/category/',
            '/login', '/register', '/admin', '/wp-admin',
            '/feed', '/rss', '/sitemap', '/robots.txt',
            'javascript:', 'mailto:', 'tel:', '#',
            '/advertisement', '/ads/', '/banner',
            '/share', '/print', '/email',
            '/api/auth/',  # Skip OAuth/API authentication URLs
            '/oauth/',
            '/callback'
        ]
        
        if any(pattern in url.lower() for pattern in skip_patterns):
            return False
        
        return True
    
    def _is_article_page(self, soup: BeautifulSoup, url: str) -> bool:
        """Determine if this page contains an article"""
        # Skip homepage and category pages
        if url.rstrip('/') == self.base_url.rstrip('/'):
            return False
        
        # Check for common article indicators
        article_indicators = [
            # HTML5 article tag
            soup.find('article'),
            # Common article content classes/IDs
            soup.find(class_=lambda x: x and any(term in x.lower() for term in 
                     ['article', 'story', 'news', 'post', 'content'])),
            soup.find(id=lambda x: x and any(term in x.lower() for term in 
                     ['article', 'story', 'news', 'post', 'content'])),
            # Multiple paragraphs (likely article content)
            len(soup.find_all('p')) > 2,
            # Article-like URL patterns
            any(pattern in url.lower() for pattern in [
                '/news/', '/article/', '/story/', '/post/',
                '/bangladesh/', '/politics/', '/international/',
                '/business/', '/sports/', '/entertainment/',
                '/opinion/', '/lifestyle/', '/technology/',
                '/health/', '/education/', '/economics/'
            ])
        ]
        
        # Must have a title
        title_found = bool(soup.find('h1') or soup.find('title'))
        
        # Must have substantial text content (reduced threshold)
        text_content = soup.get_text()
        has_content = len(text_content.strip()) > 300
        
        # Check if any article indicators are present
        has_indicators = any(article_indicators)
        
        # More permissive: if it has content and title, and URL looks like an article, consider it an article
        url_looks_like_article = len(url.split('/')) >= 4 and not any(skip in url.lower() for skip in [
            '/category/', '/tag/', '/author/', '/search', '/page/', '/api/', '/auth/'
        ])
        
        return title_found and has_content and (has_indicators or url_looks_like_article)
    
    def _get_article_urls(self, max_articles: int) -> List[str]:
        """Override base method - not used in enhanced scraper"""
        return []
    
    def _extract_article_content(self, soup: BeautifulSoup, url: str) -> Optional[Article]:
        """Extract article content using enhanced methods"""
        try:
            # Extract title with multiple fallbacks
            title = self._extract_title(soup)
            if not title:
                logger.warning(f"Could not extract title from {url}")
                return None
            
            # Extract content with multiple fallbacks
            content = self._extract_content(soup)
            if not content or len(content) < 100:
                logger.warning(f"Could not extract sufficient content from {url}")
                return None
            
            # Extract metadata
            author = self._extract_author(soup)
            publication_date = self._extract_publication_date(soup)
            
            if not publication_date:
                publication_date = datetime.now()
            
            # Detect language
            language = self._detect_language(f"{title} {content}")
            
            return Article(
                url=url,
                title=title,
                content=content,
                author=author,
                publication_date=publication_date,
                source=self.source_name,
                scraped_at=datetime.now(),
                language=language
            )
            
        except Exception as e:
            logger.error(f"Failed to extract article content from {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title with multiple fallbacks"""
        title_selectors = [
            'h1.title', 'h1.headline', 'h1.article-title',
            '.story-title h1', '.news-title h1', '.post-title h1',
            'article h1', 'main h1', '.content h1',
            'h1', '.title', '.headline'
        ]
        
        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem and elem.get_text().strip():
                return self._clean_text(elem.get_text())
        
        # Fallback to page title
        title_elem = soup.find('title')
        if title_elem:
            return self._clean_text(title_elem.get_text())
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article content with multiple fallbacks"""
        content_selectors = [
            'article .content', 'article .article-content', 'article .story-content',
            '.article-body', '.story-body', '.news-content', '.post-content',
            '.entry-content', '.main-content', 'main article',
            'article', '.content', 'main'
        ]
        
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                # Remove unwanted elements
                for unwanted in elem.select('script, style, .advertisement, .ad, .social-share, .related-articles'):
                    unwanted.decompose()
                
                content = self._clean_text(elem.get_text())
                if len(content) > 200:  # Minimum content threshold
                    return content
        
        # Fallback: collect all paragraphs
        paragraphs = soup.find_all('p')
        content = ' '.join([self._clean_text(p.get_text()) for p in paragraphs])
        
        return content
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article author"""
        author_selectors = [
            '.author-name', '.byline .author', '.story-author',
            '[data-author]', '.author', '.by-author',
            '.post-author', '.article-author'
        ]
        
        for selector in author_selectors:
            elem = soup.select_one(selector)
            if elem and elem.get_text().strip():
                return self._clean_text(elem.get_text())
        
        return None
    
    def _extract_publication_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract publication date"""
        date_selectors = [
            'time[datetime]', '.publish-date', '.story-date',
            '.news-date', '[data-publish-date]', '.date',
            '.post-date', '.article-date'
        ]
        
        for selector in date_selectors:
            elem = soup.select_one(selector)
            if elem:
                date_str = elem.get('datetime') or elem.get_text()
                if date_str:
                    parsed_date = self._parse_date(date_str)
                    if parsed_date:
                        return parsed_date
        
        return None