# Media Bias Detector

A full-stack application for scraping, analyzing, and detecting bias in news articles from various sources.

## Features

- 🔍 **Web Scraping**: Scrape articles from multiple news sources
- 🧠 **Bias Analysis**: AI-powered bias detection and sentiment analysis
- 📊 **Dashboard**: Real-time statistics and visualizations
- 🗄️ **Database Storage**: Persistent storage with MongoDB
- 🌐 **Web Interface**: React-based frontend for easy interaction

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

This will install both frontend and backend dependencies.

### 2. Setup Database

```bash
npm run setup-db
```

Follow the interactive guide to configure MongoDB (Atlas cloud or local installation).

### 3. Start the Application

```bash
npm run dev
```

This will start both the backend API server and frontend development server.

- **Frontend**: http://localhost:3000 (or next available port)
- **Backend API**: http://localhost:5000

## Database Options

### Option 1: MongoDB Atlas (Recommended)
- Free cloud database
- No local installation required
- Run `npm run setup-db` and choose option 1

### Option 2: Local MongoDB
- Install MongoDB Community Server
- Run `npm run setup-db` and choose option 2

## Available Scripts

- `npm run dev` - Start both frontend and backend
- `npm run backend` - Start only the backend API
- `npm run frontend` - Start only the frontend
- `npm run setup-db` - Configure database connection
- `npm run build-frontend` - Build frontend for production
- `npm test` - Run all tests

## Usage

### Manual Scraping

1. Go to the **Manual Scraper** page
2. **Scrape by URL**: Enter any news article URL
3. **Scrape by Source**: Select from available news sources
4. Articles are automatically stored and analyzed for bias

### View Articles

1. Go to the **Articles** page
2. Browse all scraped articles
3. View bias analysis results
4. Filter by source, date, or search terms

### Dashboard

1. Go to the **Dashboard** page
2. View statistics and trends
3. See bias distribution across sources
4. Monitor scraping activity

## Architecture

### Backend (Python/Flask)
- **API Routes**: RESTful API endpoints
- **Scrapers**: Modular web scrapers for different news sources
- **Bias Analyzer**: NLP-based bias detection
- **Storage Service**: MongoDB integration
- **Models**: Data models for articles and analysis

### Frontend (React/TypeScript)
- **Pages**: Dashboard, Articles, Manual Scraper
- **Components**: Reusable UI components
- **Services**: API integration
- **Context**: State management

### Database (MongoDB)
- **Articles Collection**: Stores scraped articles
- **Indexes**: Optimized for search and filtering
- **Aggregation**: Statistics and analytics

## News Sources

Currently supported news sources:
- Prothom Alo
- Daily Star
- BD Pratidin
- Ekattor TV
- ATN News

## Bias Analysis

The system analyzes articles for:
- **Political Bias**: Left/Center/Right leaning
- **Sentiment**: Positive/Neutral/Negative
- **Emotional Language**: Objective vs Emotional
- **Factual vs Opinion**: Content classification
- **Overall Bias Score**: Composite bias rating

## Development

### Project Structure

```
├── api/                    # Backend API
│   ├── routes/            # API route handlers
│   └── app.py            # Flask application
├── config/                # Configuration
│   └── database.py       # Database connection
├── frontend/              # React frontend
│   ├── src/              # Source code
│   └── public/           # Static assets
├── models/                # Data models
├── scrapers/              # Web scrapers
├── services/              # Business logic
└── tests/                 # Test files
```

### Adding New Scrapers

1. Create a new scraper class in `scrapers/`
2. Extend `BaseScraper` class
3. Implement required methods
4. Register in `ScraperManager`

### Environment Variables

Create a `.env` file (or use `npm run setup-db`):

```env
MONGODB_URI=your_mongodb_connection_string
DATABASE_NAME=media_bias_detector
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
LOG_LEVEL=INFO
```

## Troubleshooting

### Database Connection Issues
- Run `npm run setup-db` to reconfigure
- Check your MongoDB connection string
- Verify network connectivity

### Scraping Issues
- Some websites may block automated requests
- Check if the website structure has changed
- Verify internet connectivity

### Frontend Issues
- Clear browser cache
- Check if backend is running
- Verify API endpoints are accessible

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details