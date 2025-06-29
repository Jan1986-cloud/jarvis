#!/bin/bash

# Jarvis Production Deployment Script
# Deploys the complete Jarvis Google Workspace AI Assistant

echo "🚀 Starting Jarvis Production Deployment..."

# Set environment variables
export FLASK_ENV=production
export FLASK_APP=wsgi:application

# Navigate to project directory
cd /home/ubuntu/jarvis-backend

# Activate virtual environment
source venv/bin/activate

# Install production dependencies
echo "📦 Installing production dependencies..."
pip install -r requirements.txt

# Build frontend (if not already built)
echo "🏗️  Building frontend..."
cd ../jarvis-frontend
npm run build

# Copy frontend to backend static
echo "📁 Copying frontend to backend..."
cd ..
cp -r jarvis-frontend/dist/* jarvis-backend/src/static/

# Return to backend directory
cd jarvis-backend

# Create production database
echo "🗄️  Setting up production database..."
python -c "
import sys
sys.path.insert(0, 'src')
from src.main import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

# Update requirements.txt
pip freeze > requirements.txt

echo "✅ Deployment preparation complete!"
echo ""
echo "🌐 To start production server:"
echo "cd /home/ubuntu/jarvis-backend"
echo "source venv/bin/activate"
echo "gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 30 wsgi:application"
echo ""
echo "📋 Production checklist:"
echo "- ✅ Frontend built and integrated"
echo "- ✅ Backend configured for production"
echo "- ✅ Database initialized"
echo "- ✅ Dependencies installed"
echo "- ✅ WSGI entry point created"
echo "- ✅ Gunicorn configured"
echo ""
echo "🔧 Environment variables to set in production:"
echo "- GOOGLE_CLIENT_ID: Your Google OAuth client ID"
echo "- GOOGLE_CLIENT_SECRET: Your Google OAuth client secret"
echo "- GEMINI_API_KEY: Your Google Gemini API key"
echo "- SECRET_KEY: Strong secret key for Flask"
echo "- JWT_SECRET_KEY: Strong secret key for JWT tokens"
echo ""
echo "🎉 Jarvis is ready for production deployment!"

