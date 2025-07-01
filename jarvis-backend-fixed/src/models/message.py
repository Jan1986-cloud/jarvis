from datetime import datetime
import uuid

from extensions import db

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(50), nullable=False)  # 'user' or 'jarvis'
    credits_used = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'content': self.content,
            'sender': self.sender,
            'credits_used': self.credits_used,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

