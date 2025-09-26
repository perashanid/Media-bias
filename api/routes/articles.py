from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import logging
from services.article_storage_service import ArticleStorageService
from services.bias_analyzer import BiasAnalyzer

logger = logging.getLogger(__name__)

# Create blueprint
articles_bp = Blueprint('articles', __name__, url_prefix='/api/articles')

# Initialize services
storage_service = ArticleStorageService()
bias_analyzer = BiasAnalyzer()


@articles_bp.route('', methods=['GET'])
def get_articles():
    """Get articles with optional filtering"""
    try:
        # Get query parameters
        source = request.args.get('source')
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Validate limit
        if limit > 200:
            limit = 200
        
        articles = []
        
        if source:
            articles = storage_service.get_articles_by_source(source, limit, skip)
        elif start_date and end_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                end_dt = datetime.fromisoformat(end_date)
                articles = storage_service.get_articles_by_date_range(start_dt, end_dt, limit)
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DD)'}), 400
        else:
            # Get recent articles (default)
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=7)
            articles = storage_service.get_articles_by_date_range(start_dt, end_dt, limit)
        
        # Convert articles to JSON
        articles_json = []
        for article in articles:
            article_dict = article.to_dict()
            if '_id' in article_dict:
                article_dict['id'] = str(article_dict.pop('_id'))
            articles_json.append(article_dict)
        
        return jsonify({
            'articles': articles_json,
            'count': len(articles_json),
            'limit': limit,
            'skip': skip
        })
        
    except Exception as e:
        logger.error(f"Failed to get articles: {e}")
        return jsonify({'error': 'Failed to retrieve articles'}), 500


@articles_bp.route('/<article_id>', methods=['GET'])
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


@articles_bp.route('/search', methods=['GET'])
def search_articles():
    """Search articles by text query"""
    try:
        query = request.args.get('q')
        limit = int(request.args.get('limit', 50))
        
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
        
        articles = storage_service.search_articles(query, limit)
        
        articles_json = []
        for article in articles:
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


@articles_bp.route('/<article_id>/bias', methods=['GET'])
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


@articles_bp.route('/<article_id>/bias', methods=['POST'])
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