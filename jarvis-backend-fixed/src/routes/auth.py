from flask import Blueprint, request, jsonify
import jwt
import os
from datetime import datetime, timedelta
from models.user import User
from main import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    """Initiate Google OAuth flow"""
    return jsonify({
        "message": "Google OAuth login",
        "redirect_url": "https://accounts.google.com/oauth2/auth",
        "instructions": "Use Google OAuth to authenticate"
    })

@auth_bp.route('/google', methods=['POST'])
def google_auth():
    """Process Google authentication"""
    try:
        data = request.get_json()
        
        # Extract user data
        email = data.get('email')
        name = data.get('name')
        google_id = data.get('google_id', email)
        
        if not email or not name:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Find or create user
        user = User.query.filter_by(email=email).first()
        is_new_user = False
        
        if not user:
            user = User(
                email=email,
                name=name,
                google_id=google_id,
                credits=500
            )
            db.session.add(user)
            is_new_user = True
        else:
            user.last_login = datetime.utcnow()
        
        db.session.commit()
        
        # Generate JWT token
        token_payload = {
            'user_id': user.id,
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(
            token_payload,
            os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret'),
            algorithm='HS256'
        )
        
        return jsonify({
            "message": "Authentication successful",
            "user": user.to_dict(),
            "token": token,
            "session_id": user.id,
            "is_new_user": is_new_user,
            "expires_in": 86400
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({
            "authenticated": False,
            "message": "No valid token provided"
        })
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(
            token,
            os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret'),
            algorithms=['HS256']
        )
        
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({
                "authenticated": False,
                "message": "User not found"
            })
        
        return jsonify({
            "authenticated": True,
            "user": user.to_dict(),
            "token_valid": True
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({
            "authenticated": False,
            "message": "Token expired"
        }), 401
    except jwt.InvalidTokenError:
        return jsonify({
            "authenticated": False,
            "message": "Invalid token"
        }), 401

