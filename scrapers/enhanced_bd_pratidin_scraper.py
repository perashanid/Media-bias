from scrapers.enhanced_scraper import EnhancedScraper
import logging

logger = logging.getLogger(__name__)


class EnhancedBDPratidinScraper(EnhancedScraper):
    """Enhanced BD Pratidin scraper that crawls the entire website"""
    
    def __init__(self):
        super().__init__("BD Pratidin", "https://www.bd-pratidin.com")
        # Customize crawling parameters for BD Pratidin
        self.max_depth = 3
        self.max_pages_per_depth = 25
    
    def _should_follow_link(self, url: str) -> bool:
        """Override to add BD Pratidin specific link filtering"""
        if not super()._should_follow_link(url):
            return False
        
        # BD Pratidin specific patterns to follow
        follow_patterns = [
            '/bangladesh/', '/politics/', '/international/',
            '/economics/', '/sports/', '/entertainment/',
            '/opinion/', '/lifestyle/', '/country/'
        ]
        
        # Skip certain BD Pratidin specific patterns
        skip_patterns = [
            '/live/', '/video/', '/photo/',
            '/gallery/', '/tag/', '/author/',
            '/search', '/page/', '/api/', '/auth/'
        ]
        
        # Check if URL contains patterns we want to follow
        has_follow_pattern = any(pattern in url.lower() for pattern in follow_patterns)
        has_skip_pattern = any(pattern in url.lower() for pattern in skip_patterns)
        
        # Be more permissive - follow any URL that looks like an article
        is_article_like = len(url.split('/')) >= 4 and not has_skip_pattern
        
        return (has_follow_pattern or is_article_like) and not has_skip_pattern
    
    def _is_article_page(self, soup, url: str) -> bool:
        """Override with BD Pratidin specific article detection"""
        # First check the parent method
        if not super()._is_article_page(soup, url):
            return False
        
        # BD Pratidin specific article indicators
        bd_pratidin_indicators = [
            soup.find(class_=lambda x: x and 'news' in x.lower()),
            soup.find(class_=lambda x: x and 'story' in x.lower()),
            soup.find('article'),
            # Check for BD Pratidin specific URL patterns
            any(pattern in url.lower() for pattern in [
                '/bangladesh/', '/politics/', '/international/',
                '/economics/', '/sports/', '/entertainment/'
            ])
        ]
        
        return any(bd_pratidin_indicators)