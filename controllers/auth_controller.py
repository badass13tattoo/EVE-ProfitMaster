"""
Authentication Controller
Handles EVE SSO authentication and user management
"""

from flask import request, session, redirect, jsonify
from typing import Dict, List, Optional
from services.eve_sso_service import EVESSOService
from models.user import User
from functools import wraps
import datetime


class AuthController:
    """Controller for authentication operations"""
    
    def __init__(self, eve_sso_service: EVESSOService, user_model, db):
        self.eve_sso_service = eve_sso_service
        self.user_model = user_model
        self.db = db
    
    def require_auth(self, f):
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            character_id = request.args.get('character_id') or request.view_args.get('character_id')
            if not character_id:
                return jsonify({'error': 'Character ID required'}), 400
            
            user = self.user_model.query.filter_by(character_id=character_id, is_active=True).first()
            if not user:
                return jsonify({'error': 'Character not found'}), 404
            
            if not self._refresh_user_token(user):
                return jsonify({'error': 'Token expired, please re-authenticate', 'requires_reauth': True}), 401
            
            return f(user, *args, **kwargs)
        return decorated_function
    
    def _refresh_user_token(self, user) -> bool:
        """Refresh user's access token"""
        try:
            new_token = self.eve_sso_service.refresh_token(user.refresh_token)
            if new_token:
                user.access_token = new_token.access_token
                user.refresh_token = new_token.refresh_token
                user.token_expires_at = new_token.expires_at
                user.scopes = new_token.scopes
                user.updated_at = datetime.utcnow()
                self.db.session.commit()
                return True
            else:
                user.is_active = False
                self.db.session.commit()
                return False
        except Exception as e:
            print(f"Error refreshing token for user {user.character_name}: {e}")
            return False
    
    def login(self, redirect_uri: str) -> str:
        """Initiate EVE SSO login"""
        scopes = [
            "publicData",
            "esi-calendar.respond_calendar_events.v1",
            "esi-skills.read_skills.v1",
            "esi-wallet.read_character_wallet.v1",
            "esi-assets.read_assets.v1",
            "esi-planets.manage_planets.v1",
            "esi-markets.structure_markets.v1",
            "esi-industry.read_character_jobs.v1",
            "esi-markets.read_character_orders.v1",
            "esi-characters.read_blueprints.v1"
        ]
        
        import secrets
        state = secrets.token_urlsafe(16)
        session['oauth_state'] = state
        
        auth_url = self.eve_sso_service.get_authorization_url(redirect_uri, scopes, state)
        return auth_url
    
    def callback(self, code: str, state: str, redirect_uri: str) -> Dict:
        """Handle EVE SSO callback"""
        if state != session.pop('oauth_state', None):
            return {'error': 'Invalid state parameter'}, 400
        
        if not code:
            return {'error': 'Authorization code not received'}, 400
        
        token = self.eve_sso_service.exchange_code_for_token(code, redirect_uri)
        if not token:
            return {'error': 'Failed to obtain token'}, 400
        
        # Verify token and get character info
        char_info = self.eve_sso_service.verify_token(token.access_token)
        if not char_info:
            return {'error': 'Failed to verify token'}, 400
        
        # Save or update user
        user = self.user_model.query.filter_by(character_id=char_info['CharacterID']).first()
        if user:
            user.access_token = token.access_token
            user.refresh_token = token.refresh_token
            user.token_expires_at = token.expires_at
            user.scopes = token.scopes
            user.updated_at = datetime.utcnow()
            user.is_active = True
        else:
            user = self.user_model(
                character_id=char_info['CharacterID'],
                character_name=char_info['CharacterName'],
                access_token=token.access_token,
                refresh_token=token.refresh_token,
                token_expires_at=token.expires_at,
                scopes=token.scopes
            )
            self.db.session.add(user)
        
        self.db.session.commit()
        
        return {'success': True, 'character_id': char_info['CharacterID']}
    
    def get_characters(self) -> List[Dict]:
        """Get list of authenticated characters"""
        users = self.user_model.query.filter_by(is_active=True).all()
        return [user.to_dict() for user in users]
    
    def remove_character(self, character_id: int) -> Dict:
        """Remove character from database"""
        try:
            user = self.user_model.query.filter_by(character_id=character_id).first()
            if user:
                user.is_active = False
                self.db.session.commit()
                return {'message': 'Character removed successfully'}
            else:
                return {'error': 'Character not found'}, 404
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500
    
    def reset_database(self) -> Dict:
        """Reset database (remove all users)"""
        try:
            self.user_model.query.update({'is_active': False})
            self.db.session.commit()
            return {'message': 'Database reset successfully'}
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500
