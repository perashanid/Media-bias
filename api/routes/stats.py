from flask import Blueprint, jsonify
import logging
from config.database import get_database
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Create blueprint
stats_bp = Blueprint('stats', __name__, url_prefix='/api/stats')


@stats_bp.route('/overview', methods=['GET'])
def get_overview_stats():
    """Get overview statistics for the home page"""
    try:
        db = get_database()
        
        # Get total articles count
        total_articles = db.articles.count_documents({})
        
        # Get articles from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_articles = db.articles.count_documents({
            'scraped_at': {'$gte': thirty_days_ago}
        })
        
        # Get total users count
        total_users = db.users.count_documents({})
        
        # Get articles with bias analysis
        analyzed_articles = db.articles.count_documents({
            'bias_scores': {'$exists': True, '$ne': None}
        })
        
        # Get unique sources count
        sources_pipeline = [
            {'$group': {'_id': '$source'}},
            {'$count': 'total_sources'}
        ]
        sources_result = list(db.articles.aggregate(sources_pipeline))
        total_sources = sources_result[0]['total_sources'] if sources_result else 0
        
        # Get articles by language
        language_pipeline = [
            {'$group': {'_id': '$language', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        language_stats = list(db.articles.aggregate(language_pipeline))
        
        # Get bias distribution
        bias_pipeline = [
            {'$match': {'bias_scores.overall_bias_score': {'$exists': True}}},
            {'$group': {
                '_id': {
                    '$cond': [
                        {'$lt': ['$bias_scores.overall_bias_score', 0.4]},
                        'Low Bias',
                        {'$cond': [
                            {'$lt': ['$bias_scores.overall_bias_score', 0.7]},
                            'Moderate Bias',
                            'High Bias'
                        ]}
                    ]
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        bias_distribution = list(db.articles.aggregate(bias_pipeline))
        
        # Get top sources by article count
        sources_pipeline = [
            {'$group': {'_id': '$source', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        top_sources = list(db.articles.aggregate(sources_pipeline))
        
        return jsonify({
            'success': True,
            'stats': {
                'total_articles': total_articles,
                'recent_articles': recent_articles,
                'total_users': total_users,
                'analyzed_articles': analyzed_articles,
                'total_sources': total_sources,
                'language_stats': language_stats,
                'bias_distribution': bias_distribution,
                'top_sources': top_sources,
                'analysis_coverage': round((analyzed_articles / total_articles * 100) if total_articles > 0 else 0, 1)
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get overview stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve statistics'
        }), 500


@stats_bp.route('/recent', methods=['GET'])
def get_recent_stats():
    """Get recent activity statistics"""
    try:
        db = get_database()
        
        # Get articles from last 7 days by day
        seven_days_ago = datetime.now() - timedelta(days=7)
        daily_pipeline = [
            {'$match': {'scraped_at': {'$gte': seven_days_ago}}},
            {'$group': {
                '_id': {
                    'year': {'$year': '$scraped_at'},
                    'month': {'$month': '$scraped_at'},
                    'day': {'$dayOfMonth': '$scraped_at'}
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        daily_stats = list(db.articles.aggregate(daily_pipeline))
        
        # Get recent articles by source
        recent_by_source_pipeline = [
            {'$match': {'scraped_at': {'$gte': seven_days_ago}}},
            {'$group': {'_id': '$source', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        recent_by_source = list(db.articles.aggregate(recent_by_source_pipeline))
        
        return jsonify({
            'success': True,
            'recent_stats': {
                'daily_articles': daily_stats,
                'sources_activity': recent_by_source
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get recent stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve recent statistics'
        }), 500