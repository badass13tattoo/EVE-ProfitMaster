import os
import requests
import base64
from flask import Flask, jsonify, request, redirect, session, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import secrets
import datetime

# 1. Отложенная инициализация расширений
db = SQLAlchemy()
cors = CORS()

# 2. Определение модели данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.BigInteger, unique=True, nullable=False)
    character_name = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<User {self.character_name}>'

# 3. Фабрика приложений
def create_app():
    """Создает и конфигурирует экземпляр приложения Flask."""
    
    app = Flask(__name__)
    load_dotenv()

    # --- Конфигурация приложения ---
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(16))
    
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        elif database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Инициализация расширений ---
    db.init_app(app)
    cors.init_app(app)

    # --- Вспомогательная функция (внутри фабрики) ---
    def refresh_access_token(user):
        CLIENT_ID = os.environ.get('EVE_CLIENT_ID')
        SECRET_KEY = os.environ.get('EVE_SECRET_KEY')
        auth_str = f"{CLIENT_ID}:{SECRET_KEY}"
        encoded_auth_str = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        token_url = 'https://login.eveonline.com/v2/oauth/token'
        headers = {'Authorization': f'Basic {encoded_auth_str}', 'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type': 'refresh_token', 'refresh_token': user.refresh_token}
        response = requests.post(token_url, headers=headers, data=data)
        token_data = response.json()

        if 'access_token' in token_data:
            user.access_token = token_data['access_token']
            user.refresh_token = token_data.get('refresh_token', user.refresh_token)
            db.session.commit()
            return True
        return False

    # --- Регистрация роутов (внутри фабрики) ---
    @app.route('/')
    def home():
        return "Привет! Это бэкенд для Eve Production Tracker. Он работает!"

    @app.route('/login')
    def login():
        CLIENT_ID = os.environ.get('EVE_CLIENT_ID')
        CALLBACK_URL = 'https://eve-profitmaster.onrender.com/callback'
        base_url = 'https://login.eveonline.com/v2/oauth/authorize'
        scopes = [
            "publicData", "esi-calendar.respond_calendar_events.v1", "esi-skills.read_skills.v1",
            "esi-wallet.read_character_wallet.v1", "esi-assets.read_assets.v1", "esi-planets.manage_planets.v1",
            "esi-markets.structure_markets.v1", "esi-industry.read_character_jobs.v1",
            "esi-markets.read_character_orders.v1", "esi-characters.read_blueprints.v1"
        ]
        params = {'response_type': 'code', 'redirect_uri': CALLBACK_URL, 'client_id': CLIENT_ID, 'scope': ' '.join(scopes), 'state': secrets.token_urlsafe(16)}
        session['oauth_state'] = params['state']
        auth_url = requests.Request('GET', base_url, params=params).prepare().url
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
        access_token = request.args.get('token')
        refresh_token = request.args.get('refresh')
        if not access_token or not refresh_token: return "Ошибка: не хватает токенов", 400

        verify_url = 'https://login.eveonline.com/oauth/verify'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(verify_url, headers=headers)
        if response.status_code != 200: return "Ошибка при верификации персонажа.", 401
        
        character_data = response.json()
        user = User.query.filter_by(character_id=character_data['CharacterID']).first()
        if user:
            user.access_token = access_token
            user.refresh_token = refresh_token
        else:
            new_user = User(character_id=character_data['CharacterID'], character_name=character_data['CharacterName'], access_token=access_token, refresh_token=refresh_token)
            db.session.add(new_user)
        db.session.commit()
        return redirect('/popup_close')

    @app.route('/popup_close')
    def popup_close():
        return render_template('popup_close.html')

    @app.route('/get_jobs')
    def get_jobs():
        users = User.query.all()
        if not users: return jsonify({}), 200
        jobs_by_character = {}
        for user in users:
            jobs_url = f'https://esi.evetech.net/latest/characters/{user.character_id}/industry/jobs/'
            headers = {'Authorization': f'Bearer {user.access_token}'}
            response = requests.get(jobs_url, headers=headers)
            if response.status_code == 401 and refresh_access_token(user):
                headers['Authorization'] = f'Bearer {user.access_token}'
                response = requests.get(jobs_url, headers=headers)
            if response.status_code == 200:
                jobs_data = response.json()
                for job in jobs_data: job['character_name'] = user.character_name
                jobs_by_character[str(user.character_id)] = jobs_data
            else:
                jobs_by_character[str(user.character_id)] = []
        return jsonify(jobs_by_character)

    @app.route('/get_characters')
    def get_characters():
        users = User.query.all()
        return jsonify([{'character_id': u.character_id, 'character_name': u.character_name} for u in users])

    @app.route('/get_character_details/<int:character_id>')
    def get_character_details(character_id):
        user = User.query.filter_by(character_id=character_id).first()
        if not user: return jsonify({'error': 'Персонаж не найден'}), 404
        if not refresh_access_token(user): print(f"Не удалось обновить токен для {user.character_name}")
        
        headers = {'Authorization': f'Bearer {user.access_token}'}
        base_url = 'https://esi.evetech.net/latest/characters'
        
        skills_resp = requests.get(f'{base_url}/{character_id}/skills/', headers=headers)
        jobs_resp = requests.get(f'{base_url}/{character_id}/industry/jobs/', headers=headers)
        planets_resp = requests.get(f'{base_url}/{character_id}/planets/', headers=headers)

        if skills_resp.status_code != 200: return jsonify({'error': 'Ошибка получения навыков'}), 500
        if jobs_resp.status_code != 200: return jsonify({'error': 'Ошибка получения работ'}), 500
        if planets_resp.status_code != 200: return jsonify({'error': 'Ошибка получения планет'}), 500

        skills_data = skills_resp.json().get('skills', [])
        jobs_data = jobs_resp.json()
        planets_data = planets_resp.json()

        def get_skill_level(skill_id):
            skill = next((s for s in skills_data if s.get('skill_id') == skill_id), {})
            return skill.get('active_skill_level', 0)

        details = {
            'lines': {
                'manufacturing': {'total': 1 + get_skill_level(3385) + get_skill_level(3389), 'used': sum(1 for j in jobs_data if j.get('activity_id') == 1)},
                'research': {'total': 1 + get_skill_level(3405) + get_skill_level(24625), 'used': sum(1 for j in jobs_data if j.get('activity_id') in [3, 4, 5, 8])}
            },
            'planets': {'total': 1 + get_skill_level(2495), 'used': len(planets_data)}
        }
        return jsonify(details)

    @app.route('/remove_character', methods=['POST'])
    def remove_character():
        data = request.get_json()
        character_id = data.get('character_id')
        if not character_id: return jsonify({'error': 'Требуется ID персонажа'}), 400
        user = User.query.filter_by(character_id=character_id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'Персонаж успешно удален'}), 200
        return jsonify({'error': 'Персонаж не найден'}), 404

    return app

# 4. Создание экземпляра приложения для Gunicorn
app = create_app()

# 5. Создание таблиц в контексте приложения
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)