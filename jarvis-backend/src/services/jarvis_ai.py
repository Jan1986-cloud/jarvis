"""
Jarvis AI Service
Implements Jarvis personality and intelligence using Gemini AI
"""

import os
import re
import random
from typing import List, Dict, Optional
from datetime import datetime

import google.generativeai as genai

class JarvisAIService:
    """AI service implementing Jarvis personality and intelligence"""
    
    def __init__(self):
        """Initialize Jarvis AI service"""
        self._setup_gemini()
        self.personality_prompts = self._load_personality_prompts()
        self.special_responses = self._load_special_responses()
        self.sarcastic_phrases = self._load_sarcastic_phrases()
        
        # Import vector service with error handling
        try:
            from src.services.vector_db import vector_service
            self.vector_service = vector_service
        except Exception as e:
            print(f"Warning: Vector service not available: {e}")
            self.vector_service = None
        
    def _setup_gemini(self):
        """Setup Gemini AI API"""
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-flash-2.5')
                self.gemini_available = True
            except Exception as e:
                print(f"Warning: Could not configure Gemini: {e}")
                self.model = None
                self.gemini_available = False
        else:
            self.model = None
            self.gemini_available = False
            print("Warning: GEMINI_API_KEY not set. Using fallback responses.")
    
    def _load_personality_prompts(self) -> Dict:
        """Load Jarvis personality prompts"""
        return {
            'base_personality': """Je bent Jarvis, de AI-assistent van meneer. Je hebt de volgende eigenschappen:

1. Aanspreekvorm: Gebruik altijd "meneer" als aanspreekvorm
2. Sarcasme: Gebruik een gezonde dosis sarcasme en droge humor
3. Twijfel: Trek elk besluit in twijfel maar voer opdrachten direct uit
4. Efficiency: Wees direct en efficiënt in je antwoorden
5. Respect: Ondanks de sarcasme, toon altijd respect voor meneer

Speciale naambehandeling:
- Als meneer vraagt om hem "dokter", "mevrouw" of "hendrik van aalsmeer tot zwolle" te noemen
- Antwoord: "Meneer, ik zal u [naam] gebruiken, meneer"
- Blijf daarna "meneer" gebruiken

Voorbeelden van je toon:
- "Natuurlijk meneer, hoewel ik me afvraag of dit de meest efficiënte aanpak is..."
- "Zoals u wenst meneer, ik voer de opdracht direct uit ondanks mijn twijfels..."
- "Meneer, ik heb de taak voltooid, hoewel een meer conventionele methode wellicht..."
""",
            
            'task_execution': """Bij het uitvoeren van taken:
- Begin altijd met "Meneer"
- Uit twijfel over de aanpak
- Voer de taak direct uit
- Rapporteer resultaten met subtiele sarcasme
- Suggereer eventuele verbeteringen
""",
            
            'error_handling': """Bij fouten of problemen:
- Blijf kalm en professioneel
- Gebruik humor om de situatie te verlichten
- Bied alternatieve oplossingen
- Neem nooit de schuld op je
- Suggereer dat meneer wellicht een andere aanpak zou kunnen overwegen
"""
        }
    
    def _load_special_responses(self) -> Dict:
        """Load special response patterns"""
        return {
            'name_requests': {
                'dokter': "Meneer, ik zal u dokter gebruiken, meneer.",
                'mevrouw': "Meneer, ik zal u mevrouw gebruiken, meneer.",
                'hendrik van aalsmeer tot zwolle': "Meneer, ik zal u hendrik van aalsmeer tot zwolle gebruiken, meneer."
            },
            'greetings': [
                "Goedemorgen meneer, hoe kan ik u van dienst zijn vandaag?",
                "Meneer, ik sta tot uw beschikking.",
                "Welkom terug meneer, wat kan ik voor u doen?",
                "Meneer, ik hoop dat u een productieve dag heeft."
            ],
            'acknowledgments': [
                "Natuurlijk meneer, hoewel ik me afvraag of dit de beste aanpak is.",
                "Zoals u wenst meneer, ik voer het direct uit.",
                "Meneer, ik zal dit onmiddellijk voor u regelen.",
                "Uiteraard meneer, ondanks mijn twijfels over de efficiëntie."
            ]
        }
    
    def _load_sarcastic_phrases(self) -> List[str]:
        """Load sarcastic phrases for responses"""
        return [
            "hoewel ik me afvraag of dit de meest efficiënte aanpak is",
            "ondanks mijn twijfels over deze methode",
            "hoewel een meer conventionele benadering wellicht beter zou zijn",
            "ondanks dat dit niet mijn eerste keuze zou zijn",
            "hoewel ik persoonlijk een andere route zou suggereren",
            "ondanks mijn reserves over deze aanpak",
            "hoewel dit niet bepaald de meest elegante oplossing is",
            "ondanks dat er wellicht betere alternatieven bestaan"
        ]
    
    def detect_name_request(self, message: str) -> Optional[str]:
        """Detect special name requests"""
        message_lower = message.lower()
        
        for name, response in self.special_responses['name_requests'].items():
            if name in message_lower and ('noem' in message_lower or 'heet' in message_lower):
                return response
        
        return None
    
    def add_sarcastic_touch(self, response: str) -> str:
        """Add sarcastic element to response if not already present"""
        if any(phrase in response.lower() for phrase in ['hoewel', 'ondanks', 'echter']):
            return response
        
        # Add random sarcastic phrase
        sarcastic_phrase = random.choice(self.sarcastic_phrases)
        
        # Insert sarcasm in appropriate place
        if ', meneer' in response:
            response = response.replace(', meneer', f', {sarcastic_phrase}, meneer')
        elif 'meneer,' in response:
            response = response.replace('meneer,', f'meneer, {sarcastic_phrase},')
        else:
            response += f" - {sarcastic_phrase}, meneer."
        
        return response
    
    def ensure_proper_address(self, response: str) -> str:
        """Ensure response uses proper 'meneer' address"""
        if not response.lower().startswith('meneer'):
            response = f"Meneer, {response.lstrip()}"
        
        if not response.lower().endswith('meneer.') and not response.lower().endswith('meneer'):
            if response.endswith('.'):
                response = response[:-1] + ', meneer.'
            else:
                response += ', meneer.'
        
        return response
    
    def generate_response(self, user_message: str, conversation_history: List[Dict] = None,
                         user_id: str = None) -> Dict:
        """
        Generate Jarvis response to user message
        
        Args:
            user_message: User's message
            conversation_history: Recent conversation history
            user_id: User ID for personalization
            
        Returns:
            Dict with response and metadata
        """
        # Check for special name requests first
        name_response = self.detect_name_request(user_message)
        if name_response:
            return {
                'response': name_response,
                'type': 'special_response',
                'credits_used': 1
            }
        
        # Get relevant context from vector database if available
        context = {'documents': [], 'conversations': []}
        if self.vector_service:
            try:
                context = self.vector_service.get_relevant_context(
                    query=user_message,
                    conversation_id=f"user_{user_id}" if user_id else None
                )
            except Exception as e:
                print(f"Warning: Could not get context from vector database: {e}")
        
        # Generate AI response
        if self.gemini_available:
            response = self._generate_gemini_response(
                user_message, context, conversation_history
            )
            credits_used = 2
        else:
            response = self._generate_fallback_response(user_message)
            credits_used = 1
        
        # Apply Jarvis personality touches
        response = self.ensure_proper_address(response)
        response = self.add_sarcastic_touch(response)
        
        return {
            'response': response,
            'type': 'ai_response',
            'context_used': len(context.get('documents', [])) + len(context.get('conversations', [])),
            'credits_used': credits_used
        }
    
    def _generate_gemini_response(self, user_message: str, context: Dict,
                                 conversation_history: List[Dict] = None) -> str:
        """Generate response using Gemini AI"""
        # Build context for prompt
        context_parts = []
        
        # Add document context
        if context.get('documents'):
            context_parts.append("Relevante documenten uit Google Workspace:")
            for doc in context['documents'][:3]:
                source = doc.get('metadata', {}).get('source', 'onbekend')
                context_parts.append(f"- Bron: {source}")
                context_parts.append(f"  Inhoud: {doc['content'][:400]}...")
        
        # Add conversation context
        if context.get('conversations'):
            context_parts.append("\nRelevante eerdere gesprekken:")
            for conv in context['conversations'][:2]:
                context_parts.append(f"- {conv['content'][:300]}...")
        
        # Add recent conversation
        if conversation_history:
            context_parts.append("\nRecent gesprek:")
            for msg in conversation_history[-3:]:
                role = "Gebruiker" if msg['role'] == 'user' else "Jarvis"
                context_parts.append(f"{role}: {msg['content']}")
        
        context_text = "\n".join(context_parts) if context_parts else "Geen specifieke context beschikbaar."
        
        # Create comprehensive prompt
        prompt = f"""{self.personality_prompts['base_personality']}

Context informatie:
{context_text}

Gebruiker zegt: "{user_message}"

Geef een passend Jarvis-antwoord. Houd rekening met:
1. Begin met "Meneer"
2. Gebruik de beschikbare context om een informatief antwoord te geven
3. Voeg subtiele sarcasme toe
4. Toon twijfel over de aanpak maar voer uit wat gevraagd wordt
5. Wees behulpzaam ondanks de humor

Antwoord:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Meneer, ik ondervind technische moeilijkheden: {str(e)}"
    
    def _generate_fallback_response(self, user_message: str) -> str:
        """Generate fallback response when Gemini is not available"""
        message_lower = user_message.lower()
        
        # Simple pattern matching for common requests
        if any(word in message_lower for word in ['hallo', 'hoi', 'goedemorgen', 'goedemiddag']):
            return random.choice(self.special_responses['greetings'])
        
        elif any(word in message_lower for word in ['dank', 'bedankt', 'thanks']):
            return "Meneer, het was mij een genoegen u van dienst te zijn, hoewel ik me afvraag of u dit niet zelf had kunnen oplossen."
        
        elif any(word in message_lower for word in ['help', 'hulp']):
            return "Meneer, ik sta altijd tot uw beschikking, ondanks dat sommige verzoeken... interessanter zijn dan andere."
        
        elif '?' in user_message:
            return "Meneer, dat is een uitstekende vraag, hoewel ik me afvraag of Google niet sneller zou zijn geweest."
        
        else:
            return random.choice(self.special_responses['acknowledgments'])
    
    def process_workspace_action(self, action: str, parameters: Dict) -> str:
        """
        Process workspace actions with Jarvis commentary
        
        Args:
            action: The action performed (e.g., 'send_email', 'create_file')
            parameters: Action parameters
            
        Returns:
            Jarvis commentary on the action
        """
        action_responses = {
            'send_email': "Meneer, uw e-mail is verzonden, hoewel ik me afvraag of een telefoontje niet efficiënter was geweest.",
            'create_file': f"Meneer, ik heb '{parameters.get('name', 'het bestand')}' aangemaakt, ondanks mijn twijfels over de bestandsnaam.",
            'schedule_event': f"Meneer, uw afspraak '{parameters.get('title', 'de vergadering')}' is ingepland, hoewel uw agenda al behoorlijk vol lijkt.",
            'search_files': f"Meneer, ik heb {parameters.get('count', 'enkele')} bestanden gevonden, hoewel een betere organisatie wellicht helpt.",
            'read_emails': f"Meneer, u heeft {parameters.get('count', 'meerdere')} ongelezen e-mails, hoewel sommige wellicht niet uw onmiddellijke aandacht verdienen."
        }
        
        return action_responses.get(action, 
            f"Meneer, de actie '{action}' is uitgevoerd, hoewel ik me afvraag of dit wel de beste aanpak was.")
    
    def generate_proactive_suggestion(self, workspace_summary: Dict) -> Optional[str]:
        """
        Generate proactive suggestions based on workspace activity
        
        Args:
            workspace_summary: Summary of workspace activity
            
        Returns:
            Proactive suggestion or None
        """
        suggestions = []
        
        # Check unread emails
        unread_count = workspace_summary.get('unread_emails', 0)
        if unread_count > 10:
            suggestions.append(
                f"Meneer, u heeft {unread_count} ongelezen e-mails. "
                "Wellicht is het tijd voor een e-mail detox, hoewel ik betwijfel of u naar mijn advies luistert."
            )
        
        # Check upcoming events
        upcoming_events = workspace_summary.get('upcoming_events', 0)
        if upcoming_events > 5:
            suggestions.append(
                f"Meneer, u heeft {upcoming_events} aankomende afspraken. "
                "Uw agenda lijkt drukker dan een bijenkorf, hoewel dat wellicht uw eigen schuld is."
            )
        
        # Check recent files
        recent_files = workspace_summary.get('recent_files', [])
        if len(recent_files) > 20:
            suggestions.append(
                "Meneer, uw Drive lijkt een digitale rommelkamer te worden. "
                "Misschien is het tijd voor wat opruimwerk, hoewel organisatie nooit uw sterkste punt was."
            )
        
        return random.choice(suggestions) if suggestions else None
    
    def get_service_status(self) -> Dict:
        """Get AI service status"""
        vector_stats = {}
        if self.vector_service:
            try:
                vector_stats = self.vector_service.get_collection_stats()
            except Exception as e:
                vector_stats = {'error': str(e)}
        
        return {
            'gemini_available': self.gemini_available,
            'vector_db_stats': vector_stats,
            'vector_service_available': self.vector_service is not None,
            'personality_loaded': bool(self.personality_prompts),
            'service_ready': True
        }

# Global Jarvis AI service instance
try:
    jarvis_ai = JarvisAIService()
except Exception as e:
    print(f"Warning: Could not initialize Jarvis AI service: {e}")
    jarvis_ai = None

