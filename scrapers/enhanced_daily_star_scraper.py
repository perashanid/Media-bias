from scrapers.enhanced_scraper import EnhancedScraper
import logging

logger = logging.getLogger(__name__)


class EnhancedDailyStarScraper(EnhancedScraper):
    """Enhanced Daily Star scraper that crawls the entire website"""
    
    def __init__(self):
        super().__init__("The Daily Star", "https://www.thedailystar.net")
        # Customize crawling parameters for Daily Star
        self.max_depth = 3
        self.max_pages_per_depth = 25
    
    def _should_follow_link(self, url: str) -> bool:
        """Override to add Daily Star specific link filtering"""
        if not super()._should_follow_link(url):
            return False
        
        # Daily Star specific patterns to follow
        follow_patterns = [
            '/news/', '/politics/', '/business/',
            '/sports/', '/entertainment/', '/opinion/',
            '/lifestyle/', '/tech/', '/world/'
        ]
        
        # Skip certain Daily Star specific patterns
        skip_patterns = [
            '/live-tv/', '/photo/', '/video/',
            '/epaper/', '/jobs/', '/classifieds/',
            '/weather/', '/api/', '/auth/'
        ]
        
        # Check if URL contains patterns we want to follow
        has_follow_pattern = any(pattern in url.lower() for pattern in follow_patterns)
        has_skip_pattern = any(pattern in url.lower() for pattern in skip_patterns)
        
        # Be more permissive - follow any URL that looks like an article
        is_article_like = len(url.split('/')) >= 4 and not has_skip_pattern
        
        return (has_follow_pattern or is_article_like) and not has_skip_pattern
    
    def _is_article_page(self, soup, url: str) -> bool:
        """Override with Daily Star specific article detection"""
        # First check the parent method
        if not super()._is_article_page(soup, url):
            return False
        
        # Daily Star specific article indicators
        daily_star_indicators = [
            soup.find(class_=lambda x: x and 'article' in x.lower()),
            soup.find(class_=lambda x: x and 'news' in x.lower()),
            soup.find('article'),
            # Check for Daily Star specific URL patterns
            any(pattern in url.lower() for pattern in [
                '/news/', '/politics/', '/business/',
                '/sports/', '/entertainment/', '/opinion/'
            ])
        ]
        
        return any(daily_star_indicators)