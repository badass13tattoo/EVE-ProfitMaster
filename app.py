import os
import requests
import base64
from flask import Flask, jsonify, request, redirect, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import secrets

# Настройки Flask
app = Flask(__name__)
CORS(app)

# ====================================================================
# НАСТРОЙКА БЕЗОПАСНОСТИ: SECRET_KEY
# ====================================================================
# Этот ключ нужен для шифрования сессий. Он должен быть уникальным и секретным.
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(16))

# Настройки базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ====================================================================
# МОДЕЛЬ БАЗЫ ДАННЫХ
# ====================================================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, unique=True, nullable=False)
    character_name = db.Column(db.String(80), nullable=False)
    access_token = db.Column(db.String(200), nullable=False)
    refresh_token = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.character_name}>'

with app.app_context():
    db.create_all()

# Настройки EVE Online
CLIENT_ID = os.environ.get('EVE_CLIENT_ID')
SECRET_KEY = os.environ.get('EVE_SECRET_KEY')
CALLBACK_URL = 'https://eve-profitmaster.onrender.com/callback'

# ====================================================================
# МАРШРУТЫ ПРИЛОЖЕНИЯ
# ====================================================================

@app.route('/')
def home():
    return "Привет! Это бэкенд для Eve Production Tracker. Он работает!"

@app.route('/login')
def login():
    base_url = 'https://login.eveonline.com/v2/oauth/authorize'
    scopes = [
        'esi-industry.read_character_jobs.v1'
    ]
    scopes_str = ' '.join(scopes)

    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state

    params = {
        'response_type': 'code',
        'redirect_uri': CALLBACK_URL,
        'client_id': CLIENT_ID,
        'scope': scopes_str,
        'state': state
    }
    auth_url = requests.Request('GET', base_url, params=params).prepare().url
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    if state != session.get('oauth_state'):
        return jsonify({'error': 'Неверный параметр state'}), 400
    
    session.pop('oauth_state', None)

    if not code:
        return jsonify({'error': 'Код авторизации не получен'}), 400

    auth_str = f"{CLIENT_ID}:{SECRET_KEY}"
    encoded_auth_str = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')

    token_url = 'https://login.eveonline.com/v2/oauth/token'
    headers = {
        'Authorization': f'Basic {encoded_auth_str}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code
    }
    response = requests.post(token_url, headers=headers, data=data)
    token_data = response.json()

    if 'access_token' in token_data:
        access_token = token_data['access_token']
        refresh_token = token_data['refresh_token']
        return redirect(f"/add_character?token={access_token}&refresh={refresh_token}")
    else:
        return jsonify({'error': 'Не удалось получить токен'}), 400

@app.route('/add_character')
def add_character():
    access_token = request.args.get('token')
    refresh_token = request.args.get('refresh')

    if not access_token or not refresh_token:
        return "Ошибка: не хватает токенов", 400

    verify_url = 'https://login.eveonline.com/oauth/verify'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(verify_url, headers=headers)
    character_data = response.json()

    if response.status_code != 200:
        return "Ошибка при верификации персонажа.", 401

    character_id = character_data['CharacterID']
    character_name = character_data['CharacterName']

    user = User.query.filter_by(character_id=character_id).first()

    if user:
        user.access_token = access_token
        user.refresh_token = refresh_token
        db.session.commit()
    else:
        new_user = User(
            character_id=character_id,
            character_name=character_name,
            access_token=access_token,
            refresh_token=refresh_token
        )
        db.session.add(new_user)
        db.session.commit()

    return redirect(f"http://localhost:8080/?token={access_token}")

@app.route('/get_jobs')
def get_jobs():
    # Получаем все токены из базы данных
    users = User.query.all()
    
    if not users:
        return jsonify({'error': 'Нет сохраненных персонажей. Пожалуйста, авторизуйтесь.'}), 404

    all_jobs = []
    
    # Перебираем каждого персонажа и запрашиваем его работы
    for user in users:
        access_token = user.access_token
        character_id = user.character_id

        # Получаем список производственных работ
        jobs_url = f'https://esi.evetech.net/latest/characters/{character_id}/industry/jobs/'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(jobs_url, headers=headers)
        
        if response.status_code == 200:
            jobs_data = response.json()
            # Добавляем данные о персонаже в каждую работу
            for job in jobs_data:
                job['character_name'] = user.character_name
            all_jobs.extend(jobs_data)
        else:
            print(f"Ошибка при получении данных для персонажа {user.character_name}: {response.status_code}")
            # Пока что не останавливаемся, просто пропускаем этого персонажа

    return jsonify(all_jobs)

if __name__ == '__main__':
    app.run(debug=True)