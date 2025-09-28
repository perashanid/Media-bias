# Development Setup Guide

## Quick Fix for Login/Registration Issues

The login and registration issues are caused by API URL configuration problems. Here's how to fix them:

### 1. Start the Backend Server

```bash
# Option 1: Use the development server script
python start_dev_server.py

# Option 2: Use the main app (if no socket issues)
python app.py
```

The backend will be available at: `http://127.0.0.1:5000`

### 2. Start the Frontend Development Server

```bash
cd frontend
npm start
```

The frontend will be available at: `http://localhost:3000`

### 3. Test the API Endpoints

```bash
# Test the API endpoints
python test_api_endpoints.py
```

### 4. Key Fixes Applied

1. **Fixed API URL construction** in `AuthContext.tsx`
   - Removed double `/api` in URLs
   - Fixed environment variable handling
   - Added proper URL construction logic

2. **Fixed CORS configuration** in `api/app.py`
   - Added proper CORS headers
   - Allowed localhost origins for development

3. **Fixed statistics endpoint** in `api/routes/statistics.py`
   - Simplified response structure
   - Removed nested objects that caused parsing issues

4. **Updated environment variables**
   - Set `REACT_APP_API_URL=/api` for both dev and prod
   - Ensures consistent API URL handling

### 5. Common Issues and Solutions

#### Issue: "Failed to load resource: 405 (METHOD NOT ALLOWED)"
**Solution**: The API routes are now properly configured. Make sure the backend server is running.

#### Issue: "SyntaxError: Unexpected token 'P', "Proxy erro"... is not valid JSON"
**Solution**: This was caused by the frontend trying to parse HTML error pages as JSON. Fixed by proper API URL configuration.

#### Issue: "Failed to load resource: 500 (Internal Server Error)"
**Solution**: The statistics endpoint has been simplified and should now return proper JSON responses.

### 6. Testing Authentication

1. **Register a new user**:
   ```javascript
   // In browser console or using the UI
   fetch('/api/auth/register', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       username: 'testuser',
       email: 'test@example.com',
       password: 'password123'
     })
   })
   ```

2. **Login**:
   ```javascript
   fetch('/api/auth/login', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       username: 'testuser',
       password: 'password123'
     })
   })
   ```

### 7. Environment Variables

Make sure these are set in your `.env.development`:

```bash
REACT_APP_API_URL=/api
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000
FLASK_HOST=127.0.0.1
```

### 8. Database Connection

The app uses MongoDB Atlas by default. If you have connection issues:

1. Check your internet connection
2. Verify MongoDB Atlas cluster is running
3. Check if your IP is whitelisted in Atlas
4. Or install MongoDB locally as a fallback

### 9. Next Steps

After fixing these issues:

1. Test user registration and login
2. Verify the dashboard loads properly
3. Test article browsing functionality
4. Check bias analysis features

The main authentication and API issues should now be resolved!