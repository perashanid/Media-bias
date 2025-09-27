from datetime import datetime, timedelta
from typing import Optional, List
import logging
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from models.user import User, UserSession
from config.database import get_database

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management and authentication"""
    
    def __init__(self):
        self.db = get_database()
        self.users_collection = self.db.users
        self.sessions_collection = self.db.user_sessions
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for users and sessions"""
        try:
            # User indexes
            self.users_collection.create_index("username", unique=True)
            self.users_collection.create_index("email", unique=True)
            
            # Session indexes
            self.sessions_collection.create_index("session_token", unique=True)
            self.sessions_collection.create_index("user_id")
            self.sessions_collection.create_index("expires_at")
            
            logger.info("User service indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create user service indexes: {e}")
    
    def create_user(self, username: str, email: str, password: str) -> Optional[User]:
        """Create a new user"""
        try:
            # Check if user already exists
            if self.get_user_by_username(username):
                logger.warning(f"User with username {username} already exists")
                return None
            
            if self.get_user_by_email(email):
                logger.warning(f"User with email {email} already exists")
                return None
            
            # Create user
            user = User(
                username=username,
                email=email,
                password_hash=User.hash_password(password),
                created_at=datetime.now()
            )
            
            # Insert into database
            result = self.users_collection.insert_one(user.to_dict())
            user.id = str(result.inserted_id)
            
            logger.info(f"Created user: {username}")
            return user
            
        except DuplicateKeyError:
            logger.warning(f"Duplicate key error when creating user {username}")
            return None
        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            user_data = self.users_collection.find_one({"username": username})
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get user by username {username}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            user_data = self.users_collection.find_one({"email": email})
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            from bson import ObjectId
            user_data = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        try:
            user = self.get_user_by_username(username)
            if user and User.verify_password(password, user.password_hash):
                # Update last login
                self.update_last_login(user.id)
                return user
            return None
        except Exception as e:
            logger.error(f"Failed to authenticate user {username}: {e}")
            return None
    
    def update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        try:
            from bson import ObjectId
            self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"last_login": datetime.now()}}
            )
        except Exception as e:
            logger.error(f"Failed to update last login for user {user_id}: {e}")
    
    def create_session(self, user_id: str, duration_hours: int = 24) -> Optional[UserSession]:
        """Create a new user session"""
        try:
            session = UserSession(
                user_id=user_id,
                session_token=UserSession.generate_session_token(),
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=duration_hours)
            )
            
            result = self.sessions_collection.insert_one(session.to_dict())
            session.id = str(result.inserted_id)
            
            logger.info(f"Created session for user {user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session for user {user_id}: {e}")
            return None
    
    def get_session(self, session_token: str) -> Optional[UserSession]:
        """Get session by token"""
        try:
            session_data = self.sessions_collection.find_one({"session_token": session_token})
            if session_data:
                session = UserSession.from_dict(session_data)
                if not session.is_expired() and session.is_active:
                    return session
                else:
                    # Clean up expired session
                    self.invalidate_session(session_token)
            return None
        except Exception as e:
            logger.error(f"Failed to get session {session_token}: {e}")
            return None
    
    def invalidate_session(self, session_token: str):
        """Invalidate a session"""
        try:
            self.sessions_collection.update_one(
                {"session_token": session_token},
                {"$set": {"is_active": False}}
            )
            logger.info(f"Invalidated session {session_token}")
        except Exception as e:
            logger.error(f"Failed to invalidate session {session_token}: {e}")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            result = self.sessions_collection.delete_many({
                "expires_at": {"$lt": datetime.now()}
            })
            logger.info(f"Cleaned up {result.deleted_count} expired sessions")
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
    
    def hide_article_for_user(self, user_id: str, article_id: str) -> bool:
        """Hide an article for a specific user"""
        try:
            from bson import ObjectId
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$addToSet": {"hidden_articles": article_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to hide article {article_id} for user {user_id}: {e}")
            return False
    
    def unhide_article_for_user(self, user_id: str, article_id: str) -> bool:
        """Unhide an article for a specific user"""
        try:
            from bson import ObjectId
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$pull": {"hidden_articles": article_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to unhide article {article_id} for user {user_id}: {e}")
            return False
    
    def get_user_hidden_articles(self, user_id: str) -> List[str]:
        """Get list of articles hidden by user"""
        try:
            user = self.get_user_by_id(user_id)
            if user and user.hidden_articles:
                return user.hidden_articles
            return []
        except Exception as e:
            logger.error(f"Failed to get hidden articles for user {user_id}: {e}")
            return []
    
    def update_user_preferences(self, user_id: str, preferences: dict) -> bool:
        """Update user preferences"""
        try:
            from bson import ObjectId
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"preferences": preferences}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update preferences for user {user_id}: {e}")
            return False