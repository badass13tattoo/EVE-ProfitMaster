# EVE Profit Master Backend API Documentation

## Обзор

EVE Profit Master Backend API предоставляет комплексное решение для планирования производства в EVE Online. API построен с использованием Flask и следует принципам RESTful архитектуры.

## Архитектура

### Сервисы

1. **EVESSOService** - Управление аутентификацией EVE SSO
2. **ESIDataService** - Сбор данных из EVE ESI API
3. **CacheService** - Управление кэшированием данных
4. **BusinessLogicService** - Бизнес-логика и обработка данных
5. **MarketDataService** - Работа с рыночными данными

### Контроллеры

1. **AuthController** - Аутентификация и управление пользователями
2. **CharacterController** - Операции с персонажами
3. **MarketController** - Рыночные данные

### Модели данных

1. **User** - Пользователи/персонажи
2. **Project** - Проекты производства
3. **CacheEntry** - Кэш записи
4. **MarketData** - Рыночные данные

## API Endpoints

### Аутентификация

#### `GET /login`

Инициирует процесс аутентификации через EVE SSO.

**Ответ:** Перенаправление на EVE SSO

#### `GET /callback`

Обрабатывает callback от EVE SSO.

**Параметры:**

- `code` (string) - Код авторизации
- `state` (string) - Состояние для безопасности

**Ответ:** Перенаправление на фронтенд

### Персонажи

#### `GET /api/characters`

Получает список авторизованных персонажей.

**Ответ:**

