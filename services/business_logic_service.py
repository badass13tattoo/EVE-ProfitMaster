"""
Business Logic Service
Handles data processing, calculations, and business rules
"""

import datetime
from typing import Dict, List, Optional
from .esi_data_service import ESIDataService


class BusinessLogicService:
    """Service for business logic and data processing"""
    
    def __init__(self, esi_service: ESIDataService):
        self.esi_service = esi_service
    
    def calculate_activity_limits(self, skills: List[Dict]) -> Dict:
        """Calculate activity limits based on character skills"""
        def get_skill_level(skill_id: int) -> int:
            for skill in skills:
                if skill.get('skill_id') == skill_id:
                    return skill.get('active_skill_level', 0)
            return 0
        
        return {
            'manufacturing': {
                'total': 1 + get_skill_level(3385) + get_skill_level(3389),
                'used': 0  # Will be calculated from jobs
            },
            'research': {
                'total': 1 + get_skill_level(3405) + get_skill_level(24625),
                'used': 0  # Will be calculated from jobs
            },
            'reactions': {
                'total': get_skill_level(46242) + get_skill_level(46241) + get_skill_level(45746),
                'used': 0  # Will be calculated from jobs
            },
            'planets': {
                'total': 1 + get_skill_level(2495),
                'used': 0  # Will be calculated from planets
            }
        }
    
    def process_jobs_data(self, jobs: List[Dict], character_id: int) -> List[Dict]:
        """Process raw jobs data into structured format"""
        processed_jobs = []
        
        for job in jobs:
            # Get product and location info
            product_info = self.esi_service.get_type_info(job.get('product_type_id', 0))
            location_info = self.esi_service.get_location_info(job.get('location_id', 0))
            
            processed_job = {
                'job_id': job.get('job_id'),
                'character_id': character_id,
                'product_type_id': job.get('product_type_id'),
                'product_name': product_info.get('name', f'Type {job.get("product_type_id")}'),
                'activity_id': job.get('activity_id'),
                'start_date': job.get('start_date'),
                'end_date': job.get('end_date'),
                'location_id': job.get('location_id'),
                'location_name': location_info.get('name', f'Location {job.get("location_id")}'),
                'status': 'in-progress' if job.get('status') == 'active' else 'completed',
                'runs': job.get('runs', 1),
                'cost': job.get('cost', 0)
            }
            processed_jobs.append(processed_job)
        
        return processed_jobs
    
    def process_planets_data(self, planets: List[Dict], character_id: int, access_token: str) -> List[Dict]:
        """Process planets data and create planet jobs"""
        processed_planets = []
        
        for planet in planets:
            try:
                # Get detailed planet information
                planet_details = self.esi_service.get_planet_details(
                    character_id, planet['planet_id'], access_token
                )
                
                # Get planet and system info
                planet_info = self.esi_service.get_planet_info(planet['planet_id'])
                system_info = self.esi_service.get_system_info(planet['solar_system_id'])
                
                # Analyze planet state
                extractors = planet_details.get('extractors', [])
                pins = planet_details.get('pins', [])
                
                # Check if planet needs attention
                needs_attention = False
                active_extractors = 0
                
                for extractor in extractors:
                    if extractor.get('state') == 'active':
                        active_extractors += 1
                        # Check if extractor needs renewal
                        if 'expiry_time' in extractor:
                            expiry_time = extractor['expiry_time']
                            if expiry_time and datetime.datetime.fromisoformat(
                                expiry_time.replace('Z', '+00:00')
                            ) <= datetime.datetime.now(datetime.timezone.utc):
                                needs_attention = True
                
                # Count active jobs on planet
                active_jobs = 0
                for pin in pins:
                    if pin.get('type_id') in [2250, 2251, 2252, 2253, 2254, 2255]:  # Extractor types
                        if pin.get('state') == 'active':
                            active_jobs += 1
                
                # Create planet jobs
                planet_jobs = []
                for extractor in extractors:
                    if extractor.get('state') == 'active':
                        planet_jobs.append({
                            'job_id': f"planet_{planet['planet_id']}_extractor_{extractor.get('pin_id', 'unknown')}",
                            'product_name': f"Extractor on {planet_info.get('name', f'Planet {planet[\"planet_id\"]}')}",
                            'product_type_id': extractor.get('type_id', 2250),
                            'activity_id': 7,  # Planet Interaction
                            'start_date': extractor.get('start_time', ''),
                            'end_date': extractor.get('expiry_time', ''),
                            'location_name': f"{planet_info.get('name', f'Planet {planet[\"planet_id\"]}')} - {system_info.get('name', f'System {planet[\"solar_system_id\"]}')}",
                            'location_id': planet['planet_id'],
                            'status': 'active' if not needs_attention else 'needs_attention',
                            'runs': 1,
                            'cost': 0,
                            'planet_id': planet['planet_id'],
                            'extractor_id': extractor.get('pin_id'),
                            'is_planet_job': True
                        })
                
                processed_planet = {
                    'planet_id': planet['planet_id'],
                    'planet_name': planet_info.get('name', f'Planet {planet["planet_id"]}'),
                    'solar_system_id': planet['solar_system_id'],
                    'solar_system_name': system_info.get('name', f'System {planet["solar_system_id"]}'),
                    'planet_type': planet_info.get('type_id'),
                    'needs_attention': needs_attention,
                    'active_extractors': active_extractors,
                    'active_jobs': active_jobs,
                    'jobs': planet_jobs,
                    'extractors': extractors,
                    'pins': pins
                }
                processed_planets.append(processed_planet)
                
            except Exception as e:
                print(f"Error processing planet {planet['planet_id']}: {e}")
                continue
        
        return processed_planets
    
    def calculate_job_usage(self, jobs: List[Dict]) -> Dict:
        """Calculate used activity slots from jobs"""
        usage = {
            'manufacturing': 0,
            'research': 0,
            'reactions': 0
        }
        
        for job in jobs:
            activity_id = job.get('activity_id')
            if activity_id == 1:  # Manufacturing
                usage['manufacturing'] += 1
            elif activity_id in [3, 4, 5, 8]:  # Research
                usage['research'] += 1
            elif activity_id == 6:  # Reactions
                usage['reactions'] += 1
        
        return usage
    
    def calculate_planet_usage(self, planets: List[Dict]) -> int:
        """Calculate used planet slots"""
        return len(planets)
    
    def get_skill_level(self, skills: List[Dict], skill_id: int) -> int:
        """Get skill level for a specific skill"""
        for skill in skills:
            if skill.get('skill_id') == skill_id:
                return skill.get('active_skill_level', 0)
        return 0
    
    def calculate_manufacturing_efficiency(self, skills: List[Dict]) -> float:
        """Calculate manufacturing efficiency based on skills"""
        # Advanced Industry skill (3385) provides 2% per level
        # Mass Production skill (3389) provides 1% per level
        industry_skill = self.get_skill_level(skills, 3385)
        mass_production_skill = self.get_skill_level(skills, 3389)
        
        efficiency = 1.0 + (industry_skill * 0.02) + (mass_production_skill * 0.01)
        return min(efficiency, 2.0)  # Cap at 200% efficiency
    
    def calculate_research_efficiency(self, skills: List[Dict]) -> float:
        """Calculate research efficiency based on skills"""
        # Research skill (3405) provides efficiency
        # Advanced Research skill (24625) provides additional efficiency
        research_skill = self.get_skill_level(skills, 3405)
        advanced_research_skill = self.get_skill_level(skills, 24625)
        
        efficiency = 1.0 + (research_skill * 0.05) + (advanced_research_skill * 0.02)
        return min(efficiency, 2.0)  # Cap at 200% efficiency
