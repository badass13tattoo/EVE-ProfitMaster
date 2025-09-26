import os
import requests
import base64
from flask import Flask, jsonify, request, redirect, session, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import secrets
import datetime

load_dotenv()
db = SQLAlchemy()
cors = CORS()

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
        
        scopes = "publicData esi-skills.read_skills.v1 esi-wallet.read_character_wallet.v1 esi-assets.read_assets.v1 esi-planets.manage_planets.v1 esi-industry.read_character_jobs.v1 esi-characters.read_blueprints.v1"
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
            resp = requests.get(f'https://esi.evetech.net/latest/characters/{user.character_id}/industry/jobs/', headers=headers)
            jobs_by_character[str(user.character_id)] = resp.json() if resp.status_code == 200 else []
        
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

    return app

app = create_app()
with app.app_context(): db.create_all()
if __name__ == '__main__': app.run(debug=True)