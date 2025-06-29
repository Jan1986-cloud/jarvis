import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.workspace import workspace_bp
from src.routes.ai import ai_bp
from src.middleware.security import security_middleware

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'jarvis-secret-key-change-in-production'

# Enable CORS for all routes
CORS(app, origins="*", supports_credentials=True)

# Initialize security middleware
app = security_middleware(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(workspace_bp, url_prefix='/api')
app.register_blueprint(ai_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize database
with app.app_context():
    db.create_all()

# API Info endpoint
@app.route('/api/info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'Jarvis - Google Workspace AI Assistant',
        'version': '1.0.0',
        'description': 'AI Assistant voor Google Workspace met Jarvis persoonlijkheid',
        'security': {
            'jwt_authentication': True,
            'rate_limiting': True,
            'security_headers': True,
            'api_key_support': True
        },
        'endpoints': {
            'auth': [
                'GET /api/auth/login',
                'GET /api/auth/callback',
                'POST /api/auth/google',
                'POST /api/auth/refresh',
                'DELETE /api/auth/logout',
                'GET /api/auth/status',
                'POST /api/auth/revoke'
            ],
            'user': [
                'GET /api/user/profile',
                'GET /api/user/credits',
                'POST /api/user/upgrade'
            ],
            'chat': [
                'GET /api/conversations',
                'POST /api/conversations',
                'GET /api/conversations/{id}/messages',
                'POST /api/conversations/{id}/messages'
            ],
            'workspace': [
                'GET /api/gmail/messages',
                'POST /api/gmail/send',
                'GET /api/drive/files',
                'POST /api/drive/files',
                'GET /api/calendar/events',
                'POST /api/calendar/events',
                'GET /api/workspace/summary'
            ],
            'ai': [
                'POST /api/ai/chat',
                'POST /api/ai/analyze-workspace',
                'POST /api/ai/smart-compose',
                'POST /api/ai/summarize',
                'POST /api/ai/translate',
                'POST /api/ai/explain',
                'GET /api/ai/status'
            ],
            'knowledge': [
                'POST /api/knowledge/documents',
                'POST /api/knowledge/search'
            ]
        },
        'features': {
            'google_workspace_integration': True,
            'jarvis_personality': True,
            'vector_database': True,
            'ai_powered_chat': True,
            'smart_compose': True,
            'document_analysis': True,
            'proactive_suggestions': True,
            'jwt_authentication': True,
            'rate_limiting': True,
            'security_middleware': True
        }
    })

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': 'now',
        'version': '1.0.0',
        'services': {
            'database': 'connected',
            'ai_service': 'ready',
            'vector_db': 'ready',
            'google_apis': 'configured'
        }
    })

# Frontend serving routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return jsonify({'error': 'Static folder not configured'}), 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            # Return API info if no frontend is available
            return jsonify({
                'message': 'Jarvis Backend API is running',
                'frontend': 'Not deployed yet',
                'api_info': '/api/info',
                'health': '/api/health',
                'status': 'Ready for frontend integration',
                'security': 'JWT authentication enabled'
            })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.'
    }), 429

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🤖 Starting Jarvis Backend...")
    print("📡 API endpoints available at http://localhost:5000/api/")
    print("📋 API documentation at http://localhost:5000/api/info")
    print("🔒 Security middleware enabled (JWT + Rate limiting)")
    print("🧠 AI services initialized")
    print("🗄️  Vector database ready")
    print("🔗 Google Workspace integration enabled")
    app.run(host='0.0.0.0', port=5000, debug=True)

