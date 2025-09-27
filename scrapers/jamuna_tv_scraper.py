import time
import random
import requests
from typing import List, Optional
from datetime import datetime
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from models.article import Article
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class JamunaTVScraper(BaseScraper):
    """Scraper for Jamuna TV (jamuna.tv)"""
    
    def __init__(self):
        super().__init__("Jamuna TV", "https://jamuna.tv")
        # Additional headers are handled in _make_request method
    
    def _get_article_urls(self, max_articles: int) -> List[str]:
        """Get article URLs from Jamuna TV homepage and category pages"""
        article_urls = []
        
        # Main categories to scrape
        categories = [
            "",  # Homepage
            "/news",
            "/politics", 
            "/international",
            "/business",
            "/sports",
            "/entertainment"
        ]
        
        for category in categories:
            if len(article_urls) >= max_articles:
                break
                
            category_url = f"{self.base_url}{category}"
            response = self._make_request(category_url)
            
            if not response:
                continue
            
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find article links
                link_selectors = [
                    'article a[href]',
                    '.news-item a[href]',
                    '.story-item a[href]',
                    '.post-item a[href]',
                    '.article-item a[href]',
                    'h2 a[href]',
                    'h3 a[href]',
                    'a[href*="/news/"]',
                    'a[href*="/politics/"]',
                    'a[href*="/international/"]',
                    'a[href*="/business/"]',
                    'a[href*="/sports/"]',
                    'a[href*="/entertainment/"]'
                ]
                
                for selector in link_selectors:
                    links = soup.select(selector)
                    for link in links:
                        href = link.get('href')
                        if href:
                            # Convert relative URLs to absolute
                            if href.startswith('/'):
                                full_url = f"{self.base_url}{href}"
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                continue
                            
                            # Filter out non-article URLs
                            if self._is_valid_article_url(full_url) and full_url not in article_urls:
                                article_urls.append(full_url)
                                
                                if len(article_urls) >= max_articles:
                                    break
                    
                    if len(article_urls) >= max_articles:
                        break
                        
            except Exception as e:
                logger.error(f"Failed to extract URLs from {category_url}: {e}")
                continue
        
        return article_urls[:max_articles]
    

    
    def _is_valid_article_url(self, url: str) -> bool:
        """Check if URL is a valid article URL for Jamuna TV"""
        if not url or not url.startswith('https://jamuna.tv'):
            return False
        
        # Skip unwanted URLs
        skip_patterns = [
            '/search', '/tag/', '/author/', '/category/',
            '/login', '/register', '/admin', '/wp-admin',
            '/feed', '/rss', '/sitemap', '/robots.txt',
            '/advertisement', '/ads/', '/banner',
            '/share', '/print', '/email', '/contact',
            '/about', '/privacy', '/terms',
            'javascript:', 'mailto:', 'tel:', '#'
        ]
        
        if any(pattern in url.lower() for pattern in skip_patterns):
            return False
        
        # Check for article-like patterns
        article_patterns = [
            '/news/', '/politics/', '/international/',
            '/business/', '/sports/', '/entertainment/',
            '/lifestyle/', '/technology/', '/opinion/',
            '/bangladesh/', '/world/', '/economy/'
        ]
        
        # URL should either have article patterns or be deep enough to be an article
        has_article_pattern = any(pattern in url.lower() for pattern in article_patterns)
        is_deep_url = len(url.split('/')) >= 4
        
        return has_article_pattern or is_deep_url
    
    def _extract_article_content(self, soup: BeautifulSoup, url: str) -> Optional[Article]:
        """Extract article content from Jamuna TV"""
        try:
            # Extract title
            title = self._extract_title_jamuna(soup)
            if not title:
                logger.warning(f"Could not extract title from {url}")
                return None
            
            # Extract content
            content = self._extract_content_jamuna(soup)
            if not content or len(content) < 100:
                logger.warning(f"Could not extract sufficient content from {url}")
                return None
            
            # Extract metadata
            author = self._extract_author_jamuna(soup)
            publication_date = self._extract_publication_date_jamuna(soup)
            
            if not publication_date:
                publication_date = datetime.now()
            
            # Detect language (Jamuna TV is primarily Bengali)
            language = self._detect_language(f"{title} {content}")
            if not language or language == 'unknown':
                language = 'bengali'  # Default for Jamuna TV
            
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
    
    def _extract_title_jamuna(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract title specifically for Jamuna TV"""
        title_selectors = [
            'h1.entry-title',
            'h1.post-title',
            'h1.article-title',
            '.news-title h1',
            '.story-title h1',
            'article h1',
            '.content-header h1',
            'h1',
            '.title',
            '.headline'
        ]
        
        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem and elem.get_text().strip():
                title = self._clean_text(elem.get_text())
                if len(title) > 10:  # Ensure it's a meaningful title
                    return title
        
        # Fallback to page title
        title_elem = soup.find('title')
        if title_elem:
            title = self._clean_text(title_elem.get_text())
            # Remove site name from title
            title = title.replace('- Jamuna TV', '').replace('| Jamuna TV', '').strip()
            if len(title) > 10:
                return title
        
        return None
    
    def _extract_content_jamuna(self, soup: BeautifulSoup) -> str:
        """Extract content specifically for Jamuna TV"""
        content_selectors = [
            '.entry-content',
            '.post-content',
            '.article-content',
            '.news-content',
            '.story-content',
            'article .content',
            '.main-content',
            'article',
            '.content'
        ]
        
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                # Remove unwanted elements
                for unwanted in elem.select('script, style, .advertisement, .ad, .social-share, .related-articles, .comments, .sidebar, nav, footer, header'):
                    unwanted.decompose()
                
                content = self._clean_text(elem.get_text())
                if len(content) > 200:  # Minimum content threshold
                    return content
        
        # Fallback: collect all paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            content = ' '.join([self._clean_text(p.get_text()) for p in paragraphs])
            if len(content) > 200:
                return content
        
        # Last resort: get all text content
        content = self._clean_text(soup.get_text())
        return content
    
    def _extract_author_jamuna(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author specifically for Jamuna TV"""
        author_selectors = [
            '.author-name',
            '.byline .author',
            '.post-author',
            '.entry-author',
            '.story-author',
            '[data-author]',
            '.author',
            '.by-author'
        ]
        
        for selector in author_selectors:
            elem = soup.select_one(selector)
            if elem and elem.get_text().strip():
                author = self._clean_text(elem.get_text())
                # Clean up common prefixes
                author = author.replace('By ', '').replace('by ', '').replace('লেখক:', '').strip()
                if len(author) > 2:
                    return author
        
        return None
    
    def _extract_publication_date_jamuna(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract publication date specifically for Jamuna TV"""
        date_selectors = [
            'time[datetime]',
            '.publish-date',
            '.post-date',
            '.entry-date',
            '.news-date',
            '.story-date',
            '[data-publish-date]',
            '.date',
            '.published'
        ]
        
        for selector in date_selectors:
            elem = soup.select_one(selector)
            if elem:
                date_str = elem.get('datetime') or elem.get('content') or elem.get_text()
                if date_str:
                    parsed_date = self._parse_date(date_str)
                    if parsed_date:
                        return parsed_date
        
        # Look for date patterns in meta tags
        meta_date = soup.find('meta', {'property': 'article:published_time'})
        if meta_date and meta_date.get('content'):
            parsed_date = self._parse_date(meta_date.get('content'))
            if parsed_date:
                return parsed_date
        
        return None
    
