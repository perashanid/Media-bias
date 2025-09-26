# Media Bias Detector - Quick Start Guide

## 🚀 Running the Application Locally

### Option 1: One-Click Start (Windows)
```bash
.\start_both.ps1
```

### Option 2: Manual Start
1. **Start Backend:**
   ```bash
   python run_backend.py
   ```

2. **Start Frontend (in new terminal):**
   ```bash
   cd frontend
   npm start
   ```

## 🌐 Access URLs

- **Frontend Application:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **Manual Scraper:** http://localhost:3000/scraper

## 📱 Application Features

### Dashboard (/)
- Overview statistics
- Bias distribution charts
- Recent articles summary

### Articles (/articles)
- Browse all scraped articles
- Search and filter functionality
- View individual article details

### Comparison (/comparison)
- Compare bias across different sources
- View similar articles
- Bias comparison reports

### Analyzer (/analyzer)
- Analyze custom text for bias
- Real-time bias detection
- Sentiment analysis

### Manual Scraper (/scraper) 🆕
- **Scrape by URL:** Enter any news article URL to scrape and analyze
- **Scrape by Source:** Select from available news sources
- **Test Mode:** Preview article content and bias analysis without storing

## 🔧 API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /api/articles` - Get articles
- `GET /api/statistics/overview` - Dashboard statistics

### Manual Scraping 🆕
- `POST /api/scrape/manual` - Scrape and store article
- `POST /api/scrape/test-url` - Test URL without storing
- `GET /api/scrape/sources` - Get available sources

## 🧪 Testing the System

### 1. Test Backend Connection
Visit: http://localhost:5000/health

### 2. Test Manual Scraping
1. Go to http://localhost:3000/scraper
2. Enter a news article URL (e.g., from BBC, CNN, etc.)
3. Click "Test Only" to preview without storing
4. Click "Scrape & Store" to save and analyze

### 3. View Results
- Check Dashboard for updated statistics
- Browse Articles page to see scraped content
- Use Analyzer to test custom text

## 🗄️ Database Configuration

The system is configured to use MongoDB Atlas:
- **Database:** rokshanid
- **Connection:** Automatically configured
- **Collections:** articles, article_groups

## 🛠️ Troubleshooting

### Backend Issues
- Ensure MongoDB connection is working
- Check Python dependencies are installed
- Verify port 5000 is available

### Frontend Issues
- Ensure Node.js is installed
- Run `npm install` in frontend directory
- Verify port 3000 is available

### Scraping Issues
- Test with simple news URLs first
- Check network connectivity
- Some sites may block automated scraping

## 📊 Free Deployment Options

### Backend (Flask API)
1. **Heroku** (Free tier available)
2. **Railway** (Free tier)
3. **Render** (Free tier)

### Frontend (React)
1. **Netlify** (Free)
2. **Vercel** (Free)
3. **GitHub Pages** (Free)

### Database
- **MongoDB Atlas** (Free tier: 512MB)
- Already configured and working

## 🎯 Next Steps

1. **Add More Sources:** Extend scrapers for additional news sites
2. **Improve Analysis:** Enhance bias detection algorithms
3. **Add Authentication:** Implement user accounts and permissions
4. **Real-time Updates:** Add WebSocket support for live updates
5. **Mobile App:** Create React Native mobile application

---

**Happy Testing! 🎉**

For issues or questions, check the console logs in both backend and frontend terminals.