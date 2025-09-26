import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from scrapers.scraper_manager import ScraperManager
from services.article_storage_service import ArticleStorageService
from services.bias_analyzer import BiasAnalyzer
from services.scheduler_service import SchedulerService
from services.monitoring_service import MonitoringService, SystemMetrics
from models.article import Article

logger = logging.getLogger(__name__)


class ScrapingOrchestrator:
    """Orchestrates the entire scraping, storage, and analysis pipeline"""
    
    def __init__(self):
        self.scraper_manager = ScraperManager()
        self.storage_service = ArticleStorageService()
        self.bias_analyzer = BiasAnalyzer()
        self.scheduler_service = SchedulerService()
        self.monitoring_service = MonitoringService()
        
        # Configuration
        self.config = {
            'articles_per_source': 20,
            'max_concurrent_scrapers': 3,
            'auto_analyze_bias': True,
            'scraping_interval_minutes': 60,  # Default 1 hour
            'analysis_batch_size': 50
        }
        
        # Statistics tracking
        self.stats = {
            'last_scraping_run': None,
            'articles_scraped_today': 0,
            'articles_analyzed_today': 0,
            'scraping_errors_today': 0,
            'analysis_errors_today': 0
        }
    
    def initialize(self):
        """Initialize the orchestrator and set up scheduled jobs"""
        try:
            logger.info("Initializing Scraping Orchestrator...")
            
            # Set up scheduled scraping jobs for each source
            sources = self.scraper_manager.get_available_sources()
            
            for source in sources:
                job_id = f"scrape_{source}"
                job_name = f"Scrape {source.replace('_', ' ').title()}"
                
                # Create a lambda function for this specific source
                scrape_function = lambda src=source: self.scrape_single_source(src)
                
                self.scheduler_service.add_job(
                    job_id=job_id,
                    name=job_name,
                    function=scrape_function,
                    interval_minutes=self.config['scraping_interval_minutes'],
                    enabled=True
                )
            
            # Set up bias analysis job
            self.scheduler_service.add_job(
                job_id="analyze_pending_bias",
                name="Analyze Pending Articles for Bias",
                function=self.analyze_pending_articles,
                interval_minutes=30,  # Run every 30 minutes
                enabled=True
            )
            
            # Set up metrics collection job
            self.scheduler_service.add_job(
                job_id="collect_metrics",
                name="Collect System Metrics",
                function=self.collect_system_metrics,
                interval_minutes=15,  # Run every 15 minutes
                enabled=True
            )
            
            # Start the scheduler
            self.scheduler_service.start()
            
            logger.info("Scraping Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Scraping Orchestrator: {e}")
            self.monitoring_service.create_alert(
                'critical',
                'Orchestrator Initialization Failed',
                f'Failed to initialize scraping orchestrator: {e}',
                'orchestrator'
            )
    
    def scrape_all_sources(self) -> Dict[str, Any]:
        """Scrape articles from all news sources"""
        try:
            logger.info("Starting scraping from all sources...")
            
            start_time = datetime.now()
            results = {
                'start_time': start_time.isoformat(),
                'sources': {},
                'total_articles': 0,
                'total_stored': 0,
                'total_duplicates': 0,
                'total_errors': 0
            }
            
            # Scrape from all sources
            scraping_results = self.scraper_manager.scrape_all_sources(
                max_articles_per_source=self.config['articles_per_source'],
                max_workers=self.config['max_concurrent_scrapers']
            )
            
            # Process and store articles from each source
            for source_name, articles in scraping_results.items():
                try:
                    if articles:
                        # Store articles
                        storage_result = self.storage_service.store_articles_batch(articles)
                        
                        results['sources'][source_name] = {
                            'scraped': len(articles),
                            'stored': storage_result['stored'],
                            'duplicates': storage_result['duplicates'],
                            'errors': storage_result['errors']
                        }
                        
                        results['total_articles'] += len(articles)
                        results['total_stored'] += storage_result['stored']
                        results['total_duplicates'] += storage_result['duplicates']
                        results['total_errors'] += storage_result['errors']
                        
                        logger.info(f"Processed {source_name}: {len(articles)} scraped, "
                                  f"{storage_result['stored']} stored, "
                                  f"{storage_result['duplicates']} duplicates")
                    else:
                        results['sources'][source_name] = {
                            'scraped': 0,
                            'stored': 0,
                            'duplicates': 0,
                            'errors': 1
                        }
                        results['total_errors'] += 1
                        
                        logger.warning(f"No articles scraped from {source_name}")
                        
                except Exception as e:
                    logger.error(f"Failed to process articles from {source_name}: {e}")
                    results['sources'][source_name] = {
                        'scraped': len(articles) if articles else 0,
                        'stored': 0,
                        'duplicates': 0,
                        'errors': 1
                    }
                    results['total_errors'] += 1
            
            # Update statistics
            self.stats['last_scraping_run'] = start_time
            self.stats['articles_scraped_today'] += results['total_articles']
            self.stats['scraping_errors_today'] += results['total_errors']
            
            # Calculate duration
            end_time = datetime.now()
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = (end_time - start_time).total_seconds()
            
            # Create monitoring alert if there were significant errors
            if results['total_errors'] > len(scraping_results) * 0.5:  # More than 50% failed
                self.monitoring_service.create_alert(
                    'error',
                    'High Scraping Failure Rate',
                    f"Scraping failed for {results['total_errors']} out of {len(scraping_results)} sources",
                    'scraper'
                )
            
            logger.info(f"Scraping completed: {results['total_stored']} new articles stored, "
                       f"{results['total_duplicates']} duplicates, {results['total_errors']} errors")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to scrape all sources: {e}")
            self.monitoring_service.create_alert(
                'error',
                'Scraping Process Failed',
                f'Failed to complete scraping process: {e}',
                'scraper'
            )
            return {'error': str(e)}
    
    def scrape_single_source(self, source_name: str) -> Dict[str, Any]:
        """Scrape articles from a single news source"""
        try:
            logger.info(f"Starting scraping from {source_name}...")
            
            start_time = datetime.now()
            
            # Scrape articles
            articles = self.scraper_manager.scrape_single_source(
                source_name, 
                self.config['articles_per_source']
            )
            
            if not articles:
                logger.warning(f"No articles scraped from {source_name}")
                return {
                    'source': source_name,
                    'scraped': 0,
                    'stored': 0,
                    'duplicates': 0,
                    'errors': 1,
                    'duration_seconds': (datetime.now() - start_time).total_seconds()
                }
            
            # Store articles
            storage_result = self.storage_service.store_articles_batch(articles)
            
            # Update statistics
            self.stats['articles_scraped_today'] += len(articles)
            if storage_result['errors'] > 0:
                self.stats['scraping_errors_today'] += storage_result['errors']
            
            result = {
                'source': source_name,
                'scraped': len(articles),
                'stored': storage_result['stored'],
                'duplicates': storage_result['duplicates'],
                'errors': storage_result['errors'],
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
            
            logger.info(f"Completed scraping {source_name}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to scrape from {source_name}: {e}")
            self.stats['scraping_errors_today'] += 1
            
            self.monitoring_service.create_alert(
                'warning',
                f'Scraping Failed for {source_name}',
                f'Failed to scrape articles from {source_name}: {e}',
                'scraper'
            )
            
            return {
                'source': source_name,
                'scraped': 0,
                'stored': 0,
                'duplicates': 0,
                'errors': 1,
                'error_message': str(e)
            }
    
    def analyze_pending_articles(self) -> Dict[str, Any]:
        """Analyze articles that haven't been processed for bias yet"""
        try:
            logger.info("Starting bias analysis for pending articles...")
            
            start_time = datetime.now()
            
            # Get articles without bias analysis
            pending_articles = self.storage_service.get_articles_without_bias_analysis(
                self.config['analysis_batch_size']
            )
            
            if not pending_articles:
                logger.info("No pending articles found for bias analysis")
                return {
                    'analyzed': 0,
                    'errors': 0,
                    'duration_seconds': 0
                }
            
            analyzed_count = 0
            error_count = 0
            
            for article in pending_articles:
                try:
                    # Perform bias analysis
                    bias_scores = self.bias_analyzer.analyze_article_bias(article)
                    
                    # Update article with bias scores
                    bias_scores_dict = bias_scores.to_dict()
                    success = self.storage_service.update_article_bias_scores(
                        article.id, bias_scores_dict
                    )
                    
                    if success:
                        analyzed_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to analyze article {article.id}: {e}")
                    error_count += 1
            
            # Update statistics
            self.stats['articles_analyzed_today'] += analyzed_count
            self.stats['analysis_errors_today'] += error_count
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                'analyzed': analyzed_count,
                'errors': error_count,
                'duration_seconds': duration
            }
            
            logger.info(f"Bias analysis completed: {analyzed_count} articles analyzed, "
                       f"{error_count} errors in {duration:.1f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze pending articles: {e}")
            self.monitoring_service.create_alert(
                'error',
                'Bias Analysis Failed',
                f'Failed to analyze pending articles: {e}',
                'analyzer'
            )
            return {'error': str(e)}
    
    def collect_system_metrics(self):
        """Collect and record system performance metrics"""
        try:
            logger.debug("Collecting system metrics...")
            
            # Get storage statistics
            storage_stats = self.storage_service.get_storage_statistics()
            
            # Calculate success rates
            total_scraped = self.stats['articles_scraped_today']
            total_errors = self.stats['scraping_errors_today']
            scraping_success_rate = ((total_scraped - total_errors) / total_scraped * 100) if total_scraped > 0 else 100
            
            total_analyzed = self.stats['articles_analyzed_today']
            analysis_errors = self.stats['analysis_errors_today']
            analysis_success_rate = ((total_analyzed - analysis_errors) / total_analyzed * 100) if total_analyzed > 0 else 100
            
            # Create metrics object
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                articles_scraped_last_hour=total_scraped,  # Simplified for demo
                articles_analyzed_last_hour=total_analyzed,
                scraping_success_rate=scraping_success_rate,
                analysis_success_rate=analysis_success_rate,
                database_size_mb=storage_stats.get('total_articles', 0) * 0.1,  # Rough estimate
                response_time_ms=100,  # Would need actual API monitoring
                error_count_last_hour=total_errors + analysis_errors
            )
            
            # Record metrics
            self.monitoring_service.record_metrics(metrics)
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the orchestrator"""
        try:
            scheduler_status = self.scheduler_service.get_scheduler_status()
            jobs_status = self.scheduler_service.get_all_jobs_status()
            system_health = self.monitoring_service.get_system_health()
            active_alerts = self.monitoring_service.get_active_alerts()
            
            return {
                'scheduler': scheduler_status,
                'jobs': jobs_status,
                'system_health': system_health,
                'active_alerts': active_alerts,
                'statistics': self.stats,
                'configuration': self.config
            }
            
        except Exception as e:
            logger.error(f"Failed to get orchestrator status: {e}")
            return {'error': str(e)}
    
    def update_scraping_interval(self, interval_minutes: int) -> bool:
        """Update scraping interval for all sources"""
        try:
            self.config['scraping_interval_minutes'] = interval_minutes
            
            # Update all scraping jobs
            sources = self.scraper_manager.get_available_sources()
            for source in sources:
                job_id = f"scrape_{source}"
                self.scheduler_service.update_job_interval(job_id, interval_minutes)
            
            logger.info(f"Updated scraping interval to {interval_minutes} minutes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update scraping interval: {e}")
            return False
    
    def stop(self):
        """Stop the orchestrator and all scheduled jobs"""
        try:
            logger.info("Stopping Scraping Orchestrator...")
            self.scheduler_service.stop()
            logger.info("Scraping Orchestrator stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop orchestrator: {e}")


# Global orchestrator instance - initialized lazily
orchestrator = None

def get_orchestrator():
    """Get the global orchestrator instance, creating it if needed"""
    global orchestrator
    if orchestrator is None:
        orchestrator = ScrapingOrchestrator()
    return orchestrator