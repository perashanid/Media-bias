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
        database_name = 'media_bias_detector'
        
        # Try multiple connection options automatically
        connection_options = [
            # Option 1: MongoDB Atlas with proper SSL handling
            {
                'uri': 'mongodb+srv://rokshanid_db_user:fSdGCVvK6bqLb6Ps@rokshanid.9rebh5y.mongodb.net/media_bias_detector?retryWrites=true&w=majority&appName=Cluster0',
                'name': 'MongoDB Atlas (Standard)',
                'options': {
                    'serverSelectionTimeoutMS': 10000,
                    'connectTimeoutMS': 10000,
                    'socketTimeoutMS': 10000
                }
            },
            # Option 2: MongoDB Atlas with TLS settings
            {
                'uri': 'mongodb+srv://rokshanid_db_user:fSdGCVvK6bqLb6Ps@rokshanid.9rebh5y.mongodb.net/media_bias_detector?retryWrites=true&w=majority&appName=Cluster0',
                'name': 'MongoDB Atlas (TLS)',
                'options': {
                    'serverSelectionTimeoutMS': 8000,
                    'connectTimeoutMS': 8000,
                    'socketTimeoutMS': 8000,
                    'tls': True,
                    'tlsAllowInvalidCertificates': True
                }
            },
            # Option 3: Local MongoDB
            {
                'uri': 'mongodb://localhost:27017/',
                'name': 'Local MongoDB',
                'options': {
                    'serverSelectionTimeoutMS': 3000,
                    'connectTimeoutMS': 3000,
                    'socketTimeoutMS': 3000
                }
            }
        ]
        
        for option in connection_options:
            try:
                logger.info(f"Attempting connection to {option['name']}...")
                
                self.client = MongoClient(option['uri'], **option['options'])
                self.database = self.client[database_name]
                
                # Test connection
                self.client.admin.command('ping')
                logger.info(f"✅ Successfully connected to {option['name']}")
                
                # Initialize database indexes
                self._create_indexes()
                
                return self.database
                
            except Exception as e:
                logger.warning(f"❌ {option['name']} failed: {str(e)[:100]}...")
                continue
        
        # If all options fail, raise error
        logger.error("❌ All database connection attempts failed!")
        logger.error("Please ensure:")
        logger.error("1. MongoDB Atlas cluster is running and accessible")
        logger.error("2. IP address is whitelisted in Atlas")
        logger.error("3. Database credentials are correct")
        logger.error("4. Or install MongoDB locally")
        raise RuntimeError("No database connection available")

    

    
    def _create_indexes(self):
        """Create necessary database indexes for optimal performance"""
        try:
            articles_collection = self.database.articles
            
            # Create indexes for articles collection (with error handling)
            indexes_to_create = [
                ([("url", ASCENDING)], {"unique": True}),
                ([("content_hash", ASCENDING)], {"unique": True}),
                ([("source", ASCENDING)], {}),
                ([("publication_date", ASCENDING)], {}),
                ([("scraped_at", ASCENDING)], {}),
                ([("language", ASCENDING)], {}),
            ]
            
            for index_spec, options in indexes_to_create:
                try:
                    articles_collection.create_index(index_spec, **options)
                except Exception as e:
                    # Index might already exist, which is fine
                    logger.debug(f"Index creation skipped (likely already exists): {e}")
            
            # Skip text index creation to avoid language override issues
            # Text search will use basic string matching instead
            logger.info("Skipping text index creation to avoid language compatibility issues")
            
            # Create indexes for article_groups collection
            groups_collection = self.database.article_groups
            try:
                groups_collection.create_index([("story_id", ASCENDING)], unique=True)
            except Exception as e:
                logger.debug(f"Story ID index creation skipped: {e}")
            
            try:
                groups_collection.create_index([("created_at", ASCENDING)])
            except Exception as e:
                logger.debug(f"Created at index creation skipped: {e}")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database indexes: {e}")
            raise
    
    def get_collection(self, collection_name: str):
        """Get a specific collection from the database"""
        if self.database is None:
            self.connect()
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


def get_articles_collection():
    """Get the articles collection"""
    if db_connection.database is None:
        db_connection.connect()
    return db_connection.database['articles']


def get_article_groups_collection():
    """Get the article_groups collection"""
    if db_connection.database is None:
        db_connection.connect()
    return db_connection.database['article_groups']


def initialize_database():
    """Initialize database connection and create indexes"""
    try:
        db = get_database()
        logger.info("Database initialized successfully")
        return db
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise