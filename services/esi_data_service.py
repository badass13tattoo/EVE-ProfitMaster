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
        """Get character industry jobs from ESI with detailed information"""
        cache_key = f"jobs_{character_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/characters/{character_id}/industry/jobs/"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            jobs_data = response.json()
            
            # Обогащаем данные дополнительной информацией
            enriched_jobs = []
            for job in jobs_data:
                enriched_job = self._enrich_job_data(job, character_id)
                enriched_jobs.append(enriched_job)
            
            self.cache_service.set(cache_key, enriched_jobs, 300)  # Cache for 5 minutes
            return enriched_jobs
        except Exception as e:
            print(f"Error getting character jobs: {e}")
            return []
    
    def _enrich_job_data(self, job: Dict, character_id: int) -> Dict:
        """Enrich job data with additional information"""
        enriched_job = job.copy()
        
        # Добавляем информацию о продукте
        if job.get('product_type_id'):
            product_info = self.get_type_info(job['product_type_id'])
            enriched_job['product_name'] = product_info.get('name', f'Type {job["product_type_id"]}')
            enriched_job['product_volume'] = product_info.get('volume', 0)
            enriched_job['product_category'] = product_info.get('category_id', 0)
            enriched_job['product_group'] = product_info.get('group_id', 0)
        
        # Добавляем информацию о локации
        if job.get('location_id'):
            location_info = self.get_location_info(job['location_id'])
            enriched_job['location_name'] = location_info.get('name', f'Location {job["location_id"]}')
            enriched_job['location_type'] = location_info.get('type', 'unknown')
            enriched_job['location_security'] = location_info.get('security_status', 0.0)
        
        # Добавляем информацию о станции/структуре
        if job.get('station_id'):
            station_info = self.get_station_info(job['station_id'])
            enriched_job['station_name'] = station_info.get('name', f'Station {job["station_id"]}')
            enriched_job['station_type'] = station_info.get('type', 'unknown')
        
        # Добавляем информацию о солнечной системе
        if job.get('system_id'):
            system_info = self.get_system_info(job['system_id'])
            enriched_job['system_name'] = system_info.get('name', f'System {job["system_id"]}')
            enriched_job['system_security'] = system_info.get('security_status', 0.0)
        
        # Добавляем информацию о корпорации
        if job.get('corporation_id'):
            corp_info = self.get_corporation_info(job['corporation_id'])
            enriched_job['corporation_name'] = corp_info.get('name', f'Corp {job["corporation_id"]}')
        
        # Добавляем расчетные поля
        enriched_job['character_id'] = character_id
        enriched_job['duration_hours'] = self._calculate_job_duration(job)
        enriched_job['time_remaining_hours'] = self._calculate_time_remaining(job)
        enriched_job['is_completed'] = job.get('status') != 'active'
        enriched_job['is_paused'] = job.get('status') == 'paused'
        enriched_job['progress_percentage'] = self._calculate_progress_percentage(job)
        
        return enriched_job
    
    def _calculate_job_duration(self, job: Dict) -> float:
        """Calculate job duration in hours"""
        try:
            start_date = datetime.datetime.fromisoformat(job.get('start_date', '').replace('Z', '+00:00'))
            end_date = datetime.datetime.fromisoformat(job.get('end_date', '').replace('Z', '+00:00'))
            duration = (end_date - start_date).total_seconds() / 3600
            return round(duration, 2)
        except:
            return 0.0
    
    def _calculate_time_remaining(self, job: Dict) -> float:
        """Calculate time remaining in hours"""
        try:
            if job.get('status') != 'active':
                return 0.0
            
            end_date = datetime.datetime.fromisoformat(job.get('end_date', '').replace('Z', '+00:00'))
            now = datetime.datetime.now(datetime.timezone.utc)
            remaining = (end_date - now).total_seconds() / 3600
            return max(0.0, round(remaining, 2))
        except:
            return 0.0
    
    def _calculate_progress_percentage(self, job: Dict) -> float:
        """Calculate job progress percentage"""
        try:
            if job.get('status') != 'active':
                return 100.0
            
            start_date = datetime.datetime.fromisoformat(job.get('start_date', '').replace('Z', '+00:00'))
            end_date = datetime.datetime.fromisoformat(job.get('end_date', '').replace('Z', '+00:00'))
            now = datetime.datetime.now(datetime.timezone.utc)
            
            total_duration = (end_date - start_date).total_seconds()
            elapsed = (now - start_date).total_seconds()
            
            if total_duration <= 0:
                return 0.0
            
            progress = min(100.0, max(0.0, (elapsed / total_duration) * 100))
            return round(progress, 1)
        except:
            return 0.0
    
    def get_station_info(self, station_id: int) -> Dict:
        """Get station information"""
        cache_key = f"station_{station_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/universe/stations/{station_id}/"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 86400)  # Cache for 24 hours
            return data
        except Exception as e:
            print(f"Error getting station info: {e}")
            return {'station_id': station_id, 'name': f'Station {station_id}'}
    
    def get_corporation_info(self, corporation_id: int) -> Dict:
        """Get corporation information"""
        cache_key = f"corporation_{corporation_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/corporations/{corporation_id}/"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 86400)  # Cache for 24 hours
            return data
        except Exception as e:
            print(f"Error getting corporation info: {e}")
            return {'corporation_id': corporation_id, 'name': f'Corp {corporation_id}'}

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
