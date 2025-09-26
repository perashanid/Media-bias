import os
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """MongoDB connection manager"""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        
    def connect(self) -> Database:
        """Establish connection to MongoDB"""
        try:
            # Get connection details from environment variables
            mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            database_name = os.getenv('DATABASE_NAME', 'media_bias_detector')
            
            # For MongoDB Atlas, append database name to URI if not present
            if 'mongodb+srv://' in mongo_uri and not mongo_uri.endswith('/'):
                mongo_uri = f"{mongo_uri}{database_name}"
            
            # Create MongoDB client with shorter timeout for testing
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
            self.database = self.client[database_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB database: {database_name}")
            
            # Initialize database indexes
            self._create_indexes()
            
            return self.database
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            logger.warning("Using mock database for testing purposes")
            return self._create_mock_database()
    
    def _create_mock_database(self):
        """Create a mock database for testing when MongoDB is not available"""
        from unittest.mock import MagicMock
        
        # Create mock database and collections
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        # Configure mock methods
        mock_collection.create_index.return_value = None
        mock_collection.insert_one.return_value = MagicMock(inserted_id="mock_id")
        mock_collection.find.return_value = []
        mock_collection.find_one.return_value = None
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
        
        mock_db.__getitem__.return_value = mock_collection
        mock_db.articles = mock_collection
        mock_db.article_groups = mock_collection
        
        self.database = mock_db
        logger.info("Mock database created for testing")
        return mock_db
    
    def _create_indexes(self):
        """Create necessary database indexes for optimal performance"""
        try:
            articles_collection = self.database.articles
            
            # Create indexes for articles collection
            articles_collection.create_index([("url", ASCENDING)], unique=True)
            articles_collection.create_index([("content_hash", ASCENDING)], unique=True)
            articles_collection.create_index([("source", ASCENDING)])
            articles_collection.create_index([("publication_date", ASCENDING)])
            articles_collection.create_index([("scraped_at", ASCENDING)])
            articles_collection.create_index([("language", ASCENDING)])
            
            # Create text index for content search
            articles_collection.create_index([("title", TEXT), ("content", TEXT)])
            
            # Create indexes for article_groups collection
            groups_collection = self.database.article_groups
            groups_collection.create_index([("story_id", ASCENDING)], unique=True)
            groups_collection.create_index([("created_at", ASCENDING)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database indexes: {e}")
            raise
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get a specific collection from the database"""
        if self.database is None:
            raise RuntimeError("Database connection not established. Call connect() first.")
        return self.database[collection_name]
    
    def close(self):
        """Close the database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")


# Global database connection instance
db_connection = DatabaseConnection()


def get_database() -> Database:
    """Get the database instance, connecting if necessary"""
    if db_connection.database is None:
        return db_connection.connect()
    return db_connection.database


def get_articles_collection() -> Collection:
    """Get the articles collection"""
    return db_connection.get_collection('articles')


def get_article_groups_collection() -> Collection:
    """Get the article_groups collection"""
    return db_connection.get_collection('article_groups')


def initialize_database():
    """Initialize database connection and create indexes"""
    try:
        db = get_database()
        logger.info("Database initialized successfully")
        return db
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise