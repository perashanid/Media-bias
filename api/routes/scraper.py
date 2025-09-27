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
    """Get list of available news sources for scraping with health status"""
    try:
        sources = scraper_manager.get_available_sources()
        scraper_info = scraper_manager.get_scraper_info()
        health_status = scraper_manager.get_scraper_health_status()
        
        return jsonify({
            'sources': sources,
            'scraper_info': scraper_info,
            'health_status': health_status,
            'total_sources': len(sources),
            'healthy_sources': health_status['healthy_scrapers']
        })
        
    except Exception as e:
        logger.error(f"Failed to get available sources: {e}")
        return jsonify({'error': 'Failed to retrieve sources'}), 500


@scraper_bp.route('/health', methods=['GET'])
def get_scraper_health():
    """Get detailed health status of all scrapers"""
    try:
        health_status = scraper_manager.get_scraper_health_status()
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Failed to get scraper health: {e}")
        return jsonify({'error': 'Failed to retrieve scraper health'}), 500


@scraper_bp.route('/health/reset', methods=['POST'])
def reset_scraper_health():
    """Reset health status for scrapers"""
    try:
        data = request.get_json() or {}
        source_name = data.get('source')
        
        scraper_manager.reset_scraper_health(source_name)
        
        message = f"Health status reset for {source_name}" if source_name else "Health status reset for all scrapers"
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Failed to reset scraper health: {e}")
        return jsonify({'error': 'Failed to reset scraper health'}), 500


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
                logger.info(f"Starting URL scraping: {url}")
                
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
                    logger.info(f"Article scraped successfully: {article.title[:50]}...")
                    
                    # Store the article
                    article_id = storage_service.store_article(article)
                    
                    if article_id:
                        logger.info(f"Article stored with ID: {article_id}")
                        
                        # Analyze bias
                        try:
                            bias_scores = bias_analyzer.analyze_article_bias(article)
                            storage_service.update_article_bias_scores(article_id, bias_scores.to_dict())
                            logger.info(f"Bias analysis completed for article {article_id}")
                            
                            return jsonify({
                                'success': True,
                                'message': 'Article scraped and analyzed successfully',
                                'article_id': article_id,
                                'title': article.title,
                                'source': article.source
                            })
                        except Exception as e:
                            logger.warning(f"Bias analysis failed: {e}")
                            return jsonify({
                                'success': True,
                                'message': 'Article scraped and stored successfully (bias analysis failed)',
                                'article_id': article_id,
                                'title': article.title,
                                'source': article.source,
                                'warning': f'Bias analysis failed: {str(e)}'
                            })
                    else:
                        logger.error("Failed to store article in database")
                        return jsonify({'success': False, 'error': 'Failed to store article in database'}), 500
                else:
                    logger.error("Failed to extract article content from URL")
                    return jsonify({'success': False, 'error': 'Failed to scrape article from URL. The URL might not contain a valid article or the website structure is not supported.'}), 400
                    
            except Exception as e:
                error_msg = f"URL scraping failed: {str(e)}"
                logger.error(error_msg)
                return jsonify({'success': False, 'error': error_msg}), 400
        
        elif source:
            # Scrape from specific source
            try:
                logger.info(f"🎯 Starting scraping from source: {source}")
                
                # Check if comprehensive scraping is requested
                comprehensive = data.get('comprehensive', False)
                max_articles = data.get('max_articles', 50 if comprehensive else 10)
                max_depth = data.get('max_depth', 3)
                analyze_bias = data.get('analyze_bias', True)
                
                # Validate source exists
                available_sources = scraper_manager.get_available_sources()
                if source not in available_sources:
                    return jsonify({
                        'success': False,
                        'error': f'Unknown source: {source}',
                        'available_sources': available_sources
                    }), 400
                
                if comprehensive:
                    logger.info(f"🔍 Comprehensive scraping from {source} (max_articles={max_articles}, max_depth={max_depth})")
                    scraped_articles = scraper_manager.comprehensive_scrape_source(source, max_articles, max_depth)
                else:
                    scraped_articles = scraper_manager.scrape_source(source, max_articles)
                
                logger.info(f"📄 Scraped {len(scraped_articles)} articles from {source}")
                
                if not scraped_articles:
                    # Get scraper health info
                    health_status = scraper_manager.get_scraper_health_status()
                    scraper_health = health_status['scraper_details'].get(source, {})
                    
                    return jsonify({
                        'success': False,
                        'error': f'No articles found from source: {source}',
                        'possible_causes': [
                            'Network connectivity issues',
                            'Website structure changes',
                            'Rate limiting or blocking',
                            'Temporary server issues'
                        ],
                        'scraper_health': scraper_health,
                        'suggestions': [
                            'Try again in a few minutes',
                            'Check if the website is accessible',
                            'Reset scraper health if needed'
                        ]
                    }), 400
                
                # Store articles and analyze bias
                stored_count = 0
                analyzed_count = 0
                errors = []
                successful_articles = []
                
                for i, article in enumerate(scraped_articles):
                    try:
                        logger.debug(f"📝 Processing article {i+1}/{len(scraped_articles)}: {article.title[:50]}...")
                        article_id = storage_service.store_article(article)
                        
                        if article_id:
                            stored_count += 1
                            article_info = {
                                'id': article_id,
                                'title': article.title,
                                'url': article.url,
                                'language': article.language
                            }
                            
                            # Analyze bias if requested
                            if analyze_bias:
                                try:
                                    bias_scores = bias_analyzer.analyze_article_bias(article)
                                    storage_service.update_article_bias_scores(article_id, bias_scores.to_dict())
                                    analyzed_count += 1
                                    article_info['bias_analyzed'] = True
                                    logger.debug(f"🧠 Bias analysis completed for article {article_id}")
                                except Exception as e:
                                    error_msg = f"Failed to analyze bias for article {article_id}: {e}"
                                    logger.warning(error_msg)
                                    errors.append(error_msg)
                                    article_info['bias_analyzed'] = False
                            
                            successful_articles.append(article_info)
                            logger.debug(f"✅ Successfully processed article {i+1}/{len(scraped_articles)}")
                        else:
                            error_msg = f"Failed to store article: {article.title[:50]}"
                            logger.warning(error_msg)
                            errors.append(error_msg)
                            
                    except Exception as e:
                        error_msg = f"Failed to process article {i+1}: {e}"
                        logger.warning(error_msg)
                        errors.append(error_msg)
                        continue
                
                # Calculate success rate
                success_rate = (stored_count / len(scraped_articles) * 100) if scraped_articles else 0
                
                response_data = {
                    'success': True,
                    'message': f'Scraped {len(scraped_articles)} articles from {source}, stored {stored_count}, analyzed {analyzed_count}',
                    'summary': {
                        'source': source,
                        'articles_scraped': len(scraped_articles),
                        'articles_stored': stored_count,
                        'articles_analyzed': analyzed_count,
                        'success_rate': round(success_rate, 1),
                        'error_count': len(errors)
                    },
                    'articles': successful_articles[:10],  # Return first 10 articles
                    'scraper_health': scraper_manager.get_scraper_health_status()['scraper_details'].get(source, {})
                }
                
                if errors:
                    response_data['warnings'] = errors[:5]  # Include first 5 errors
                    response_data['total_errors'] = len(errors)
                
                logger.info(f"🎯 {source} scraping completed: {stored_count}/{len(scraped_articles)} articles stored ({success_rate:.1f}%)")
                
                return jsonify(response_data)
                
            except Exception as e:
                error_msg = f"Source scraping failed: {str(e)}"
                logger.error(error_msg)
                return jsonify({'success': False, 'error': error_msg}), 400
        
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


