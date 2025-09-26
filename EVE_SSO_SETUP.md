# Настройка EVE Online SSO для EVE Profit Master

## Шаг 1: Создание EVE Online Application

1. Перейдите на [EVE Developers Portal](https://developers.eveonline.com/)
2. Войдите используя ваш EVE Online аккаунт
3. Создайте новое приложение (Application)
4. Заполните следующие поля:

   - **Application Name**: `EVE Profit Master`
   - **Description**: `Production tracking tool for EVE Online industrialists`
   - **Connection Type**: `Authentication & API Access`
   - **Permissions/Scopes**: Выберите следующие разрешения:
     - `publicData` - базовая информация о персонаже
     - `esi-calendar.respond_calendar_events.v1` - календарь событий
     - `esi-skills.read_skills.v1` - чтение навыков
     - `esi-wallet.read_character_wallet.v1` - чтение кошелька
     - `esi-assets.read_assets.v1` - чтение ассетов
     - `esi-planets.manage_planets.v1` - управление планетами
     - `esi-markets.structure_markets.v1` - рынки структур
     - `esi-industry.read_character_jobs.v1` - чтение производственных работ
     - `esi-markets.read_character_orders.v1` - чтение ордеров персонажа
     - `esi-characters.read_blueprints.v1` - чтение чертежей

5. **Callback URL**:
   - Для разработки: `http://localhost:5000/callback`
   - Для продакшена: `https://your-domain.com/callback`

## Шаг 2: Настройка переменных окружения

Создайте файл `.env` в корневой папке проекта:

```env
# EVE Online SSO Configuration
EVE_CLIENT_ID=ваш_client_id_здесь
EVE_SECRET_KEY=ваш_secret_key_здесь

# Flask Configuration
FLASK_SECRET_KEY=ваш_секретный_ключ_flask

# Database Configuration
# Для локальной разработки:
DATABASE_URL=sqlite:///instance/database.db
# Для продакшена (PostgreSQL):
# DATABASE_URL=postgresql://username:password@localhost/eve_profitmaster

# Environment
FLASK_ENV=development
```

**ВАЖНО**: Замените `ваш_client_id_здесь` и `ваш_secret_key_здесь` на реальные значения из вашего EVE приложения!

## Шаг 3: Локальный запуск

### Backend (Flask):

```bash
# Активируйте виртуальное окружение
venv\Scripts\activate  # Windows
# или
source venv/bin/activate  # Linux/Mac

# Установите зависимости (если еще не установлены)
pip install -r requirements.txt

# Запустите Flask сервер
python app.py
```

Сервер будет доступен по адресу: `http://localhost:5000`

### Frontend (Vue.js):

```bash
# Перейдите в папку frontend
cd eve-production-tracker-frontend

# Установите зависимости (если еще не установлены)
npm install

# Запустите dev сервер
npm run serve
```

Фронтенд будет доступен по адресу: `http://localhost:8080`

## Шаг 4: Первый запуск

1. Откройте браузер и перейдите на `http://localhost:8080`
2. Нажмите кнопку "Войти через EVE Online"
3. Авторизуйтесь в EVE Online SSO
4. После успешной авторизации вы будете перенаправлены обратно в приложение
5. Приложение автоматически загрузит ваши реальные данные из EVE Online

## Возможные проблемы и решения

### Ошибка CORS

Если возникают CORS ошибки, убедитесь что в `app.py` правильно настроен CORS для локальной разработки.

### Ошибка "Client ID not found"

- Проверьте что `.env` файл создан в корневой папке проекта
- Убедитесь что переменная `EVE_CLIENT_ID` установлена правильно
- Перезапустите Flask сервер после изменения `.env`

### Ошибка callback URL

- В настройках EVE приложения убедитесь что callback URL точно соответствует:
  - `http://localhost:5000/callback` для разработки
  - Ваш реальный домен для продакшена

### База данных не создается

- Убедитесь что папка `instance` существует в корне проекта
- Проверьте права на запись в эту папку
- При первом запуске база данных SQLite создается автоматически

## Структура данных

После авторизации приложение будет получать следующие данные из EVE Online:

- **Персонажи**: Список ваших авторизованных персонажей
- **Производственные работы**: Все активные и завершенные работы
- **Навыки**: Уровни промышленных навыков для расчета слотов
- **Планеты**: Информация о занятых планетах для PI

## Переход на продакшен

Для развертывания на продакшен сервере:

1. Измените `FLASK_ENV=production` в `.env`
2. Используйте PostgreSQL вместо SQLite
3. Обновите callback URL в настройках EVE приложения
4. Настройте веб-сервер (nginx + gunicorn)

## Безопасность

- **Никогда не коммитьте `.env` файл в git**
- Регулярно обновляйте `FLASK_SECRET_KEY`
- Используйте HTTPS в продакшене
- Ограничьте доступ к базе данных

---

Теперь ваше приложение готово к работе с реальными данными EVE Online! 🚀
