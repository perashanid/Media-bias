from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from models.article import Article
from config.database import get_articles_collection, get_database
from services.topic_extractor import TopicExtractor

logger = logging.getLogger(__name__)


class ArticleStorageService:
    """Service for storing and managing articles in MongoDB with deduplication"""
    
    def __init__(self):
        self._articles_collection = None
        self._database = None
        self.topic_extractor = TopicExtractor()
    
    @property
    def articles_collection(self):
        """Lazy initialization of articles collection"""
        if self._articles_collection is None:
            self._articles_collection = get_articles_collection()
        return self._articles_collection
    
    @property
    def database(self):
        """Lazy initialization of database"""
        if self._database is None:
            self._database = get_database()
        return self._database
        
    def store_article(self, article: Article) -> Optional[str]:
        """Store a single article with duplicate checking"""
        try:
            # Extract topics if not already present
            if not article.topics:
                article.topics = self.topic_extractor.extract_topics(
                    article.title, 
                    article.content, 
                    article.language
                )
            
            # Convert article to dictionary for MongoDB storage
            article_dict = article.to_dict()
            
            # Check for existing article by URL first
            existing_by_url = self.articles_collection.find_one({'url': article.url})
            if existing_by_url:
                logger.debug(f"Article already exists with URL: {article.url}")
                return str(existing_by_url['_id'])
            
            # Check for existing article by content hash
            existing_by_hash = self.articles_collection.find_one({'content_hash': article.content_hash})
            if existing_by_hash:
                logger.debug(f"Article already exists with content hash: {article.content_hash}")
                return str(existing_by_hash['_id'])
            
            # Insert new article
            result = self.articles_collection.insert_one(article_dict)
            logger.info(f"Successfully stored new article: {article.title[:50]}...")
            return str(result.inserted_id)
            
        except DuplicateKeyError as e:
            logger.warning(f"Duplicate article detected: {e}")
            # Try to find and return existing article ID
            existing = self.articles_collection.find_one({
                '$or': [
                    {'url': article.url},
                    {'content_hash': article.content_hash}
                ]
            })
            return str(existing['_id']) if existing else None
            
        except Exception as e:
            logger.error(f"Failed to store article: {e}")
            return None
    
    def store_articles_batch(self, articles: List[Article]) -> Dict[str, Any]:
        """Store multiple articles in batch with deduplication"""
        results = {
            'stored': 0,
            'duplicates': 0,
            'errors': 0,
            'stored_ids': [],
            'duplicate_ids': []
        }
        
        for article in articles:
            article_id = self.store_article(article)
            if article_id:
                # Check if this was a new insertion or existing article
                if self._is_recently_inserted(article_id):
                    results['stored'] += 1
                    results['stored_ids'].append(article_id)
                else:
                    results['duplicates'] += 1
                    results['duplicate_ids'].append(article_id)
            else:
                results['errors'] += 1
        
        logger.info(f"Batch storage complete: {results['stored']} stored, {results['duplicates']} duplicates, {results['errors']} errors")
        return results
    
    def _is_recently_inserted(self, article_id: str) -> bool:
        """Check if article was recently inserted (within last minute)"""
        try:
            article = self.articles_collection.find_one({'_id': ObjectId(article_id)})
            if article and 'scraped_at' in article:
                time_diff = datetime.now() - article['scraped_at']
                return time_diff.total_seconds() < 60  # Consider recent if inserted within last minute
            return False
        except Exception:
            return False
    
    def get_article_by_id(self, article_id: str) -> Optional[Article]:
        """Retrieve article by ID"""
        try:
            article_dict = self.articles_collection.find_one({'_id': ObjectId(article_id)})
            if article_dict:
                return Article.from_dict(article_dict)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve article {article_id}: {e}")
            return None
    
    def get_articles_by_source(self, source: str, limit: int = 100, skip: int = 0) -> List[Article]:
        """Retrieve articles by source with pagination"""
        try:
            cursor = self.articles_collection.find({'source': source}).skip(skip).limit(limit).sort('publication_date', -1)
            articles = []
            for article_dict in cursor:
                articles.append(Article.from_dict(article_dict))
            return articles
        except Exception as e:
            logger.error(f"Failed to retrieve articles by source {source}: {e}")
            return []
    
    def get_articles_by_date_range(self, start_date: datetime, end_date: datetime, limit: int = 100) -> List[Article]:
        """Retrieve articles within date range"""
        try:
            cursor = self.articles_collection.find({
                'publication_date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }).limit(limit).sort('publication_date', -1)
            
            articles = []
            for article_dict in cursor:
                articles.append(Article.from_dict(article_dict))
            return articles
        except Exception as e:
            logger.error(f"Failed to retrieve articles by date range: {e}")
            return []
    
    def search_articles(self, query: str, limit: int = 50) -> List[Article]:
        """Search articles by text content using regex since text index is disabled"""
        try:
            # Use regex search instead of text index
            cursor = self.articles_collection.find({
                '$or': [
                    {'title': {'$regex': query, '$options': 'i'}},
                    {'content': {'$regex': query, '$options': 'i'}}
                ]
            }).limit(limit).sort('publication_date', -1)
            
            articles = []
            for article_dict in cursor:
                articles.append(Article.from_dict(article_dict))
            return articles
        except Exception as e:
            logger.error(f"Failed to search articles: {e}")
            return []
    
    def get_article_count_by_source(self) -> Dict[str, int]:
        """Get count of articles by source"""
        try:
            pipeline = [
                {'$group': {'_id': '$source', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}
            ]
            
            result = {}
            for doc in self.articles_collection.aggregate(pipeline):
                result[doc['_id']] = doc['count']
            
            return result
        except Exception as e:
            logger.error(f"Failed to get article count by source: {e}")
            return {}
    
    def update_article_bias_scores(self, article_id: str, bias_scores: Dict[str, Any]) -> bool:
        """Update bias scores for an article"""
        try:
            result = self.articles_collection.update_one(
                {'_id': ObjectId(article_id)},
                {'$set': {'bias_scores': bias_scores}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update bias scores for article {article_id}: {e}")
            return False
    
    def get_articles_without_bias_analysis(self, limit: int = 100) -> List[Article]:
        """Get articles that haven't been analyzed for bias yet"""
        try:
            cursor = self.articles_collection.find({
                '$or': [
                    {'bias_scores': {'$exists': False}},
                    {'bias_scores': None}
                ]
            }).limit(limit).sort('scraped_at', 1)  # Oldest first
            
            articles = []
            for article_dict in cursor:
                articles.append(Article.from_dict(article_dict))
            return articles
        except Exception as e:
            logger.error(f"Failed to retrieve articles without bias analysis: {e}")
            return []
    
    def cleanup_old_articles(self, retention_days: int = 365) -> int:
        """Remove articles older than retention period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            result = self.articles_collection.delete_many({
                'scraped_at': {'$lt': cutoff_date}
            })
            
            deleted_count = result.deleted_count
            logger.info(f"Cleaned up {deleted_count} articles older than {retention_days} days")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old articles: {e}")
            return 0
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            total_articles = self.articles_collection.count_documents({})
            
            # Articles by language
            language_pipeline = [
                {'$group': {'_id': '$language', 'count': {'$sum': 1}}}
            ]
            language_stats = {}
            for doc in self.articles_collection.aggregate(language_pipeline):
                language_stats[doc['_id']] = doc['count']
            
            # Articles with bias analysis
            analyzed_count = self.articles_collection.count_documents({
                'bias_scores': {'$exists': True, '$ne': None}
            })
            
            # Recent articles (last 7 days)
            recent_cutoff = datetime.now() - timedelta(days=7)
            recent_count = self.articles_collection.count_documents({
                'scraped_at': {'$gte': recent_cutoff}
            })
            
            return {
                'total_articles': total_articles,
                'analyzed_articles': analyzed_count,
                'unanalyzed_articles': total_articles - analyzed_count,
                'recent_articles': recent_count,
                'language_distribution': language_stats,
                'source_distribution': self.get_article_count_by_source()
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage statistics: {e}")
            return {}
    
    def get_available_topics(self) -> List[str]:
        """Get list of all available topics from stored articles"""
        try:
            # Get topics from topic extractor
            predefined_topics = self.topic_extractor.get_available_topics()
            
            # Get topics from database
            pipeline = [
                {'$match': {'topics': {'$exists': True, '$ne': None, '$ne': []}}},
                {'$unwind': '$topics'},
                {'$group': {'_id': '$topics'}},
                {'$sort': {'_id': 1}}
            ]
            
            db_topics = [doc['_id'] for doc in self.articles_collection.aggregate(pipeline)]
            
            # Combine and deduplicate
            all_topics = list(set(predefined_topics + db_topics))
            all_topics.sort()
            
            return all_topics
            
        except Exception as e:
            logger.error(f"Failed to get available topics: {e}")
            return self.topic_extractor.get_available_topics()
    
    def get_articles_by_topic(self, topic: str, limit: int = 50, skip: int = 0) -> List[Article]:
        """Get articles filtered by topic"""
        try:
            cursor = self.articles_collection.find(
                {'topics': topic}
            ).sort('publication_date', -1).skip(skip).limit(limit)
            
            articles = []
            for doc in cursor:
                try:
                    article = Article.from_dict(doc)
                    articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to convert document to Article: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Failed to get articles by topic {topic}: {e}")
            return []
    
    def get_articles_count_by_topic(self, topic: str) -> int:
        """Get count of articles filtered by topic"""
        try:
            return self.articles_collection.count_documents({'topics': topic})
        except Exception as e:
            logger.error(f"Failed to get articles count by topic {topic}: {e}")
            return 0
    
    def get_articles_count_by_source(self, source: str) -> int:
        """Get count of articles filtered by source"""
        try:
            return self.articles_collection.count_documents({'source': source})
        except Exception as e:
            logger.error(f"Failed to get articles count by source {source}: {e}")
            return 0
    
    def get_articles_count_by_date_range(self, start_date: datetime, end_date: datetime) -> int:
        """Get count of articles in date range"""
        try:
            return self.articles_collection.count_documents({
                'publication_date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            })
        except Exception as e:
            logger.error(f"Failed to get articles count by date range: {e}")
            return 0