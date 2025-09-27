from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
import hashlib
import secrets


@dataclass
class User:
    """Data model for users"""
    username: str
    email: str
    password_hash: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    id: Optional[str] = None
    hidden_articles: Optional[List[str]] = None  # List of article IDs hidden by this user
    preferences: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize default values"""
        if self.hidden_articles is None:
            self.hidden_articles = []
        if self.preferences is None:
            self.preferences = {
                'theme': 'light',
                'articles_per_page': 20,
                'default_time_range': 7  # days
            }

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_value = password_hash.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value
        except ValueError:
            return False

    def hide_article(self, article_id: str):
        """Hide an article for this user"""
        if article_id not in self.hidden_articles:
            self.hidden_articles.append(article_id)

    def unhide_article(self, article_id: str):
        """Unhide an article for this user"""
        if article_id in self.hidden_articles:
            self.hidden_articles.remove(article_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        data = asdict(self)
        if self.id:
            data['_id'] = ObjectId(self.id)
        return data

    def to_public_dict(self) -> Dict[str, Any]:
        """Convert to dictionary without sensitive information"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'preferences': self.preferences
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User from MongoDB document"""
        if '_id' in data:
            data['id'] = str(data.pop('_id'))
        return cls(**data)


@dataclass
class UserSession:
    """Data model for user sessions"""
    user_id: str
    session_token: str
    created_at: datetime
    expires_at: datetime
    is_active: bool = True
    id: Optional[str] = None

    @staticmethod
    def generate_session_token() -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)

    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.now() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        data = asdict(self)
        if self.id:
            data['_id'] = ObjectId(self.id)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSession':
        """Create UserSession from MongoDB document"""
        if '_id' in data:
            data['id'] = str(data.pop('_id'))
        return cls(**data)