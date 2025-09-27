from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from models.article import Article
from scrapers.base_scraper import BaseScraper
import logging
import time
import random
import requests

logger = logging.getLogger(__name__)


class SomoyNewsScraper(BaseScraper):
    """Scraper for Somoy News (https://www.somoynews.tv/)"""
    
    def __init__(self):
        super().__init__("Somoy News", "https://www.somoynews.tv")
        # Override headers for better success rate
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
        ]
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent for requests"""
        return random.choice(self.user_agents)
    
    def _make_request(self, url: str, attempt: int = 0) -> Optional[requests.Response]:
        """Override to add better anti-blocking measures"""
        try:
            # Add longer delays for Somoy News
            if attempt > 0:
                delay = min(self.base_delay * (2 ** attempt) + random.uniform(2, 5), self.max_delay)
                logger.info(f"Rate limiting detected, waiting {delay:.2f} seconds")
                time.sleep(delay)
            else:
                # Base delay between requests - longer for Somoy News
                time.sleep(random.uniform(2, 4))
            
            headers = {
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
                'DNT': '1'
            }
            
            response = self.session.get(url, headers=headers, timeout=30, allow_redirects=True)
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
    
    def _get_article_urls(self, max_articles: int) -> List[str]:
        """Get article URLs from Somoy News homepage and alternative approaches"""
        article_urls = []
        
        # Try multiple approaches since main site might be blocked
        approaches = [
            "",  # Homepage
            "/sitemap.xml",  # Try sitemap
            "/rss",  # Try RSS
            "/feed",  # Try feed
        ]
        
        for approach in approaches:
            if len(article_urls) >= max_articles:
                break
                
            if approach.startswith('/'):
                url = f"{self.base_url}{approach}"
            else:
                url = f"{self.base_url}/{approach}" if approach else self.base_url
                
            response = self._make_request(url)
            
            if not response:
                continue
            
            try:
                if 'xml' in approach:
                    # Handle XML/RSS feeds
                    soup = BeautifulSoup(response.content, 'xml')
                    
                    # Look for RSS items or sitemap URLs
                    items = soup.find_all(['item', 'url'])
                    for item in items:
                        link_elem = item.find('link') or item.find('loc')
                        if link_elem:
                            link_url = link_elem.get_text()
                            if self._is_article_url(link_url) and link_url not in article_urls:
                                article_urls.append(link_url)
                                if len(article_urls) >= max_articles:
                                    break
                else:
                    # Handle regular HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for article links
                    link_selectors = [
                        'a[href*="/news/"]',
                        'a[href*="/article/"]',
                        'a[href*="/story/"]',
                        'a[href*="/details/"]',
                        'a[href*="/2025/"]',
                        'a[href*="/2024/"]',
                        'h1 a',
                        'h2 a',
                        'h3 a',
                        'h4 a'
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
                                if self._is_article_url(full_url) and full_url not in article_urls:
                                    article_urls.append(full_url)
                                    
                                    if len(article_urls) >= max_articles:
                                        break
                        
                        if len(article_urls) >= max_articles:
                            break
                        
            except Exception as e:
                logger.error(f"Failed to extract URLs from {url}: {e}")
                continue
        
        return article_urls[:max_articles]
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL is likely an article URL"""
        # Somoy News article URL patterns (need to discover actual patterns)
        article_patterns = [
            '/news/',
            '/article/',
            '/story/',
            '/details/',
            '/post/',
            '/bangladesh/',
            '/politics/',
            '/international/',
            '/sports/',
            '/entertainment/',
            '/business/'
        ]
        
        # Exclude non-article URLs
        exclude_patterns = [
            '/live/',
            '/video/',
            '/photo/',
            '/gallery/',
            '/tag/',
            '/author/',
            '/search',
            '/page/',
            '/category/',
            '/archive/',
            '.jpg',
            '.png',
            '.pdf',
            '.gif',
            '.mp4',
            '/assets/',
            '/css/',
            '/js/',
            '/contact',
            '/about',
            'javascript:',
            'mailto:',
            '#'
        ]
        
        # Must be from Somoy News domain
        if 'somoynews.tv' not in url:
            return False
        
        # Check if URL contains article patterns and doesn't contain exclude patterns
        has_article_pattern = any(pattern in url for pattern in article_patterns)
        has_exclude_pattern = any(pattern in url for pattern in exclude_patterns)
        
        # Must have some content in the URL (not just domain)
        has_content = len(url.split('/')[-1]) > 0
        
        return has_article_pattern and not has_exclude_pattern and has_content
    
    def _extract_article_content(self, soup: BeautifulSoup, url: str) -> Optional[Article]:
        """Extract article content from Somoy News page"""
        try:
            # Extract title
            title_selectors = [
                'h1.title',
                'h1.headline',
                '.news-title h1',
                '.story-title h1',
                '.article-title h1',
                '.post-title h1',
                'h1'
            ]
            
            title = None
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = self._clean_text(title_elem.get_text())
                    break
            
            if not title:
                logger.warning(f"Could not extract title from {url}")
                return None
            
            # Extract content
            content_selectors = [
                '.news-content',
                '.story-content',
                '.article-content',
                '.content-body',
                '.post-content',
                '.entry-content',
                'article',
                '.news-details',
                '.description',
                '.news-body'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove unwanted elements
                    for unwanted in content_elem.select('script, style, .advertisement, .ad, .social-share, .related-news, .video-player, .sidebar, nav, header, footer'):
                        unwanted.decompose()
                    
                    content = self._clean_text(content_elem.get_text())
                    if len(content) > 100:  # Ensure we have substantial content
                        break
            
            # Fallback: try to get content from paragraphs if main content not found
            if len(content) < 100:
                paragraphs = soup.find_all('p')
                content_parts = []
                for p in paragraphs:
                    p_text = self._clean_text(p.get_text())
                    if len(p_text) > 20:  # Skip very short paragraphs
                        content_parts.append(p_text)
                content = ' '.join(content_parts)
            
            if not content:
                logger.warning(f"Could not extract content from {url}")
                return None
            
            # Extract author
            author_selectors = [
                '.author-name',
                '.byline',
                '.news-author',
                '.reporter-name',
                '.author-info',
                '.correspondent',
                '[data-author]'
            ]
            
            author = None
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = self._clean_text(author_elem.get_text())
                    # Clean author text (remove common prefixes)
                    prefixes = ['প্রতিবেদক:', 'সংবাদদাতা:', 'By ', 'লিখেছেন:', 'Reporter:', 'Correspondent:']
                    for prefix in prefixes:
                        if author.startswith(prefix):
                            author = author[len(prefix):].strip()
                            break
                    break
            
            # Extract publication date
            date_selectors = [
                '.publish-date',
                '.news-date',
                '.date-time',
                'time[datetime]',
                '.meta-date',
                '.published-date',
                '.post-date',
                '[data-publish-date]'
            ]
            
            publication_date = None
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date_str = date_elem.get('datetime') or date_elem.get_text()
                    publication_date = self._parse_date(date_str)
                    break
            
            if not publication_date:
                publication_date = datetime.now()
            
            # Detect language (Somoy News is primarily Bengali)
            language = self._detect_language(f"{title} {content}")
            
            # Create Article object
            article = Article(
                url=url,
                title=title,
                content=content,
                author=author,
                publication_date=publication_date,
                source=self.source_name,
                scraped_at=datetime.now(),
                language=language
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Failed to extract article content from {url}: {e}")
            return None