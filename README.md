# Media Bias Detector

A comprehensive system for detecting and analyzing bias in news articles from Bangladeshi media sources. The system scrapes articles from multiple news sources, analyzes them for various types of bias, and provides comparative analysis across different sources.

## Recent Fixes & Improvements

### ✅ Fixed Issues
- **Git Repository**: Added proper `.gitignore` to reduce tracked files from 10k+ to ~100 essential files
- **API Routing**: Fixed 404 errors by properly registering Flask blueprints
- **Comparison Feature**: Enhanced comparison view to support multiple input types:
  - URLs (with automatic scraping)
  - Raw text input
  - Existing article IDs
- **Custom Comparison**: Users can now add and compare multiple articles, URLs, or text snippets
- **Frontend Build**: Fixed TypeScript compilation errors

### 🚀 New Features
- **Multi-Input Comparison**: Compare articles from different sources using various input methods
- **Custom Text Analysis**: Analyze bias in any text without needing to scrape articles
- **Enhanced UI**: Improved comparison interface with tabs and input management
- **Better Error Handling**: More informative error messages and fallback options

## Features

- **Multi-source News Scraping**: Automated scraping from 5 major Bangladeshi news sources
- **Comprehensive Bias Analysis**: Detects sentiment, political bias, emotional language, and factual vs opinion content
- **Comparative Analysis**: Compares bias patterns across different news sources
- **Real-time Dashboard**: Web interface for viewing articles and bias analysis
- **Automated Scheduling**: Configurable automated scraping and analysis
- **Monitoring & Alerts**: System health monitoring with email alerts
- **Multi-language Support**: Handles both Bengali and English content

## Architecture

### Backend Services
- **Flask API**: RESTful API for all operations
- **MongoDB**: Document database for storing articles and analysis results
- **Scraper Manager**: Coordinates scraping from multiple news sources
- **Bias Analyzer**: ML-based bias detection engine
- **Scheduler Service**: Manages automated tasks
- **Monitoring Service**: System health and alerting

### Frontend
- **React TypeScript**: Modern web interface
- **Material-UI**: Professional UI components
- **Recharts**: Data visualization and charts
- **Responsive Design**: Works on desktop and mobile

