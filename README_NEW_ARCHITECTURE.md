# EVE Profit Master Backend - Новая Архитектура

## 🚀 Обзор

EVE Profit Master Backend - это комплексное решение для планирования производства в EVE Online, построенное с использованием современной архитектуры и лучших практик разработки.

## ✨ Основные возможности

- **EVE SSO Аутентификация** - Безопасный вход через EVE Online
- **Сбор данных ESI** - Получение данных о персонажах, работах, планетах
- **Рыночные данные** - Цены, ордера, расчет стоимости
- **Планирование проектов** - Создание и управление производственными проектами
- **Кэширование** - Многоуровневое кэширование для оптимизации
- **REST API** - Современный API с полной документацией

## 🏗️ Архитектура

### Сервисы (Services)

- **EVESSOService** - Управление аутентификацией EVE SSO
- **ESIDataService** - Сбор данных из EVE ESI API
- **CacheService** - Управление кэшированием данных
- **BusinessLogicService** - Бизнес-логика и обработка данных
- **MarketDataService** - Работа с рыночными данными

### Контроллеры (Controllers)

- **AuthController** - Аутентификация и управление пользователями
- **CharacterController** - Операции с персонажами
- **MarketController** - Рыночные данные

### Модели (Models)

- **User** - Пользователи/персонажи
- **Project** - Проекты производства
- **CacheEntry** - Кэш записи
- **MarketData** - Рыночные данные

## 📁 Структура проекта

```
eve-profitmaster-backend/
├── app.py                 # Основное приложение (legacy)
├── app_new.py            # Новое приложение с архитектурой
├── services/             # Сервисы
│   ├── __init__.py
│   ├── eve_sso_service.py
│   ├── esi_data_service.py
│   ├── cache_service.py
│   ├── business_logic_service.py
│   └── market_data_service.py
├── controllers/          # Контроллеры
│   ├── __init__.py
│   ├── auth_controller.py
│   ├── character_controller.py
│   └── market_controller.py
├── models/              # Модели данных
│   ├── __init__.py
│   ├── user.py
│   ├── project.py
│   ├── cache_entry.py
│   └── market_data.py
├── templates/           # HTML шаблоны
│   └── popup_close.html
├── requirements.txt     # Зависимости (legacy)
├── requirements_new.txt # Новые зависимости
├── API_DOCUMENTATION.md # Документация API
├── DEPLOYMENT_GUIDE.md  # Руководство по развертыванию
├── MIGRATION_GUIDE.md   # Руководство по миграции
└── API_EXAMPLES.md      # Примеры использования API
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements_new.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env`:

```env
EVE_CLIENT_ID=your_eve_client_id
EVE_SECRET_KEY=your_eve_secret_key
DATABASE_URL=postgresql://username:password@localhost:5432/eve_profitmaster
FLASK_SECRET_KEY=your_secret_key
FLASK_ENV=development
```

### 3. Запуск приложения

```bash
python app_new.py
```

Приложение будет доступно по адресу `http://localhost:5000`

## 📚 Документация

- [API Документация](API_DOCUMENTATION.md) - Полная документация API
- [Руководство по развертыванию](DEPLOYMENT_GUIDE.md) - Развертывание на различных платформах
- [Руководство по миграции](MIGRATION_GUIDE.md) - Миграция с старой архитектуры
- [Примеры использования API](API_EXAMPLES.md) - Примеры кода для фронтенда

## 🔧 API Endpoints

### Аутентификация

- `GET /login` - Инициация EVE SSO входа
- `GET /callback` - Обработка callback от EVE SSO

### Персонажи

- `GET /api/characters` - Список персонажей
- `GET /api/characters/{id}/details` - Детали персонажа
- `GET /api/characters/{id}/jobs` - Работы персонажа
- `GET /api/characters/{id}/planets` - Планеты персонажа
- `GET /api/characters/{id}/skills` - Навыки персонажа
- `GET /api/characters/{id}/blueprints` - Чертежи персонажа
- `GET /api/characters/{id}/assets` - Активы персонажа

### Рыночные данные

- `GET /api/market/types/{id}/prices` - Цены на предмет
- `GET /api/market/calculate-value` - Расчет стоимости
- `GET /api/market/regions/{id}/orders` - Рыночные ордера
- `GET /api/market/regions/{id}/prices` - Цены региона

### Утилиты

- `GET /api/types/{id}` - Информация о типе предмета
- `GET /api/locations/{id}` - Информация о локации
- `GET /health` - Проверка состояния API

## 🔄 Обратная совместимость

Новая архитектура полностью совместима с существующим фронтендом. Все legacy endpoints сохранены:

- `/get_characters` → `/api/characters`
- `/get_character_details/{id}` → `/api/characters/{id}/details`
- `/get_jobs` → `/api/characters/{id}/jobs`
- И многие другие...

## 🚀 Развертывание

### Render

```bash
# Настройте переменные окружения в Render
# Запустите: gunicorn app_new:app
```

### Heroku

```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

### VPS

```bash
# Следуйте инструкциям в DEPLOYMENT_GUIDE.md
```

## 🧪 Тестирование

```bash
# Проверка состояния
curl http://localhost:5000/health

# Тест аутентификации
curl http://localhost:5000/login

# Тест API
curl http://localhost:5000/api/characters
```

## 📊 Мониторинг

### Логи

```bash
# Логи приложения
tail -f logs/app.log

# Логи базы данных
tail -f /var/log/postgresql/postgresql-*.log
```

### Метрики

- Health check: `GET /health`
- Количество пользователей
- Статус базы данных
- Переменные окружения

## 🔒 Безопасность

- **EVE SSO** - Официальная аутентификация EVE Online
- **HTTPS** - Рекомендуется для продакшена
- **Валидация данных** - Проверка всех входящих данных
- **Обработка ошибок** - Безопасная обработка ошибок

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Создайте Pull Request

## 📝 Лицензия

MIT License

## 🆘 Поддержка

Если у вас возникли проблемы:

1. Проверьте [документацию](API_DOCUMENTATION.md)
2. Изучите [примеры](API_EXAMPLES.md)
3. Создайте issue в репозитории

## 🔄 Миграция с старой версии

Следуйте [руководству по миграции](MIGRATION_GUIDE.md) для перехода с `app.py` на `app_new.py`.

## 📈 Планы развития

- [ ] Проекты и BOM декомпозиция
- [ ] Расширенная аналитика
- [ ] Уведомления
- [ ] Мобильное приложение
- [ ] API для третьих лиц

---

**EVE Profit Master Backend** - Ваш надежный помощник в планировании производства EVE Online! 🚀
