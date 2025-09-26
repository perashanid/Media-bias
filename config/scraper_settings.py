"""Scraper configuration settings."""

import os

class ScraperSettings:
    """Configuration settings for web scrapers."""
    
    # Rate limiting settings
    DELAY_BETWEEN_REQUESTS = float(os.getenv('SCRAPER_DELAY', 2.0))  # seconds
    RANDOMIZE_DELAY = True
    DELAY_RANDOMIZATION_FACTOR = 0.5
    
    # Retry settings
    MAX_RETRIES = int(os.getenv('SCRAPER_MAX_RETRIES', 3))
    RETRY_DELAY = float(os.getenv('SCRAPER_RETRY_DELAY', 5.0))  # seconds
    EXPONENTIAL_BACKOFF = True
    
    # Request settings
    REQUEST_TIMEOUT = int(os.getenv('SCRAPER_TIMEOUT', 30))  # seconds
    
    # User agents for rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    
    # News source configurations
    NEWS_SOURCES = {
        'prothom_alo': {
            'base_url': 'https://www.prothomalo.com/',
            'name': 'Prothom Alo',
            'language': 'bengali',
            'enabled': True
        },
        'daily_star': {
            'base_url': 'https://www.thedailystar.net/',
            'name': 'The Daily Star',
            'language': 'english',
            'enabled': True
        },
        'bd_pratidin': {
            'base_url': 'https://www.bd-pratidin.com/',
            'name': 'BD Pratidin',
            'language': 'bengali',
            'enabled': True
        },
        'ekattor_tv': {
            'base_url': 'https://ekattor.tv/',
            'name': 'Ekattor TV',
            'language': 'bengali',
            'enabled': True
        },
        'atn_news': {
            'base_url': 'https://www.atnnewstv.com/',
            'name': 'ATN News TV',
            'language': 'bengali',
            'enabled': True
        }
    }
    
    # Scraping schedule settings
    SCRAPING_INTERVAL_HOURS = int(os.getenv('SCRAPING_INTERVAL_HOURS', 6))
    MAX_ARTICLES_PER_SOURCE = int(os.getenv('MAX_ARTICLES_PER_SOURCE', 50))
    
    # Content extraction settings
    MIN_ARTICLE_LENGTH = int(os.getenv('MIN_ARTICLE_LENGTH', 100))  # characters
    MAX_ARTICLE_LENGTH = int(os.getenv('MAX_ARTICLE_LENGTH', 50000))  # characters