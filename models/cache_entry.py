"""
Cache Entry Model
Database model for cache entries
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


class CacheEntry:
    """Cache entry model for caching data"""
    
    def __init__(self, db: SQLAlchemy):
        self.db = db
        self.model = self._create_model()
    
    def _create_model(self):
        class CacheEntryModel(self.db.Model):
            __tablename__ = 'cache_entries'
            
            id = self.db.Column(self.db.Integer, primary_key=True)
            cache_key = self.db.Column(self.db.String(255), unique=True, nullable=False, index=True)
            cache_data = self.db.Column(self.db.Text, nullable=False)  # JSON string
            expires_at = self.db.Column(self.db.DateTime, nullable=False, index=True)
            created_at = self.db.Column(self.db.DateTime, default=datetime.utcnow)
            
            def __repr__(self):
                return f'<CacheEntry {self.cache_key}>'
            
            def to_dict(self):
                return {
                    'id': self.id,
                    'cache_key': self.cache_key,
                    'expires_at': self.expires_at.isoformat() if self.expires_at else None,
                    'created_at': self.created_at.isoformat() if self.created_at else None
                }
        
        return CacheEntryModel
