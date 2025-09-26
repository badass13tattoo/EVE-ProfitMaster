"""
User Model
Database model for user/character data
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Optional


class User:
    """User model for EVE characters"""
    
    def __init__(self, db: SQLAlchemy):
        self.db = db
        self.model = self._create_model()
    
    def _create_model(self):
        class UserModel(self.db.Model):
            __tablename__ = 'users'
            
            id = self.db.Column(self.db.Integer, primary_key=True)
            character_id = self.db.Column(self.db.BigInteger, unique=True, nullable=False, index=True)
            character_name = self.db.Column(self.db.String(255), nullable=False)
            corporation_id = self.db.Column(self.db.BigInteger, nullable=True)
            alliance_id = self.db.Column(self.db.BigInteger, nullable=True)
            access_token = self.db.Column(self.db.Text, nullable=False)
            refresh_token = self.db.Column(self.db.Text, nullable=False)
            token_expires_at = self.db.Column(self.db.DateTime, nullable=True)
            scopes = self.db.Column(self.db.Text, nullable=True)  # JSON string of scopes
            created_at = self.db.Column(self.db.DateTime, default=datetime.utcnow)
            updated_at = self.db.Column(self.db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            is_active = self.db.Column(self.db.Boolean, default=True)
            
            def __repr__(self):
                return f'<User {self.character_name}>'
            
            def to_dict(self):
                return {
                    'id': self.id,
                    'character_id': self.character_id,
                    'character_name': self.character_name,
                    'corporation_id': self.corporation_id,
                    'alliance_id': self.alliance_id,
                    'is_active': self.is_active,
                    'created_at': self.created_at.isoformat() if self.created_at else None,
                    'updated_at': self.updated_at.isoformat() if self.updated_at else None
                }
        
        return UserModel
