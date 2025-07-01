from flask import Blueprint, request, jsonify
import jwt
import os
from models.user import User
from models.conversation import Conversation
from models.message import Message
from main import db

user_bp = Blueprint('user', __name__)

def get_current_user():
    """Get current user from JWT token"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(
            token,
            os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret'),
            algorithms=['HS256']
        )
        return User.query.get(payload['user_id'])
    except:
        return None

@user_bp.route('/user/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({"user": user.to_dict()})

@user_bp.route('/user/credits', methods=['GET'])
def get_credits():
    """Get user credits"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({
        "credits": user.credits,
        "usage_today": 0,  # Placeholder
        "usage_this_month": 0  # Placeholder
    })

@user_bp.route('/conversations', methods=['GET'])
def get_conversations():
    """Get user conversations"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    conversations = Conversation.query.filter_by(user_id=user.id).order_by(Conversation.updated_at.desc()).all()
    
    return jsonify({
        "conversations": [conv.to_dict() for conv in conversations],
        "total": len(conversations)
    })

@user_bp.route('/conversations', methods=['POST'])
def create_conversation():
    """Create new conversation"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    title = data.get('title', 'New Conversation')
    initial_message = data.get('initial_message')
    
    # Create conversation
    conversation = Conversation(
        user_id=user.id,
        title=title
    )
    db.session.add(conversation)
    db.session.flush()  # Get the ID
    
    # Add initial message if provided
    if initial_message:
        message = Message(
            conversation_id=conversation.id,
            content=initial_message,
            sender='user'
        )
        db.session.add(message)
    
    db.session.commit()
    
    return jsonify({
        "conversation": conversation.to_dict(),
        "message": message.to_dict() if initial_message else None
    })

@user_bp.route('/conversations/<conversation_id>/messages', methods=['GET'])
def get_messages(conversation_id):
    """Get conversation messages"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Verify conversation belongs to user
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=user.id).first()
    if not conversation:
        return jsonify({"error": "Conversation not found"}), 404
    
    messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.timestamp.asc()).all()
    
    return jsonify({
        "messages": [msg.to_dict() for msg in messages],
        "total": len(messages)
    })