```json
[
  {
    "id": 1,
    "character_id": 123456789,
    "character_name": "Character Name",
    "corporation_id": 987654321,
    "alliance_id": 456789123,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### `GET /api/characters/{character_id}/details`

Получает детальную информацию о персонаже включая лимиты активности.

**Ответ:**

```json
{
  "lines": {
    "manufacturing": {
      "total": 10,
      "used": 3
    },
    "research": {
      "total": 5,
      "used": 1
    },
    "reactions": {
      "total": 2,
      "used": 0
    }
  },
  "planets": {
    "total": 4,
    "used": 2
  }
}
```

#### `GET /api/characters/{character_id}/jobs`

Получает данные о работах персонажа.

**Ответ:**

```json
{
  "123456789": [
    {
      "job_id": 12345,
      "product_name": "Tritanium",
      "product_type_id": 34,
      "activity_id": 1,
      "start_date": "2024-01-01T00:00:00Z",
      "end_date": "2024-01-02T00:00:00Z",
      "location_name": "Jita IV - Moon 4 - Caldari Navy Assembly Plant",
      "location_id": 60003760,
      "status": "in-progress",
      "runs": 1,
      "cost": 1000000
    }
  ]
}
```

#### `GET /api/characters/{character_id}/planets`

Получает данные о планетах персонажа.

**Ответ:**

```json
[
  {
    "planet_id": 40000001,
    "planet_name": "Planet Name",
    "solar_system_id": 30000001,
    "solar_system_name": "System Name",
    "planet_type": 11,
    "needs_attention": false,
    "active_extractors": 2,
    "active_jobs": 2,
    "jobs": [
      {
        "job_id": "planet_40000001_extractor_12345",
        "product_name": "Extractor on Planet Name",
        "product_type_id": 2250,
        "activity_id": 7,
        "start_date": "2024-01-01T00:00:00Z",
        "end_date": "2024-01-02T00:00:00Z",
        "location_name": "Planet Name - System Name",
        "location_id": 40000001,
        "status": "active",
        "runs": 1,
        "cost": 0,
        "planet_id": 40000001,
        "extractor_id": 12345,
        "is_planet_job": true
      }
    ]
  }
]
```

#### `GET /api/characters/{character_id}/skills`

Получает навыки персонажа.

#### `GET /api/characters/{character_id}/blueprints`

Получает чертежи персонажа.

#### `GET /api/characters/{character_id}/assets`

Получает активы персонажа.

#### `GET /api/characters/{character_id}/portrait`

Получает URL портрета персонажа.

#### `DELETE /api/characters/{character_id}`

Удаляет персонажа из базы данных.

### Рыночные данные

#### `GET /api/market/types/{type_id}/prices`

Получает цены для конкретного типа предмета.

**Параметры:**

- `region_id` (int, optional) - ID региона (по умолчанию 10000002)

**Ответ:**

```json
{
  "type_id": 34,
  "region_id": 10000002,
  "buy_price": 5.5,
  "sell_price": 5.6,
  "buy_volume": 1000000,
  "sell_volume": 500000,
  "spread": 0.1
}
```

#### `GET /api/market/regions/{region_id}/orders`

Получает рыночные ордера для региона.

**Параметры:**

- `type_id` (int, optional) - ID типа предмета

#### `GET /api/market/regions/{region_id}/prices`

Получает цены для региона.

#### `GET /api/market/calculate-value`

Вычисляет рыночную стоимость количества предметов.

**Параметры:**

- `type_id` (int) - ID типа предмета
- `quantity` (int) - Количество
- `region_id` (int, optional) - ID региона

#### `GET /api/market/regions/{region_id}`

Получает информацию о регионе.

#### `GET /api/market/groups`

Получает группы рынка.

#### `GET /api/market/groups/{group_id}`

Получает информацию о группе рынка.

### Утилиты

#### `GET /api/types/{type_id}`

Получает информацию о типе предмета.

#### `GET /api/locations/{location_id}`

Получает информацию о локации.

#### `GET /health`

Проверка состояния API.

#### `POST /api/reset`

Сброс базы данных (удаление всех пользователей).

## Legacy Endpoints

Для обратной совместимости доступны следующие legacy endpoints:

- `GET /get_characters`
- `GET /get_character_details/{character_id}`
- `GET /get_jobs`
- `GET /get_character_planets/{character_id}`
- `GET /get_character_skills/{character_id}`
- `GET /get_character_blueprints/{character_id}`
- `GET /get_character_portrait/{character_id}`
- `GET /get_type_info/{type_id}`
- `GET /get_location_info/{location_id}`
- `POST /remove_character`
- `POST /reset_database`

## Обработка ошибок

API возвращает стандартные HTTP коды состояния:

- `200` - Успешный запрос
- `400` - Неверный запрос
- `401` - Не авторизован
- `404` - Не найдено
- `500` - Внутренняя ошибка сервера

Ошибки возвращаются в формате JSON:

```json
{
  "error": "Описание ошибки"
}
```

## Кэширование

API использует многоуровневое кэширование:

1. **Память** - Быстрый доступ к часто используемым данным
2. **База данных** - Долгосрочное хранение кэшированных данных

Время жизни кэша:

- Навыки: 1 час
- Работы: 5 минут
- Планеты: 30 минут
- Типы предметов: 24 часа
- Локации: 24 часа

## Аутентификация

API использует EVE SSO для аутентификации. Процесс:

1. Пользователь переходит на `/login`
2. Перенаправление на EVE SSO
3. Пользователь авторизуется в EVE
4. EVE перенаправляет на `/callback`
5. API сохраняет токены и перенаправляет на фронтенд

## Развертывание

### Переменные окружения

- `EVE_CLIENT_ID` - ID клиента EVE SSO
- `EVE_SECRET_KEY` - Секретный ключ EVE SSO
- `DATABASE_URL` - URL базы данных PostgreSQL
- `FLASK_SECRET_KEY` - Секретный ключ Flask
- `FLASK_ENV` - Окружение (development/production)

### Запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск в режиме разработки
python app.py

# Запуск с Gunicorn (продакшн)
gunicorn app:app
```

## Мониторинг

API предоставляет endpoint `/health` для проверки состояния:

```json
{
  "status": "healthy",
  "database_connected": true,
  "user_count": 5,
  "environment_vars": {
    "EVE_CLIENT_ID": true,
    "EVE_SECRET_KEY": true,
    "DATABASE_URL": true
  }
}
```
