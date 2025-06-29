from flask import Blueprint, jsonify, request
from src.models.user import User, Conversation, Message, GoogleToken, db
from src.services.jarvis_ai import jarvis_ai
from src.services.vector_db import vector_service
from datetime import datetime

user_bp = Blueprint('user', __name__)

# User Management Routes
@user_bp.route('/user/profile', methods=['GET'])
def get_user_profile():
    """Get current user profile"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/user/credits', methods=['GET'])
def get_user_credits():
    """Get user credits status"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get_or_404(user_id)
    return jsonify({
        'credits': user.credits,
        'user_id': user.id
    })

@user_bp.route('/user/upgrade', methods=['POST'])
def upgrade_credits():
    """Upgrade user credits (placeholder for payment integration)"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.json
    package = data.get('package', 'pro')
    
    # Credit packages
    packages = {
        'pro': 2000,
        'business': 5000,
        'enterprise': 999999
    }
    
    if package not in packages:
        return jsonify({'error': 'Invalid package'}), 400
    
    user = User.query.get_or_404(user_id)
    user.add_credits(packages[package])
    db.session.commit()
    
    return jsonify({
        'message': f'Credits upgraded to {package}',
        'credits': user.credits
    })

# Conversation Management Routes
@user_bp.route('/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations for user"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    conversations = Conversation.query.filter_by(user_id=user_id).order_by(Conversation.created_at.desc()).all()
    return jsonify([conv.to_dict() for conv in conversations])

@user_bp.route('/conversations', methods=['POST'])
def create_conversation():
    """Create new conversation"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.json
    title = data.get('title', f'Gesprek {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    
    conversation = Conversation(
        user_id=user_id,
        title=title
    )
    db.session.add(conversation)
    db.session.commit()
    
    return jsonify(conversation.to_dict()), 201

@user_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
def get_messages(conversation_id):
    """Get messages for a conversation"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Verify conversation belongs to user
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=user_id).first_or_404()
    
    messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc()).all()
    return jsonify([msg.to_dict() for msg in messages])

@user_bp.route('/conversations/<int:conversation_id>/messages', methods=['POST'])
def send_message(conversation_id):
    """Send a message in a conversation with AI response"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Verify conversation belongs to user
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=user_id).first_or_404()
    user = User.query.get_or_404(user_id)
    
    data = request.json
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Message content required'}), 400
    
    # Get recent conversation history for context
    recent_messages = Message.query.filter_by(conversation_id=conversation_id)\
        .order_by(Message.created_at.desc()).limit(10).all()
    
    conversation_history = [msg.to_dict() for msg in reversed(recent_messages)]
    
    # Generate AI response using Jarvis AI service
    ai_result = jarvis_ai.generate_response(
        user_message=content,
        conversation_history=conversation_history,
        user_id=user_id
    )
    
    total_credits_needed = 1 + ai_result['credits_used']  # 1 for user message + AI credits
    
    # Check credits
    if not user.use_credits(total_credits_needed):
        return jsonify({'error': 'Insufficient credits'}), 402
    
    # Create user message
    user_message = Message(
        conversation_id=conversation_id,
        role='user',
        content=content,
        credits_used=1
    )
    db.session.add(user_message)
    
    # Create AI response message
    ai_message = Message(
        conversation_id=conversation_id,
        role='assistant',
        content=ai_result['response'],
        credits_used=ai_result['credits_used']
    )
    db.session.add(ai_message)
    
    # Add conversation context to vector database for future reference
    try:
        updated_history = conversation_history + [
            {'role': 'user', 'content': content},
            {'role': 'assistant', 'content': ai_result['response']}
        ]
        vector_service.add_conversation_context(
            conversation_id=str(conversation_id),
            messages=updated_history[-6:]  # Keep last 6 messages
        )
    except Exception as e:
        print(f"Error adding conversation context: {e}")
    
    db.session.commit()
    
    return jsonify({
        'user_message': user_message.to_dict(),
        'ai_response': ai_message.to_dict(),
        'ai_metadata': {
            'type': ai_result['type'],
            'context_used': ai_result.get('context_used', 0)
        },
        'credits_used': total_credits_needed,
        'remaining_credits': user.credits
    }), 201

# Vector Database Routes
@user_bp.route('/knowledge/documents', methods=['POST'])
def add_document():
    """Add document to user's knowledge base"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get_or_404(user_id)
    
    # Check credits
    if not user.use_credits(3):  # 3 credits for document processing
        return jsonify({'error': 'Insufficient credits'}), 402
    
    data = request.json
    content = data.get('content', '').strip()
    source = data.get('source', f'user_upload_{user_id}')
    metadata = data.get('metadata', {})
    
    if not content:
        return jsonify({'error': 'Document content required'}), 400
    
    try:
        # Add user context to metadata
        metadata.update({
            'user_id': user_id,
            'uploaded_by': 'user',
            'upload_time': datetime.utcnow().isoformat()
        })
        
        # Add document to vector database
        doc_id = vector_service.add_document(
            content=content,
            source=source,
            metadata=metadata
        )
        
        db.session.commit()  # Save credit usage
        
        return jsonify({
            'message': 'Document added to knowledge base',
            'document_id': doc_id,
            'credits_used': 3,
            'remaining_credits': user.credits
        }), 201
        
    except Exception as e:
        # Rollback credit usage on error
        user.add_credits(3)
        db.session.commit()
        return jsonify({'error': f'Failed to add document: {str(e)}'}), 500

@user_bp.route('/knowledge/search', methods=['POST'])
def search_knowledge():
    """Search user's knowledge base"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get_or_404(user_id)
    
    # Check credits
    if not user.use_credits(1):  # 1 credit for search
        return jsonify({'error': 'Insufficient credits'}), 402
    
    data = request.json
    query = data.get('query', '').strip()
    max_results = min(data.get('max_results', 5), 20)
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    try:
        # Search in vector database
        results = vector_service.search_documents(
            query=query,
            n_results=max_results
        )
        
        # Filter results for user's documents (if needed)
        user_results = [
            result for result in results
            if result.get('metadata', {}).get('user_id') == user_id
        ]
        
        db.session.commit()  # Save credit usage
        
        return jsonify({
            'results': user_results,
            'query': query,
            'count': len(user_results),
            'credits_used': 1,
            'remaining_credits': user.credits
        })
        
    except Exception as e:
        # Rollback credit usage on error
        user.add_credits(1)
        db.session.commit()
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

# AI Service Status Routes
@user_bp.route('/ai/status', methods=['GET'])
def get_ai_status():
    """Get AI service status"""
    return jsonify(jarvis_ai.get_service_status())

@user_bp.route('/ai/proactive', methods=['GET'])
def get_proactive_suggestions():
    """Get proactive suggestions from Jarvis"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # This would typically integrate with workspace summary
    # For now, return a sample suggestion
    mock_summary = {
        'unread_emails': 15,
        'upcoming_events': 3,
        'recent_files': 25
    }
    
    suggestion = jarvis_ai.generate_proactive_suggestion(mock_summary)
    
    return jsonify({
        'suggestion': suggestion,
        'timestamp': datetime.utcnow().isoformat()
    })

# Health check route
@user_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'jarvis-backend',
        'ai_service': jarvis_ai.gemini_available,
        'vector_db': vector_service.get_collection_stats(),
        'timestamp': datetime.utcnow().isoformat()
    })

