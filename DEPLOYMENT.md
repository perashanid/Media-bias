# Deployment Guide - Modern Media Bias Detector

## Render Deployment (Recommended)

### Prerequisites
- GitHub repository with your code
- MongoDB Atlas account (free tier available)
- Render account (free tier available)

### Step 1: Database Setup (MongoDB Atlas)

1. **Create MongoDB Atlas Account**
   - Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
   - Create a free account and cluster

2. **Get Connection String**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/database`)

### Step 2: Deploy to Render

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - **Name**: `media-bias-detector` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `./render-build.sh`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT api.app:app`

3. **Set Environment Variables**
   ```
   FLASK_ENV=production
   MONGODB_URI=your_mongodb_atlas_connection_string
   SECRET_KEY=your_strong_secret_key_here
   JWT_SECRET_KEY=your_jwt_secret_key_here
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app

### Step 3: Generate Secret Keys

Use Python to generate secure keys:

```python
import secrets
print("SECRET_KEY:", secrets.token_urlsafe(32))
print("JWT_SECRET_KEY:", secrets.token_urlsafe(32))
```

### Step 4: Verify Deployment

1. **Check Build Logs**
   - Monitor the build process in Render dashboard
   - Ensure frontend builds successfully

2. **Test Application**
   - Visit your Render URL (e.g., `https://your-app-name.onrender.com`)
   - Test user registration and login
   - Verify API endpoints work

## Environment Variables Reference

### Required Variables
- `FLASK_ENV`: Set to `production`
- `MONGODB_URI`: Your MongoDB Atlas connection string
- `SECRET_KEY`: Strong secret key for Flask sessions
- `JWT_SECRET_KEY`: Strong secret key for JWT tokens

### Optional Variables
- `PORT`: Port number (automatically set by Render)
- `SCRAPING_INTERVAL_HOURS`: How often to scrape (default: 6)
- `MAX_ARTICLES_PER_SOURCE`: Max articles per source (default: 100)
- `RATE_LIMIT_ENABLED`: Enable rate limiting (default: true)

## Troubleshooting

### Build Failures
- Check that `render-build.sh` is executable
- Verify all dependencies are in `requirements.txt`
- Check Node.js version compatibility

### Runtime Errors
- Check environment variables are set correctly
- Verify MongoDB connection string
- Check application logs in Render dashboard

### Frontend Issues
- Ensure frontend builds successfully
- Check that static files are served correctly
- Verify API endpoints are accessible

## Performance Optimization

### Database
- Use MongoDB Atlas for better performance
- Enable database indexes for faster queries
- Consider upgrading to paid tier for production

### Application
- Use Render's paid tier for better performance
- Enable caching where appropriate
- Monitor resource usage

## Security Considerations

### Environment Variables
- Never commit secret keys to version control
- Use strong, unique keys for production
- Rotate keys regularly

### Database
- Use MongoDB Atlas with authentication
- Restrict database access to your application
- Enable database encryption

### Application
- Keep dependencies updated
- Monitor for security vulnerabilities
- Use HTTPS (automatically provided by Render)

## Monitoring

### Application Health
- Use the `/health` endpoint for monitoring
- Set up uptime monitoring
- Monitor application logs

### Performance
- Monitor response times
- Track error rates
- Monitor resource usage

## Scaling

### Horizontal Scaling
- Render supports automatic scaling
- Consider upgrading to paid plans for better scaling

### Database Scaling
- MongoDB Atlas provides automatic scaling
- Monitor database performance
- Consider sharding for large datasets

## Backup and Recovery

### Database Backup
- MongoDB Atlas provides automatic backups
- Consider additional backup strategies for critical data

### Application Backup
- Keep your code in version control
- Document your deployment configuration
- Maintain environment variable backups (without secrets)