from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time
from datetime import datetime
from models.article import Article
from scrapers.prothom_alo_scraper import ProthomAloScraper
from scrapers.daily_star_scraper import DailyStarScraper
from scrapers.bd_pratidin_scraper import BDPratidinScraper
from scrapers.ekattor_tv_scraper import EkattorTVScraper
from scrapers.atn_news_scraper import ATNNewsScraper
from scrapers.jamuna_tv_scraper import JamunaTVScraper

logger = logging.getLogger(__name__)


class ScraperManager:
    """Enhanced scraper manager with improved error handling and monitoring"""
    
    def __init__(self):
        self.scrapers = {
            'prothom_alo': ProthomAloScraper(),
            'daily_star': DailyStarScraper(),
            'bd_pratidin': BDPratidinScraper(),
            'ekattor_tv': EkattorTVScraper(),
            'atn_news': ATNNewsScraper(),
            'jamuna_tv': JamunaTVScraper()
        }
        
        # Track scraper health and performance
        self.scraper_stats = {
            source: {
                'last_successful_scrape': None,
                'total_articles_scraped': 0,
                'total_errors': 0,
                'average_response_time': 0.0,
                'is_healthy': True
            }
            for source in self.scrapers.keys()
        }
        
    def scrape_all_sources(self, max_articles_per_source: int = 20, max_workers: int = 3) -> Dict[str, List[Article]]:
        """Scrape articles from all news sources concurrently with enhanced monitoring"""
        results = {}
        scraping_stats = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit scraping tasks for each source
            future_to_source = {
                executor.submit(self._scrape_source_with_monitoring, source_name, scraper, max_articles_per_source): source_name
                for source_name, scraper in self.scrapers.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    articles, stats = future.result()
                    results[source_name] = articles
                    scraping_stats[source_name] = stats
                    
                    # Update scraper health stats
                    self._update_scraper_stats(source_name, len(articles), stats['response_time'], success=True)
                    
                    logger.info(f"✅ {source_name}: {len(articles)} articles in {stats['response_time']:.2f}s")
                    
                except Exception as e:
                    logger.error(f"❌ {source_name}: {e}")
                    results[source_name] = []
                    scraping_stats[source_name] = {'error': str(e), 'response_time': 0}
                    
                    # Update scraper health stats
                    self._update_scraper_stats(source_name, 0, 0, success=False)
        
        total_articles = sum(len(articles) for articles in results.values())
        successful_sources = len([r for r in results.values() if r])
        
        logger.info(f"📊 Scraping Summary: {total_articles} articles from {successful_sources}/{len(self.scrapers)} sources")
        
        return results
    
    def scrape_single_source(self, source_name: str, max_articles: int = 20) -> List[Article]:
        """Scrape articles from a single news source with enhanced error handling"""
        if source_name not in self.scrapers:
            logger.error(f"❌ Unknown source: {source_name}")
            available_sources = ', '.join(self.scrapers.keys())
            logger.info(f"Available sources: {available_sources}")
            return []
        
        try:
            start_time = time.time()
            scraper = self.scrapers[source_name]
            
            # Check if scraper is healthy
            if not self.scraper_stats[source_name]['is_healthy']:
                logger.warning(f"⚠️ {source_name} marked as unhealthy, attempting anyway...")
            
            articles = scraper.scrape_articles(max_articles)
            response_time = time.time() - start_time
            
            # Update stats
            self._update_scraper_stats(source_name, len(articles), response_time, success=True)
            
            logger.info(f"✅ {source_name}: {len(articles)} articles in {response_time:.2f}s")
            return articles
            
        except Exception as e:
            response_time = time.time() - start_time if 'start_time' in locals() else 0
            self._update_scraper_stats(source_name, 0, response_time, success=False)
            
            logger.error(f"❌ {source_name}: {e}")
            return []
    
    def scrape_source(self, source_name: str, limit: int = 20) -> List[Article]:
        """Alias for scrape_single_source for backward compatibility"""
        return self.scrape_single_source(source_name, limit)
    
    def comprehensive_scrape_source(self, source_name: str, max_articles: int = 100, max_depth: int = 3) -> List[Article]:
        """Perform comprehensive crawling of a source using regular scraper with higher limits"""
        logger.info(f"🔍 Comprehensive scraping from {source_name} (limit: {max_articles})")
        return self.scrape_single_source(source_name, max_articles)
    
    def get_available_sources(self) -> List[str]:
        """Get list of available news sources"""
        return list(self.scrapers.keys())
    
    def get_scraper_info(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive information about all available scrapers"""
        info = {}
        for source_name, scraper in self.scrapers.items():
            stats = self.scraper_stats[source_name]
            info[source_name] = {
                'source_name': scraper.source_name,
                'base_url': scraper.base_url,
                'max_retries': scraper.max_retries,
                'base_delay': scraper.base_delay,
                'is_healthy': stats['is_healthy'],
                'last_successful_scrape': stats['last_successful_scrape'],
                'total_articles_scraped': stats['total_articles_scraped'],
                'total_errors': stats['total_errors'],
                'average_response_time': stats['average_response_time']
            }
        return info
    
    def get_scraper_health_status(self) -> Dict[str, Any]:
        """Get health status of all scrapers"""
        healthy_count = sum(1 for stats in self.scraper_stats.values() if stats['is_healthy'])
        total_count = len(self.scrapers)
        
        return {
            'healthy_scrapers': healthy_count,
            'total_scrapers': total_count,
            'health_percentage': (healthy_count / total_count) * 100 if total_count > 0 else 0,
            'scraper_details': self.scraper_stats
        }
    
    def reset_scraper_health(self, source_name: Optional[str] = None):
        """Reset health status for a specific scraper or all scrapers"""
        if source_name:
            if source_name in self.scraper_stats:
                self.scraper_stats[source_name]['is_healthy'] = True
                self.scraper_stats[source_name]['total_errors'] = 0
                logger.info(f"🔄 Reset health status for {source_name}")
        else:
            for source in self.scraper_stats:
                self.scraper_stats[source]['is_healthy'] = True
                self.scraper_stats[source]['total_errors'] = 0
            logger.info("🔄 Reset health status for all scrapers")
    
    def _scrape_source_with_monitoring(self, source_name: str, scraper, max_articles: int) -> tuple:
        """Scrape a source with detailed monitoring"""
        start_time = time.time()
        
        try:
            articles = scraper.scrape_articles(max_articles)
            response_time = time.time() - start_time
            
            stats = {
                'response_time': response_time,
                'articles_found': len(articles),
                'success': True
            }
            
            return articles, stats
            
        except Exception as e:
            response_time = time.time() - start_time
            stats = {
                'response_time': response_time,
                'articles_found': 0,
                'success': False,
                'error': str(e)
            }
            
            raise e
    
    def _update_scraper_stats(self, source_name: str, articles_count: int, response_time: float, success: bool):
        """Update scraper statistics"""
        stats = self.scraper_stats[source_name]
        
        if success:
            stats['last_successful_scrape'] = datetime.now().isoformat()
            stats['total_articles_scraped'] += articles_count
            
            # Update average response time
            if stats['average_response_time'] == 0:
                stats['average_response_time'] = response_time
            else:
                stats['average_response_time'] = (stats['average_response_time'] + response_time) / 2
            
            # Mark as healthy if it was unhealthy
            if not stats['is_healthy']:
                stats['is_healthy'] = True
                logger.info(f"✅ {source_name} marked as healthy again")
        else:
            stats['total_errors'] += 1
            
            # Mark as unhealthy if too many consecutive errors
            if stats['total_errors'] >= 3:
                stats['is_healthy'] = False
                logger.warning(f"⚠️ {source_name} marked as unhealthy after {stats['total_errors']} errors")