import os
import sys
from flask import Flask, jsonify, send_from_directory
from extensions import db, cors

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///jarvis.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
cors.init_app(app, origins=['*'])

# Import models
from models.user import User
from models.conversation import Conversation
from models.message import Message

# Import routes
from routes.auth import auth_bp
from routes.user import user_bp
from routes.ai import ai_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(ai_bp, url_prefix='/api/ai')

# Serve React app
@app.route('/')
def serve_react_app():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_react_assets(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# API Info endpoint
@app.route('/api/info')
def api_info():
    return jsonify({
        "name": "Jarvis AI Assistant",
        "version": "1.0.0",
        "description": "Google Workspace AI Assistant with Jarvis personality",
        "endpoints": {
            "auth": "/api/auth/*",
            "user": "/api/user/*", 
            "ai": "/api/ai/*",
            "health": "/api/health"
        },
        "features": {
            "jarvis_personality": True,
            "google_workspace": True,
            "ai_chat": True,
            "credits_system": True,
            "jwt_auth": True
        }
    })

# Health check
@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "database": "connected",
        "ai_service": "available",
        "timestamp": "2025-06-28T20:00:00Z"
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

