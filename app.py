import os
import requests
import base64
from flask import Flask, jsonify, request, redirect, session, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import secrets
import datetime

# --- Отложенная инициализация ---
db = SQLAlchemy()
cors = CORS()

# --- Модель данных ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.BigInteger, unique=True, nullable=False)
    character_name = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<User {self.character_name}>'

# --- Фабрика приложений ---
def create_app():
    """Создает и конфигурирует экземпляр приложения Flask."""
    
    app = Flask(__name__, instance_relative_config=True) # Указываем папку для шаблонов
    load_dotenv()

    # --- Конфигурация ---
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

    # --- Вспомогательная функция ---
    def refresh_access_token(user):
        # (Код этой функции остается без изменений)
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
        else:
            print(f"Ошибка при обновлении токена для {user.character_name}: {token_data.get('error_description')}")
            return False

    # --- Роуты ---
    @app.route('/')
    def home():
        return "Привет! Это бэкенд для Eve Production Tracker. Он работает!"

    @app.route('/login')
    def login():
        # (Код этого роута остается без изменений)
        CLIENT_ID = os.environ.get('EVE_CLIENT_ID')
        CALLBACK_URL = 'https://eve-profitmaster.onrender.com/callback'
        base_url = 'https://login.eveonline.com/v2/oauth/authorize'
        scopes = [
            "publicData", "esi-calendar.respond_calendar_events.v1", "esi-skills.read_skills.v1",
            "esi-wallet.read_character_wallet.v1", "esi-assets.read_assets.v1", "esi-planets.manage_planets.v1",
            "esi-markets.structure_markets.v1", "esi-industry.read_character_jobs.v1",
            "esi-markets.read_character_orders.v1", "esi-characters.read_blueprints.v1"
        ]
        scopes_str = ' '.join(scopes)
        state = secrets.token_urlsafe(16)
        session['oauth_state'] = state
        params = {
            'response_type': 'code', 'redirect_uri': CALLBACK_URL,
            'client_id': CLIENT_ID, 'scope': scopes_str, 'state': state
        }
        auth_url = requests.Request('GET', base_url, params=params).prepare().url
        return redirect(auth_url)

    @app.route('/callback')
    def callback():
        # (Код этого роута остается без изменений)
        CLIENT_ID = os.environ.get('EVE_CLIENT_ID')
        SECRET_KEY = os.environ.get('EVE_SECRET_KEY')
        code = request.args.get('code')
        state = request.args.get('state')
        if state != session.get('oauth_state'): return jsonify({'error': 'Неверный параметр state'}), 400
        session.pop('oauth_state', None)
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
        else:
            return jsonify({'error': 'Не удалось получить токен'}), 400

    @app.route('/add_character')
    def add_character():
        # (Код этого роута изменен только в конце)
        access_token = request.args.get('token')
        refresh_token = request.args.get('refresh')
        if not access_token or not refresh_token: return "Ошибка: не хватает токенов", 400
        verify_url = 'https://login.eveonline.com/oauth/verify'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(verify_url, headers=headers)
        if response.status_code != 200: return "Ошибка при верификации персонажа.", 401
        character_data = response.json()
        character_id = character_data['CharacterID']
        character_name = character_data['CharacterName']
        user = User.query.filter_by(character_id=character_id).first()
        if user:
            user.access_token = access_token
            user.refresh_token = refresh_token
        else:
            new_user = User(character_id=character_id, character_name=character_name, access_token=access_token, refresh_token=refresh_token)
            db.session.add(new_user)
        db.session.commit()
        return redirect('/popup_close')

    @app.route('/popup_close')
    def popup_close():
        return render_template('popup_close.html')

    @app.route('/get_jobs')
    def get_jobs():
        # (Код этого роута остается без изменений)
        users = User.query.all()
        if not users: return jsonify([]), 200
        all_jobs = []
        for user in users:
            jobs_url = f'https://esi.evetech.net/latest/characters/{user.character_id}/industry/jobs/'
            headers = {'Authorization': f'Bearer {user.access_token}'}
            response = requests.get(jobs_url, headers=headers)
            if response.status_code == 401:
                if refresh_access_token(user):
                    headers['Authorization'] = f'Bearer {user.access_token}'
                    response = requests.get(jobs_url, headers=headers)
            if response.status_code == 200:
                jobs_data = response.json()
                for job in jobs_data: job['character_name'] = user.character_name
                all_jobs.extend(jobs_data)
            else:
                print(f"Ошибка при получении данных для персонажа {user.character_name}. Код: {response.status_code}")
        return jsonify(all_jobs)

    @app.route('/get_characters')
    def get_characters():
        users = User.query.all()
        characters = [{'character_id': user.character_id, 'character_name': user.character_name} for user in users]
        return jsonify(characters)

    @app.route('/get_character_activity/<int:character_id>')
    def get_character_activity(character_id):
        user = User.query.filter_by(character_id=character_id).first()
        if not user: return jsonify({'error': 'Персонаж не найден'}), 404
        headers = {'Authorization': f'Bearer {user.access_token}'}
        skills_url = f'https://esi.evetech.net/latest/characters/{character_id}/skills/'
        skills_response = requests.get(skills_url, headers=headers)
        if skills_response.status_code != 200: return jsonify({'error': 'Не удалось получить данные о навыках'}), skills_response.status_code
        skills_data = skills_response.json().get('skills', [])
        jobs_url = f'https://esi.evetech.net/latest/characters/{character_id}/industry/jobs/'
        jobs_response = requests.get(jobs_url, headers=headers)
        if jobs_response.status_code != 200: return jsonify({'error': 'Не удалось получить данные о работах'}), jobs_response.status_code
        jobs_data = jobs_response.json()
        mass_prod_skill = next((s for s in skills_data if s.get('skill_id') == 3385), None)
        manufacturing_slots = 1 + (mass_prod_skill.get('active_skill_level', 0) if mass_prod_skill else 0)
        lab_op_skill = next((s for s in skills_data if s.get('skill_id') == 3405), None)
        research_slots = 1 + (lab_op_skill.get('active_skill_level', 0) if lab_op_skill else 0)
        used_manufacturing = sum(1 for job in jobs_data if job.get('activity_id') == 1)
        used_research = sum(1 for job in jobs_data if job.get('activity_id') in [3, 4, 5, 8])
        activity = {'manufacturing': {'total': manufacturing_slots, 'used': used_manufacturing}, 'research': {'total': research_slots, 'used': used_research}}
        return jsonify(activity)

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
        else:
            return jsonify({'error': 'Персонаж не найден'}), 404

    return app

# --- Создаем экземпляр приложения для Gunicorn ---
app = create_app()

# Создаем таблицы в контексте приложения
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)