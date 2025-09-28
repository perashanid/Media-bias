#!/usr/bin/env python3

import logging
from services.article_storage_service import ArticleStorageService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_category_pages():
    """Remove category pages from the database"""
    print("=== CLEANING UP CATEGORY PAGES ===")
    
    try:
        storage_service = ArticleStorageService()
        
        # Get initial count
        initial_count = storage_service.get_total_articles_count()
        print(f"Initial article count: {initial_count}")
        
        # Define category page patterns to remove
        category_patterns = [
            # Daily Star category pages
            'https://www.thedailystar.net/news/bangladesh',
            'https://www.thedailystar.net/news/world',
            'https://www.thedailystar.net/news/asia',
            'https://www.thedailystar.net/news/investigative-stories',
            'https://www.thedailystar.net/business',
            'https://www.thedailystar.net/sports',
            'https://www.thedailystar.net/lifestyle',
            'https://www.thedailystar.net/opinion',
            
            # Other potential category pages
            'https://www.prothomalo.com/bangladesh',
            'https://www.prothomalo.com/world',
            'https://www.bd-pratidin.com/country',
            'https://www.bd-pratidin.com/international-news',
        ]
        
        removed_count = 0
        
        # Remove articles with category URLs
        print("Removing category pages by URL...")
        for pattern in category_patterns:
            result = storage_service.articles_collection.delete_many({'url': pattern})
            if result.deleted_count > 0:
                print(f"  Removed {result.deleted_count} articles with URL: {pattern}")
                removed_count += result.deleted_count
        
        # Remove articles with generic "News" title and short content (likely category pages)
        print("Removing articles with generic 'News' title...")
        result = storage_service.articles_collection.delete_many({
            'title': 'News',
            '$expr': {'$lt': [{'$strLenCP': '$content'}, 5000]}  # Content less than 5000 chars
        })
        if result.deleted_count > 0:
            print(f"  Removed {result.deleted_count} articles with generic 'News' title")
            removed_count += result.deleted_count
        
        # Remove articles with URLs ending in category names (no article ID)
        print("Removing articles with category-like URLs...")
        category_endings = [
            '/bangladesh$',
            '/world$', 
            '/business$',
            '/sports$',
            '/lifestyle$',
            '/opinion$',
            '/asia$',
            '/europe$',
            '/country$',
            '/international-news$'
        ]
        
        for ending in category_endings:
            result = storage_service.articles_collection.delete_many({
                'url': {'$regex': ending}
            })
            if result.deleted_count > 0:
                print(f"  Removed {result.deleted_count} articles with URLs ending in {ending}")
                removed_count += result.deleted_count
        
        # Get final count
        final_count = storage_service.get_total_articles_count()
        print(f"\nCleanup complete:")
        print(f"  Initial count: {initial_count}")
        print(f"  Final count: {final_count}")
        print(f"  Removed: {removed_count}")
        print(f"  Net change: {final_count - initial_count}")
        
        # Show remaining articles by source
        print("\nRemaining articles by source:")
        source_counts = storage_service.get_article_count_by_source()
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count}")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    cleanup_category_pages()