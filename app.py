import os
import requests
import base64
from flask import Flask, jsonify, request, redirect, session, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import secrets
import datetime
import time

load_dotenv()
db = SQLAlchemy()
cors = CORS()

# Простой кэш для типов и локаций
type_cache = {}
location_cache = {}
cache_duration = 3600  # 1 час

# Проверяем загрузку переменных окружения
print("DATABASE_URL:", os.environ.get('DATABASE_URL', 'NOT SET'))
print("EVE_CLIENT_ID:", os.environ.get('EVE_CLIENT_ID', 'NOT SET'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.BigInteger, unique=True, nullable=False)
    character_name = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(16))
    database_url = os.environ.get('DATABASE_URL') or 'postgresql://eve_profitmaster_v2_user:dimISkVaaTRhbCYnLbgNNjnCvudXwRaq@dpg-d39v2lp5pdvs73botp5g-a.frankfurt-postgres.render.com/eve_profitmaster_v2'
    if database_url:
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        elif database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    cors.init_app(app)

    def get_cached_type_info(type_id):
        """Получает информацию о типе с кэшированием"""
        current_time = time.time()
        if type_id in type_cache:
            cached_data, timestamp = type_cache[type_id]
            if current_time - timestamp < cache_duration:
                return cached_data
        
        try:
            resp = requests.get(f'https://esi.evetech.net/latest/universe/types/{type_id}/')
            if resp.status_code == 200:
                type_data = resp.json()
                cached_data = {
                    'type_id': type_id,
                    'name': type_data.get('name', f'Type {type_id}'),
                    'description': type_data.get('description', ''),
                    'group_id': type_data.get('group_id'),
                    'market_group_id': type_data.get('market_group_id')
                }
                type_cache[type_id] = (cached_data, current_time)
                return cached_data
        except:
            pass
        
        return {'type_id': type_id, 'name': f'Type {type_id}'}

    def get_cached_location_info(location_id):
        """Получает информацию о локации с кэшированием"""
        current_time = time.time()
        if location_id in location_cache:
            cached_data, timestamp = location_cache[location_id]
            if current_time - timestamp < cache_duration:
                return cached_data
        
        try:
            if location_id > 1000000000000:  # Structure
                resp = requests.get(f'https://esi.evetech.net/latest/universe/structures/{location_id}/')
                if resp.status_code == 200:
                    location_data = resp.json()
                    cached_data = {
                        'location_id': location_id,
                        'name': location_data.get('name', f'Structure {location_id}'),
                        'type': 'structure',
                        'solar_system_id': location_data.get('solar_system_id')
                    }
                    location_cache[location_id] = (cached_data, current_time)
                    return cached_data
            else:  # Station
                resp = requests.get(f'https://esi.evetech.net/latest/universe/stations/{location_id}/')
                if resp.status_code == 200:
                    location_data = resp.json()
                    cached_data = {
                        'location_id': location_id,
                        'name': location_data.get('name', f'Station {location_id}'),
                        'type': 'station',
                        'solar_system_id': location_data.get('system_id')
                    }
                    location_cache[location_id] = (cached_data, current_time)
                    return cached_data
        except:
            pass
        
        return {'location_id': location_id, 'name': f'Location {location_id}'}

    def refresh_access_token(user):
        try:
            CLIENT_ID = os.environ.get('EVE_CLIENT_ID')
            SECRET_KEY = os.environ.get('EVE_SECRET_KEY')
            
            if not CLIENT_ID or not SECRET_KEY:
                print("Missing EVE_CLIENT_ID or EVE_SECRET_KEY environment variables")
                return False
                
            auth_str = f"{CLIENT_ID}:{SECRET_KEY}"
            encoded_auth_str = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
            token_url = 'https://login.eveonline.com/v2/oauth/token'
            headers = {'Authorization': f'Basic {encoded_auth_str}', 'Content-Type': 'application/x-www-form-urlencoded'}
            data = {'grant_type': 'refresh_token', 'refresh_token': user.refresh_token}
            
            print(f"Refreshing token for user {user.character_name}")
            response = requests.post(token_url, headers=headers, data=data)
            print(f"Token refresh response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Token refresh failed: {response.text}")
                return False
                
            token_data = response.json()
            if 'access_token' in token_data:
                user.access_token = token_data['access_token']
                user.refresh_token = token_data.get('refresh_token', user.refresh_token)
                db.session.commit()
                print("Token refreshed successfully")
                return True
            else:
                print(f"Token refresh response missing access_token: {token_data}")
                return False
        except Exception as e:
            print(f"Error refreshing token: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    @app.route('/')
    def home(): return "Бэкенд EVE Profit Master работает!"
    
    @app.route('/health')
    def health():
        try:
            # Test database connection
            user_count = User.query.count()
            return jsonify({
                'status': 'healthy',
                'database_connected': True,
                'user_count': user_count,
                'environment_vars': {
                    'EVE_CLIENT_ID': bool(os.environ.get('EVE_CLIENT_ID')),
                    'EVE_SECRET_KEY': bool(os.environ.get('EVE_SECRET_KEY')),
                    'DATABASE_URL': bool(os.environ.get('DATABASE_URL'))
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'database_connected': False,
                'error': str(e)
            }), 500

    @app.route('/login')
    def login():
        CLIENT_ID = os.environ.get('EVE_CLIENT_ID')
        # Определяем callback URL в зависимости от режима
        if app.config.get('FLASK_ENV') == 'development':
            CALLBACK_URL = 'http://localhost:5000/callback'
        else:
            CALLBACK_URL = 'https://eve-profitmaster.onrender.com/callback'
        
        print(f"Using callback URL: {CALLBACK_URL}")
        print(f"Client ID: {CLIENT_ID}")
        
        scopes = "publicData esi-calendar.respond_calendar_events.v1 esi-skills.read_skills.v1 esi-wallet.read_character_wallet.v1 esi-assets.read_assets.v1 esi-planets.manage_planets.v1 esi-markets.structure_markets.v1 esi-industry.read_character_jobs.v1 esi-markets.read_character_orders.v1 esi-characters.read_blueprints.v1"
        params = {'response_type': 'code', 'redirect_uri': CALLBACK_URL, 'client_id': CLIENT_ID, 'scope': scopes, 'state': secrets.token_urlsafe(16)}
        session['oauth_state'] = params['state']
        auth_url = requests.Request('GET', 'https://login.eveonline.com/v2/oauth/authorize', params=params).prepare().url
        print(f"Generated auth URL: {auth_url}")
        return redirect(auth_url)

    @app.route('/callback')
    def callback():
        CLIENT_ID = os.environ.get('EVE_CLIENT_ID')
        SECRET_KEY = os.environ.get('EVE_SECRET_KEY')
        code = request.args.get('code')
        state = request.args.get('state')
        if state != session.pop('oauth_state', None): return jsonify({'error': 'Неверный параметр state'}), 400
        if not code: return jsonify({'error': 'Код авторизации не получен'}), 400
        auth_str = f"{CLIENT_ID}:{SECRET_KEY}"
        encoded_auth_str = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        token_url = 'https://login.eveonline.com/v2/oauth/token'
        headers = {'Authorization': f'Basic {encoded_auth_str}', 'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type': 'authorization_code', 'code': code}
        response = requests.post(token_url, headers=headers, data=data)
        token_data = response.json()
        if 'access_token' in token_data:
            return redirect(f"/add_character?token={token_data['access_token']}&refresh={token_data['refresh_token']}")
        return jsonify({'error': 'Не удалось получить токен'}), 400

    @app.route('/add_character')
    def add_character():
        access_token, refresh_token = request.args.get('token'), request.args.get('refresh')
        if not all([access_token, refresh_token]): return "Ошибка: не хватает токенов", 400
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://login.eveonline.com/oauth/verify', headers=headers)
        if response.status_code != 200: return "Ошибка при верификации персонажа.", 401
        char_data = response.json()
        user = User.query.filter_by(character_id=char_data['CharacterID']).first()
        if user: 
            user.access_token, user.refresh_token = access_token, refresh_token
        else: 
            db.session.add(User(character_id=char_data['CharacterID'], character_name=char_data['CharacterName'], access_token=access_token, refresh_token=refresh_token))
        db.session.commit()
        
        # Перенаправляем на фронтенд в зависимости от режима
        if app.config.get('FLASK_ENV') == 'development':
            return redirect('http://localhost:8080/?auth=success')
        else:
            return redirect('https://eve-profitmaster-1.onrender.com/?auth=success')

    @app.route('/popup_close')
    def popup_close(): return render_template('popup_close.html')

    @app.route('/get_jobs')
    def get_jobs():
        users = User.query.all()
        jobs_by_character = {}
        users_to_remove = []
        
        for user in users:
            if not refresh_access_token(user): 
                print(f"Token refresh failed for {user.character_name}, marking for removal")
                users_to_remove.append(user)
                continue
            
            headers = {'Authorization': f'Bearer {user.access_token}'}
            jobs_url = f'https://esi.evetech.net/latest/characters/{user.character_id}/industry/jobs/'
            print(f"Fetching jobs for {user.character_name} from {jobs_url}")
            
            resp = requests.get(jobs_url, headers=headers)
            print(f"Jobs API response for {user.character_name}: {resp.status_code}")
            
            if resp.status_code == 200:
                jobs_data = resp.json()
                # Преобразуем данные EVE ESI API в формат, ожидаемый frontend
                transformed_jobs = []
                for job in jobs_data:
                    # Получаем название продукта с кэшированием
                    product_type_id = job.get('product_type_id')
                    product_info = get_cached_type_info(product_type_id) if product_type_id else {'name': 'Unknown Product'}
                    product_name = product_info.get('name', f'Type {product_type_id}')
                    
                    # Получаем название локации с кэшированием
                    location_id = job.get('location_id')
                    location_info = get_cached_location_info(location_id) if location_id else {'name': 'Unknown Location'}
                    location_name = location_info.get('name', f'Location {location_id}')
                    
                    transformed_job = {
                        'job_id': job.get('job_id'),
                        'product_name': product_name,
                        'product_type_id': job.get('product_type_id'),
                        'activity_id': job.get('activity_id'),
                        'start_date': job.get('start_date'),
                        'end_date': job.get('end_date'),
                        'location_name': location_name,
                        'location_id': job.get('location_id'),
                        'status': 'in-progress' if job.get('status') == 'active' else 'completed',
                        'runs': job.get('runs', 1),
                        'cost': job.get('cost', 0)
                    }
                    transformed_jobs.append(transformed_job)
                
                jobs_by_character[str(user.character_id)] = transformed_jobs
                print(f"Found {len(transformed_jobs)} jobs for {user.character_name}")
                if transformed_jobs:
                    print(f"Sample job data: {transformed_jobs[0]}")
            else:
                print(f"Jobs API error for {user.character_name}: {resp.text}")
                jobs_by_character[str(user.character_id)] = []
        
        # Remove users with invalid tokens
        for user in users_to_remove:
            db.session.delete(user)
        if users_to_remove:
            db.session.commit()
            print(f"Removed {len(users_to_remove)} users with invalid tokens")
            
        return jsonify(jobs_by_character)

    @app.route('/get_characters')
    def get_characters():
        return jsonify([{'character_id': u.character_id, 'character_name': u.character_name} for u in User.query.all()])

    @app.route('/get_character_details/<int:character_id>')
    def get_character_details(character_id):
        try:
            print(f"Getting character details for ID: {character_id}")
            user = User.query.filter_by(character_id=character_id).first()
            if not user: 
                print(f"User not found for character_id: {character_id}")
                return jsonify({'error': 'Персонаж не найден'}), 404
            
            print(f"Found user: {user.character_name}")
            if not refresh_access_token(user): 
                print("Failed to refresh access token - removing character from database")
                # Remove the character with invalid token from database
                db.session.delete(user)
                db.session.commit()
                return jsonify({'error': 'Токен доступа истек. Пожалуйста, войдите в систему заново.', 'requires_reauth': True}), 401
            
            headers = {'Authorization': f'Bearer {user.access_token}'}
            base_url = 'https://esi.evetech.net/latest/characters'
            
            print("Making API requests to EVE ESI...")
            skills_resp = requests.get(f'{base_url}/{character_id}/skills/', headers=headers)
            jobs_resp = requests.get(f'{base_url}/{character_id}/industry/jobs/', headers=headers)
            planets_resp = requests.get(f'{base_url}/{character_id}/planets/', headers=headers)

            print(f"Skills API status: {skills_resp.status_code}")
            print(f"Jobs API status: {jobs_resp.status_code}")
            print(f"Planets API status: {planets_resp.status_code}")

            skills = skills_resp.json().get('skills', []) if skills_resp.status_code == 200 else []
            jobs = jobs_resp.json() if jobs_resp.status_code == 200 else []
            planets = planets_resp.json() if planets_resp.status_code == 200 else []

            def get_skill(skill_id): return next((s.get('active_skill_level', 0) for s in skills if s.get('skill_id') == skill_id), 0)

            result = {
                'lines': {
                    'manufacturing': {'total': 1 + get_skill(3385) + get_skill(3389), 'used': sum(1 for j in jobs if j.get('activity_id') == 1)},
                    'research': {'total': 1 + get_skill(3405) + get_skill(24625), 'used': sum(1 for j in jobs if j.get('activity_id') in [3, 4, 5, 8])},
                    'reactions': {'total': get_skill(46242) + get_skill(46241) + get_skill(45746), 'used': sum(1 for j in jobs if j.get('activity_id') == 6)}
                },
                'planets': {'total': 1 + get_skill(2495), 'used': len(planets)}
            }
            
            print(f"Returning result: {result}")
            return jsonify(result)
            
        except Exception as e:
            print(f"Error in get_character_details: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

    @app.route('/remove_character', methods=['POST'])
    def remove_character():
        user = User.query.filter_by(character_id=request.get_json().get('character_id')).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'Персонаж успешно удален'}), 200
        return jsonify({'error': 'Персонаж не найден'}), 404

    @app.route('/reset_database', methods=['POST'])
    def reset_database():
        try:
            # Удаляем все записи из таблицы User
            User.query.delete()
            db.session.commit()
            
            print("Database reset completed - all users removed")
            return jsonify({'message': 'База данных успешно очищена. Все персонажи удалены.'}), 200
        except Exception as e:
            print(f"Error resetting database: {str(e)}")
            return jsonify({'error': f'Ошибка очистки базы данных: {str(e)}'}), 500

    @app.route('/check_token_scopes/<int:character_id>')
    def check_token_scopes(character_id):
        try:
            user = User.query.filter_by(character_id=character_id).first()
            if not user:
                return jsonify({'error': 'Персонаж не найден'}), 404
            
            if not refresh_access_token(user):
                return jsonify({'error': 'Не удалось обновить токен'}), 401
            
            headers = {'Authorization': f'Bearer {user.access_token}'}
            # Проверяем токен через EVE SSO verify endpoint
            verify_resp = requests.get('https://login.eveonline.com/oauth/verify', headers=headers)
            
            if verify_resp.status_code == 200:
                token_info = verify_resp.json()
                scopes = token_info.get('Scopes', '').split(' ')
                return jsonify({
                    'character_name': user.character_name,
                    'scopes': scopes,
                    'has_industry_jobs_scope': 'esi-industry.read_character_jobs.v1' in scopes
                })
            else:
                return jsonify({'error': 'Не удалось проверить токен'}), 500
                
        except Exception as e:
            print(f"Error checking token scopes: {str(e)}")
            return jsonify({'error': f'Ошибка проверки скоупов: {str(e)}'}), 500

    @app.route('/get_character_portrait/<int:character_id>')
    def get_character_portrait(character_id):
        return jsonify({
            'portrait_url': f'https://images.evetech.net/characters/{character_id}/portrait?size=128'
        })

    @app.route('/get_type_info/<int:type_id>')
    def get_type_info(type_id):
        try:
            type_info = get_cached_type_info(type_id)
            return jsonify(type_info)
        except Exception as e:
            return jsonify({'error': f'Ошибка получения информации о типе: {str(e)}'}), 500

    @app.route('/get_location_info/<int:location_id>')
    def get_location_info(location_id):
        try:
            location_info = get_cached_location_info(location_id)
            return jsonify(location_info)
        except Exception as e:
            return jsonify({'error': f'Ошибка получения информации о локации: {str(e)}'}), 500

    @app.route('/get_character_skills/<int:character_id>')
    def get_character_skills(character_id):
        try:
            user = User.query.filter_by(character_id=character_id).first()
            if not user:
                return jsonify({'error': 'Персонаж не найден'}), 404
            
            if not refresh_access_token(user):
                return jsonify({'error': 'Не удалось обновить токен'}), 401
            
            headers = {'Authorization': f'Bearer {user.access_token}'}
            resp = requests.get(f'https://esi.evetech.net/latest/characters/{character_id}/skills/', headers=headers)
            
            if resp.status_code == 200:
                skills_data = resp.json()
                return jsonify(skills_data)
            else:
                return jsonify({'error': 'Не удалось получить навыки'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Ошибка получения навыков: {str(e)}'}), 500

    @app.route('/get_character_blueprints/<int:character_id>')
    def get_character_blueprints(character_id):
        try:
            user = User.query.filter_by(character_id=character_id).first()
            if not user:
                return jsonify({'error': 'Персонаж не найден'}), 404
            
            if not refresh_access_token(user):
                return jsonify({'error': 'Не удалось обновить токен'}), 401
            
            headers = {'Authorization': f'Bearer {user.access_token}'}
            resp = requests.get(f'https://esi.evetech.net/latest/characters/{character_id}/blueprints/', headers=headers)
            
            if resp.status_code == 200:
                blueprints_data = resp.json()
                return jsonify(blueprints_data)
            else:
                return jsonify({'error': 'Не удалось получить блюпринты'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Ошибка получения блюпринтов: {str(e)}'}), 500

    @app.route('/get_character_planets/<int:character_id>')
    def get_character_planets(character_id):
        try:
            user = User.query.filter_by(character_id=character_id).first()
            if not user:
                return jsonify({'error': 'Персонаж не найден'}), 404
            
            if not refresh_access_token(user):
                return jsonify({'error': 'Не удалось обновить токен'}), 401
            
            headers = {'Authorization': f'Bearer {user.access_token}'}
            
            # Получаем список планет
            planets_resp = requests.get(f'https://esi.evetech.net/latest/characters/{character_id}/planets/', headers=headers)
            
            if planets_resp.status_code != 200:
                return jsonify({'error': 'Не удалось получить планеты'}), 500
            
            planets_data = planets_resp.json()
            planets_with_details = []
            
            # Для каждой планеты получаем детальную информацию
            for planet in planets_data:
                try:
                    # Получаем детали планеты
                    planet_detail_resp = requests.get(f'https://esi.evetech.net/latest/characters/{character_id}/planets/{planet["planet_id"]}/', headers=headers)
                    
                    if planet_detail_resp.status_code == 200:
                        planet_detail = planet_detail_resp.json()
                        
                        # Получаем информацию о планете из universe API
                        planet_info_resp = requests.get(f'https://esi.evetech.net/latest/universe/planets/{planet["planet_id"]}/')
                        planet_info = planet_info_resp.json() if planet_info_resp.status_code == 200 else {}
                        
                        # Получаем информацию о системе
                        system_info_resp = requests.get(f'https://esi.evetech.net/latest/universe/systems/{planet["solar_system_id"]}/')
                        system_info = system_info_resp.json() if system_info_resp.status_code == 200 else {}
                        
                        # Анализируем состояние планеты
                        extractors = planet_detail.get('extractors', [])
                        pins = planet_detail.get('pins', [])
                        
                        # Проверяем, требует ли планета внимания
                        needs_attention = False
                        active_extractors = 0
                        
                        for extractor in extractors:
                            if extractor.get('state') == 'active':
                                active_extractors += 1
                                # Проверяем, нужно ли обновить экстрактор
                                if 'expiry_time' in extractor:
                                    expiry_time = extractor['expiry_time']
                                    if expiry_time and datetime.datetime.fromisoformat(expiry_time.replace('Z', '+00:00')) <= datetime.datetime.now(datetime.timezone.utc):
                                        needs_attention = True
                        
                        # Проверяем, есть ли активные работы на планете
                        active_jobs = 0
                        for pin in pins:
                            if pin.get('type_id') in [2250, 2251, 2252, 2253, 2254, 2255]:  # Типы экстракторов
                                if pin.get('state') == 'active':
                                    active_jobs += 1
                        
                        # Создаем "работы" для планеты
                        planet_jobs = []
                        
                        # Добавляем работу для каждого экстрактора
                        for extractor in extractors:
                            if extractor.get('state') == 'active':
                                start_time = extractor.get('start_time', '')
                                expiry_time = extractor.get('expiry_time', '')
                                
                                # Вычисляем время до завершения
                                time_remaining_hours = 0
                                duration_hours = 0
                                progress_percentage = 0
                                
                                if start_time and expiry_time:
                                    try:
                                        start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                                        expiry_dt = datetime.datetime.fromisoformat(expiry_time.replace('Z', '+00:00'))
                                        now = datetime.datetime.now(datetime.timezone.utc)
                                        
                                        duration_hours = (expiry_dt - start_dt).total_seconds() / 3600
                                        time_remaining_hours = max(0, (expiry_dt - now).total_seconds() / 3600)
                                        
                                        if duration_hours > 0:
                                            progress_percentage = min(100, max(0, ((now - start_dt).total_seconds() / (expiry_dt - start_dt).total_seconds()) * 100))
                                        
                                    except Exception as e:
                                        print(f"Error parsing dates for extractor {extractor.get('pin_id')}: {e}")
                                
                                # Определяем приоритет на основе времени до завершения
                                priority = 'low'
                                if time_remaining_hours < 1:
                                    priority = 'high'
                                elif time_remaining_hours < 24:
                                    priority = 'medium'
                                
                                planet_jobs.append({
                                    'job_id': f"planet_{planet['planet_id']}_extractor_{extractor.get('pin_id', 'unknown')}",
                                    'product_name': f"Extractor on {planet_info.get('name', f'Planet {planet["planet_id"]}')}",
                                    'product_type_id': extractor.get('type_id', 2250),
                                    'activity_id': 7,  # Planet Interaction
                                    'start_date': start_time,
                                    'end_date': expiry_time,
                                    'location_name': f"{planet_info.get('name', f'Planet {planet["planet_id"]}')} - {system_info.get('name', f'System {planet["solar_system_id"]}')}",
                                    'location_id': planet['planet_id'],
                                    'status': 'active' if not needs_attention else 'needs_attention',
                                    'runs': 1,
                                    'cost': 0,
                                    'planet_id': planet['planet_id'],
                                    'extractor_id': extractor.get('pin_id'),
                                    'is_planet_job': True,
                                    'duration_hours': round(duration_hours, 2),
                                    'time_remaining_hours': round(time_remaining_hours, 2),
                                    'progress_percentage': round(progress_percentage, 1),
                                    'priority': priority,
                                    'is_completed': time_remaining_hours <= 0,
                                    'is_paused': False
                                })
                        
                        # Вычисляем общее время до завершения всех работ на планете
                        earliest_expiry = None
                        latest_expiry = None
                        total_time_remaining = 0
                        
                        for job in planet_jobs:
                            if job.get('end_date'):
                                try:
                                    expiry_dt = datetime.datetime.fromisoformat(job['end_date'].replace('Z', '+00:00'))
                                    if earliest_expiry is None or expiry_dt < earliest_expiry:
                                        earliest_expiry = expiry_dt
                                    if latest_expiry is None or expiry_dt > latest_expiry:
                                        latest_expiry = expiry_dt
                                    total_time_remaining += job.get('time_remaining_hours', 0)
                                except:
                                    pass
                        
                        # Определяем время до следующего завершения
                        next_completion_hours = 0
                        if earliest_expiry:
                            now = datetime.datetime.now(datetime.timezone.utc)
                            next_completion_hours = max(0, (earliest_expiry - now).total_seconds() / 3600)
                        
                        planet_data = {
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
                            'pins': pins,
                            # Временная информация
                            'next_completion_hours': round(next_completion_hours, 2),
                            'total_time_remaining_hours': round(total_time_remaining, 2),
                            'earliest_expiry': earliest_expiry.isoformat() if earliest_expiry else None,
                            'latest_expiry': latest_expiry.isoformat() if latest_expiry else None,
                            'extractor_expiry_time': earliest_expiry.isoformat() if earliest_expiry else None
                        }
                        
                        planets_with_details.append(planet_data)
                        
                except Exception as e:
                    print(f"Error getting details for planet {planet['planet_id']}: {str(e)}")
                    continue
            
            return jsonify(planets_with_details)
            
        except Exception as e:
            print(f"Error loading planets: {str(e)}")
            return jsonify({'error': f'Ошибка получения планет: {str(e)}'}), 500

    # Industry endpoints - Detailed industrial jobs data collection
    @app.route('/api/industry/characters/<int:character_id>/jobs/detailed')
    def get_detailed_industry_jobs(character_id):
        """Get detailed industry jobs data with all enriched information"""
        try:
            user = User.query.filter_by(character_id=character_id).first()
            if not user:
                return jsonify({'error': 'Character not found'}), 404
            
            # Refresh access token
            if not refresh_access_token(user):
                return jsonify({'error': 'Authentication failed'}), 401
            
            # Get jobs data
            jobs_url = f'https://esi.evetech.net/latest/characters/{user.character_id}/industry/jobs/'
            headers = {'Authorization': f'Bearer {user.access_token}'}
            
            resp = requests.get(jobs_url, headers=headers)
            if resp.status_code != 200:
                return jsonify({'error': f'ESI API error: {resp.status_code}'}), 500
            
            jobs_data = resp.json()
            
            # Process and enrich jobs data
            processed_jobs = []
            for job in jobs_data:
                # Get product info
                product_type_id = job.get('product_type_id')
                product_info = get_cached_type_info(product_type_id) if product_type_id else {'name': 'Unknown Product'}
                
                # Get location info
                location_id = job.get('location_id')
                location_info = get_cached_location_info(location_id) if location_id else {'name': 'Unknown Location'}
                
                # Calculate additional fields
                start_date = datetime.datetime.fromisoformat(job.get('start_date', '').replace('Z', '+00:00'))
                end_date = datetime.datetime.fromisoformat(job.get('end_date', '').replace('Z', '+00:00'))
                now = datetime.datetime.now(datetime.timezone.utc)
                
                duration_hours = (end_date - start_date).total_seconds() / 3600
                time_remaining_hours = max(0, (end_date - now).total_seconds() / 3600) if job.get('status') == 'active' else 0
                progress_percentage = min(100, max(0, ((now - start_date).total_seconds() / (end_date - start_date).total_seconds()) * 100)) if job.get('status') == 'active' else 100
                
                # Determine priority
                priority = 'low'
                if time_remaining_hours < 1 and job.get('status') == 'active':
                    priority = 'high'
                elif time_remaining_hours < 24 and job.get('status') == 'active':
                    priority = 'medium'
                
                # Determine risk level based on system security (simplified)
                risk_level = 'low'  # Default, would need system info to determine properly
                
                processed_job = {
                    'job_id': job.get('job_id'),
                    'character_id': character_id,
                    'product_type_id': job.get('product_type_id'),
                    'product_name': product_info.get('name', f'Type {job.get("product_type_id")}'),
                    'activity_id': job.get('activity_id'),
                    'activity_name': get_activity_name(job.get('activity_id')),
                    'start_date': job.get('start_date'),
                    'end_date': job.get('end_date'),
                    'location_id': job.get('location_id'),
                    'location_name': location_info.get('name', f'Location {job.get("location_id")}'),
                    'status': job.get('status'),
                    'runs': job.get('runs', 1),
                    'cost': job.get('cost', 0),
                    'duration_hours': round(duration_hours, 2),
                    'time_remaining_hours': round(time_remaining_hours, 2),
                    'is_completed': job.get('status') != 'active',
                    'is_paused': job.get('status') == 'paused',
                    'progress_percentage': round(progress_percentage, 1),
                    'priority': priority,
                    'risk_level': risk_level,
                    'efficiency': 100.0,  # Simplified
                    'system_name': 'Unknown',  # Would need additional API call
                    'system_security': 0.5  # Default, would need additional API call
                }
                processed_jobs.append(processed_job)
            
            return jsonify({
                'character_id': character_id,
                'jobs': processed_jobs,
                'total_jobs': len(processed_jobs),
                'active_jobs': len([j for j in processed_jobs if j['status'] == 'active']),
                'completed_jobs': len([j for j in processed_jobs if j['is_completed']])
            })
            
        except Exception as e:
            print(f"Error getting detailed industry jobs: {str(e)}")
            return jsonify({'error': f'Ошибка получения индустриальных работ: {str(e)}'}), 500

    def get_activity_name(activity_id):
        """Get human-readable activity name"""
        activities = {
            1: "Manufacturing",
            3: "Researching Technology",
            4: "Researching Time Efficiency",
            5: "Researching Material Efficiency", 
            6: "Copying",
            7: "Duplicating",
            8: "Reverse Engineering",
            9: "Invention",
            11: "Reaction"
        }
        return activities.get(activity_id, f"Activity {activity_id}")

    return app

app = create_app()
with app.app_context(): db.create_all()
if __name__ == '__main__': app.run(debug=True)