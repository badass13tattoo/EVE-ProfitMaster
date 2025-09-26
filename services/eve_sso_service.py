"""
EVE SSO Authentication Service
Handles EVE Online Single Sign-On authentication and token management
"""

import os
import base64
import requests
import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class EVEToken:
    access_token: str
    refresh_token: str
    expires_at: datetime.datetime
    scopes: List[str]


class EVESSOService:
    """Service for handling EVE SSO authentication and token management"""
    
    def __init__(self, client_id: str, secret_key: str):
        self.client_id = client_id
        self.secret_key = secret_key
        self.auth_string = base64.b64encode(f"{client_id}:{secret_key}".encode()).decode()
        self.base_url = "https://login.eveonline.com"
    
    def get_authorization_url(self, redirect_uri: str, scopes: List[str], state: str = None) -> str:
        """Generate EVE SSO authorization URL"""
        if not state:
            import secrets
            state = secrets.token_urlsafe(16)
        
        params = {
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'client_id': self.client_id,
            'scope': ' '.join(scopes),
            'state': state
        }
        
        url = f"{self.base_url}/v2/oauth/authorize"
        return requests.Request('GET', url, params=params).prepare().url
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Optional[EVEToken]:
        """Exchange authorization code for access token"""
        try:
            url = f"{self.base_url}/v2/oauth/token"
            headers = {
                'Authorization': f'Basic {self.auth_string}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri
            }
            
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=token_data.get('expires_in', 1200))
            
            return EVEToken(
                access_token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                expires_at=expires_at,
                scopes=token_data.get('scope', '').split(' ')
            )
        except Exception as e:
            print(f"Error exchanging code for token: {e}")
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[EVEToken]:
        """Refresh access token using refresh token"""
        try:
            url = f"{self.base_url}/v2/oauth/token"
            headers = {
                'Authorization': f'Basic {self.auth_string}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=token_data.get('expires_in', 1200))
            
            return EVEToken(
                access_token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token', refresh_token),
                expires_at=expires_at,
                scopes=token_data.get('scope', '').split(' ')
            )
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return None
    
    def verify_token(self, access_token: str) -> Optional[Dict]:
        """Verify access token and get character information"""
        try:
            url = f"{self.base_url}/oauth/verify"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error verifying token: {e}")
            return None
