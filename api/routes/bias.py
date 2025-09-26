from flask import Blueprint, request, jsonify
import logging
from services.bias_analyzer import BiasAnalyzer
from services.article_storage_service import ArticleStorageService

logger = logging.getLogger(__name__)

# Create blueprint
bias_bp = Blueprint('bias', __name__, url_prefix='/api/bias')

# Initialize services
bias_analyzer = BiasAnalyzer()
storage_service = ArticleStorageService()


@bias_bp.route('/analyze-text', methods=['POST'])
def analyze_text_bias():
    """Analyze bias for arbitrary text (for testing and demonstration)"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        language = data.get('language')  # Optional language specification
        
        if not text.strip():
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        # Analyze text
        analysis = bias_analyzer.analyze_text_sample(text, language)
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Failed to analyze text bias: {e}")
        return jsonify({'error': 'Failed to analyze text bias'}), 500


@bias_bp.route('/batch-analyze', methods=['POST'])
def batch_analyze_articles():
    """Analyze bias for multiple articles in batch"""
    try:
        data = request.get_json()
        
        if not data or 'article_ids' not in data:
            return jsonify({'error': 'article_ids field is required'}), 400
        
        article_ids = data['article_ids']
        
        if not isinstance(article_ids, list) or len(article_ids) == 0:
            return jsonify({'error': 'article_ids must be a non-empty list'}), 400
        
        if len(article_ids) > 50:  # Limit batch size
            return jsonify({'error': 'Maximum 50 articles can be analyzed in one batch'}), 400
        
        results = []
        successful_analyses = 0
        failed_analyses = 0
        
        for article_id in article_ids:
            try:
                # Get article
                article = storage_service.get_article_by_id(article_id)
                
                if not article:
                    results.append({
                        'article_id': article_id,
                        'status': 'error',
                        'error': 'Article not found'
                    })
                    failed_analyses += 1
                    continue
                
                # Perform bias analysis
                bias_scores = bias_analyzer.analyze_article_bias(article)
                
                # Update article with bias scores
                bias_scores_dict = bias_scores.to_dict()
                update_success = storage_service.update_article_bias_scores(article_id, bias_scores_dict)
                
                if update_success:
                    results.append({
                        'article_id': article_id,
                        'status': 'success',
                        'bias_scores': bias_scores_dict
                    })
                    successful_analyses += 1
                else:
                    results.append({
                        'article_id': article_id,
                        'status': 'error',
                        'error': 'Failed to update bias scores'
                    })
                    failed_analyses += 1
                
            except Exception as e:
                logger.error(f"Failed to analyze article {article_id}: {e}")
                results.append({
                    'article_id': article_id,
                    'status': 'error',
                    'error': str(e)
                })
                failed_analyses += 1
        
        return jsonify({
            'results': results,
            'summary': {
                'total_requested': len(article_ids),
                'successful_analyses': successful_analyses,
                'failed_analyses': failed_analyses
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to perform batch analysis: {e}")
        return jsonify({'error': 'Failed to perform batch analysis'}), 500


@bias_bp.route('/analyze-pending', methods=['POST'])
def analyze_pending_articles():
    """Analyze bias for articles that haven't been analyzed yet"""
    try:
        # Get limit from request
        data = request.get_json() or {}
        limit = data.get('limit', 100)
        
        if limit > 500:  # Safety limit
            limit = 500
        
        # Get articles without bias analysis
        pending_articles = storage_service.get_articles_without_bias_analysis(limit)
        
        if not pending_articles:
            return jsonify({
                'message': 'No pending articles found for analysis',
                'analyzed_count': 0
            })
        
        successful_analyses = 0
        failed_analyses = 0
        
        for article in pending_articles:
            try:
                # Perform bias analysis
                bias_scores = bias_analyzer.analyze_article_bias(article)
                
                # Update article with bias scores
                bias_scores_dict = bias_scores.to_dict()
                update_success = storage_service.update_article_bias_scores(article.id, bias_scores_dict)
                
                if update_success:
                    successful_analyses += 1
                else:
                    failed_analyses += 1
                    
            except Exception as e:
                logger.error(f"Failed to analyze pending article {article.id}: {e}")
                failed_analyses += 1
        
        return jsonify({
            'message': f'Analyzed {successful_analyses} articles',
            'summary': {
                'total_pending': len(pending_articles),
                'successful_analyses': successful_analyses,
                'failed_analyses': failed_analyses
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to analyze pending articles: {e}")
        return jsonify({'error': 'Failed to analyze pending articles'}), 500


@bias_bp.route('/distribution', methods=['GET'])
def get_bias_distribution():
    """Get distribution of bias scores across all analyzed articles"""
    try:
        # Get time range from query parameters
        days = int(request.args.get('days', 30))
        source = request.args.get('source')  # Optional source filter
        
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get articles
        if source:
            articles = storage_service.get_articles_by_source(source, 1000)
            # Filter by date range
            articles = [a for a in articles if start_date <= a.publication_date <= end_date]
        else:
            articles = storage_service.get_articles_by_date_range(start_date, end_date, 1000)
        
        # Filter only analyzed articles
        analyzed_articles = [a for a in articles if a.bias_scores]
        
        if not analyzed_articles:
            return jsonify({
                'message': 'No analyzed articles found for the specified criteria',
                'distribution': {}
            })
        
        # Calculate bias score distributions
        sentiment_scores = [a.bias_scores.sentiment_score for a in analyzed_articles]
        political_scores = [a.bias_scores.political_bias_score for a in analyzed_articles]
        emotional_scores = [a.bias_scores.emotional_language_score for a in analyzed_articles]
        factual_scores = [a.bias_scores.factual_vs_opinion_score for a in analyzed_articles]
        overall_scores = [a.bias_scores.overall_bias_score for a in analyzed_articles]
        
        # Create distribution buckets
        def create_distribution(scores, buckets=10):
            min_score = min(scores)
            max_score = max(scores)
            bucket_size = (max_score - min_score) / buckets
            
            distribution = {}
            for i in range(buckets):
                bucket_start = min_score + (i * bucket_size)
                bucket_end = bucket_start + bucket_size
                bucket_key = f"{bucket_start:.2f}-{bucket_end:.2f}"
                
                count = sum(1 for score in scores if bucket_start <= score < bucket_end)
                # Handle the last bucket to include the maximum value
                if i == buckets - 1:
                    count = sum(1 for score in scores if bucket_start <= score <= bucket_end)
                
                distribution[bucket_key] = count
            
            return distribution
        
        return jsonify({
            'distribution': {
                'sentiment': create_distribution(sentiment_scores),
                'political_bias': create_distribution(political_scores),
                'emotional_language': create_distribution(emotional_scores),
                'factual_content': create_distribution(factual_scores),
                'overall_bias': create_distribution(overall_scores)
            },
            'summary_statistics': {
                'sentiment': {
                    'mean': sum(sentiment_scores) / len(sentiment_scores),
                    'min': min(sentiment_scores),
                    'max': max(sentiment_scores)
                },
                'political_bias': {
                    'mean': sum(political_scores) / len(political_scores),
                    'min': min(political_scores),
                    'max': max(political_scores)
                },
                'emotional_language': {
                    'mean': sum(emotional_scores) / len(emotional_scores),
                    'min': min(emotional_scores),
                    'max': max(emotional_scores)
                },
                'factual_content': {
                    'mean': sum(factual_scores) / len(factual_scores),
                    'min': min(factual_scores),
                    'max': max(factual_scores)
                },
                'overall_bias': {
                    'mean': sum(overall_scores) / len(overall_scores),
                    'min': min(overall_scores),
                    'max': max(overall_scores)
                }
            },
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'source_filter': source,
            'total_analyzed_articles': len(analyzed_articles)
        })
        
    except Exception as e:
        logger.error(f"Failed to get bias distribution: {e}")
        return jsonify({'error': 'Failed to retrieve bias distribution'}), 500