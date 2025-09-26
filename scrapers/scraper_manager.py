from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from models.article import Article
from scrapers.prothom_alo_scraper import ProthomAloScraper
from scrapers.daily_star_scraper import DailyStarScraper
from scrapers.bd_pratidin_scraper import BDPratidinScraper
from scrapers.ekattor_tv_scraper import EkattorTVScraper
from scrapers.atn_news_scraper import ATNNewsScraper

logger = logging.getLogger(__name__)


class ScraperManager:
    """Manages all news scrapers and coordinates scraping operations"""
    
    def __init__(self):
        self.scrapers = {
            'prothom_alo': ProthomAloScraper(),
            'daily_star': DailyStarScraper(),
            'bd_pratidin': BDPratidinScraper(),
            'ekattor_tv': EkattorTVScraper(),
            'atn_news': ATNNewsScraper()
        }
        
    def scrape_all_sources(self, max_articles_per_source: int = 20, max_workers: int = 3) -> Dict[str, List[Article]]:
        """Scrape articles from all news sources concurrently"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit scraping tasks for each source
            future_to_source = {
                executor.submit(scraper.scrape_articles, max_articles_per_source): source_name
                for source_name, scraper in self.scrapers.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    articles = future.result()
                    results[source_name] = articles
                    logger.info(f"Completed scraping {len(articles)} articles from {source_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to scrape from {source_name}: {e}")
                    results[source_name] = []
        
        total_articles = sum(len(articles) for articles in results.values())
        logger.info(f"Total articles scraped: {total_articles}")
        
        return results
    
    def scrape_single_source(self, source_name: str, max_articles: int = 20) -> List[Article]:
        """Scrape articles from a single news source"""
        if source_name not in self.scrapers:
            logger.error(f"Unknown source: {source_name}")
            return []
        
        try:
            scraper = self.scrapers[source_name]
            articles = scraper.scrape_articles(max_articles)
            logger.info(f"Scraped {len(articles)} articles from {source_name}")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to scrape from {source_name}: {e}")
            return []
    
    def scrape_source(self, source_name: str, limit: int = 20) -> List[Article]:
        """Alias for scrape_single_source for backward compatibility"""
        return self.scrape_single_source(source_name, limit)
    
    def get_available_sources(self) -> List[str]:
        """Get list of available news sources"""
        return list(self.scrapers.keys())
    
    def get_scraper_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available scrapers"""
        info = {}
        for source_name, scraper in self.scrapers.items():
            info[source_name] = {
                'source_name': scraper.source_name,
                'base_url': scraper.base_url,
                'max_retries': scraper.max_retries,
                'base_delay': scraper.base_delay
            }
        return info