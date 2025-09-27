import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List, Optional

# Import services
from services.article_storage_service import ArticleStorageService
from services.bias_analyzer import BiasAnalyzer
from services.article_comparator import ArticleComparator
from scrapers.scraper_manager import ScraperManager
from config.database import initialize_database

# Import blueprints
from api.routes.articles import articles_bp
from api.routes.bias import bias_bp
from api.routes.comparison import comparison_bp
from api.routes.statistics import statistics_bp
from api.routes.scraper import scraper_bp
from api.routes.auth import auth_bp


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/build', static_url_path='')

# Configure CORS for production
if os.getenv('FLASK_ENV') == 'production':
    CORS(app, origins=['https://your-app-name.onrender.com'])
else:
    CORS(app)  # Allow all origins in development

# Register blueprints
app.register_blueprint(articles_bp)
app.register_blueprint(bias_bp)
app.register_blueprint(comparison_bp)
app.register_blueprint(statistics_bp)
app.register_blueprint(scraper_bp)
app.register_blueprint(auth_bp)


# Initialize services
storage_service = ArticleStorageService()
bias_analyzer = BiasAnalyzer()
article_comparator = ArticleComparator()
scraper_manager = ScraperManager()

# Import user service for authentication
from services.user_service import UserService
user_service = UserService()


