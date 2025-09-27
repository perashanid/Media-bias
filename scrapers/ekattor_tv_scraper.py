from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from models.article import Article
from scrapers.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class EkattorTVScraper(BaseScraper):
    """Scraper for Ekattor TV (https://ekattor.tv/)"""
    
    def __init__(self):
        super().__init__("Ekattor TV", "https://ekattor.tv")
    
    def _get_article_urls(self, max_articles: int) -> List[str]:
        """Get article URLs from Ekattor TV homepage and category pages"""
        article_urls = []
        
        # Focus on homepage for better results
        categories = [
            "",  # Homepage
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
                
                # Updated selectors based on debug findings
                link_selectors = [
                    'a[href*="/news/"]',  # Main news articles
                    'h2 a',  # Headlines
                    'a[href*="/national/"]',
                    'a[href*="/politics/"]',
                    'a[href*="/international/"]',
                    'a[href*="/capital/"]',
                    'a[href*="/business/"]',
                    'a[href*="/sports/"]',
                    'a[href*="/entertainment/"]'
                ]
                
                for selector in link_selectors:
                    links = soup.select(selector)
                    for link in links:
                        href = link.get('href')
                        if href:
                            # Handle relative URLs
                            if href.startswith('//ekattor.tv/'):
                                full_url = f"https:{href}"
                            elif href.startswith('/'):
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
        # Ekattor TV article URLs typically contain these patterns
        article_patterns = [
            '/news/',
            '/national/',
            '/politics/',
            '/international/',
            '/capital/',
            '/business/',
            '/sports/',
            '/entertainment/',
            '/lifestyle/',
            '/country/'
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
            '/tv-schedule/',
            '.jpg',
            '.png',
            '.pdf',
            '/archive',
            '/category'
        ]
        
        # Must have article ID pattern (numbers at the end)
        import re
        has_article_id = re.search(r'/\d{5}/', url) or '/news/' in url
        
        # Check if URL contains article patterns and doesn't contain exclude patterns
        has_article_pattern = any(pattern in url for pattern in article_patterns)
        has_exclude_pattern = any(pattern in url for pattern in exclude_patterns)
        
        return has_article_pattern and not has_exclude_pattern and has_article_id
    
    def _extract_article_content(self, soup: BeautifulSoup, url: str) -> Optional[Article]:
        """Extract article content from Ekattor TV page"""
        try:
            # Extract title
            title_selectors = [
                'h1.title',
                'h1.headline',
                '.news-title h1',
                '.story-title h1',
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
            
            # Extract content - Updated selectors based on debug findings
            content_selectors = [
                '.content',  # Found in debug
                '.news-content',
                '.story-content',
                '.article-content',
                '.content-body',
                '.news-details',
                '.description',
                'article',
                '.post-content'
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
                '[data-author]'
            ]
            
            author = None
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = self._clean_text(author_elem.get_text())
                    # Clean author text (remove common prefixes)
                    prefixes = ['প্রতিবেদক:', 'সংবাদদাতা:', 'By ', 'লিখেছেন:', 'Reporter:']
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
            
            # Detect language (Ekattor TV is primarily Bengali)
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