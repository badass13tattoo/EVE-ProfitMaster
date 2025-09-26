"""
Character Controller
Handles character-related operations and data retrieval
"""

from flask import request, jsonify
from typing import Dict, List
from services.esi_data_service import ESIDataService
from services.business_logic_service import BusinessLogicService
from controllers.auth_controller import AuthController


class CharacterController:
    """Controller for character operations"""
    
    def __init__(self, esi_service: ESIDataService, business_logic_service: BusinessLogicService, auth_controller: AuthController):
        self.esi_service = esi_service
        self.business_logic_service = business_logic_service
        self.auth_controller = auth_controller
    
    def get_character_details(self, user) -> Dict:
        """Get detailed character information including activity limits"""
        try:
            # Get skills and calculate limits
            skills = self.esi_service.get_character_skills(user.character_id, user.access_token)
            limits = self.business_logic_service.calculate_activity_limits(skills)
            
            # Get jobs to calculate used slots
            jobs = self.esi_service.get_character_jobs(user.character_id, user.access_token)
            job_usage = self.business_logic_service.calculate_job_usage(jobs)
            
            # Update limits with actual usage
            limits['manufacturing']['used'] = job_usage['manufacturing']
            limits['research']['used'] = job_usage['research']
            limits['reactions']['used'] = job_usage['reactions']
            
            # Get planets
            planets = self.esi_service.get_character_planets(user.character_id, user.access_token)
            limits['planets']['used'] = self.business_logic_service.calculate_planet_usage(planets)
            
            return limits
        except Exception as e:
            print(f"Error getting character details: {e}")
            return {'error': f'Internal server error: {str(e)}'}, 500
    
    def get_character_jobs(self, user) -> Dict:
        """Get character jobs data"""
        try:
            jobs = self.esi_service.get_character_jobs(user.character_id, user.access_token)
            processed_jobs = self.business_logic_service.process_jobs_data(jobs, user.character_id)
            
            # Convert to dict format expected by frontend
            jobs_dict = {
                str(user.character_id): processed_jobs
            }
            
            return jobs_dict
        except Exception as e:
            print(f"Error getting character jobs: {e}")
            return {'error': f'Internal server error: {str(e)}'}, 500
    
    def get_character_planets(self, user) -> List[Dict]:
        """Get character planets data"""
        try:
            planets = self.esi_service.get_character_planets(user.character_id, user.access_token)
            processed_planets = self.business_logic_service.process_planets_data(planets, user.character_id, user.access_token)
            return processed_planets
        except Exception as e:
            print(f"Error getting character planets: {e}")
            return {'error': f'Internal server error: {str(e)}'}, 500
    
    def get_character_skills(self, user) -> Dict:
        """Get character skills"""
        try:
            skills = self.esi_service.get_character_skills(user.character_id, user.access_token)
            return {'skills': skills}
        except Exception as e:
            print(f"Error getting character skills: {e}")
            return {'error': f'Internal server error: {str(e)}'}, 500
    
    def get_character_blueprints(self, user) -> List[Dict]:
        """Get character blueprints"""
        try:
            blueprints = self.esi_service.get_character_blueprints(user.character_id, user.access_token)
            return blueprints
        except Exception as e:
            print(f"Error getting character blueprints: {e}")
            return {'error': f'Internal server error: {str(e)}'}, 500
    
    def get_character_assets(self, user) -> List[Dict]:
        """Get character assets"""
        try:
            assets = self.esi_service.get_character_assets(user.character_id, user.access_token)
            return assets
        except Exception as e:
            print(f"Error getting character assets: {e}")
            return {'error': f'Internal server error: {str(e)}'}, 500
    
    def get_character_portrait(self, character_id: int) -> Dict:
        """Get character portrait URL"""
        return {
            'portrait_url': f'https://images.evetech.net/characters/{character_id}/portrait?size=128'
        }
    
    def get_all_jobs(self) -> Dict:
        """Get all jobs for all characters (legacy endpoint)"""
        try:
            from models.user import User
            users = User.query.filter_by(is_active=True).all()
            all_jobs = {}
            
            for user in users:
                if not self.auth_controller._refresh_user_token(user):
                    continue
                
                jobs = self.esi_service.get_character_jobs(user.character_id, user.access_token)
                processed_jobs = self.business_logic_service.process_jobs_data(jobs, user.character_id)
                
                all_jobs[str(user.character_id)] = processed_jobs
            
            return all_jobs
        except Exception as e:
            print(f"Error getting all jobs: {e}")
            return {'error': f'Internal server error: {str(e)}'}, 500
