#!/usr/bin/env python3
"""
System optimization script for Media Bias Detector
Optimizes database queries, indexes, and system performance
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_database, get_articles_collection
from services.article_storage_service import ArticleStorageService
from services.monitoring_service import MonitoringService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SystemOptimizer:
    """System optimization utilities"""
    
    def __init__(self):
        self.db = get_database()
        self.articles_collection = get_articles_collection()
        self.storage_service = ArticleStorageService()
        self.monitoring_service = MonitoringService()
    
    def optimize_database_indexes(self):
        """Optimize database indexes for better performance"""
        logger.info("🔧 Optimizing database indexes...")
        
        try:
            # Create compound indexes for common queries
            indexes_to_create = [
                # Source and date queries
                [("source", 1), ("publication_date", -1)],
                [("source", 1), ("scraped_at", -1)],
                
                # Language and date queries
                [("language", 1), ("publication_date", -1)],
                
                # Bias analysis queries
                [("bias_scores.overall_bias_score", 1)],
                [("bias_scores.sentiment_score", 1)],
                [("bias_scores.political_bias_score", 1)],
                
                # Content similarity queries
                [("content_hash", 1), ("source", 1)],
                
                # Analysis status queries
                [("bias_scores", 1), ("scraped_at", -1)],
            ]
            
            for index_spec in indexes_to_create:
                try:
                    self.articles_collection.create_index(index_spec)
                    logger.info(f"✅ Created index: {index_spec}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        logger.info(f"ℹ️  Index already exists: {index_spec}")
                    else:
                        logger.error(f"❌ Failed to create index {index_spec}: {e}")
            
            # Create text search index if not exists
            try:
                self.articles_collection.create_index([
                    ("title", "text"),
                    ("content", "text")
                ], name="article_text_search", default_language="english")
                logger.info("✅ Created text search index")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("ℹ️  Text search index already exists")
                else:
                    logger.error(f"❌ Failed to create text search index: {e}")
            
            logger.info("✅ Database index optimization completed")
            
        except Exception as e:
            logger.error(f"❌ Database index optimization failed: {e}")
    
    def cleanup_old_data(self, retention_days=365):
        """Clean up old data to improve performance"""
        logger.info(f"🧹 Cleaning up data older than {retention_days} days...")
        
        try:
            # Clean up old articles
            deleted_count = self.storage_service.cleanup_old_articles(retention_days)
            logger.info(f"✅ Cleaned up {deleted_count} old articles")
            
            # Clean up old monitoring data
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Clean up old alerts (keep last 90 days)
            alert_cutoff = datetime.now() - timedelta(days=90)
            old_alerts = [alert for alert in self.monitoring_service.alerts if alert.timestamp < alert_cutoff]
            self.monitoring_service.alerts = [alert for alert in self.monitoring_service.alerts if alert.timestamp >= alert_cutoff]
            logger.info(f"✅ Cleaned up {len(old_alerts)} old alerts")
            
            # Clean up old metrics (keep last 30 days)
            metrics_cutoff = datetime.now() - timedelta(days=30)
            old_metrics = [metric for metric in self.monitoring_service.metrics_history if metric.timestamp < metrics_cutoff]
            self.monitoring_service.metrics_history = [metric for metric in self.monitoring_service.metrics_history if metric.timestamp >= metrics_cutoff]
            logger.info(f"✅ Cleaned up {len(old_metrics)} old metrics")
            
        except Exception as e:
            logger.error(f"❌ Data cleanup failed: {e}")
    
    def optimize_database_performance(self):
        """Optimize database performance settings"""
        logger.info("⚡ Optimizing database performance...")
        
        try:
            # Get database statistics
            stats = self.db.command("dbStats")
            logger.info(f"Database size: {stats.get('dataSize', 0) / 1024 / 1024:.2f} MB")
            logger.info(f"Index size: {stats.get('indexSize', 0) / 1024 / 1024:.2f} MB")
            
            # Analyze collection statistics
            collection_stats = self.db.command("collStats", "articles")
            logger.info(f"Articles collection size: {collection_stats.get('size', 0) / 1024 / 1024:.2f} MB")
            logger.info(f"Articles count: {collection_stats.get('count', 0)}")
            
            # Check index usage
            index_stats = list(self.articles_collection.aggregate([
                {"$indexStats": {}}
            ]))
            
            logger.info("Index usage statistics:")
            for index_stat in index_stats:
                name = index_stat.get('name', 'unknown')
                accesses = index_stat.get('accesses', {}).get('ops', 0)
                logger.info(f"  - {name}: {accesses} operations")
            
            # Compact collection if needed (for development only)
            if os.getenv('FLASK_ENV') == 'development':
                try:
                    self.db.command("compact", "articles")
                    logger.info("✅ Collection compacted")
                except Exception as e:
                    logger.warning(f"⚠️  Collection compaction failed: {e}")
            
        except Exception as e:
            logger.error(f"❌ Database performance optimization failed: {e}")
    
    def validate_data_integrity(self):
        """Validate data integrity and fix issues"""
        logger.info("🔍 Validating data integrity...")
        
        try:
            # Check for duplicate URLs
            pipeline = [
                {"$group": {"_id": "$url", "count": {"$sum": 1}, "docs": {"$push": "$_id"}}},
                {"$match": {"count": {"$gt": 1}}}
            ]
            
            duplicates = list(self.articles_collection.aggregate(pipeline))
            if duplicates:
                logger.warning(f"⚠️  Found {len(duplicates)} duplicate URLs")
                
                # Remove duplicates (keep the first one)
                for duplicate in duplicates:
                    docs_to_remove = duplicate['docs'][1:]  # Keep first, remove rest
                    for doc_id in docs_to_remove:
                        self.articles_collection.delete_one({"_id": doc_id})
                    logger.info(f"✅ Removed {len(docs_to_remove)} duplicate articles for URL: {duplicate['_id']}")
            else:
                logger.info("✅ No duplicate URLs found")
            
            # Check for articles without content hash
            articles_without_hash = self.articles_collection.count_documents({"content_hash": {"$exists": False}})
            if articles_without_hash > 0:
                logger.warning(f"⚠️  Found {articles_without_hash} articles without content hash")
                
                # Update articles without content hash
                articles_to_update = self.articles_collection.find({"content_hash": {"$exists": False}})
                updated_count = 0
                
                for article in articles_to_update:
                    import hashlib
                    content_hash = hashlib.sha256(article['content'].encode()).hexdigest()
                    self.articles_collection.update_one(
                        {"_id": article["_id"]},
                        {"$set": {"content_hash": content_hash}}
                    )
                    updated_count += 1
                
                logger.info(f"✅ Updated {updated_count} articles with content hash")
            else:
                logger.info("✅ All articles have content hash")
            
            # Check for invalid bias scores
            invalid_bias_scores = self.articles_collection.count_documents({
                "bias_scores.overall_bias_score": {"$not": {"$gte": 0, "$lte": 1}}
            })
            
            if invalid_bias_scores > 0:
                logger.warning(f"⚠️  Found {invalid_bias_scores} articles with invalid bias scores")
                # Could implement bias score recalculation here
            else:
                logger.info("✅ All bias scores are valid")
            
        except Exception as e:
            logger.error(f"❌ Data integrity validation failed: {e}")
    
    def generate_performance_report(self):
        """Generate system performance report"""
        logger.info("📊 Generating performance report...")
        
        try:
            # Get storage statistics
            storage_stats = self.storage_service.get_storage_statistics()
            
            # Get database statistics
            db_stats = self.db.command("dbStats")
            
            # Calculate performance metrics
            total_articles = storage_stats.get('total_articles', 0)
            analyzed_articles = storage_stats.get('analyzed_articles', 0)
            analysis_coverage = (analyzed_articles / total_articles * 100) if total_articles > 0 else 0
            
            # Generate report
            report = f"""