@scraper_bp.route('/comprehensive', methods=['POST'])
def comprehensive_scrape():
    """Perform comprehensive scraping by crawling entire website"""
    try:
        data = request.get_json() or {}
        source = data.get('source')
        max_articles = data.get('max_articles', 100)
        max_depth = data.get('max_depth', 3)
        
        if not source:
            return jsonify({'error': 'Source parameter is required'}), 400
        
        logger.info(f"Starting comprehensive scraping from {source} (max_articles={max_articles}, max_depth={max_depth})")
        
        # Perform comprehensive scraping
        scraped_articles = scraper_manager.comprehensive_scrape_source(source, max_articles, max_depth)
        
        if not scraped_articles:
            return jsonify({
                'success': False,
                'error': f'No articles found during comprehensive scraping of {source}'
            }), 400
        
        # Store articles and analyze bias
        stored_count = 0
        analyzed_count = 0
        errors = []
        
        for i, article in enumerate(scraped_articles):
            try:
                logger.info(f"Processing article {i+1}/{len(scraped_articles)}: {article.title[:50]}...")
                article_id = storage_service.store_article(article)
                if article_id:
                    stored_count += 1
                    logger.info(f"Article stored with ID: {article_id}")
                    
                    try:
                        bias_scores = bias_analyzer.analyze_article_bias(article)
                        storage_service.update_article_bias_scores(article_id, bias_scores.to_dict())
                        analyzed_count += 1
                        logger.debug(f"Bias analysis completed for article {article_id}")
                    except Exception as e:
                        error_msg = f"Failed to analyze bias for article {article_id}: {e}"
                        logger.warning(error_msg)
                        errors.append(error_msg)
                else:
                    error_msg = f"Failed to store article: {article.title[:50]}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
            except Exception as e:
                error_msg = f"Failed to process article {i+1}: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
                continue
        
        response_data = {
            'success': True,
            'message': f'Comprehensive scraping completed: {len(scraped_articles)} articles found, {stored_count} stored, {analyzed_count} analyzed',
            'articles_scraped': len(scraped_articles),
            'articles_stored': stored_count,
            'articles_analyzed': analyzed_count,
            'source': source,
            'max_depth': max_depth
        }
        
        if errors:
            response_data['warnings'] = errors[:10]  # Include first 10 errors
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Comprehensive scraping failed: {e}")
        return jsonify({'error': f'Comprehensive scraping failed: {str(e)}'}), 500


