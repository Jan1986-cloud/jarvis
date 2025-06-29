"""
WSGI Entry Point voor Jarvis Production Deployment
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app
from src.config import get_config

# Configure app for production
config_class = get_config()
app.config.from_object(config_class)

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')

if __name__ == "__main__":
    # For development testing
    app.run(host='0.0.0.0', port=5000, debug=False)
else:
    # For Gunicorn
    application = app