def get_current_user_id():
    """Get current user ID from request headers"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        user_session = user_service.get_session(token)
        if user_session:
            return user_session.user_id
    return None


def filter_articles_for_user(articles, user_id=None):
    """Filter out articles hidden by the user"""
    if not user_id:
        return articles
    
    hidden_articles = user_service.get_user_hidden_articles(user_id)
    if not hidden_articles:
        return articles
    
    return [article for article in articles if str(article.id) not in hidden_articles]


def initialize_app():
    """Initialize database and services"""
    try:
        initialize_database()
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")

# Initialize app on startup
initialize_app()


# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Serve React app for all non-API routes"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(os.path.join(app.static_folder, 'static'), filename)


# Article endpoints
@app.route('/api/topics', methods=['GET'])
def get_available_topics():
    """Get list of available topics"""
    try:
        topics = storage_service.get_available_topics()
        return jsonify({
            'topics': topics,
            'count': len(topics)
        })
    except Exception as e:
        logger.error(f"Failed to get available topics: {e}")
        return jsonify({'error': 'Failed to retrieve topics'}), 500


@app.route('/api/articles', methods=['GET'])
def get_articles():
    """Get articles with optional filtering"""
    try:
        # Get query parameters
        source = request.args.get('source')
        topic = request.args.get('topic')
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Validate limit
        if limit > 200:
            limit = 200
        
        articles = []
        
        if topic:
            # Get articles by topic
            articles = storage_service.get_articles_by_topic(topic, limit, skip)
        elif source:
            # Get articles by source
            articles = storage_service.get_articles_by_source(source, limit, skip)
        elif start_date and end_date:
            # Get articles by date range
            try:
                start_dt = datetime.fromisoformat(start_date)
                end_dt = datetime.fromisoformat(end_date)
                articles = storage_service.get_articles_by_date_range(start_dt, end_dt, limit)
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DD)'}), 400
        else:
            # Get all articles (default) - most recent first
            articles = storage_service.get_recent_articles(limit, skip)
        
        # Filter articles for current user (if authenticated)
        current_user_id = get_current_user_id()
        filtered_articles = filter_articles_for_user(articles, current_user_id)
        
        # Convert articles to JSON
        articles_json = []
        for article in filtered_articles:
            article_dict = article.to_dict()
            # Convert ObjectId to string for JSON serialization
            if '_id' in article_dict:
                article_dict['id'] = str(article_dict.pop('_id'))
            articles_json.append(article_dict)
        
        # Get total count for pagination
        total_count = 0
        if topic:
            total_count = storage_service.get_articles_count_by_topic(topic)
        elif source:
            total_count = storage_service.get_articles_count_by_source(source)
        elif start_date and end_date:
            # For date range, get total count in that range
            total_count = storage_service.get_articles_count_by_date_range(start_dt, end_dt)
        else:
            # Get total count of all articles
            total_count = storage_service.get_total_articles_count()
        
        return jsonify({
            'articles': articles_json,
            'count': len(articles_json),
            'total_count': total_count,
            'limit': limit,
            'skip': skip,
            'has_more': skip + len(articles_json) < total_count
        })
        
    except Exception as e:
        logger.error(f"Failed to get articles: {e}")
        return jsonify({'error': 'Failed to retrieve articles'}), 500


@app.route('/api/articles/<article_id>', methods=['GET'])
def get_article(article_id):
    """Get a specific article by ID"""
    try:
        article = storage_service.get_article_by_id(article_id)
        
        if not article:
            return jsonify({'error': 'Article not found'}), 404
        
        article_dict = article.to_dict()
        if '_id' in article_dict:
            article_dict['id'] = str(article_dict.pop('_id'))
        
        return jsonify(article_dict)
        
    except Exception as e:
        logger.error(f"Failed to get article {article_id}: {e}")
        return jsonify({'error': 'Failed to retrieve article'}), 500





@app.route('/api/articles/search', methods=['GET'])
def search_articles():
    """Search articles by text query"""
    try:
        query = request.args.get('q')
        limit = int(request.args.get('limit', 50))
        
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
        
        articles = storage_service.search_articles(query, limit)
        
        # Filter articles for current user (if authenticated)
        current_user_id = get_current_user_id()
        filtered_articles = filter_articles_for_user(articles, current_user_id)
        
        articles_json = []
        for article in filtered_articles:
            article_dict = article.to_dict()
            if '_id' in article_dict:
                article_dict['id'] = str(article_dict.pop('_id'))
            articles_json.append(article_dict)
        
        return jsonify({
            'articles': articles_json,
            'count': len(articles_json),
            'query': query
        })
        
    except Exception as e:
        logger.error(f"Failed to search articles: {e}")
        return jsonify({'error': 'Failed to search articles'}), 500


# Bias analysis endpoints
@app.route('/api/articles/<article_id>/bias', methods=['GET'])
def get_article_bias(article_id):
    """Get bias analysis for a specific article"""
    try:
        article = storage_service.get_article_by_id(article_id)
        
        if not article:
            return jsonify({'error': 'Article not found'}), 404
        
        # Get detailed bias analysis
        detailed_analysis = bias_analyzer.get_detailed_analysis(article)
        
        return jsonify(detailed_analysis)
        
    except Exception as e:
        logger.error(f"Failed to get bias analysis for article {article_id}: {e}")
        return jsonify({'error': 'Failed to analyze article bias'}), 500


@app.route('/api/articles/<article_id>/bias', methods=['POST'])
def analyze_article_bias(article_id):
    """Analyze or re-analyze bias for a specific article"""
    try:
        article = storage_service.get_article_by_id(article_id)
        
        if not article:
            return jsonify({'error': 'Article not found'}), 404
        
        # Perform bias analysis
        bias_scores = bias_analyzer.analyze_article_bias(article)
        
        # Update article with bias scores
        bias_scores_dict = bias_scores.to_dict()
        success = storage_service.update_article_bias_scores(article_id, bias_scores_dict)
        
        if success:
            return jsonify({
                'message': 'Bias analysis completed',
                'bias_scores': bias_scores_dict
            })
        else:
            return jsonify({'error': 'Failed to update bias scores'}), 500
        
    except Exception as e:
        logger.error(f"Failed to analyze bias for article {article_id}: {e}")
        return jsonify({'error': 'Failed to analyze article bias'}), 500


@app.route('/api/bias/analyze-text', methods=['POST'])
def analyze_text_bias():
    """Analyze bias for arbitrary text (for testing)"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        language = data.get('language')  # Optional
        
        # Analyze text
        analysis = bias_analyzer.analyze_text_sample(text, language)
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Failed to analyze text bias: {e}")
        return jsonify({'error': 'Failed to analyze text bias'}), 500


