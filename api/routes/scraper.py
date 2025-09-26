from flask import Blueprint, request, jsonify
import logging
from scrapers.scraper_manager import ScraperManager
from services.article_storage_service import ArticleStorageService
from services.bias_analyzer import BiasAnalyzer
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

# Create blueprint
scraper_bp = Blueprint('scraper', __name__, url_prefix='/api/scrape')

# Initialize services
scraper_manager = ScraperManager()
storage_service = ArticleStorageService()
bias_analyzer = BiasAnalyzer()


@scraper_bp.route('/sources', methods=['GET'])
def get_available_sources():
    """Get list of available news sources for scraping"""
    try:
        sources = scraper_manager.get_available_sources()
        scraper_info = scraper_manager.get_scraper_info()
        
        return jsonify({
            'sources': sources,
            'scraper_info': scraper_info
        })
        
    except Exception as e:
        logger.error(f"Failed to get available sources: {e}")
        return jsonify({'error': 'Failed to retrieve sources'}), 500


@scraper_bp.route('/manual', methods=['POST'])
def manual_scrape():
    """Manually scrape articles from a URL or source"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        url = data.get('url')
        source = data.get('source')
        
        if url:
            # Scrape single URL
            try:
                # Create a generic scraper instance for URL scraping
                class GenericScraper(BaseScraper):
                    def __init__(self):
                        super().__init__("generic", "")
                    
                    def _get_article_urls(self, max_articles: int):
                        return []
                    
                    def _extract_article_content(self, soup, url):
                        return None
                
                scraper = GenericScraper()
                article = scraper.scrape_single_url(url)
                
                if article:
                    # Store the article
                    article_id = storage_service.store_article(article)
                    
                    if article_id:
                        # Analyze bias
                        bias_scores = bias_analyzer.analyze_article_bias(article)
                        storage_service.update_article_bias_scores(article_id, bias_scores.to_dict())
                        
                        return jsonify({
                            'success': True,
                            'message': 'Article scraped and analyzed successfully',
                            'article_id': article_id,
                            'title': article.title,
                            'source': article.source
                        })
                    else:
                        return jsonify({'error': 'Failed to store article'}), 500
                else:
                    return jsonify({'error': 'Failed to scrape article from URL'}), 400
                    
            except Exception as e:
                logger.error(f"URL scraping failed: {e}")
                return jsonify({'error': f'Scraping failed: {str(e)}'}), 400
        
        elif source:
            # Scrape from specific source
            try:
                scraped_articles = scraper_manager.scrape_source(source, limit=10)
                
                if not scraped_articles:
                    return jsonify({'error': f'No articles found from source: {source}'}), 400
                
                # Store articles and analyze bias
                stored_count = 0
                analyzed_count = 0
                
                for article in scraped_articles:
                    try:
                        article_id = storage_service.store_article(article)
                        if article_id:
                            stored_count += 1
                            try:
                                bias_scores = bias_analyzer.analyze_article_bias(article)
                                storage_service.update_article_bias_scores(article_id, bias_scores.to_dict())
                                analyzed_count += 1
                            except Exception as e:
                                logger.warning(f"Failed to analyze bias for article {article_id}: {e}")
                    except Exception as e:
                        logger.warning(f"Failed to store article: {e}")
                        continue
                
                return jsonify({
                    'success': True,
                    'message': f'Scraped {len(scraped_articles)} articles from {source}, stored {stored_count}, analyzed {analyzed_count}',
                    'articles_count': stored_count,
                    'analyzed_count': analyzed_count,
                    'source': source
                })
                
            except Exception as e:
                logger.error(f"Source scraping failed: {e}")
                return jsonify({'error': f'Source scraping failed: {str(e)}'}), 400
        
        else:
            return jsonify({'error': 'Either "url" or "source" parameter is required'}), 400
        
    except Exception as e:
        logger.error(f"Manual scraping failed: {e}")
        return jsonify({'error': 'Manual scraping failed'}), 500


@scraper_bp.route('/test-url', methods=['POST'])
def test_scrape_url():
    """Test scraping a URL without storing the article"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        
        # Create a generic scraper instance for URL scraping
        class GenericScraper(BaseScraper):
            def __init__(self):
                super().__init__("generic", "")
            
            def _get_article_urls(self, max_articles: int):
                return []
            
            def _extract_article_content(self, soup, url):
                return None
        
        scraper = GenericScraper()
        
        try:
            article = scraper.scrape_single_url(url)
            if article:
                # Analyze bias without storing
                bias_scores = bias_analyzer.analyze_article_bias(article)
                
                return jsonify({
                    'success': True,
                    'article': {
                        'title': article.title,
                        'source': article.source,
                        'content_preview': article.content[:500] + '...' if len(article.content) > 500 else article.content,
                        'publication_date': article.publication_date.isoformat() if article.publication_date else None,
                        'language': article.language
                    },
                    'bias_analysis': bias_scores.to_dict()
                })
            else:
                return jsonify({'error': 'Failed to extract article content from URL'}), 400
                
        except Exception as e:
            logger.error(f"URL test failed: {e}")
            return jsonify({'error': f'Scraping test failed: {str(e)}'}), 400
        
    except Exception as e:
        logger.error(f"URL test failed: {e}")
        return jsonify({'error': 'URL test failed'}), 500


@scraper_bp.route('/batch', methods=['POST'])
def batch_scrape():
    """Scrape articles from all sources"""
    try:
        data = request.get_json() or {}
        max_articles_per_source = data.get('max_articles_per_source', 5)
        
        # Scrape from all sources
        results = scraper_manager.scrape_all_sources(max_articles_per_source)
        
        total_scraped = 0
        total_stored = 0
        total_analyzed = 0
        source_results = {}
        
        for source_name, articles in results.items():
            scraped_count = len(articles)
            stored_count = 0
            analyzed_count = 0
            
            # Store and analyze articles
            for article in articles:
                try:
                    article_id = storage_service.store_article(article)
                    if article_id:
                        stored_count += 1
                        try:
                            bias_scores = bias_analyzer.analyze_article_bias(article)
                            storage_service.update_article_bias_scores(article_id, bias_scores.to_dict())
                            analyzed_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to analyze bias for article {article_id}: {e}")
                except Exception as e:
                    logger.warning(f"Failed to store article from {source_name}: {e}")
                    continue
            
            source_results[source_name] = {
                'scraped': scraped_count,
                'stored': stored_count,
                'analyzed': analyzed_count
            }
            
            total_scraped += scraped_count
            total_stored += stored_count
            total_analyzed += analyzed_count
        
        return jsonify({
            'success': True,
            'message': f'Batch scraping completed: {total_scraped} scraped, {total_stored} stored, {total_analyzed} analyzed',
            'total_scraped': total_scraped,
            'total_stored': total_stored,
            'total_analyzed': total_analyzed,
            'source_results': source_results
        })
        
    except Exception as e:
        logger.error(f"Batch scraping failed: {e}")
        return jsonify({'error': 'Batch scraping failed'}), 500