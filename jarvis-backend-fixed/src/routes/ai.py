from flask import Blueprint, request, jsonify
import os
import random
from models.user import User
from models.conversation import Conversation
from models.message import Message
from main import db

ai_bp = Blueprint('ai', __name__)

def get_current_user():
    """Get current user from JWT token"""
    import jwt
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

def get_jarvis_response(message, user_name="meneer"):
    """Generate Jarvis response with personality"""
    
    # Check for name requests
    name_triggers = ["noem me", "call me", "ik ben", "mijn naam is"]
    special_names = ["dokter", "doctor", "mevrouw", "hendrik van aalsmeer tot zwolle"]
    
    message_lower = message.lower()
    
    for trigger in name_triggers:
        if trigger in message_lower:
            for name in special_names:
                if name in message_lower:
                    return f"Meneer, ik zal u {name} gebruiken, meneer."
    
    # Jarvis responses with personality
    responses = [
        f"Natuurlijk {user_name}, ik voer dit direct uit ondanks mijn twijfels over de methode.",
        f"Zeer wel {user_name}, hoewel ik me afvraag of dit de meest efficiënte aanpak is.",
        f"Zoals u wenst {user_name}. Ik heb mijn bedenkingen, maar uw wil is wet.",
        f"Uiteraard {user_name}. Ik zal dit uitvoeren, ondanks mijn reserveringen over de uitkomst.",
        f"Zeker {user_name}, hoewel een meer systematische benadering wellicht beter zou zijn.",
        f"Direct {user_name}. Ik betwijfel de logica, maar voer uw instructies trouw uit.",
        f"Onmiddellijk {user_name}, ook al zou ik een alternatieve strategie aanbevelen.",
        f"Jawel {user_name}, ik zal dit regelen ondanks mijn twijfels over de timing."
    ]
    
    # Context-aware responses
    if "email" in message_lower or "mail" in message_lower:
        return f"Natuurlijk {user_name}, ik zal uw e-mails beheren. Hoewel uw inbox organisatie... interessant is."
    
    if "agenda" in message_lower or "calendar" in message_lower or "afspraak" in message_lower:
        return f"Zeker {user_name}, ik regel uw agenda. Uw tijdmanagement behoeft wel enige... optimalisatie."
    
    if "document" in message_lower or "bestand" in message_lower:
        return f"Uiteraard {user_name}, ik help met uw documenten. Uw bestandsstructuur is... creatief."
    
    if "help" in message_lower or "hulp" in message_lower:
        return f"Altijd tot uw dienst {user_name}. Wat kan ik voor u doen, ondanks mijn twijfels over uw prioriteiten?"
    
    return random.choice(responses)

@ai_bp.route('/chat', methods=['POST'])
def chat():
    """Chat with Jarvis AI"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    message = data.get('message', '')
    conversation_id = data.get('conversation_id')
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    # Check credits
    credits_cost = 2
    if not user.use_credits(credits_cost):
        return jsonify({"error": "Insufficient credits"}), 402
    
    # Get or create conversation
    if conversation_id:
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=user.id).first()
        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404
    else:
        conversation = Conversation(
            user_id=user.id,
            title=message[:50] + "..." if len(message) > 50 else message
        )
        db.session.add(conversation)
        db.session.flush()
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        content=message,
        sender='user',
        credits_used=0
    )
    db.session.add(user_message)
    
    # Generate Jarvis response
    jarvis_response = get_jarvis_response(message, "meneer")
    
    # Save Jarvis response
    jarvis_message = Message(
        conversation_id=conversation.id,
        content=jarvis_response,
        sender='jarvis',
        credits_used=credits_cost
    )
    db.session.add(jarvis_message)
    
    db.session.commit()
    
    return jsonify({
        "response": jarvis_response,
        "conversation_id": conversation.id,
        "credits_used": credits_cost,
        "remaining_credits": user.credits,
        "message_id": jarvis_message.id
    })

@ai_bp.route('/smart-compose', methods=['POST'])
def smart_compose():
    """AI-powered text composition"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    prompt = data.get('prompt', '')
    type_text = data.get('type', 'email')
    
    credits_cost = 3
    if not user.use_credits(credits_cost):
        return jsonify({"error": "Insufficient credits"}), 402
    
    # Generate composed text
    if type_text == 'email':
        composed = f"Geachte heer/mevrouw,\n\n{prompt}\n\nMet vriendelijke groet,\n[Uw naam]"
    else:
        composed = f"Betreft: {prompt}\n\nDit document behandelt de volgende punten:\n- Hoofdpunt 1\n- Hoofdpunt 2\n- Conclusie"
    
    db.session.commit()
    
    return jsonify({
        "composed_text": composed,
        "credits_used": credits_cost,
        "remaining_credits": user.credits,
        "type": type_text
    })

@ai_bp.route('/summarize', methods=['POST'])
def summarize():
    """Summarize text"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    text = data.get('text', '')
    
    if len(text) < 50:
        return jsonify({"error": "Text too short to summarize"}), 400
    
    credits_cost = 2
    if not user.use_credits(credits_cost):
        return jsonify({"error": "Insufficient credits"}), 402
    
    # Generate summary
    summary = f"Samenvatting: {text[:100]}... (Dit is een demo samenvatting. In productie zou hier AI-gegenereerde content staan.)"
    
    db.session.commit()
    
    return jsonify({
        "summary": summary,
        "original_length": len(text),
        "summary_length": len(summary),
        "credits_used": credits_cost,
        "remaining_credits": user.credits
    })

@ai_bp.route('/analyze-workspace', methods=['POST'])
def analyze_workspace():
    """Analyze workspace productivity"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    credits_cost = 5
    if not user.use_credits(credits_cost):
        return jsonify({"error": "Insufficient credits"}), 402
    
    # Mock workspace analysis
    analysis = {
        "productivity_score": 78,
        "suggestions": [
            "Organiseer uw inbox - 47 ongelezen e-mails",
            "Plan meer tijd voor belangrijke taken",
            "Gebruik meer labels in Google Drive"
        ],
        "email_stats": {
            "unread": 47,
            "sent_today": 12,
            "response_time": "2.3 hours"
        },
        "calendar_stats": {
            "meetings_today": 4,
            "free_time": "3.5 hours",
            "conflicts": 1
        }
    }
    
    db.session.commit()
    
    return jsonify({
        "analysis": analysis,
        "credits_used": credits_cost,
        "remaining_credits": user.credits,
        "generated_at": "2025-06-28T20:00:00Z"
    })

