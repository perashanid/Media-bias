from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import logging
from services.article_storage_service import ArticleStorageService
from services.article_comparator import ArticleComparator

logger = logging.getLogger(__name__)

# Create blueprint
comparison_bp = Blueprint('comparison', __name__, url_prefix='/api/comparison')

# Initialize services
storage_service = ArticleStorageService()
article_comparator = ArticleComparator()


@comparison_bp.route('/articles/<article_id>/similar', methods=['GET'])
def get_similar_articles(article_id):
    """Get articles similar to the specified article"""
    try:
        target_article = storage_service.get_article_by_id(article_id)
        
        if not target_article:
            return jsonify({'error': 'Article not found'}), 404
        
        # Get candidate articles from recent time period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        candidate_articles = storage_service.get_articles_by_date_range(start_date, end_date, 500)
        
        # Find related articles
        threshold = float(request.args.get('threshold', 0.3))
        related_articles = article_comparator.find_related_articles(
            target_article, candidate_articles, threshold
        )
        
        # Convert to JSON
        related_json = []
        for article in related_articles:
            article_dict = article.to_dict()
            if '_id' in article_dict:
                article_dict['id'] = str(article_dict.pop('_id'))
            related_json.append(article_dict)
        
        return jsonify({
            'target_article_id': article_id,
            'related_articles': related_json,
            'count': len(related_json),
            'threshold': threshold
        })
        
    except Exception as e:
        logger.error(f"Failed to find similar articles for {article_id}: {e}")
        return jsonify({'error': 'Failed to find similar articles'}), 500


@comparison_bp.route('/articles/<article_id>/report', methods=['GET'])
def get_comparison_report(article_id):
    """Get bias comparison report for an article and its related articles"""
    try:
        target_article = storage_service.get_article_by_id(article_id)
        
        if not target_article:
            return jsonify({'error': 'Article not found'}), 404
        
        # Get candidate articles
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3)  # Shorter window for comparison
        candidate_articles = storage_service.get_articles_by_date_range(start_date, end_date, 200)
        
        # Find related articles
        related_articles = article_comparator.find_related_articles(
            target_article, candidate_articles, 0.4  # Higher threshold for comparison
        )
        
        if not related_articles:
            return jsonify({
                'message': 'No related articles found for comparison',
                'target_article_id': article_id
            })
        
        # Include target article in comparison
        all_articles = [target_article] + related_articles
        
        # Generate comparison report
        comparison_report = article_comparator.generate_comparison_report(all_articles)
        
        if not comparison_report:
            return jsonify({'error': 'Failed to generate comparison report'}), 500
        
        # Convert to JSON
        report_dict = comparison_report.to_dict()
        
        # Convert article IDs
        for i, article in enumerate(report_dict['articles']):
            if '_id' in article:
                article['id'] = str(article.pop('_id'))
        
        return jsonify(report_dict)
        
    except Exception as e:
        logger.error(f"Failed to generate comparison for article {article_id}: {e}")
        return jsonify({'error': 'Failed to generate comparison report'}), 500


