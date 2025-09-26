# Руководство по развертыванию EVE Profit Master Backend

## Обзор

Это руководство описывает процесс развертывания backend-части EVE Profit Master на различных платформах.

## Архитектура

### Компоненты

1. **Flask Application** - Основное приложение
2. **PostgreSQL Database** - База данных
3. **Redis (опционально)** - Кэш
4. **Nginx (опционально)** - Reverse proxy

### Структура проекта

```
eve-profitmaster-backend/
├── app.py                 # Основное приложение (legacy)
├── app_new.py            # Новое приложение с архитектурой
├── services/             # Сервисы
│   ├── eve_sso_service.py
│   ├── esi_data_service.py
│   ├── cache_service.py
│   ├── business_logic_service.py
│   └── market_data_service.py
├── controllers/          # Контроллеры
│   ├── auth_controller.py
│   ├── character_controller.py
│   └── market_controller.py
├── models/              # Модели данных
│   ├── user.py
│   ├── project.py
│   ├── cache_entry.py
│   └── market_data.py
├── requirements.txt     # Зависимости
└── templates/          # HTML шаблоны
    └── popup_close.html
```

## Локальная разработка

### Требования

- Python 3.8+
- PostgreSQL 12+
- Git

### Установка

1. **Клонирование репозитория**

```bash
git clone <repository-url>
cd eve-profitmaster-backend
```

2. **Создание виртуального окружения**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. **Установка зависимостей**

```bash
pip install -r requirements.txt
```

4. **Настройка переменных окружения**
   Создайте файл `.env`:

```env
EVE_CLIENT_ID=your_eve_client_id
EVE_SECRET_KEY=your_eve_secret_key
DATABASE_URL=postgresql://username:password@localhost:5432/eve_profitmaster
FLASK_SECRET_KEY=your_secret_key
FLASK_ENV=development
```

5. **Настройка базы данных**

```bash
# Создание базы данных
createdb eve_profitmaster

# Инициализация таблиц (автоматически при запуске)
python app_new.py
```

6. **Запуск приложения**

```bash
python app_new.py
```

Приложение будет доступно по адресу `http://localhost:5000`

## Развертывание на Render

### Подготовка

1. **Создание аккаунта на Render**

   - Зарегистрируйтесь на https://render.com
   - Подключите GitHub репозиторий

2. **Настройка EVE SSO**
   - Перейдите в https://developers.eveonline.com/
   - Создайте новое приложение
   - Укажите callback URL: `https://your-app-name.onrender.com/callback`

### Создание сервисов

1. **Web Service**

   - Выберите "New Web Service"
   - Подключите репозиторий
   - Настройки:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app_new:app`
     - **Environment**: Python 3

2. **PostgreSQL Database**
   - Выберите "New PostgreSQL"
   - Выберите план (Free tier доступен)
   - Запишите connection string

### Настройка переменных окружения

В настройках Web Service добавьте:

```
EVE_CLIENT_ID=your_eve_client_id
EVE_SECRET_KEY=your_eve_secret_key
DATABASE_URL=postgresql://user:pass@host:port/dbname
FLASK_SECRET_KEY=your_secret_key
FLASK_ENV=production
```

### Деплой

1. Нажмите "Deploy"
2. Дождитесь завершения сборки
3. Проверьте логи на наличие ошибок

## Развертывание на Heroku

### Подготовка

1. **Установка Heroku CLI**

```bash
# Ubuntu/Debian
sudo apt-get install heroku

# macOS
brew install heroku

# Windows
# Скачайте с https://devcenter.heroku.com/articles/heroku-cli
```

2. **Создание приложения**

```bash
heroku create your-app-name
```

3. **Добавление PostgreSQL**

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### Настройка

1. **Создание Procfile**

```
web: gunicorn app_new:app
```

2. **Настройка переменных окружения**

```bash
heroku config:set EVE_CLIENT_ID=your_eve_client_id
heroku config:set EVE_SECRET_KEY=your_eve_secret_key
heroku config:set FLASK_SECRET_KEY=your_secret_key
heroku config:set FLASK_ENV=production
```

3. **Деплой**

```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## Развертывание на VPS

### Требования

- Ubuntu 20.04+ / CentOS 8+
- 2GB RAM минимум
- 20GB дискового пространства

