from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from models.article import Article
from scrapers.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class ProthomAloScraper(BaseScraper):
    """Scraper for Prothom Alo (https://www.prothomalo.com/)"""
    
    def __init__(self):
        super().__init__("Prothom Alo", "https://www.prothomalo.com")
    
    def _get_article_urls(self, max_articles: int) -> List[str]:
        """Get article URLs from Prothom Alo homepage and category pages"""
        article_urls = []
        
        # Main categories to scrape
        categories = [
            "",  # Homepage
            "/bangladesh",
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
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find article links - Prothom Alo uses various link patterns
                link_selectors = [
                    'a[href*="/bangladesh/"]',
                    'a[href*="/politics/"]',
                    'a[href*="/international/"]',
                    'a[href*="/business/"]',
                    'a[href*="/sports/"]',
                    'a[href*="/entertainment/"]',
                    '.story-card a',
                    '.news-card a',
                    'h2 a',
                    'h3 a'
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
        # Prothom Alo article URLs typically contain these patterns
        article_patterns = [
            '/bangladesh/',
            '/politics/',
            '/international/',
            '/business/',
            '/sports/',
            '/entertainment/',
            '/opinion/',
            '/lifestyle/'
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
            '.jpg',
            '.png',
            '.pdf'
        ]
        
        # Check if URL contains article patterns and doesn't contain exclude patterns
        has_article_pattern = any(pattern in url for pattern in article_patterns)
        has_exclude_pattern = any(pattern in url for pattern in exclude_patterns)
        
        return has_article_pattern and not has_exclude_pattern
    
    def _extract_article_content(self, soup: BeautifulSoup, url: str) -> Optional[Article]:
        """Extract article content from Prothom Alo page"""
        try:
            # Extract title
            title_selectors = [
                'h1.title',
                'h1.headline',
                '.story-title h1',
                '.news-title h1',
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
                '.story-content',
                '.news-content',
                '.article-content',
                '.content-body',
                '[data-story-content]'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove unwanted elements
                    for unwanted in content_elem.select('script, style, .advertisement, .ad, .social-share'):
                        unwanted.decompose()
                    
                    content = self._clean_text(content_elem.get_text())
                    break
            
            if not content:
                logger.warning(f"Could not extract content from {url}")
                return None
            
            # Extract author
            author_selectors = [
                '.author-name',
                '.byline .author',
                '.story-author',
                '[data-author]'
            ]
            
            author = None
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = self._clean_text(author_elem.get_text())
                    break
            
            # Extract publication date
            date_selectors = [
                '.publish-date',
                '.story-date',
                '.news-date',
                'time[datetime]',
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
            
            # Detect language
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