=== Media Bias Detector Performance Report ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Database Statistics:
- Database size: {db_stats.get('dataSize', 0) / 1024 / 1024:.2f} MB
- Index size: {db_stats.get('indexSize', 0) / 1024 / 1024:.2f} MB
- Collections: {db_stats.get('collections', 0)}

Article Statistics:
- Total articles: {total_articles:,}
- Analyzed articles: {analyzed_articles:,}
- Analysis coverage: {analysis_coverage:.1f}%
- Recent articles (7 days): {storage_stats.get('recent_articles', 0):,}

Language Distribution:
"""
            
            for language, count in storage_stats.get('language_distribution', {}).items():
                percentage = (count / total_articles * 100) if total_articles > 0 else 0
                report += f"- {language.title()}: {count:,} ({percentage:.1f}%)\n"
            
            report += "\nSource Distribution:\n"
            for source, count in storage_stats.get('source_distribution', {}).items():
                percentage = (count / total_articles * 100) if total_articles > 0 else 0
                report += f"- {source}: {count:,} ({percentage:.1f}%)\n"
            
            # Save report
            os.makedirs('reports', exist_ok=True)
            report_file = f"reports/performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(report_file, 'w') as f:
                f.write(report)
            
            logger.info(f"✅ Performance report saved to: {report_file}")
            print(report)
            
        except Exception as e:
            logger.error(f"❌ Performance report generation failed: {e}")
    
    def run_full_optimization(self):
        """Run complete system optimization"""
        logger.info("🚀 Starting full system optimization...")
        
        start_time = datetime.now()
        
        try:
            # Step 1: Optimize database indexes
            self.optimize_database_indexes()
            
            # Step 2: Clean up old data
            self.cleanup_old_data()
            
            # Step 3: Optimize database performance
            self.optimize_database_performance()
            
            # Step 4: Validate data integrity
            self.validate_data_integrity()
            
            # Step 5: Generate performance report
            self.generate_performance_report()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"🎉 Full system optimization completed in {duration:.1f} seconds")
            
        except Exception as e:
            logger.error(f"❌ System optimization failed: {e}")
            raise


def main():
    """Main optimization function"""
    print("🔧 Media Bias Detector System Optimizer")
    print("=" * 50)
    
    optimizer = SystemOptimizer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "indexes":
            optimizer.optimize_database_indexes()
        elif command == "cleanup":
            retention_days = int(sys.argv[2]) if len(sys.argv) > 2 else 365
            optimizer.cleanup_old_data(retention_days)
        elif command == "performance":
            optimizer.optimize_database_performance()
        elif command == "validate":
            optimizer.validate_data_integrity()
        elif command == "report":
            optimizer.generate_performance_report()
        elif command == "full":
            optimizer.run_full_optimization()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: indexes, cleanup, performance, validate, report, full")
            sys.exit(1)
    else:
        # Run full optimization by default
        optimizer.run_full_optimization()


if __name__ == "__main__":
    main()