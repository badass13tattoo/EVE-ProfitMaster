# Руководство по миграции на новую архитектуру

## Обзор

Это руководство описывает процесс миграции с существующего `app.py` на новую архитектуру `app_new.py`.

## Преимущества новой архитектуры

1. **Разделение ответственности** - Код разделен на сервисы, контроллеры и модели
2. **Лучшая тестируемость** - Каждый компонент можно тестировать отдельно
3. **Масштабируемость** - Легко добавлять новые функции
4. **Кэширование** - Улучшенная система кэширования
5. **Обработка ошибок** - Централизованная обработка ошибок
6. **Документация** - Полная документация API

## Структура новой архитектуры

```
services/           # Бизнес-логика
├── eve_sso_service.py      # EVE SSO аутентификация
├── esi_data_service.py     # Сбор данных из ESI
├── cache_service.py        # Управление кэшем
├── business_logic_service.py # Бизнес-логика
└── market_data_service.py  # Рыночные данные

controllers/        # API контроллеры
├── auth_controller.py      # Аутентификация
├── character_controller.py # Персонажи
└── market_controller.py    # Рыночные данные

models/            # Модели данных
├── user.py                # Пользователи
├── project.py             # Проекты
├── cache_entry.py         # Кэш
└── market_data.py         # Рыночные данные
```

## Пошаговая миграция

### Шаг 1: Подготовка

1. **Создайте резервную копию**

```bash
cp app.py app_old.py
cp requirements.txt requirements_old.txt
```

2. **Установите новые зависимости**

```bash
pip install -r requirements_new.txt
```

### Шаг 2: Тестирование новой архитектуры

1. **Запустите новое приложение**

```bash
python app_new.py
```

2. **Проверьте работоспособность**

```bash
curl http://localhost:5000/health
```

3. **Протестируйте основные функции**
   - Аутентификация через EVE SSO
   - Получение данных персонажей
   - Работа с рыночными данными

### Шаг 3: Обновление фронтенда

Новая архитектура полностью совместима с существующим фронтендом. Все legacy endpoints сохранены:

- `/get_characters` → `/api/characters`
- `/get_character_details/{id}` → `/api/characters/{id}/details`
- `/get_jobs` → `/api/characters/{id}/jobs`
- И т.д.

### Шаг 4: Переключение на новую архитектуру

1. **Остановите старое приложение**

```bash
# Если используете systemd
sudo systemctl stop eve-profitmaster

# Если используете PM2
pm2 stop eve-profitmaster

# Если используете Docker
docker stop eve-profitmaster
```

2. **Замените файлы**

```bash
mv app.py app_legacy.py
mv app_new.py app.py
```

3. **Обновите зависимости**

```bash
mv requirements.txt requirements_legacy.txt
mv requirements_new.txt requirements.txt
pip install -r requirements.txt
```

4. **Запустите новое приложение**

```bash
python app.py
```

### Шаг 5: Проверка работоспособности

1. **Проверьте health endpoint**

```bash
curl http://localhost:5000/health
```

2. **Протестируйте основные функции**

   - Вход через EVE SSO
   - Получение данных персонажей
   - Работа с планетарной индустрией

3. **Проверьте логи**

```bash
# Если используете systemd
sudo journalctl -u eve-profitmaster -f

# Если используете PM2
pm2 logs eve-profitmaster
```

## Новые возможности

### 1. Улучшенное кэширование

```python
# Старый способ
type_cache = {}
location_cache = {}

# Новый способ
cache_service = CacheService(db)
cache_service.set('key', data, ttl=3600)
cached_data = cache_service.get('key')
```

### 2. Централизованная обработка ошибок

```python
# Старый способ
try:
    # код
except Exception as e:
    print(f"Error: {e}")
    return jsonify({'error': str(e)}), 500

# Новый способ
try:
    # код
except Exception as e:
    logger.error(f"Error: {e}")
    return jsonify({'error': 'Internal server error'}), 500
```

### 3. Модульная архитектура

```python
# Старый способ - все в одном файле
def get_character_details(character_id):
    # 50+ строк кода

# Новый способ - разделение по сервисам
class CharacterController:
    def get_character_details(self, user):
        skills = self.esi_service.get_character_skills(user.character_id, user.access_token)
        limits = self.business_logic_service.calculate_activity_limits(skills)
        return limits
```

## Обратная совместимость

Все существующие endpoints сохранены:

### Legacy endpoints (сохранены)

- `GET /get_characters`
- `GET /get_character_details/{id}`
- `GET /get_jobs`
- `GET /get_character_planets/{id}`
- `GET /get_character_skills/{id}`
- `GET /get_character_blueprints/{id}`
- `GET /get_character_portrait/{id}`
- `GET /get_type_info/{id}`
- `GET /get_location_info/{id}`
- `POST /remove_character`
- `POST /reset_database`

### Новые API endpoints

- `GET /api/characters`
- `GET /api/characters/{id}/details`
- `GET /api/characters/{id}/jobs`
- `GET /api/characters/{id}/planets`
- `GET /api/characters/{id}/skills`
- `GET /api/characters/{id}/blueprints`
- `GET /api/characters/{id}/assets`
- `GET /api/characters/{id}/portrait`
- `DELETE /api/characters/{id}`
- `GET /api/market/types/{id}/prices`
- `GET /api/market/calculate-value`
- И многие другие...

## Откат к старой версии

Если что-то пойдет не так, можно легко откатиться:

1. **Остановите новое приложение**

```bash
sudo systemctl stop eve-profitmaster
```

2. **Верните старые файлы**

```bash
mv app.py app_new.py
mv app_legacy.py app.py
mv requirements.txt requirements_new.txt
mv requirements_legacy.txt requirements.txt
```

3. **Запустите старое приложение**

```bash
python app.py
```

## Мониторинг после миграции

### 1. Проверка производительности

```bash
# Мониторинг использования памяти
htop

# Мониторинг базы данных
sudo -u postgres psql eve_profitmaster -c "SELECT * FROM pg_stat_activity;"
```

### 2. Проверка логов

```bash
# Логи приложения
sudo journalctl -u eve-profitmaster -f

# Логи базы данных
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### 3. Проверка API

```bash
# Health check
curl http://localhost:5000/health

# Тест основных функций
curl http://localhost:5000/api/characters
```

## Устранение проблем

### Проблема: Ошибка импорта модулей

**Решение:**

```bash
# Убедитесь, что все файлы на месте
ls -la services/
ls -la controllers/
ls -la models/

# Проверьте PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Проблема: Ошибка подключения к базе данных

**Решение:**

```bash
# Проверьте DATABASE_URL
echo $DATABASE_URL

# Проверьте подключение
psql $DATABASE_URL -c "SELECT 1;"
```

### Проблема: Ошибка EVE SSO

**Решение:**

```bash
# Проверьте переменные окружения
echo $EVE_CLIENT_ID
echo $EVE_SECRET_KEY

# Проверьте callback URL в настройках EVE SSO
```

## Рекомендации

1. **Тестируйте в dev окружении** - Сначала протестируйте на dev сервере
2. **Создайте резервные копии** - Всегда создавайте бэкапы перед миграцией
3. **Мониторьте логи** - Следите за логами после миграции
4. **Постепенное внедрение** - Можно запустить оба приложения параллельно
5. **Документируйте изменения** - Записывайте все изменения

## Поддержка

Если у вас возникли проблемы с миграцией:

1. Проверьте логи приложения
2. Убедитесь, что все зависимости установлены
3. Проверьте переменные окружения
4. Создайте issue в репозитории с подробным описанием проблемы
