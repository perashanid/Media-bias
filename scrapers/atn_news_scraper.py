from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from models.article import Article
from scrapers.base_scraper import BaseScraper
import logging
import json

logger = logging.getLogger(__name__)


class ATNNewsScraper(BaseScraper):
    """Scraper for ATN News TV (https://www.atnnewstv.com/)"""
    
    def __init__(self):
        super().__init__("ATN News TV", "https://www.atnnewstv.com")
    
    def _get_article_urls(self, max_articles: int) -> List[str]:
        """Get article URLs from ATN News TV JSON endpoints"""
        article_urls = []
        
        # ATN News uses JSON endpoints for content
        json_endpoints = [
            "https://www.atnnewstv.com/assets/news/Spot-Light.json"
        ]
        
        for endpoint in json_endpoints:
            if len(article_urls) >= max_articles:
                break
                
            response = self._make_request(endpoint)
            
            if not response:
                continue
            
            try:
                data = response.json()
                
                if 'posts' in data:
                    posts = data['posts']
                    
                    for post in posts:
                        if len(article_urls) >= max_articles:
                            break
                            
                        post_id = post.get('post_id')
                        if post_id:
                            # Construct article URL using the pattern: /details/{post_id}
                            article_url = f"{self.base_url}/details/{post_id}"
                            
                            if article_url not in article_urls:
                                article_urls.append(article_url)
                        
            except Exception as e:
                logger.error(f"Failed to extract URLs from {endpoint}: {e}")
                continue
        
        return article_urls[:max_articles]
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL is likely an article URL"""
        # ATN News uses various patterns for articles
        if 'atnnewstv.com' not in url:
            return False
        
        # Article patterns for ATN News
        article_patterns = [
            '/details/',
            '/bangladesh/',
            '/politics/',
            '/international/',
            '/sports/',
            '/entertainment/',
            '/news/',
            '/national/'
        ]
        
        # Exclude non-article URLs
        exclude_patterns = [
            '.jpg', '.png', '.pdf', '.gif', '.mp4',
            '/assets/', '/images/', '/css/', '/js/',
            '/sitemap/', '/rss/', '/feed/', '/search',
            '/tag/', '/author/', '/category/', '/page/',
            '/live/', '/video/', '/gallery/'
        ]
        
        has_article_pattern = any(pattern in url for pattern in article_patterns)
        has_exclude_pattern = any(pattern in url for pattern in exclude_patterns)
        
        # URL should be deep enough to be an article
        is_deep_url = len(url.split('/')) >= 4
        
        return has_article_pattern and not has_exclude_pattern and is_deep_url
    
    def _extract_article_content(self, soup: BeautifulSoup, url: str) -> Optional[Article]:
        """Extract article content from ATN News TV page"""
        try:
            # Extract title from h1 tag
            title_elem = soup.select_one('h1')
            if not title_elem:
                # Fallback to page title
                title_elem = soup.select_one('title')
            
            if title_elem:
                title = self._clean_text(title_elem.get_text())
                # Clean title (remove site name)
                if '::' in title:
                    title = title.split('::')[0].strip()
            else:
                logger.warning(f"Could not extract title from {url}")
                return None
            
            # Extract content from the specific div structure used by ATN News
            content = ""
            
            # ATN News uses div with classes "col-sm-12 col-md-12 text-justify" for content
            content_elem = soup.select_one('.col-sm-12.col-md-12.text-justify')
            
            if content_elem:
                # Remove unwanted elements
                for unwanted in content_elem.select('script, style, .advertisement, .ad, .social-share, .related-news, .video-player'):
                    unwanted.decompose()
                
                content = self._clean_text(content_elem.get_text())
            
            # Fallback: try to get content from meta description or JSON-LD
            if len(content) < 100:
                # Try JSON-LD structured data
                json_ld = soup.find('script', {'type': 'application/ld+json'})
                if json_ld:
                    try:
                        structured_data = json.loads(json_ld.string)
                        if 'description' in structured_data:
                            content = self._clean_text(structured_data['description'])
                    except:
                        pass
                
                # Try meta description
                if len(content) < 100:
                    meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
                    if meta_desc and meta_desc.get('content'):
                        content = self._clean_text(meta_desc.get('content'))
            
            if not content or len(content) < 50:
                logger.warning(f"Could not extract sufficient content from {url}")
                return None
            
            # Extract author from JSON-LD structured data
            author = None
            json_ld = soup.find('script', {'type': 'application/ld+json'})
            if json_ld:
                try:
                    structured_data = json.loads(json_ld.string)
                    if 'author' in structured_data:
                        author_data = structured_data['author']
                        if isinstance(author_data, dict) and 'name' in author_data:
                            author = author_data['name']
                        elif isinstance(author_data, str):
                            author = author_data
                except:
                    pass
            
            # Default author if not found
            if not author:
                author = "ATN News Desk"
            
            # Extract publication date from JSON-LD structured data
            publication_date = None
            if json_ld:
                try:
                    structured_data = json.loads(json_ld.string)
                    if 'datePublished' in structured_data:
                        date_str = structured_data['datePublished']
                        publication_date = self._parse_date(date_str)
                    elif 'dateModified' in structured_data:
                        date_str = structured_data['dateModified']
                        publication_date = self._parse_date(date_str)
                except:
                    pass
            
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