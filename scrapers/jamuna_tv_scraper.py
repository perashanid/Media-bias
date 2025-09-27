import time
import random
import requests
from typing import List, Optional
from datetime import datetime
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from models.article import Article
from scrapers.enhanced_scraper import EnhancedScraper

logger = logging.getLogger(__name__)


class JamunaTVScraper(EnhancedScraper):
    """Scraper for Jamuna TV (jamuna.tv)"""
    
    def __init__(self):
        super().__init__("Jamuna TV", "https://jamuna.tv")
        # Additional headers are handled in _make_request method
    
    def scrape_articles(self, max_articles: int = 50) -> List[Article]:
        """Scrape articles from Jamuna TV"""
        logger.info(f"Starting to scrape {self.source_name}")
        
        try:
            # First try to get articles from main sections
            articles = []
            
            # Main news sections to scrape
            sections = [
                "https://jamuna.tv/news",
                "https://jamuna.tv/politics", 
                "https://jamuna.tv/international",
                "https://jamuna.tv/business",
                "https://jamuna.tv/sports",
                "https://jamuna.tv/entertainment",
                "https://jamuna.tv/lifestyle",
                "https://jamuna.tv/technology"
            ]
            
            articles_per_section = max_articles // len(sections)
            
            for section_url in sections:
                if len(articles) >= max_articles:
                    break
                    
                logger.info(f"Scraping section: {section_url}")
                section_articles = self._scrape_section(section_url, articles_per_section)
                articles.extend(section_articles)
                
                # Add delay between sections
                time.sleep(random.uniform(2, 4))
            
            # If we don't have enough articles, use comprehensive crawling
            if len(articles) < max_articles // 2:
                logger.info("Not enough articles found in sections, starting comprehensive crawl")
                crawl_articles = self.crawl_website(max_articles - len(articles), max_depth=2)
                articles.extend(crawl_articles)
            
            logger.info(f"Successfully scraped {len(articles)} articles from {self.source_name}")
            return articles[:max_articles]
            
        except Exception as e:
            logger.error(f"Failed to scrape {self.source_name}: {e}")
            return []
    
    def _scrape_section(self, section_url: str, max_articles: int) -> List[Article]:
        """Scrape articles from a specific section"""
        articles = []
        
        try:
            response = self._make_request(section_url)
            if not response:
                return articles
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links in the section
            article_links = self._extract_article_links(soup, section_url)
            
            logger.info(f"Found {len(article_links)} article links in {section_url}")
            
            # Scrape each article
            for i, article_url in enumerate(article_links[:max_articles]):
                try:
                    logger.info(f"Scraping article {i+1}/{min(len(article_links), max_articles)}: {article_url}")
                    article = self._scrape_single_article(article_url)
                    if article:
                        articles.append(article)
                        logger.info(f"Successfully scraped: {article.title[:50]}...")
                    
                    # Add delay between requests
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.error(f"Failed to scrape article {article_url}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Failed to scrape section {section_url}: {e}")
        
        return articles
    
    def _extract_article_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract article links from a page"""
        links = set()
        
        # Common selectors for article links on Jamuna TV
        article_selectors = [
            'article a[href]',
            '.news-item a[href]',
            '.story-item a[href]',
            '.post-item a[href]',
            '.article-item a[href]',
            '.news-list a[href]',
            '.content-item a[href]',
            'h2 a[href]',
            'h3 a[href]',
            '.title a[href]',
            '.headline a[href]'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            for elem in elements:
                href = elem.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    if self._is_valid_article_url(full_url):
                        links.add(full_url)
        
        # Also look for any links that look like articles
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                if self._is_valid_article_url(full_url):
                    links.add(full_url)
        
        return list(links)
    
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
                language = 'Bengali'  # Default for Jamuna TV
            
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
    
    def _should_follow_link(self, url: str) -> bool:
        """Override to be more specific for Jamuna TV"""
        if not super()._should_follow_link(url):
            return False
        
        # Only follow Jamuna TV links
        if not url.startswith('https://jamuna.tv'):
            return False
        
        return True
    
    def _is_article_page(self, soup: BeautifulSoup, url: str) -> bool:
        """Override to be more specific for Jamuna TV"""
        # Skip homepage
        if url.rstrip('/') == 'https://jamuna.tv':
            return False
        
        # Check for Jamuna TV specific article indicators
        jamuna_indicators = [
            soup.find('article'),
            soup.find(class_=lambda x: x and any(term in x.lower() for term in 
                     ['entry-content', 'post-content', 'article-content', 'news-content'])),
            soup.find('h1'),  # Articles should have a main heading
            len(soup.find_all('p')) > 3,  # Should have multiple paragraphs
        ]
        
        # Must have title and substantial content
        title_found = bool(soup.find('h1') or soup.find('title'))
        text_content = soup.get_text()
        has_content = len(text_content.strip()) > 500
        
        # Check if any Jamuna TV indicators are present
        has_indicators = any(jamuna_indicators)
        
        # URL should look like an article
        url_looks_like_article = (
            len(url.split('/')) >= 4 and 
            not any(skip in url.lower() for skip in [
                '/category/', '/tag/', '/author/', '/search', '/page/', 
                '/api/', '/auth/', '/contact', '/about'
            ])
        )
        
        return title_found and has_content and has_indicators and url_looks_like_article