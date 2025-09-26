from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import logging
from services.article_storage_service import ArticleStorageService
from services.article_comparator import ArticleComparator

logger = logging.getLogger(__name__)

# Create blueprint
statistics_bp = Blueprint('statistics', __name__, url_prefix='/api/statistics')

# Initialize services
storage_service = ArticleStorageService()
article_comparator = ArticleComparator()


@statistics_bp.route('/overview', methods=['GET'])
def get_overview_statistics():
    """Get overview statistics for the dashboard"""
    try:
        # Get storage statistics
        storage_stats = storage_service.get_storage_statistics()
        
        # Get article counts by source
        source_counts = storage_service.get_article_count_by_source()
        
        return jsonify({
            'total_articles': storage_stats.get('total_articles', 0),
            'analyzed_articles': storage_stats.get('analyzed_articles', 0),
            'unanalyzed_articles': storage_stats.get('unanalyzed_articles', 0),
            'recent_articles': storage_stats.get('recent_articles', 0),
            'language_distribution': storage_stats.get('language_distribution', {}),
            'source_distribution': source_counts,
            'analysis_coverage': {
                'percentage': (storage_stats.get('analyzed_articles', 0) / 
                             max(storage_stats.get('total_articles', 1), 1)) * 100
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get overview statistics: {e}")
        return jsonify({'error': 'Failed to retrieve overview statistics'}), 500


@statistics_bp.route('/sources', methods=['GET'])
def get_source_statistics():
    """Get detailed statistics by news source"""
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
        
        # Calculate statistics for each source
        source_stats = {}
        for source, source_articles in articles_by_source.items():
            analyzed_articles = [a for a in source_articles if a.bias_scores]
            
            if analyzed_articles:
                # Calculate average bias scores
                avg_sentiment = sum(a.bias_scores.sentiment_score for a in analyzed_articles) / len(analyzed_articles)
                avg_political = sum(a.bias_scores.political_bias_score for a in analyzed_articles) / len(analyzed_articles)
                avg_emotional = sum(a.bias_scores.emotional_language_score for a in analyzed_articles) / len(analyzed_articles)
                avg_factual = sum(a.bias_scores.factual_vs_opinion_score for a in analyzed_articles) / len(analyzed_articles)
                avg_overall = sum(a.bias_scores.overall_bias_score for a in analyzed_articles) / len(analyzed_articles)
            else:
                avg_sentiment = avg_political = avg_emotional = avg_factual = avg_overall = 0.0
            
            source_stats[source] = {
                'total_articles': len(source_articles),
                'analyzed_articles': len(analyzed_articles),
                'analysis_percentage': (len(analyzed_articles) / len(source_articles)) * 100 if source_articles else 0,
                'average_bias_scores': {
                    'sentiment': avg_sentiment,
                    'political_bias': avg_political,
                    'emotional_language': avg_emotional,
                    'factual_content': avg_factual,
                    'overall_bias': avg_overall
                },
                'language_distribution': self._get_language_distribution(source_articles)
            }
        
        return jsonify({
            'source_statistics': source_stats,
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'total_articles_in_period': len(articles)
        })
        
    except Exception as e:
        logger.error(f"Failed to get source statistics: {e}")
        return jsonify({'error': 'Failed to retrieve source statistics'}), 500


@statistics_bp.route('/bias-trends', methods=['GET'])
def get_bias_trends():
    """Get bias trends over time"""
    try:
        # Get time range from query parameters
        days = int(request.args.get('days', 30))
        source = request.args.get('source')  # Optional source filter
        
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
        
        # Group articles by day
        daily_trends = {}
        for article in analyzed_articles:
            day_key = article.publication_date.strftime('%Y-%m-%d')
            
            if day_key not in daily_trends:
                daily_trends[day_key] = {
                    'date': day_key,
                    'article_count': 0,
                    'sentiment_scores': [],
                    'political_bias_scores': [],
                    'emotional_language_scores': [],
                    'overall_bias_scores': []
                }
            
            daily_trends[day_key]['article_count'] += 1
            daily_trends[day_key]['sentiment_scores'].append(article.bias_scores.sentiment_score)
            daily_trends[day_key]['political_bias_scores'].append(article.bias_scores.political_bias_score)
            daily_trends[day_key]['emotional_language_scores'].append(article.bias_scores.emotional_language_score)
            daily_trends[day_key]['overall_bias_scores'].append(article.bias_scores.overall_bias_score)
        
        # Calculate daily averages
        trend_data = []
        for day_key in sorted(daily_trends.keys()):
            day_data = daily_trends[day_key]
            
            trend_data.append({
                'date': day_key,
                'article_count': day_data['article_count'],
                'average_sentiment': sum(day_data['sentiment_scores']) / len(day_data['sentiment_scores']),
                'average_political_bias': sum(day_data['political_bias_scores']) / len(day_data['political_bias_scores']),
                'average_emotional_language': sum(day_data['emotional_language_scores']) / len(day_data['emotional_language_scores']),
                'average_overall_bias': sum(day_data['overall_bias_scores']) / len(day_data['overall_bias_scores'])
            })
        
        return jsonify({
            'trend_data': trend_data,
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'source_filter': source,
            'total_analyzed_articles': len(analyzed_articles)
        })
        
    except Exception as e:
        logger.error(f"Failed to get bias trends: {e}")
        return jsonify({'error': 'Failed to retrieve bias trends'}), 500


@statistics_bp.route('/comparison-summary', methods=['GET'])
def get_comparison_summary():
    """Get summary of bias comparisons across sources"""
    try:
        # Get time range from query parameters
        days = int(request.args.get('days', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get articles
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
        
        # Calculate summary statistics
        summary_stats = {
            'most_biased_source': None,
            'least_biased_source': None,
            'most_positive_sentiment': None,
            'most_negative_sentiment': None,
            'most_factual_content': None,
            'most_opinion_content': None
        }
        
        if source_comparison:
            # Find extremes
            sources_by_bias = [(source, data['average_overall_bias']) 
                             for source, data in source_comparison.items()]
            sources_by_bias.sort(key=lambda x: x[1])
            
            if sources_by_bias:
                summary_stats['least_biased_source'] = sources_by_bias[0][0]
                summary_stats['most_biased_source'] = sources_by_bias[-1][0]
            
            # Find sentiment extremes
            sources_by_sentiment = [(source, data['average_sentiment']) 
                                  for source, data in source_comparison.items()]
            sources_by_sentiment.sort(key=lambda x: x[1])
            
            if sources_by_sentiment:
                summary_stats['most_negative_sentiment'] = sources_by_sentiment[0][0]
                summary_stats['most_positive_sentiment'] = sources_by_sentiment[-1][0]
            
            # Find factual content extremes
            sources_by_factual = [(source, data['average_factual_content']) 
                                for source, data in source_comparison.items()]
            sources_by_factual.sort(key=lambda x: x[1])
            
            if sources_by_factual:
                summary_stats['most_opinion_content'] = sources_by_factual[0][0]
                summary_stats['most_factual_content'] = sources_by_factual[-1][0]
        
        return jsonify({
            'source_comparison': source_comparison,
            'summary_statistics': summary_stats,
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get comparison summary: {e}")
        return jsonify({'error': 'Failed to retrieve comparison summary'}), 500


def _get_language_distribution(articles):
    """Helper function to get language distribution for a list of articles"""
    language_counts = {}
    for article in articles:
        lang = article.language
        language_counts[lang] = language_counts.get(lang, 0) + 1
    return language_counts