@comparison_bp.route('/sources', methods=['GET'])
def compare_sources():
    """Compare bias patterns across different news sources"""
    try:
        # Get time range from query parameters
        days = int(request.args.get('days', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get articles from the specified time range
        articles = storage_service.get_articles_by_date_range(start_date, end_date, 1000)
        
        # Group articles by source
        articles_by_source = {}
        for article in articles:
            source = article.source
            if source not in articles_by_source:
                articles_by_source[source] = []
            articles_by_source[source].append(article)
        
        # Compare bias patterns across sources
        source_comparison = article_comparator.compare_source_bias_patterns(articles_by_source)
        
        return jsonify({
            'source_comparison': source_comparison,
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'total_articles_analyzed': len(articles)
        })
        
    except Exception as e:
        logger.error(f"Failed to compare sources: {e}")
        return jsonify({'error': 'Failed to compare sources'}), 500


@comparison_bp.route('/clusters', methods=['GET'])
def get_story_clusters():
    """Get story clusters from recent articles"""
    try:
        # Get time range and similarity threshold from query parameters
        days = int(request.args.get('days', 7))
        threshold = float(request.args.get('threshold', 0.4))
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get recent articles
        articles = storage_service.get_articles_by_date_range(start_date, end_date, 500)
        
        # Find story clusters
        clusters = article_comparator.find_story_clusters(articles, threshold)
        
        # Convert clusters to JSON
        clusters_json = []
        for cluster in clusters:
            cluster_articles = []
            for article in cluster:
                article_dict = article.to_dict()
                if '_id' in article_dict:
                    article_dict['id'] = str(article_dict.pop('_id'))
                cluster_articles.append(article_dict)
            
            clusters_json.append({
                'articles': cluster_articles,
                'article_count': len(cluster_articles),
                'sources': list(set(article.source for article in cluster))
            })
        
        return jsonify({
            'clusters': clusters_json,
            'cluster_count': len(clusters_json),
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'similarity_threshold': threshold
        })
        
    except Exception as e:
        logger.error(f"Failed to get story clusters: {e}")
        return jsonify({'error': 'Failed to get story clusters'}), 500


@comparison_bp.route('/bias-differences', methods=['POST'])
def calculate_bias_differences():
    """Calculate bias differences for a specific set of articles"""
    try:
        data = request.get_json()
        
        if not data or 'article_ids' not in data:
            return jsonify({'error': 'article_ids field is required'}), 400
        
        article_ids = data['article_ids']
        
        if len(article_ids) < 2:
            return jsonify({'error': 'At least 2 articles are required for comparison'}), 400
        
        # Get articles
        articles = []
        for article_id in article_ids:
            article = storage_service.get_article_by_id(article_id)
            if article:
                articles.append(article)
        
        if len(articles) < 2:
            return jsonify({'error': 'Could not find enough valid articles for comparison'}), 400
        
        # Calculate bias differences
        bias_differences = article_comparator.calculate_bias_differences(articles)
        
        # Generate comparison report
        comparison_report = article_comparator.generate_comparison_report(articles)
        
        result = {
            'bias_differences': bias_differences,
            'article_count': len(articles),
            'sources_compared': list(set(article.source for article in articles))
        }
        
        if comparison_report:
            result['comparison_report'] = {
                'story_id': comparison_report.story_id,
                'key_differences': comparison_report.key_differences,
                'similarity_scores': comparison_report.similarity_scores
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to calculate bias differences: {e}")
        return jsonify({'error': 'Failed to calculate bias differences'}), 500


@comparison_bp.route('/custom', methods=['POST'])
def custom_comparison():
    """Compare custom inputs (URLs, text, or article IDs)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        inputs = data.get('inputs', [])
        
        if len(inputs) < 2:
            return jsonify({'error': 'At least 2 inputs are required for comparison'}), 400
        
        from models.article import Article
        from services.bias_analyzer import BiasAnalyzer
        
        bias_analyzer = BiasAnalyzer()
        articles = []
        
        # Process each input
        for i, input_item in enumerate(inputs):
            input_type = input_item.get('type')  # 'url', 'text', or 'article_id'
            
            if input_type == 'article_id':
                # Get existing article
                article = storage_service.get_article_by_id(input_item['value'])
                if article:
                    articles.append(article)
                    
            elif input_type == 'url':
                # For URL scraping, we'll use a simple approach for now
                try:
                    import requests
                    from bs4 import BeautifulSoup
                    from datetime import datetime
                    
                    response = requests.get(input_item['value'], timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract title and content (basic extraction)
                    title = soup.find('title')
                    title_text = title.get_text().strip() if title else input_item.get('title', 'Scraped Article')
                    
                    # Get text content
                    for script in soup(["script", "style"]):
                        script.decompose()
                    content = soup.get_text()
                    
                    # Clean up content
                    lines = (line.strip() for line in content.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    content = ' '.join(chunk for chunk in chunks if chunk)
                    
                    if len(content) > 100:  # Only process if we got meaningful content
                        article = Article(
                            title=title_text,
                            content=content[:5000],  # Limit content length
                            source=input_item.get('source', 'Scraped'),
                            url=input_item['value'],
                            publication_date=datetime.now(),
                            language=input_item.get('language', 'en'),
                            author=None,
                            scraped_at=datetime.now()
                        )
                        
                        # Analyze bias for scraped article
                        bias_scores = bias_analyzer.analyze_article_bias(article)
                        article.bias_scores = bias_scores
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to scrape URL {input_item['value']}: {e}")
                    continue
                    
            elif input_type == 'text':
                # Create article from text
                try:
                    from datetime import datetime
                    article = Article(
                        title=input_item.get('title', f'Custom Text {i+1}'),
                        content=input_item['value'],
                        source=input_item.get('source', 'Custom Input'),
                        url='',
                        publication_date=datetime.now(),
                        language=input_item.get('language', 'en'),
                        author=None,
                        scraped_at=datetime.now()
                    )
                    
                    # Analyze bias for text
                    bias_scores = bias_analyzer.analyze_article_bias(article)
                    article.bias_scores = bias_scores
                    articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to process text input: {e}")
                    continue
        
        if len(articles) < 2:
            return jsonify({'error': 'Could not process enough valid inputs for comparison'}), 400
        
        # Generate comparison report
        comparison_report = article_comparator.generate_comparison_report(articles)
        
        if not comparison_report:
            return jsonify({'error': 'Failed to generate comparison report'}), 500
        
        # Convert to JSON
        report_dict = comparison_report.to_dict()
        
        # Convert article data
        for article in report_dict['articles']:
            if '_id' in article:
                article['id'] = str(article.pop('_id'))
        
        return jsonify(report_dict)
        
    except Exception as e:
        logger.error(f"Failed to perform custom comparison: {e}")
        return jsonify({'error': 'Failed to perform custom comparison'}), 500