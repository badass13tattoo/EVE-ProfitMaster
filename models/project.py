"""
Project Model
Database model for production projects
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Optional, Dict, Any


class Project:
    """Project model for production projects"""
    
    def __init__(self, db: SQLAlchemy):
        self.db = db
        self.model = self._create_model()
    
    def _create_model(self):
        class ProjectModel(self.db.Model):
            __tablename__ = 'projects'
            
            id = self.db.Column(self.db.Integer, primary_key=True)
            user_id = self.db.Column(self.db.Integer, self.db.ForeignKey('users.id'), nullable=False)
            name = self.db.Column(self.db.String(255), nullable=False)
            description = self.db.Column(self.db.Text, nullable=True)
            target_item_id = self.db.Column(self.db.Integer, nullable=False)
            target_item_name = self.db.Column(self.db.String(255), nullable=False)
            target_quantity = self.db.Column(self.db.Integer, default=1)
            project_data = self.db.Column(self.db.Text, nullable=False)  # JSON string of project structure
            created_at = self.db.Column(self.db.DateTime, default=datetime.utcnow)
            updated_at = self.db.Column(self.db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            is_active = self.db.Column(self.db.Boolean, default=True)
            
            def __repr__(self):
                return f'<Project {self.name}>'
            
            def to_dict(self):
                import json
                return {
                    'id': self.id,
                    'user_id': self.user_id,
                    'name': self.name,
                    'description': self.description,
                    'target_item_id': self.target_item_id,
                    'target_item_name': self.target_item_name,
                    'target_quantity': self.target_quantity,
                    'project_data': json.loads(self.project_data) if self.project_data else {},
                    'created_at': self.created_at.isoformat() if self.created_at else None,
                    'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                    'is_active': self.is_active
                }
        
        return ProjectModel