# Article comparison endpoints
@app.route('/api/articles/<article_id>/similar', methods=['GET'])
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


@app.route('/api/articles/<article_id>/comparison', methods=['GET'])
def get_article_comparison(article_id):
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


# Statistics and dashboard endpoints
@app.route('/api/statistics/overview', methods=['GET'])
def get_overview_statistics():
    """Get overview statistics for dashboard"""
    try:
        # Get storage statistics with fallback
        try:
            storage_stats = storage_service.get_storage_statistics()
        except Exception as e:
            logger.warning(f"Failed to get storage statistics, using defaults: {e}")
            storage_stats = {
                'total_articles': 0,
                'analyzed_articles': 0,
                'language_distribution': {},
                'source_distribution': {}
            }
        
        # Get recent articles for analysis with fallback
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            recent_articles = storage_service.get_articles_by_date_range(start_date, end_date, 100)
        except Exception as e:
            logger.warning(f"Failed to get recent articles, using empty list: {e}")
            recent_articles = []
        
        # Calculate bias distribution
        bias_distribution = {'left': 0, 'center': 0, 'right': 0}
        sentiment_distribution = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for article in recent_articles:
            try:
                if hasattr(article, 'bias_scores') and article.bias_scores:
                    political_bias = getattr(article.bias_scores, 'political_bias', 0.5)
                    if political_bias < 0.4:
                        bias_distribution['left'] += 1
                    elif political_bias > 0.6:
                        bias_distribution['right'] += 1
                    else:
                        bias_distribution['center'] += 1
                    
                    sentiment = getattr(article.bias_scores, 'sentiment_score', 0.5)
                    if sentiment < 0.4:
                        sentiment_distribution['negative'] += 1
                    elif sentiment > 0.6:
                        sentiment_distribution['positive'] += 1
                    else:
                        sentiment_distribution['neutral'] += 1
            except Exception as e:
                logger.debug(f"Error processing article bias data: {e}")
                continue
        
        # Get source counts with fallback
        try:
            source_counts = storage_service.get_article_count_by_source()
        except Exception as e:
            logger.warning(f"Failed to get source counts, using empty dict: {e}")
            source_counts = {}
        
        return jsonify({
            'total_articles': storage_stats.get('total_articles', 0),
            'analyzed_articles': storage_stats.get('analyzed_articles', 0),
            'recent_articles': len(recent_articles),
            'bias_distribution': bias_distribution,
            'sentiment_distribution': sentiment_distribution,
            'language_distribution': storage_stats.get('language_distribution', {}),
            'source_counts': source_counts
        })
        
    except Exception as e:
        logger.error(f"Failed to get overview statistics: {e}")
        # Return minimal working response instead of error
        return jsonify({
            'total_articles': 0,
            'analyzed_articles': 0,
            'recent_articles': 0,
            'bias_distribution': {'left': 0, 'center': 0, 'right': 0},
            'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
            'language_distribution': {},
            'source_counts': {}
        })

@app.route('/api/statistics/sources', methods=['GET'])
def get_source_statistics():
    """Get statistics by news source"""
    try:
        # Get article counts by source
        source_counts = storage_service.get_article_count_by_source()
        
        # Get storage statistics
        storage_stats = storage_service.get_storage_statistics()
        
        return jsonify({
            'source_counts': source_counts,
            'total_articles': storage_stats.get('total_articles', 0),
            'analyzed_articles': storage_stats.get('analyzed_articles', 0),
            'language_distribution': storage_stats.get('language_distribution', {}),
            'recent_articles': storage_stats.get('recent_articles', 0)
        })
        
    except Exception as e:
        logger.error(f"Failed to get source statistics: {e}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500


@app.route('/api/statistics/bias-comparison', methods=['GET'])
def get_bias_comparison_statistics():
    """Get bias comparison statistics across sources"""
    try:
        # Get recent articles grouped by source
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
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
                'end_date': end_date.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get bias comparison statistics: {e}")
        return jsonify({'error': 'Failed to retrieve bias comparison statistics'}), 500





if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)