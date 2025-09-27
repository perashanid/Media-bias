from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from models.article import Article
from scrapers.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class ATNNewsScraper(BaseScraper):
    """Scraper for ATN News TV (https://www.atnnewstv.com/)"""
    
    def __init__(self):
        super().__init__("ATN News TV", "https://www.atnnewstv.com")
    
    def _get_article_urls(self, max_articles: int) -> List[str]:
        """Get article URLs from ATN News TV using sitemap approach"""
        article_urls = []
        
        try:
            # Use sitemap approach since regular pages don't show articles
            from datetime import datetime, timedelta
            
            # Try last few days of sitemaps
            for days_back in range(5):  # Try last 5 days
                if len(article_urls) >= max_articles:
                    break
                
                date = datetime.now() - timedelta(days=days_back)
                date_str = date.strftime("%Y-%m-%d")
                sitemap_url = f"https://www.atnnewstv.com/sitemap/sitemap-daily-{date_str}.xml"
                
                response = self._make_request(sitemap_url)
                if not response:
                    continue
                
                try:
                    soup = BeautifulSoup(response.content, 'xml')
                    urls = soup.find_all('loc')
                    
                    for url_elem in urls:
                        url = url_elem.get_text()
                        
                        # Filter for actual articles (not images)
                        if self._is_article_url(url) and url not in article_urls:
                            article_urls.append(url)
                            
                            if len(article_urls) >= max_articles:
                                break
                                
                except Exception as e:
                    logger.error(f"Failed to parse sitemap {sitemap_url}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Failed to get article URLs from sitemap: {e}")
        
        return article_urls[:max_articles]
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL is likely an article URL"""
        # ATN News uses /details/ pattern for articles
        if 'atnnewstv.com' not in url:
            return False
        
        # Must have /details/ pattern with article ID
        if '/details/' in url:
            # Extract article ID and validate it's numeric
            try:
                article_id = url.split('/details/')[-1]
                return article_id.isdigit() and len(article_id) > 3
            except:
                return False
        
        # Exclude non-article URLs
        exclude_patterns = [
            '.jpg', '.png', '.pdf', '.gif', '.mp4',
            '/assets/', '/images/', '/css/', '/js/',
            '/sitemap/', '/rss/', '/feed/'
        ]
        
        has_exclude_pattern = any(pattern in url for pattern in exclude_patterns)
        return not has_exclude_pattern
    
    def _extract_article_content(self, soup: BeautifulSoup, url: str) -> Optional[Article]:
        """Extract article content from ATN News TV page"""
        try:
            # Extract title
            title_selectors = [
                'h1.title',
                'h1.headline',
                '.news-title h1',
                '.story-title h1',
                '.article-title h1',
                '.page-title h1',
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
            
            # Extract content - ATN News doesn't seem to have main content in HTML
            # Based on investigation, articles might not have extractable content
            # Try basic paragraph extraction
            content = ""
            
            # Try to get content from paragraphs
            paragraphs = soup.find_all('p')
            content_parts = []
            for p in paragraphs:
                p_text = self._clean_text(p.get_text())
                if len(p_text) > 20:  # Skip very short paragraphs
                    content_parts.append(p_text)
            
            content = ' '.join(content_parts)
            
            # If no content found, create minimal content from title
            if len(content) < 50:
                content = f"Article from ATN News: {title}"
            
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
            
            # Detect language (ATN News is primarily Bengali)
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