from flask import Blueprint, jsonify, request
from src.models.user import User, db
from src.services.jarvis_ai import jarvis_ai
from src.services.vector_db import vector_service
from src.services.google_api import google_service
from datetime import datetime
import json

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai/chat', methods=['POST'])
def ai_chat():
    """Direct AI chat endpoint"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get_or_404(user_id)
    data = request.json
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'Message required'}), 400
    
    # Generate AI response
    ai_result = jarvis_ai.generate_response(
        user_message=message,
        conversation_history=data.get('history', []),
        user_id=user_id
    )
    
    # Check and use credits
    if not user.use_credits(ai_result['credits_used']):
        return jsonify({'error': 'Insufficient credits'}), 402
    
    db.session.commit()
    
    return jsonify({
        'response': ai_result['response'],
        'type': ai_result['type'],
        'context_used': ai_result.get('context_used', 0),
        'credits_used': ai_result['credits_used'],
        'remaining_credits': user.credits
    })

@ai_bp.route('/ai/analyze-workspace', methods=['POST'])
def analyze_workspace():
    """Analyze workspace and provide insights"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get_or_404(user_id)
    
    # Check credits (5 credits for comprehensive analysis)
    if not user.use_credits(5):
        return jsonify({'error': 'Insufficient credits'}), 402
    
    try:
        # This would integrate with actual workspace data
        # For now, provide mock analysis
        analysis = {
            'email_summary': 'Meneer, u heeft 12 ongelezen e-mails, waarvan 3 urgent lijken.',
            'calendar_summary': 'Meneer, u heeft 4 vergaderingen vandaag, hoewel ik me afvraag of ze allemaal nodig zijn.',
            'drive_summary': 'Meneer, uw Drive bevat 247 bestanden, waarvan sommige wellicht kunnen worden opgeruimd.',
            'productivity_score': 7.5,
            'suggestions': [
                'Overweeg e-mail batching om efficiënter te werken',
                'Uw agenda lijkt overvol - misschien tijd voor prioritering',
                'Enkele bestanden zijn al maanden niet geopend'
            ]
        }
        
        # Generate Jarvis commentary
        commentary = jarvis_ai.generate_proactive_suggestion({
            'unread_emails': 12,
            'upcoming_events': 4,
            'recent_files': 247
        })
        
        db.session.commit()
        
        return jsonify({
            'analysis': analysis,
            'jarvis_commentary': commentary,
            'analyzed_at': datetime.utcnow().isoformat(),
            'credits_used': 5,
            'remaining_credits': user.credits
        })
        
    except Exception as e:
        # Rollback credits on error
        user.add_credits(5)
        db.session.commit()
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@ai_bp.route('/ai/smart-compose', methods=['POST'])
def smart_compose():
    """Smart compose for emails and documents"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get_or_404(user_id)
    data = request.json
    
    compose_type = data.get('type', 'email')  # email, document, response
    context = data.get('context', '')
    tone = data.get('tone', 'professional')
    length = data.get('length', 'medium')
    
    # Check credits
    credits_needed = 3 if compose_type == 'email' else 5
    if not user.use_credits(credits_needed):
        return jsonify({'error': 'Insufficient credits'}), 402
    
    try:
        # Generate smart compose content
        if jarvis_ai.gemini_available:
            prompt = f"""Schrijf een {compose_type} met de volgende specificaties:
            
Context: {context}
Toon: {tone}
Lengte: {length}

