import base64
from flask import Flask, request, redirect, jsonify, session
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app) # Разрешаем кросс-доменные запросы
app.secret_key = 'some_super_secret_key' # Секретный ключ для сессий

# Твои данные из Eve Online Developer
CLIENT_ID = 'fb702fa78148403c9542f98190ec84da'
SECRET_KEY = 'xqIz7s8drtUCchn19YRLdN44SAnNOOfTtowygNIK'
# Твой публичный URL, который мы используем для обратного вызова
CALLBACK_URL = 'https://eve-profitmaster.onrender.com/callback'

# EVE SSO endpoints
AUTH_URL = 'https://login.eveonline.com/v2/oauth/authorize'
TOKEN_URL = 'https://login.eveonline.com/v2/oauth/token'

@app.route('/')
def home():
    return "Привет! Это бэкенд. Авторизируйся через фронтенд."

@app.route('/login')
def login():
    # Создаем URL для авторизации
    scopes = 'esi-calendar.respond_calendar_events.v1 esi-skills.read_skills.v1 esi-wallet.read_character_wallet.v1 esi-assets.read_assets.v1 esi-planets.manage_planets.v1 esi-markets.structure_markets.v1 esi-industry.read_character_jobs.v1 esi-markets.read_character_orders.v1 esi-characters.read_blueprints.v1'
    auth_url = (f"{AUTH_URL}?response_type=code&redirect_uri={CALLBACK_URL}"
                f"&client_id={CLIENT_ID}&scope={scopes}")
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Получаем код авторизации от EVE Online
    code = request.args.get('code')
    
    # Обмениваем код на токен
    auth_string = f"{CLIENT_ID}:{SECRET_KEY}"
    encoded_auth_string = base64.b64encode(auth_string.encode()).decode()

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {encoded_auth_string}'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
    }
    
    response = requests.post(TOKEN_URL, data=data, headers=headers)
    token_data = response.json()
    
    if 'access_token' in token_data:
        # Сохраняем токены в сессии
        session['access_token'] = token_data['access_token']
        # Теперь перенаправляем пользователя на ФРОНТЕНД
        return redirect('http://localhost:8080')
    else:
        return jsonify({'error': 'Не удалось получить токен'}), 400

@app.route('/get_jobs')
def get_jobs():
    if 'access_token' not in session:
        return jsonify({'error': 'Сначала авторизируйтесь'}), 401

    access_token = session['access_token']

    # 1. Получаем ID персонажа
    verify_url = 'https://login.eveonline.com/oauth/verify'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(verify_url, headers=headers)
    
    if response.status_code != 200:
        return jsonify({'error': 'Ошибка при верификации токена'}), 401

    character_data = response.json()
    character_id = character_data['characterID']

    # 2. Получаем список производственных работ
    jobs_url = f'https://esi.evetech.net/latest/characters/{character_id}/industry/jobs/'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(jobs_url, headers=headers)
    
    if response.status_code == 200:
        jobs_data = response.json()
        return jsonify(jobs_data)
    else:
        return jsonify({'error': f'Не удалось получить данные о работах. Код ошибки: {response.status_code}'}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
