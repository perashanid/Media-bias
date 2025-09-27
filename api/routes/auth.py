from flask import Blueprint, request, jsonify, session
from datetime import datetime
import logging
from functools import wraps

from services.user_service import UserService

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
user_service = UserService()


def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        token = auth_header.split(' ')[1]
        user_session = user_service.get_session(token)
        
        if not user_session:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # Add user info to request context
        request.current_user_id = user_session.user_id
        request.current_session = user_session
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
    """Get current user from request context"""
    if hasattr(request, 'current_user_id'):
        return user_service.get_user_by_id(request.current_user_id)
    return None


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email is required'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Create user
        user = user_service.create_user(username, email, password)
        
        if not user:
            return jsonify({'error': 'Username or email already exists'}), 409
        
        # Create session
        user_session = user_service.create_session(user.id)
        
        if not user_session:
            return jsonify({'error': 'Failed to create session'}), 500
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_public_dict(),
            'session_token': user_session.session_token,
            'expires_at': user_session.expires_at.isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Authenticate user
        user = user_service.authenticate_user(username, password)
        
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Create session
        user_session = user_service.create_session(user.id)
        
        if not user_session:
            return jsonify({'error': 'Failed to create session'}), 500
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_public_dict(),
            'session_token': user_session.session_token,
            'expires_at': user_session.expires_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return jsonify({'error': 'Login failed'}), 500


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user"""
    try:
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        
        user_service.invalidate_session(token)
        
        return jsonify({'message': 'Logout successful'})
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        return jsonify({'error': 'Logout failed'}), 500


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user_info():
    """Get current user information"""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_public_dict()
        })
        
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        return jsonify({'error': 'Failed to get user information'}), 500


@auth_bp.route('/preferences', methods=['GET'])
@require_auth
def get_user_preferences():
    """Get user preferences"""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'preferences': user.preferences or {}
        })
        
    except Exception as e:
        logger.error(f"Failed to get user preferences: {e}")
        return jsonify({'error': 'Failed to get preferences'}), 500


@auth_bp.route('/preferences', methods=['PUT'])
@require_auth
def update_user_preferences():
    """Update user preferences"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        preferences = data.get('preferences', {})
        
        success = user_service.update_user_preferences(request.current_user_id, preferences)
        
        if success:
            return jsonify({'message': 'Preferences updated successfully'})
        else:
            return jsonify({'error': 'Failed to update preferences'}), 500
        
    except Exception as e:
        logger.error(f"Failed to update user preferences: {e}")
        return jsonify({'error': 'Failed to update preferences'}), 500


@auth_bp.route('/articles/<article_id>/hide', methods=['POST'])
@require_auth
def hide_article():
    """Hide an article for the current user"""
    try:
        article_id = request.view_args['article_id']
        
        success = user_service.hide_article_for_user(request.current_user_id, article_id)
        
        if success:
            return jsonify({'message': 'Article hidden successfully'})
        else:
            return jsonify({'error': 'Failed to hide article'}), 500
        
    except Exception as e:
        logger.error(f"Failed to hide article: {e}")
        return jsonify({'error': 'Failed to hide article'}), 500


@auth_bp.route('/articles/<article_id>/unhide', methods=['POST'])
@require_auth
def unhide_article():
    """Unhide an article for the current user"""
    try:
        article_id = request.view_args['article_id']
        
        success = user_service.unhide_article_for_user(request.current_user_id, article_id)
        
        if success:
            return jsonify({'message': 'Article unhidden successfully'})
        else:
            return jsonify({'error': 'Failed to unhide article'}), 500
        
    except Exception as e:
        logger.error(f"Failed to unhide article: {e}")
        return jsonify({'error': 'Failed to unhide article'}), 500


@auth_bp.route('/articles/hidden', methods=['GET'])
@require_auth
def get_hidden_articles():
    """Get list of articles hidden by current user"""
    try:
        hidden_articles = user_service.get_user_hidden_articles(request.current_user_id)
        
        return jsonify({
            'hidden_articles': hidden_articles,
            'count': len(hidden_articles)
        })
        
    except Exception as e:
        logger.error(f"Failed to get hidden articles: {e}")
        return jsonify({'error': 'Failed to get hidden articles'}), 500