Maak het professioneel maar met een subtiele Jarvis-touch (licht sarcasme waar gepast).
"""
            
            response = jarvis_ai.model.generate_content(prompt)
            composed_text = response.text
        else:
            composed_text = f"Meneer, hier is een concept {compose_type} gebaseerd op uw verzoek, hoewel ik me afvraag of u niet zelf sneller zou zijn geweest."
        
        db.session.commit()
        
        return jsonify({
            'composed_text': composed_text,
            'type': compose_type,
            'tone': tone,
            'length': length,
            'credits_used': credits_needed,
            'remaining_credits': user.credits
        })
        
    except Exception as e:
        # Rollback credits on error
        user.add_credits(credits_needed)
        db.session.commit()
        return jsonify({'error': f'Compose failed: {str(e)}'}), 500

@ai_bp.route('/ai/summarize', methods=['POST'])
def summarize_content():
    """Summarize documents or conversations"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get_or_404(user_id)
    data = request.json
    
    content = data.get('content', '').strip()
    summary_type = data.get('type', 'brief')  # brief, detailed, bullet_points
    
    if not content:
        return jsonify({'error': 'Content to summarize required'}), 400
    
    # Check credits
    if not user.use_credits(2):
        return jsonify({'error': 'Insufficient credits'}), 402
    
    try:
        if jarvis_ai.gemini_available:
            prompt = f"""Maak een {summary_type} samenvatting van de volgende tekst.
            Gebruik een professionele maar licht sarcastische Jarvis-toon.
            
Tekst om samen te vatten:
{content[:2000]}  # Limit content length

Samenvatting:"""
            
            response = jarvis_ai.model.generate_content(prompt)
            summary = response.text
        else:
            summary = "Meneer, hier is een samenvatting: de tekst bevat informatie die wellicht relevant is voor uw doeleinden."
        
        db.session.commit()
        
        return jsonify({
            'summary': summary,
            'summary_type': summary_type,
            'original_length': len(content),
            'summary_length': len(summary),
            'compression_ratio': round(len(summary) / len(content), 2),
            'credits_used': 2,
            'remaining_credits': user.credits
        })
        
    except Exception as e:
        # Rollback credits on error
        user.add_credits(2)
        db.session.commit()
        return jsonify({'error': f'Summarization failed: {str(e)}'}), 500

@ai_bp.route('/ai/translate', methods=['POST'])
def translate_text():
    """Translate text with Jarvis personality"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get_or_404(user_id)
    data = request.json
    
    text = data.get('text', '').strip()
    target_language = data.get('target_language', 'english')
    
    if not text:
        return jsonify({'error': 'Text to translate required'}), 400
    
    # Check credits
    if not user.use_credits(2):
        return jsonify({'error': 'Insufficient credits'}), 402
    
    try:
        if jarvis_ai.gemini_available:
            prompt = f"""Vertaal de volgende tekst naar {target_language}.
            Behoud de oorspronkelijke betekenis en toon.
            
Tekst om te vertalen:
{text}

Vertaling:"""
            
            response = jarvis_ai.model.generate_content(prompt)
            translation = response.text
        else:
            translation = f"Meneer, hier zou de vertaling naar {target_language} staan, als mijn vertaalsystemen beschikbaar waren."
        
        db.session.commit()
        
        return jsonify({
            'translation': translation,
            'source_language': 'auto-detected',
            'target_language': target_language,
            'original_text': text,
            'credits_used': 2,
            'remaining_credits': user.credits
        })
        
    except Exception as e:
        # Rollback credits on error
        user.add_credits(2)
        db.session.commit()
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

@ai_bp.route('/ai/explain', methods=['POST'])
def explain_concept():
    """Explain complex concepts in simple terms"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get_or_404(user_id)
    data = request.json
    
    concept = data.get('concept', '').strip()
    complexity_level = data.get('level', 'intermediate')  # beginner, intermediate, advanced
    
    if not concept:
        return jsonify({'error': 'Concept to explain required'}), 400
    
    # Check credits
    if not user.use_credits(3):
        return jsonify({'error': 'Insufficient credits'}), 402
    
    try:
        if jarvis_ai.gemini_available:
            prompt = f"""Leg het concept "{concept}" uit op {complexity_level} niveau.
            Gebruik een duidelijke, informatieve stijl met een subtiele Jarvis-touch.
            Maak het begrijpelijk maar niet neerbuigend.
            
Uitleg:"""
            
            response = jarvis_ai.model.generate_content(prompt)
            explanation = response.text
        else:
            explanation = f"Meneer, {concept} is een interessant onderwerp dat wellicht verdere studie verdient."
        
        db.session.commit()
        
        return jsonify({
            'explanation': explanation,
            'concept': concept,
            'complexity_level': complexity_level,
            'credits_used': 3,
            'remaining_credits': user.credits
        })
        
    except Exception as e:
        # Rollback credits on error
        user.add_credits(3)
        db.session.commit()
        return jsonify({'error': f'Explanation failed: {str(e)}'}), 500

@ai_bp.route('/ai/status', methods=['GET'])
def get_ai_status():
    """Get comprehensive AI service status"""
    return jsonify({
        'jarvis_ai': jarvis_ai.get_service_status(),
        'vector_db': vector_service.get_collection_stats(),
        'services_available': {
            'chat': True,
            'smart_compose': jarvis_ai.gemini_available,
            'summarize': jarvis_ai.gemini_available,
            'translate': jarvis_ai.gemini_available,
            'explain': jarvis_ai.gemini_available,
            'workspace_analysis': True
        },
        'timestamp': datetime.utcnow().isoformat()
    })

