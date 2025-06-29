from flask import Blueprint, jsonify, request, session, g
from src.services.oauth import get_google_oauth_url, exchange_code_for_tokens
from src.models.user import db, User, GoogleToken
from src.middleware.security import security_manager, require_auth, rate_limit
import uuid
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/login', methods=['GET'])
@rate_limit(limit=10, window=300)  # 10 requests per 5 minutes
def login():
    """Initialize Google OAuth login flow"""
    try:
        authorization_url, state = get_google_oauth_url()
        
        # Store state in session for CSRF protection
        session['oauth_state'] = state
        
        return jsonify({
            'authorization_url': authorization_url,
            'state': state,
            'message': 'Redirect user to authorization_url to complete OAuth flow'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to initialize OAuth: {str(e)}'}), 500

@auth_bp.route('/auth/callback', methods=['GET'])
@rate_limit(limit=10, window=300)
def callback():
    """Handle Google OAuth callback"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            return jsonify({'error': f'OAuth error: {error}'}), 400
        
        if not code:
            return jsonify({'error': 'Authorization code not provided'}), 400
        
        # Verify state for CSRF protection
        if state != session.get('oauth_state'):
            return jsonify({'error': 'Invalid state parameter'}), 400
        
        # Exchange code for tokens
        tokens = exchange_code_for_tokens(code)
        
        if not tokens:
            return jsonify({'error': 'Failed to exchange code for tokens'}), 400
        
        # Process the tokens
        return process_google_auth(tokens)
        
    except Exception as e:
        return jsonify({'error': f'OAuth callback failed: {str(e)}'}), 500

@auth_bp.route('/auth/google', methods=['POST'])
@rate_limit(limit=20, window=300)
def google_auth():
    """Process Google authentication data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No authentication data provided'}), 400
        
        return process_google_auth(data)
        
    except Exception as e:
        return jsonify({'error': f'Google authentication failed: {str(e)}'}), 500

def process_google_auth(auth_data):
    """Process Google authentication data and create/update user"""
    try:
        # Extract user info
        email = auth_data.get('email')
        name = auth_data.get('name')
        google_id = auth_data.get('google_id')
        
        if not email:
            return jsonify({'error': 'Email not provided in authentication data'}), 400
        
        # Find or create user
        user = User.query.filter_by(email=email).first()
        is_new_user = False
        
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                name=name or email.split('@')[0],
                google_id=google_id,
                credits=500,  # Starting credits
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            is_new_user = True
        else:
            # Update existing user
            if name:
                user.name = name
            if google_id:
                user.google_id = google_id
            user.last_login = datetime.utcnow()
        
        # Store/update Google tokens
        google_token = GoogleToken.query.filter_by(user_id=user.id).first()
        
        if not google_token:
            google_token = GoogleToken(
                user_id=user.id,
                access_token=auth_data.get('access_token', ''),
                refresh_token=auth_data.get('refresh_token', ''),
                expires_at=datetime.utcnow(),  # Will be updated with real expiry
                scope=auth_data.get('scope', '')
            )
            db.session.add(google_token)
        else:
            google_token.access_token = auth_data.get('access_token', '')
            if auth_data.get('refresh_token'):
                google_token.refresh_token = auth_data.get('refresh_token')
            google_token.scope = auth_data.get('scope', '')
            google_token.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Generate JWT token
        jwt_token = security_manager.generate_jwt_token(user.id, user.email)
        
        return jsonify({
            'message': 'Authentication successful',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'credits': user.credits,
                'is_active': user.is_active
            },
            'token': jwt_token,
            'session_id': user.id,
            'is_new_user': is_new_user,
            'expires_in': 86400  # 24 hours
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to process authentication: {str(e)}'}), 500

@auth_bp.route('/auth/refresh', methods=['POST'])
@rate_limit(limit=30, window=300)
def refresh_token():
    """Refresh JWT token"""
    try:
        data = request.get_json()
        old_token = data.get('token')
        
        if not old_token:
            return jsonify({'error': 'Token not provided'}), 400
        
        # Verify old token (even if expired)
        try:
            user_data = security_manager.verify_jwt_token(old_token)
            if 'error' in user_data and user_data['error'] != 'Token expired':
                return jsonify({'error': 'Invalid token'}), 401
        except:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get user from database
        user = User.query.get(user_data.get('user_id'))
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404
        
        # Generate new token
        new_token = security_manager.generate_jwt_token(user.id, user.email)
        
        return jsonify({
            'token': new_token,
            'expires_in': 86400,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'credits': user.credits
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 500

@auth_bp.route('/auth/logout', methods=['DELETE'])
@require_auth
def logout():
    """Logout user and invalidate token"""
    try:
        user_id = g.current_user['user_id']
        
        # In a production app, you would add the token to a blacklist
        # For now, we just return success
        
        return jsonify({
            'message': 'Logout successful',
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@auth_bp.route('/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    try:
        token = None
        
        # Check Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                pass
        
        # Check X-Auth-Token header
        elif 'X-Auth-Token' in request.headers:
            token = request.headers['X-Auth-Token']
        
        if not token:
            return jsonify({
                'authenticated': False,
                'message': 'No authentication token provided'
            })
        
        # Verify token
        user_data = security_manager.verify_jwt_token(token)
        if 'error' in user_data:
            return jsonify({
                'authenticated': False,
                'error': user_data['error']
            })
        
        # Get user from database
        user = User.query.get(user_data['user_id'])
        if not user or not user.is_active:
            return jsonify({
                'authenticated': False,
                'error': 'User not found or inactive'
            })
        
        return jsonify({
            'authenticated': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'credits': user.credits,
                'is_active': user.is_active
            },
            'token_valid': True
        })
        
    except Exception as e:
        return jsonify({
            'authenticated': False,
            'error': f'Status check failed: {str(e)}'
        })

@auth_bp.route('/auth/revoke', methods=['POST'])
@require_auth
def revoke_access():
    """Revoke Google API access"""
    try:
        user_id = g.current_user['user_id']
        
        # Remove Google tokens from database
        GoogleToken.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        return jsonify({
            'message': 'Google API access revoked successfully',
            'user_id': user_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to revoke access: {str(e)}'}), 500

