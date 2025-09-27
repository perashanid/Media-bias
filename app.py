#!/usr/bin/env python3
"""
Modern Media Bias Detector - Production Entry Point
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv

# Load appropriate environment file
env_file = '.env.production' if os.getenv('FLASK_ENV') == 'production' else '.env.development'
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv('.env')

from api.app import app

if __name__ == '__main__':
    # Production configuration
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting Modern Media Bias Detector on {host}:{port}")
    print(f"🌍 Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    app.run(host=host, port=port, debug=debug)