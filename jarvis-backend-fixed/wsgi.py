"""
WSGI Entry Point voor Jarvis AI Assistant
Optimized for Railway.com deployment
"""

import os
import sys

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Import the Flask application
from src.main import app, db

# Create database tables
with app.app_context():
    db.create_all()

# WSGI application
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