### Установка

1. **Обновление системы**

```bash
sudo apt update && sudo apt upgrade -y
```

2. **Установка Python и зависимостей**

```bash
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx git
```

3. **Настройка PostgreSQL**

```bash
sudo -u postgres createuser --interactive
sudo -u postgres createdb eve_profitmaster
```

4. **Клонирование и настройка приложения**

```bash
git clone <repository-url>
cd eve-profitmaster-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Настройка systemd сервиса**
   Создайте файл `/etc/systemd/system/eve-profitmaster.service`:

```ini
[Unit]
Description=EVE Profit Master Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/eve-profitmaster-backend
Environment=PATH=/path/to/eve-profitmaster-backend/venv/bin
ExecStart=/path/to/eve-profitmaster-backend/venv/bin/gunicorn --workers 3 --bind unix:eve-profitmaster.sock -m 007 app_new:app
Restart=always

[Install]
WantedBy=multi-user.target
```

6. **Настройка Nginx**
   Создайте файл `/etc/nginx/sites-available/eve-profitmaster`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/eve-profitmaster-backend/eve-profitmaster.sock;
    }
}
```

7. **Запуск сервисов**

```bash
sudo systemctl enable eve-profitmaster
sudo systemctl start eve-profitmaster
sudo systemctl enable nginx
sudo systemctl restart nginx
```

## Мониторинг и логи

### Логи приложения

```bash
# Render
# Логи доступны в веб-интерфейсе

# Heroku
heroku logs --tail

# VPS
sudo journalctl -u eve-profitmaster -f
```

### Мониторинг базы данных

```bash
# PostgreSQL
sudo -u postgres psql eve_profitmaster
```

### Проверка состояния

```bash
curl https://your-app-url/health
```

## Безопасность

### Рекомендации

1. **Используйте HTTPS** - Настройте SSL сертификат
2. **Ограничьте доступ к базе данных** - Используйте firewall
3. **Регулярно обновляйте зависимости** - `pip install --upgrade -r requirements.txt`
4. **Используйте сильные пароли** - Для всех сервисов
5. **Настройте мониторинг** - Отслеживайте ошибки и производительность

### Переменные окружения

Никогда не коммитьте файлы с секретными данными:

- `.env`
- `config.py` с паролями
- Ключи и токены

## Масштабирование

### Горизонтальное масштабирование

1. **Load Balancer** - Nginx или CloudFlare
2. **Несколько экземпляров** - Запуск на разных портах
3. **База данных** - Read replicas

### Вертикальное масштабирование

1. **Увеличение RAM** - Больше кэша
2. **Более быстрый CPU** - Лучшая производительность
3. **SSD диски** - Быстрее I/O

## Резервное копирование

### База данных

```bash
# Создание бэкапа
pg_dump eve_profitmaster > backup.sql

# Восстановление
psql eve_profitmaster < backup.sql
```

### Автоматическое резервное копирование

```bash
# Crontab
0 2 * * * pg_dump eve_profitmaster > /backups/eve_profitmaster_$(date +\%Y\%m\%d).sql
```

## Устранение неполадок

### Частые проблемы

1. **Ошибка подключения к базе данных**

   - Проверьте DATABASE_URL
   - Убедитесь, что PostgreSQL запущен

2. **Ошибка EVE SSO**

   - Проверьте EVE_CLIENT_ID и EVE_SECRET_KEY
   - Убедитесь, что callback URL правильный

3. **Ошибка импорта модулей**

   - Проверьте PYTHONPATH
   - Убедитесь, что все зависимости установлены

4. **Ошибка 500**
   - Проверьте логи приложения
   - Убедитесь, что все переменные окружения установлены

### Логи для отладки

```bash
# Включение debug режима
export FLASK_ENV=development
export FLASK_DEBUG=1
```

## Обновление

### Процесс обновления

1. **Создание бэкапа**

```bash
pg_dump eve_profitmaster > backup_before_update.sql
```

2. **Обновление кода**

```bash
git pull origin main
pip install -r requirements.txt
```

3. **Применение миграций** (если есть)

```bash
python migrate.py
```

4. **Перезапуск сервиса**

```bash
sudo systemctl restart eve-profitmaster
```

5. **Проверка работоспособности**

```bash
curl https://your-app-url/health
```
