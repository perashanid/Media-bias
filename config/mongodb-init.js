// MongoDB initialization script
db = db.getSiblingDB('media_bias_detector');

// Create collections
db.createCollection('articles');
db.createCollection('bias_scores');
db.createCollection('comparison_reports');

// Create indexes for better performance
db.articles.createIndex({ "url": 1 }, { unique: true });
db.articles.createIndex({ "content_hash": 1 }, { unique: true });
db.articles.createIndex({ "source": 1 });
db.articles.createIndex({ "publication_date": -1 });
db.articles.createIndex({ "scraped_at": -1 });
db.articles.createIndex({ "language": 1 });
db.articles.createIndex({ "bias_scores": 1 });

// Text search index for content search
db.articles.createIndex({ 
    "title": "text", 
    "content": "text" 
}, { 
    name: "article_text_search",
    default_language: "english"
});

// Compound indexes for common queries
db.articles.createIndex({ "source": 1, "publication_date": -1 });
db.articles.createIndex({ "language": 1, "publication_date": -1 });
db.articles.createIndex({ "bias_scores.overall_bias_score": 1 });

// Create user for application (if authentication is enabled)
if (db.getUser('media_bias_app') === null) {
    db.createUser({
        user: 'media_bias_app',
        pwd: 'app_password_change_in_production',
        roles: [
            { role: 'readWrite', db: 'media_bias_detector' }
        ]
    });
}

print('MongoDB initialization completed successfully');