@scraper_bp.route('/statistics', methods=['GET'])
def get_scraping_statistics():
    """Get comprehensive scraping statistics"""
    try:
        # Get scraper health and performance stats
        health_status = scraper_manager.get_scraper_health_status()
        scraper_info = scraper_manager.get_scraper_info()
        
        # Get recent scraping activity from database
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        try:
            recent_articles = storage_service.get_articles_by_date_range(start_date, end_date, 1000)
            
            # Group by source
            articles_by_source = {}
            for article in recent_articles:
                source = article.source
                if source not in articles_by_source:
                    articles_by_source[source] = []
                articles_by_source[source].append(article)
            
            source_stats = {}
            for source, articles in articles_by_source.items():
                source_stats[source] = {
                    'recent_articles': len(articles),
                    'languages': list(set(article.language for article in articles if article.language)),
                    'avg_content_length': sum(len(article.content) for article in articles) / len(articles) if articles else 0
                }
        except Exception as e:
            logger.warning(f"Failed to get recent articles: {e}")
            source_stats = {}
        
        return jsonify({
            'scraper_health': health_status,
            'scraper_performance': {
                source: {
                    'source_name': info['source_name'],
                    'base_url': info['base_url'],
                    'is_healthy': info['is_healthy'],
                    'total_articles_scraped': info['total_articles_scraped'],
                    'total_errors': info['total_errors'],
                    'average_response_time': info['average_response_time'],
                    'last_successful_scrape': info['last_successful_scrape']
                }
                for source, info in scraper_info.items()
            },
            'recent_activity': source_stats,
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get scraping statistics: {e}")
        return jsonify({'error': 'Failed to retrieve scraping statistics'}), 500


@scraper_bp.route('/validate-source', methods=['POST'])
def validate_source():
    """Validate if a source is working properly"""
    try:
        data = request.get_json()
        if not data or 'source' not in data:
            return jsonify({'error': 'Source parameter is required'}), 400
        
        source_name = data['source']
        
        # Check if source exists
        available_sources = scraper_manager.get_available_sources()
        if source_name not in available_sources:
            return jsonify({
                'valid': False,
                'error': f'Unknown source: {source_name}',
                'available_sources': available_sources
            }), 400
        
        # Try to scrape a small number of articles to test
        logger.info(f"🔍 Validating source: {source_name}")
        
        try:
            test_articles = scraper_manager.scrape_single_source(source_name, 2)
            
            if test_articles:
                # Test article structure
                sample_article = test_articles[0]
                validation_results = {
                    'has_title': bool(sample_article.title and len(sample_article.title) > 5),
                    'has_content': bool(sample_article.content and len(sample_article.content) > 100),
                    'has_url': bool(sample_article.url),
                    'has_date': bool(sample_article.publication_date),
                    'language_detected': bool(sample_article.language)
                }
                
                all_valid = all(validation_results.values())
                
                return jsonify({
                    'valid': all_valid,
                    'source': source_name,
                    'test_results': {
                        'articles_found': len(test_articles),
                        'validation': validation_results,
                        'sample_article': {
                            'title': sample_article.title[:100] + '...' if len(sample_article.title) > 100 else sample_article.title,
                            'content_length': len(sample_article.content),
                            'language': sample_article.language,
                            'url': sample_article.url
                        }
                    },
                    'scraper_health': scraper_manager.get_scraper_health_status()['scraper_details'].get(source_name, {})
                })
            else:
                return jsonify({
                    'valid': False,
                    'source': source_name,
                    'error': 'No articles could be scraped',
                    'scraper_health': scraper_manager.get_scraper_health_status()['scraper_details'].get(source_name, {})
                })
                
        except Exception as e:
            return jsonify({
                'valid': False,
                'source': source_name,
                'error': f'Validation failed: {str(e)}',
                'scraper_health': scraper_manager.get_scraper_health_status()['scraper_details'].get(source_name, {})
            })
        
    except Exception as e:
        logger.error(f"Source validation failed: {e}")
        return jsonify({'error': 'Source validation failed'}), 500


@scraper_bp.route('/batch', methods=['POST'])
def batch_scrape():
    """Scrape articles from all sources with enhanced monitoring"""
    try:
        data = request.get_json() or {}
        max_articles_per_source = data.get('max_articles_per_source', 5)
        analyze_bias = data.get('analyze_bias', True)
        
        logger.info(f"🚀 Starting batch scraping: {max_articles_per_source} articles per source")
        
        # Scrape from all sources
        results = scraper_manager.scrape_all_sources(max_articles_per_source)
        
        total_scraped = 0
        total_stored = 0
        total_analyzed = 0
        total_errors = 0
        source_results = {}
        
        for source_name, articles in results.items():
            scraped_count = len(articles)
            stored_count = 0
            analyzed_count = 0
            error_count = 0
            
            logger.info(f"📝 Processing {scraped_count} articles from {source_name}")
            
            # Store and analyze articles
            for i, article in enumerate(articles):
                try:
                    article_id = storage_service.store_article(article)
                    if article_id:
                        stored_count += 1
                        logger.debug(f"✅ Stored article {i+1}/{scraped_count} from {source_name}")
                        
                        # Analyze bias if requested
                        if analyze_bias:
                            try:
                                bias_scores = bias_analyzer.analyze_article_bias(article)
                                storage_service.update_article_bias_scores(article_id, bias_scores.to_dict())
                                analyzed_count += 1
                                logger.debug(f"🧠 Analyzed bias for article {i+1}/{scraped_count} from {source_name}")
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to analyze bias for article {article_id}: {e}")
                                error_count += 1
                    else:
                        logger.warning(f"⚠️ Failed to store article {i+1}/{scraped_count} from {source_name}")
                        error_count += 1
                        
                except Exception as e:
                    logger.warning(f"❌ Failed to process article {i+1}/{scraped_count} from {source_name}: {e}")
                    error_count += 1
                    continue
            
            source_results[source_name] = {
                'scraped': scraped_count,
                'stored': stored_count,
                'analyzed': analyzed_count,
                'errors': error_count,
                'success_rate': (stored_count / scraped_count * 100) if scraped_count > 0 else 0
            }
            
            total_scraped += scraped_count
            total_stored += stored_count
            total_analyzed += analyzed_count
            total_errors += error_count
            
            logger.info(f"📊 {source_name}: {stored_count}/{scraped_count} stored ({source_results[source_name]['success_rate']:.1f}%)")
        
        # Calculate overall success rate
        overall_success_rate = (total_stored / total_scraped * 100) if total_scraped > 0 else 0
        
        logger.info(f"🎯 Batch scraping completed: {total_stored}/{total_scraped} articles stored ({overall_success_rate:.1f}%)")
        
        return jsonify({
            'success': True,
            'message': f'Batch scraping completed: {total_scraped} scraped, {total_stored} stored, {total_analyzed} analyzed',
            'summary': {
                'total_scraped': total_scraped,
                'total_stored': total_stored,
                'total_analyzed': total_analyzed,
                'total_errors': total_errors,
                'overall_success_rate': round(overall_success_rate, 1),
                'sources_processed': len(results)
            },
            'source_results': source_results,
            'scraper_health': scraper_manager.get_scraper_health_status()
        })
        
    except Exception as e:
        logger.error(f"❌ Batch scraping failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Batch scraping failed: {str(e)}',
            'scraper_health': scraper_manager.get_scraper_health_status()
        }), 500