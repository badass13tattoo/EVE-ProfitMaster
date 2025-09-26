"""
Industry Controller - Handles detailed industry jobs data collection and analysis
"""

from typing import Dict, List, Optional
from services.esi_data_service import ESIDataService
from services.business_logic_service import BusinessLogicService
from services.market_data_service import MarketDataService


class IndustryController:
    def __init__(self):
        self.esi_service = ESIDataService()
        self.business_logic = BusinessLogicService()
        self.market_service = MarketDataService()
    
    def get_character_industry_summary(self, character_id: int, access_token: str) -> Dict:
        """Get comprehensive industry summary for a character"""
        try:
            # Получаем все промышленные работы
            jobs = self.esi_service.get_character_jobs(character_id, access_token)
            
            if not jobs:
                return {
                    'character_id': character_id,
                    'total_jobs': 0,
                    'active_jobs': 0,
                    'completed_jobs': 0,
                    'paused_jobs': 0,
                    'jobs_by_activity': {},
                    'jobs_by_location': {},
                    'jobs_by_priority': {},
                    'total_cost': 0,
                    'total_value': 0,
                    'efficiency_rating': 0.0,
                    'risk_distribution': {},
                    'recent_activity': [],
                    'upcoming_completions': [],
                    'needs_attention': []
                }
            
            # Обрабатываем данные
            processed_jobs = self.business_logic.process_jobs_data(jobs, character_id)
            
            # Анализируем данные
            summary = self._analyze_jobs_data(processed_jobs, character_id)
            
            return summary
            
        except Exception as e:
            print(f"Error getting industry summary for character {character_id}: {e}")
            return {'error': str(e)}
    
    def get_jobs_by_activity(self, character_id: int, access_token: str, activity_id: Optional[int] = None) -> Dict:
        """Get jobs filtered by activity type"""
        try:
            jobs = self.esi_service.get_character_jobs(character_id, access_token)
            processed_jobs = self.business_logic.process_jobs_data(jobs, character_id)
            
            if activity_id:
                filtered_jobs = [job for job in processed_jobs if job['activity_id'] == activity_id]
            else:
                filtered_jobs = processed_jobs
            
            # Группируем по активности
            jobs_by_activity = {}
            for job in filtered_jobs:
                activity = job['activity_name']
                if activity not in jobs_by_activity:
                    jobs_by_activity[activity] = []
                jobs_by_activity[activity].append(job)
            
            return {
                'character_id': character_id,
                'activity_id': activity_id,
                'jobs_by_activity': jobs_by_activity,
                'total_jobs': len(filtered_jobs)
            }
            
        except Exception as e:
            print(f"Error getting jobs by activity for character {character_id}: {e}")
            return {'error': str(e)}
    
    def get_jobs_by_location(self, character_id: int, access_token: str) -> Dict:
        """Get jobs grouped by location with security analysis"""
        try:
            jobs = self.esi_service.get_character_jobs(character_id, access_token)
            processed_jobs = self.business_logic.process_jobs_data(jobs, character_id)
            
            # Группируем по локации
            jobs_by_location = {}
            location_security = {}
            
            for job in processed_jobs:
                location = job['location_name']
                if location not in jobs_by_location:
                    jobs_by_location[location] = []
                    location_security[location] = job['system_security']
                jobs_by_location[location].append(job)
            
            # Анализируем безопасность локаций
            security_analysis = self._analyze_location_security(jobs_by_location, location_security)
            
            return {
                'character_id': character_id,
                'jobs_by_location': jobs_by_location,
                'location_security': location_security,
                'security_analysis': security_analysis,
                'total_locations': len(jobs_by_location)
            }
            
        except Exception as e:
            print(f"Error getting jobs by location for character {character_id}: {e}")
            return {'error': str(e)}
    
    def get_priority_jobs(self, character_id: int, access_token: str, priority: str = 'high') -> Dict:
        """Get jobs by priority level"""
        try:
            jobs = self.esi_service.get_character_jobs(character_id, access_token)
            processed_jobs = self.business_logic.process_jobs_data(jobs, character_id)
            
            # Фильтруем по приоритету
            priority_jobs = [job for job in processed_jobs if job['priority'] == priority]
            
            # Сортируем по времени до завершения
            priority_jobs.sort(key=lambda x: x['time_remaining_hours'])
            
            return {
                'character_id': character_id,
                'priority': priority,
                'jobs': priority_jobs,
                'count': len(priority_jobs)
            }
            
        except Exception as e:
            print(f"Error getting priority jobs for character {character_id}: {e}")
            return {'error': str(e)}
    
    def get_jobs_needing_attention(self, character_id: int, access_token: str) -> Dict:
        """Get jobs that need immediate attention"""
        try:
            jobs = self.esi_service.get_character_jobs(character_id, access_token)
            processed_jobs = self.business_logic.process_jobs_data(jobs, character_id)
            
            # Находим работы, требующие внимания
            attention_jobs = []
            
            for job in processed_jobs:
                needs_attention = False
                reasons = []
                
                # Проверяем время до завершения
                if job['time_remaining_hours'] < 1 and not job['is_completed']:
                    needs_attention = True
                    reasons.append("Завершается менее чем через час")
                
                # Проверяем высокий приоритет
                if job['priority'] == 'high':
                    needs_attention = True
                    reasons.append("Высокий приоритет")
                
                # Проверяем высокий риск
                if job['risk_level'] == 'high':
                    needs_attention = True
                    reasons.append("Высокий риск (низкая безопасность)")
                
                # Проверяем приостановленные работы
                if job['is_paused']:
                    needs_attention = True
                    reasons.append("Работа приостановлена")
                
                if needs_attention:
                    job['attention_reasons'] = reasons
                    attention_jobs.append(job)
            
            # Сортируем по срочности
            attention_jobs.sort(key=lambda x: x['time_remaining_hours'])
            
            return {
                'character_id': character_id,
                'jobs_needing_attention': attention_jobs,
                'count': len(attention_jobs)
            }
            
        except Exception as e:
            print(f"Error getting jobs needing attention for character {character_id}: {e}")
            return {'error': str(e)}
    
    def _analyze_jobs_data(self, jobs: List[Dict], character_id: int) -> Dict:
        """Analyze processed jobs data and create summary"""
        if not jobs:
            return {}
        
        # Основная статистика
        total_jobs = len(jobs)
        active_jobs = len([j for j in jobs if j['status'] == 'active'])
        completed_jobs = len([j for j in jobs if j['is_completed']])
        paused_jobs = len([j for j in jobs if j['is_paused']])
        
        # Группировка по активности
        jobs_by_activity = {}
        for job in jobs:
            activity = job['activity_name']
            if activity not in jobs_by_activity:
                jobs_by_activity[activity] = 0
            jobs_by_activity[activity] += 1
        
        # Группировка по локации
        jobs_by_location = {}
        for job in jobs:
            location = job['location_name']
            if location not in jobs_by_location:
                jobs_by_location[location] = 0
            jobs_by_location[location] += 1
        
        # Группировка по приоритету
        jobs_by_priority = {'high': 0, 'medium': 0, 'low': 0}
        for job in jobs:
            priority = job['priority']
            if priority in jobs_by_priority:
                jobs_by_priority[priority] += 1
        
        # Финансовая информация
        total_cost = sum(job['cost'] for job in jobs)
        
        # Распределение рисков
        risk_distribution = {'high': 0, 'medium': 0, 'low': 0}
        for job in jobs:
            risk = job['risk_level']
            if risk in risk_distribution:
                risk_distribution[risk] += 1
        
        # Эффективность
        efficiency_rating = sum(job['efficiency'] for job in jobs) / total_jobs if total_jobs > 0 else 0
        
        # Предстоящие завершения (следующие 24 часа)
        upcoming_completions = [
            job for job in jobs 
            if job['status'] == 'active' and job['time_remaining_hours'] <= 24
        ]
        upcoming_completions.sort(key=lambda x: x['time_remaining_hours'])
        
        # Работы, требующие внимания
        needs_attention = [
            job for job in jobs 
            if (job['time_remaining_hours'] < 1 and not job['is_completed']) or 
               job['priority'] == 'high' or 
               job['is_paused']
        ]
        
        return {
            'character_id': character_id,
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'completed_jobs': completed_jobs,
            'paused_jobs': paused_jobs,
            'jobs_by_activity': jobs_by_activity,
            'jobs_by_location': jobs_by_location,
            'jobs_by_priority': jobs_by_priority,
            'total_cost': total_cost,
            'efficiency_rating': round(efficiency_rating, 2),
            'risk_distribution': risk_distribution,
            'upcoming_completions': upcoming_completions[:10],  # Топ 10
            'needs_attention': needs_attention[:10]  # Топ 10
        }
    
    def _analyze_location_security(self, jobs_by_location: Dict, location_security: Dict) -> Dict:
        """Analyze security status of locations"""
        security_analysis = {
            'high_sec_locations': 0,
            'low_sec_locations': 0,
            'null_sec_locations': 0,
            'total_jobs_in_high_sec': 0,
            'total_jobs_in_low_sec': 0,
            'total_jobs_in_null_sec': 0,
            'risky_locations': []
        }
        
        for location, jobs in jobs_by_location.items():
            security = location_security.get(location, 0.0)
            job_count = len(jobs)
            
            if security >= 0.5:
                security_analysis['high_sec_locations'] += 1
                security_analysis['total_jobs_in_high_sec'] += job_count
            elif security >= 0.0:
                security_analysis['low_sec_locations'] += 1
                security_analysis['total_jobs_in_low_sec'] += job_count
            else:
                security_analysis['null_sec_locations'] += 1
                security_analysis['total_jobs_in_null_sec'] += job_count
                
                # Добавляем в список рискованных локаций
                security_analysis['risky_locations'].append({
                    'location': location,
                    'security': security,
                    'job_count': job_count
                })
        
        return security_analysis
