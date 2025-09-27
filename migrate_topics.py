#!/usr/bin/env python3
"""
Migration script to add topics to existing articles
"""

import logging
from config.database import get_database
from services.topic_extractor import TopicExtractor
from models.article import Article

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_topics():
    """Add topics to existing articles that don't have them"""
    try:
        db = get_database()
        articles_collection = db.articles
        topic_extractor = TopicExtractor()
        
        # Find articles without topics
        articles_without_topics = articles_collection.find({
            '$or': [
                {'topics': {'$exists': False}},
                {'topics': None},
                {'topics': []}
            ]
        })
        
        count = articles_collection.count_documents({
            '$or': [
                {'topics': {'$exists': False}},
                {'topics': None},
                {'topics': []}
            ]
        })
        
        logger.info(f"Found {count} articles without topics")
        
        updated_count = 0
        for article_doc in articles_without_topics:
            try:
                # Extract topics
                topics = topic_extractor.extract_topics(
                    article_doc.get('title', ''),
                    article_doc.get('content', ''),
                    article_doc.get('language', 'bengali')
                )
                
                # Update article with topics
                articles_collection.update_one(
                    {'_id': article_doc['_id']},
                    {'$set': {'topics': topics}}
                )
                
                updated_count += 1
                if updated_count % 10 == 0:
                    logger.info(f"Updated {updated_count}/{count} articles")
                    
            except Exception as e:
                logger.error(f"Failed to update article {article_doc.get('_id')}: {e}")
                continue
        
        logger.info(f"Migration complete: Updated {updated_count} articles with topics")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate_topics()