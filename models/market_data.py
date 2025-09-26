"""
Market Data Model
Database model for market data
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


class MarketData:
    """Market data model for storing market prices"""
    
    def __init__(self, db: SQLAlchemy):
        self.db = db
        self.model = self._create_model()
    
    def _create_model(self):
        class MarketDataModel(self.db.Model):
            __tablename__ = 'market_data'
            
            id = self.db.Column(self.db.Integer, primary_key=True)
            type_id = self.db.Column(self.db.Integer, nullable=False, index=True)
            region_id = self.db.Column(self.db.Integer, nullable=False, index=True)
            buy_price = self.db.Column(self.db.Float, nullable=True)
            sell_price = self.db.Column(self.db.Float, nullable=True)
            volume = self.db.Column(self.db.BigInteger, nullable=True)
            updated_at = self.db.Column(self.db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            
            # Composite index for type_id and region_id
            __table_args__ = (
                self.db.Index('ix_market_data_type_region', 'type_id', 'region_id'),
            )
            
            def __repr__(self):
                return f'<MarketData {self.type_id} in {self.region_id}>'
            
            def to_dict(self):
                return {
                    'id': self.id,
                    'type_id': self.type_id,
                    'region_id': self.region_id,
                    'buy_price': self.buy_price,
                    'sell_price': self.sell_price,
                    'volume': self.volume,
                    'updated_at': self.updated_at.isoformat() if self.updated_at else None
                }
        
        return MarketDataModel
