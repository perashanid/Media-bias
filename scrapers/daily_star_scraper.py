from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from models.article import Article
from scrapers.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class DailyStarScraper(BaseScraper):
    """Scraper for The Daily Star (https://www.thedailystar.net/)"""
    
    def __init__(self):
        super().__init__("The Daily Star", "https://www.thedailystar.net")
    
    def _get_article_urls(self, max_articles: int) -> List[str]:
        """Get article URLs from The Daily Star homepage and category pages"""
        article_urls = []
        
        # Main categories to scrape
        categories = [
            "",  # Homepage
            "/news/bangladesh",  # Bangladesh news
            "/news/world",  # World news
            "/business",  # Business
            "/sports",  # Sports
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
                
                # Find article links - Updated selectors based on current structure
                link_selectors = [
                    'a[href*="/news/"]',  # Primary news links
                    'a[href*="/business/"]',
                    'a[href*="/sports/"]',
                    'a[href*="/lifestyle/"]',
                    'a[href*="/opinion/"]',
                    'h1 a', 'h2 a', 'h3 a', 'h4 a',  # Headlines
                    '.story a', '.article a', '.news a'  # Generic article containers
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
                logger.error(f"Failed to extract URLs from {category_url}: {e}")
                continue
        
        return article_urls[:max_articles]
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL is likely an article URL"""
        # The Daily Star article URLs typically contain these patterns
        article_patterns = [
            '/news/',
            '/business/',
            '/sports/',
            '/lifestyle/',
            '/opinion/',
            '/editorial/',
            '/city/',
            '/health/',
            '/star-youth/',
            '/showbiz/',
            '/slow-reads/',
            '/star-multimedia/'
        ]
        
        # Exclude non-article URLs
        exclude_patterns = [
            '/live-news/',
            '/video/',
            '/photo/',
            '/gallery/',
            '/tag/',
            '/author/',
            '/search',
            '/page/',
            '.jpg',
            '.png',
            '.pdf',
            '/homepage',
            '/archive'
        ]
        
        # Check if URL contains article patterns and doesn't contain exclude patterns
        has_article_pattern = any(pattern in url for pattern in article_patterns)
        has_exclude_pattern = any(pattern in url for pattern in exclude_patterns)
        
        # Additional validation - URL should be deep enough to be an article (more than just category)
        is_deep_url = len(url.split('/')) >= 5  # Changed from 4 to 5 to avoid category pages
        
        # Also check if URL has article-like structure (contains year or article ID)
        import re
        has_article_structure = (
            re.search(r'/\d{4}/', url) or  # Contains year
            re.search(r'-\d{6,}', url) or  # Contains article ID
            len(url.split('/')) >= 6  # Very deep URL likely to be article
        )
        
        return has_article_pattern and not has_exclude_pattern and (is_deep_url or has_article_structure)
    
    def _extract_article_content(self, soup: BeautifulSoup, url: str) -> Optional[Article]:
        """Extract article content from The Daily Star page"""
        try:
            # Extract title
            title_selectors = [
                'h1.headline',
                'h1.title',
                '.story-headline h1',
                '.article-title h1',
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
            
            # Extract content - Updated selectors based on current structure
            content_selectors = [
                '.story-content',
                '.article-content', 
                '.news-content',
                '.content-body',
                '.story-body',
                'article',  # Generic article tag
                '.post-content',
                '.entry-content'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove unwanted elements
                    for unwanted in content_elem.select('script, style, .advertisement, .ad, .social-share, .related-news, .sidebar, nav, header, footer'):
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
                '.story-author',
                '.author-info .name',
                '[data-author]'
            ]
            
            author = None
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = self._clean_text(author_elem.get_text())
                    # Clean author text (remove "By" prefix if present)
                    if author.lower().startswith('by '):
                        author = author[3:].strip()
                    break
            
            # Extract publication date
            date_selectors = [
                '.publish-date',
                '.story-date',
                '.date-time',
                'time[datetime]',
                '.meta-date',
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
            
            # Detect language (The Daily Star is primarily English)
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