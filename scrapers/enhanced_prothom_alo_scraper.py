from scrapers.enhanced_scraper import EnhancedScraper
import logging

logger = logging.getLogger(__name__)


class EnhancedProthomAloScraper(EnhancedScraper):
    """Enhanced Prothom Alo scraper that crawls the entire website"""
    
    def __init__(self):
        super().__init__("Prothom Alo", "https://www.prothomalo.com")
        # Customize crawling parameters for Prothom Alo
        self.max_depth = 4
        self.max_pages_per_depth = 30
    
    def _should_follow_link(self, url: str) -> bool:
        """Override to add Prothom Alo specific link filtering"""
        if not super()._should_follow_link(url):
            return False
        
        # Prothom Alo specific patterns to follow
        follow_patterns = [
            '/bangladesh/', '/politics/', '/international/',
            '/business/', '/sports/', '/entertainment/',
            '/opinion/', '/lifestyle/', '/education/',
            '/technology/', '/health/', '/environment/'
        ]
        
        # Skip certain Prothom Alo specific patterns
        skip_patterns = [
            '/live-news/', '/photo-gallery/', '/video/',
            '/epaper/', '/jobs/', '/classifieds/',
            '/weather/', '/prayer-time/', '/currency/',
            '/api/', '/oauth/', '/auth/'  # Skip API and auth URLs
        ]
        
        # Check if URL contains patterns we want to follow
        has_follow_pattern = any(pattern in url.lower() for pattern in follow_patterns)
        has_skip_pattern = any(pattern in url.lower() for pattern in skip_patterns)
        
        # For Prothom Alo, be more permissive - follow any URL that doesn't have skip patterns
        # and either has follow patterns OR looks like an article URL
        is_article_like = len(url.split('/')) >= 4 and not has_skip_pattern
        
        return (has_follow_pattern or is_article_like) and not has_skip_pattern
    
    def _is_article_page(self, soup, url: str) -> bool:
        """Override with Prothom Alo specific article detection"""
        # First check the parent method
        if not super()._is_article_page(soup, url):
            return False
        
        # Prothom Alo specific article indicators
        prothom_alo_indicators = [
            soup.find(class_=lambda x: x and 'story' in x.lower()),
            soup.find(class_=lambda x: x and 'news' in x.lower()),
            soup.find('article'),
            # Check for Prothom Alo specific URL patterns
            any(pattern in url.lower() for pattern in [
                '/bangladesh/', '/politics/', '/international/',
                '/business/', '/sports/', '/entertainment/'
            ])
        ]
        
        return any(prothom_alo_indicators)