### News Sources
- Prothom Alo (Bengali)
- The Daily Star (English)
- BD Pratidin (Bengali)
- Ekattor TV (Bengali)
- ATN News TV (Bengali)

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd media-bias-detector
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env.development
   # Edit .env.development with your settings
   ```

3. **Start development environment**
   ```bash
   chmod +x scripts/*.sh
   ./scripts/deploy.sh development
   ```

4. **Test the system**
   ```bash
   # Test API endpoints and features
   python test_system.py
   
   # Or run individual tests
   python test_api_simple.py
   python test_db_connection.py
   ```

4. **Access the application**
   - Main application: http://localhost:5000
   - React dev server: http://localhost:3000
   - MongoDB: localhost:27017

### Production Deployment

1. **Prepare production environment**
   ```bash
   cp .env.example .env.production
   # Edit .env.production with production settings
   # Update passwords and security keys
   ```

2. **Deploy to production**
   ```bash
   ./scripts/deploy.sh production
   ```

3. **Configure SSL (recommended)**
   - Place SSL certificates in `config/ssl/`
   - Update nginx configuration for HTTPS

## Configuration

### Environment Variables

Key configuration options in `.env` files:

```bash
# Database
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=media_bias_detector
MONGODB_USERNAME=admin
MONGODB_PASSWORD=your_password

# Scraping
SCRAPING_INTERVAL_HOURS=2
MAX_ARTICLES_PER_SOURCE=30
SCRAPER_DELAY=3.0

# Monitoring
ENABLE_MONITORING=true
SMTP_SERVER=smtp.gmail.com
ALERT_TO_EMAILS=admin@yourdomain.com

# Security
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
```

### Scraping Configuration

Customize scraping behavior in `config/scraper_settings.py`:
- Scraping intervals per source
- Article limits and filters
- Rate limiting settings
- Retry policies

### Monitoring Configuration

Configure monitoring thresholds in `config/monitoring_config.json`:
- Success rate thresholds
- Response time limits
- Error count limits
- Alert retention policies

## API Documentation

### Articles API
- `GET /api/articles` - List articles with filtering
- `GET /api/articles/{id}` - Get specific article
- `GET /api/articles/search` - Search articles
- `POST /api/articles/{id}/bias` - Analyze article bias

### Bias Analysis API
- `POST /api/bias/analyze-text` - Analyze arbitrary text
- `POST /api/bias/batch-analyze` - Batch analyze articles
- `GET /api/bias/distribution` - Get bias distribution stats

### Comparison API
- `GET /api/comparison/articles/{id}/similar` - Find similar articles
- `GET /api/comparison/articles/{id}/report` - Generate comparison report
- `GET /api/comparison/sources` - Compare bias across sources

### Statistics API
- `GET /api/statistics/overview` - System overview
- `GET /api/statistics/sources` - Source-wise statistics
- `GET /api/statistics/bias-trends` - Bias trends over time

## Usage Examples

### Analyzing Text for Bias

```python
import requests

response = requests.post('http://localhost:5000/api/bias/analyze-text', json={
    'text': 'Your text to analyze here',
    'language': 'english'  # or 'bengali'
})

bias_result = response.json()
print(f"Overall bias: {bias_result['overall_bias_score']}")
print(f"Sentiment: {bias_result['sentiment_score']}")
```

### Getting Article Comparisons

```python
# Find similar articles
response = requests.get(f'http://localhost:5000/api/comparison/articles/{article_id}/similar')
similar_articles = response.json()['related_articles']

# Generate comparison report
response = requests.get(f'http://localhost:5000/api/comparison/articles/{article_id}/report')
comparison_report = response.json()
```

## Monitoring and Maintenance

### Health Monitoring

Check system health:
```bash
curl http://localhost:5000/health
```

View monitoring dashboard in the web interface or check logs:
```bash
docker-compose logs -f app
```

### Backup and Restore

**Create backup:**
```bash
./scripts/backup.sh
```

**Restore from backup:**
```bash
./scripts/restore.sh backups/media_bias_backup_20231201_120000.tar.gz
```

### Log Management

Logs are stored in the `logs/` directory:
- `media_bias_detector.log` - Main application log
- Automatic log rotation configured
- Different log levels for development/production

## Development

### Project Structure

```
media-bias-detector/
├── api/                    # Flask API
│   ├── app.py             # Main application
│   └── routes/            # API route modules
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── types/         # TypeScript types
│   └── public/
├── scrapers/              # News scrapers
├── services/              # Backend services
├── models/                # Data models
├── config/                # Configuration files
├── scripts/               # Deployment scripts
└── docs/                  # Documentation
```

### Adding New News Sources

1. Create new scraper class extending `BaseScraper`
2. Implement `_get_article_urls()` and `_extract_article_content()`
3. Add scraper to `ScraperManager`
4. Update configuration

### Extending Bias Analysis

1. Add new analysis methods to bias analyzer services
2. Update `BiasScore` model with new metrics
3. Modify API endpoints to return new metrics
4. Update frontend to display new analysis

### Running Tests

```bash
# Backend tests
cd api && python -m pytest

# Frontend tests
cd frontend && npm test

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Troubleshooting

### Common Issues

**MongoDB Connection Issues:**
- Check MongoDB container is running: `docker-compose ps`
- Verify connection settings in environment file
- Check MongoDB logs: `docker-compose logs mongodb`

**Scraping Failures:**
- Check network connectivity
- Verify website structure hasn't changed
- Review scraper logs for specific errors
- Adjust rate limiting if getting blocked

**High Memory Usage:**
- Reduce batch sizes in configuration
- Increase scraping intervals
- Monitor with `docker stats`

**Frontend Build Issues:**
- Clear node_modules: `rm -rf frontend/node_modules`
- Reinstall dependencies: `cd frontend && npm install`
- Check Node.js version compatibility

### Performance Optimization

**Database:**
- Ensure proper indexing (handled automatically)
- Regular cleanup of old articles
- Monitor database size

**Scraping:**
- Adjust concurrent scraper limits
- Optimize scraping intervals
- Use appropriate delays between requests

**Analysis:**
- Process articles in batches
- Use background processing for large datasets
- Cache frequently accessed results

## Security Considerations

### Production Security

1. **Change default passwords** in production environment
2. **Use HTTPS** with proper SSL certificates
3. **Configure firewall** to restrict access
4. **Regular security updates** for dependencies
5. **Monitor access logs** for suspicious activity
6. **Backup encryption** for sensitive data

### API Security

- Rate limiting enabled by default
- Input validation on all endpoints
- CORS configuration for frontend access
- Authentication tokens for admin operations

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Commit changes: `git commit -am 'Add feature'`
5. Push to branch: `git push origin feature-name`
6. Submit pull request

### Code Style

- Python: Follow PEP 8, use Black formatter
- TypeScript: Use ESLint and Prettier
- Commit messages: Use conventional commits format

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `docs/`
- Review logs for error details

## Acknowledgments

- News sources for providing public content
- Open source libraries and frameworks used
- Contributors and maintainers