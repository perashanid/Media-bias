#!/usr/bin/env python3
"""
Run the Flask backend server
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ['PYTHONPATH'] = str(project_root)

# Import and run the Flask app
if __name__ == '__main__':
    from api.app import app
    
    # Get configuration from environment variables
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = False  # Disable debug mode to avoid reloader issues
    
    print(f"🚀 Starting Flask backend on http://{host}:{port}")
    print("🔧 API endpoints available at:")
    print(f"   - Health check: http://{host}:{port}/health")
    print(f"   - Articles: http://{host}:{port}/api/articles")
    print(f"   - Statistics: http://{host}:{port}/api/statistics/overview")
    print(f"   - Manual scraper: http://{host}:{port}/api/scrape/manual")
    print("💡 Press Ctrl+C to stop the server")
    
    try:
        app.run(host=host, port=port, debug=debug, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Backend error: {e}")
        sys.exit(1)