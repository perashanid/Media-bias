from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
import hashlib


@dataclass
class BiasScore:
    """Data model for bias analysis scores"""
    sentiment_score: float  # -1 (negative) to 1 (positive)
    political_bias_score: float  # -1 (left) to 1 (right)
    emotional_language_score: float  # 0 (neutral) to 1 (highly emotional)
    factual_vs_opinion_score: float  # 0 (opinion) to 1 (factual)
    overall_bias_score: float  # 0 (unbiased) to 1 (highly biased)
    analyzed_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BiasScore':
        """Create BiasScore from dictionary"""
        return cls(**data)


@dataclass
class Article:
    """Data model for news articles"""
    url: str
    title: str
    content: str
    author: Optional[str]
    publication_date: datetime
    source: str
    scraped_at: datetime
    language: str
    id: Optional[str] = None
    content_hash: Optional[str] = None
    bias_scores: Optional[BiasScore] = None
    topics: Optional[list] = None

    def __post_init__(self):
        """Generate content hash after initialization"""
        if self.content_hash is None:
            self.content_hash = self._generate_content_hash()

    def _generate_content_hash(self) -> str:
        """Generate SHA-256 hash of article content for duplicate detection"""
        content_for_hash = f"{self.title}{self.content}{self.source}"
        return hashlib.sha256(content_for_hash.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        data = asdict(self)
        if self.bias_scores:
            data['bias_scores'] = self.bias_scores.to_dict()
        if self.id:
            data['_id'] = ObjectId(self.id)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """Create Article from MongoDB document"""
        # Handle ObjectId conversion
        if '_id' in data:
            data['id'] = str(data.pop('_id'))
        
        # Handle bias_scores conversion
        if 'bias_scores' in data and data['bias_scores']:
            data['bias_scores'] = BiasScore.from_dict(data['bias_scores'])
        
        return cls(**data)


@dataclass
class ComparisonReport:
    """Data model for article comparison reports"""
    story_id: str
    articles: list  # List of Article objects
    bias_differences: Dict[str, float]  # source -> percentage difference
    key_differences: list  # List of key differences
    similarity_scores: Dict[str, float]  # source pairs -> similarity score
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        return {
            'story_id': self.story_id,
            'articles': [article.to_dict() for article in self.articles],
            'bias_differences': self.bias_differences,
            'key_differences': self.key_differences,
            'similarity_scores': self.similarity_scores,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComparisonReport':
        """Create ComparisonReport from MongoDB document"""
        data['articles'] = [Article.from_dict(article_data) for article_data in data['articles']]
        return cls(**data)