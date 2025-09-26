"""
EVE ESI Data Service
Handles data collection from EVE ESI API with caching
"""

import requests
import time
from typing import Dict, List, Optional, Any
from .cache_service import CacheService


class ESIDataService:
    """Service for collecting data from EVE ESI API"""
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
        self.base_url = "https://esi.evetech.net/latest"
    
    def get_character_skills(self, character_id: int, access_token: str) -> List[Dict]:
        """Get character skills from ESI"""
        cache_key = f"skills_{character_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/characters/{character_id}/skills/"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 3600)  # Cache for 1 hour
            return data.get('skills', [])
        except Exception as e:
            print(f"Error getting character skills: {e}")
            return []
    
    def get_character_jobs(self, character_id: int, access_token: str) -> List[Dict]:
        """Get character industry jobs from ESI"""
        cache_key = f"jobs_{character_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/characters/{character_id}/industry/jobs/"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 300)  # Cache for 5 minutes
            return data
        except Exception as e:
            print(f"Error getting character jobs: {e}")
            return []
    
    def get_character_planets(self, character_id: int, access_token: str) -> List[Dict]:
        """Get character planets from ESI"""
        cache_key = f"planets_{character_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/characters/{character_id}/planets/"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 1800)  # Cache for 30 minutes
            return data
        except Exception as e:
            print(f"Error getting character planets: {e}")
            return []
    
    def get_character_blueprints(self, character_id: int, access_token: str) -> List[Dict]:
        """Get character blueprints from ESI"""
        cache_key = f"blueprints_{character_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/characters/{character_id}/blueprints/"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 3600)  # Cache for 1 hour
            return data
        except Exception as e:
            print(f"Error getting character blueprints: {e}")
            return []
    
    def get_character_assets(self, character_id: int, access_token: str) -> List[Dict]:
        """Get character assets from ESI"""
        cache_key = f"assets_{character_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/characters/{character_id}/assets/"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 1800)  # Cache for 30 minutes
            return data
        except Exception as e:
            print(f"Error getting character assets: {e}")
            return []
    
    def get_type_info(self, type_id: int) -> Dict:
        """Get type information from ESI"""
        cache_key = f"type_{type_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/universe/types/{type_id}/"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 86400)  # Cache for 24 hours
            return data
        except Exception as e:
            print(f"Error getting type info: {e}")
            return {'type_id': type_id, 'name': f'Type {type_id}'}
    
    def get_location_info(self, location_id: int) -> Dict:
        """Get location information from ESI"""
        cache_key = f"location_{location_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            if location_id > 1000000000000:  # Structure
                url = f"{self.base_url}/universe/structures/{location_id}/"
            else:  # Station
                url = f"{self.base_url}/universe/stations/{location_id}/"
            
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 86400)  # Cache for 24 hours
            return data
        except Exception as e:
            print(f"Error getting location info: {e}")
            return {'location_id': location_id, 'name': f'Location {location_id}'}
    
    def get_planet_details(self, character_id: int, planet_id: int, access_token: str) -> Dict:
        """Get detailed planet information from ESI"""
        cache_key = f"planet_details_{character_id}_{planet_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/characters/{character_id}/planets/{planet_id}/"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 1800)  # Cache for 30 minutes
            return data
        except Exception as e:
            print(f"Error getting planet details: {e}")
            return {}
    
    def get_system_info(self, system_id: int) -> Dict:
        """Get solar system information from ESI"""
        cache_key = f"system_{system_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/universe/systems/{system_id}/"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 86400)  # Cache for 24 hours
            return data
        except Exception as e:
            print(f"Error getting system info: {e}")
            return {'system_id': system_id, 'name': f'System {system_id}'}
    
    def get_planet_info(self, planet_id: int) -> Dict:
        """Get planet information from ESI"""
        cache_key = f"planet_info_{planet_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/universe/planets/{planet_id}/"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 86400)  # Cache for 24 hours
            return data
        except Exception as e:
            print(f"Error getting planet info: {e}")
            return {'planet_id': planet_id, 'name': f'Planet {planet_id}'}
