"""
Security Middleware voor Jarvis Backend
Handles JWT authentication, rate limiting, en security headers
"""

import jwt
import time
from functools import wraps
from flask import request, jsonify, current_app, g
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

class SecurityManager:
    def __init__(self):
        self.rate_limits = defaultdict(list)
        self.blocked_ips = set()
        self.jwt_secret = 'jarvis-jwt-secret-change-in-production'
        self.jwt_algorithm = 'HS256'
    
    def generate_jwt_token(self, user_id, email, expires_hours=24):
        """Generate JWT token voor user authenticatie"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=expires_hours),
            'iat': datetime.utcnow(),
            'iss': 'jarvis-ai-assistant'
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token
    
    def verify_jwt_token(self, token):
        """Verify JWT token en return user data"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return {
                'user_id': payload['user_id'],
                'email': payload['email'],
                'exp': payload['exp']
            }
        except jwt.ExpiredSignatureError:
            return {'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}
    
    def get_client_ip(self, request):
        """Get real client IP address"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def check_rate_limit(self, ip, limit=100, window=3600):
        """Check rate limiting (default: 100 requests per hour)"""
        current_time = time.time()
        
        # Clean old entries
        self.rate_limits[ip] = [
            timestamp for timestamp in self.rate_limits[ip]
            if current_time - timestamp < window
        ]
        
        # Check if limit exceeded
        if len(self.rate_limits[ip]) >= limit:
            return False
        
        # Add current request
        self.rate_limits[ip].append(current_time)
        return True
    
    def add_security_headers(self, response):
        """Add security headers to response"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        return response

# Global security manager instance
security_manager = SecurityManager()

def require_auth(f):
    """Decorator voor routes die authenticatie vereisen"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
        
        # Check X-Auth-Token header (alternative)
        elif 'X-Auth-Token' in request.headers:
            token = request.headers['X-Auth-Token']
        
        if not token:
            return jsonify({'error': 'Authentication token required'}), 401
        
        # Verify token
        user_data = security_manager.verify_jwt_token(token)
        if 'error' in user_data:
            return jsonify({'error': user_data['error']}), 401
        
        # Add user data to request context
        g.current_user = user_data
        return f(*args, **kwargs)
    
    return decorated_function

def rate_limit(limit=100, window=3600):
    """Decorator voor rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = security_manager.get_client_ip(request)
            
            if not security_manager.check_rate_limit(ip, limit, window):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {limit} requests per {window//60} minutes'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_api_key(f):
    """Decorator voor API key validatie (voor externe integraties)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # In productie: valideer tegen database
        valid_api_keys = [
            'jarvis-api-key-demo',
            'jarvis-api-key-production'
        ]
        
        if api_key not in valid_api_keys:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def security_middleware(app):
    """Initialize security middleware voor Flask app"""
    
    @app.before_request
    def before_request():
        # Check for blocked IPs
        ip = security_manager.get_client_ip(request)
        if ip in security_manager.blocked_ips:
            return jsonify({'error': 'Access denied'}), 403
        
        # Add request timestamp
        g.request_start_time = time.time()
    
    @app.after_request
    def after_request(response):
        # Add security headers
        response = security_manager.add_security_headers(response)
        
        # Add request timing header
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            response.headers['X-Response-Time'] = f'{duration:.3f}s'
        
        return response
    
    return app

# Utility functions
def hash_password(password):
    """Hash password using SHA-256 (in productie: gebruik bcrypt)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

def generate_api_key(user_id):
    """Generate API key voor user"""
    timestamp = str(int(time.time()))
    data = f"{user_id}:{timestamp}:jarvis-api"
    return hashlib.sha256(data.encode()).hexdigest()[:32]

# Export functions
__all__ = [
    'SecurityManager',
    'security_manager',
    'require_auth',
    'rate_limit',
    'validate_api_key',
    'security_middleware',
    'hash_password',
    'verify_password',
    'generate_api_key'
]

