# Исправление проблемы EVE SSO (Ошибка 400)

## 🚨 Проблема

При нажатии кнопки авторизации возникает ошибка 400 с URL:

```
https://login.eveonline.com/v2/oauth/authorize?response_type=code&redirect_uri=https://eve-profitmaster.onrender.com/callback&client_id=fb702fa78148403c9542f98190ec84da&scope=...&state=...
```

## ✅ Решение

### 1. Обновите EVE приложение на https://developers.eveonline.com/

**Callback URL должен быть:**

```
https://eve-profitmaster.onrender.com/callback
```

**Scopes должны включать:**

- `publicData`
- `esi-calendar.respond_calendar_events.v1`
- `esi-skills.read_skills.v1`
- `esi-wallet.read_character_wallet.v1`
- `esi-assets.read_assets.v1`
- `esi-planets.manage_planets.v1`
- `esi-markets.structure_markets.v1`
- `esi-industry.read_character_jobs.v1`
- `esi-markets.read_character_orders.v1`
- `esi-characters.read_blueprints.v1`

### 2. Проверьте переменные окружения

Убедитесь что в вашем `.env` файле установлены:

```env
EVE_CLIENT_ID=fb702fa78148403c9542f98190ec84da
EVE_SECRET_KEY=ваш_secret_key_здесь
FLASK_ENV=production
```

### 3. Перезапустите приложение

После обновления настроек EVE приложения:

1. Перезапустите backend сервер
2. Обновите страницу фронтенда
3. Попробуйте авторизацию снова

## 🔍 Диагностика

### Проверка настроек EVE приложения:

1. Перейдите на https://developers.eveonline.com/
2. Войдите в ваш аккаунт
3. Найдите приложение "EVE Profit Master"
4. Проверьте что Callback URL точно соответствует: `https://eve-profitmaster.onrender.com/callback`
5. Убедитесь что все необходимые scopes выбраны

### Проверка переменных окружения:

```bash
# Запустите тест
python test_eve_sso.py
```

### Проверка backend:

```bash
# Проверьте health endpoint
curl https://eve-profitmaster.onrender.com/health
```

## 📝 Изменения в коде

Обновлены следующие файлы:

- `app.py` - обновлены scopes и исправлен redirect URL
- `test_eve_sso.py` - обновлены scopes для тестирования
- `EVE_SSO_SETUP.md` - обновлена документация
- `EVE_SSO_UPDATE.md` - обновлены scopes

## 🚀 После исправления

1. **Обновите EVE приложение** с правильными настройками
2. **Перезапустите backend** сервер
3. **Протестируйте авторизацию** на https://eve-profitmaster.onrender.com
4. **Проверьте загрузку данных** после успешной авторизации

## ❗ Важные моменты

- Callback URL должен точно совпадать с тем, что указано в EVE приложении
- Все scopes должны быть выбраны в настройках EVE приложения
- Переменные окружения должны быть установлены правильно
- Backend должен быть перезапущен после изменений

После выполнения всех шагов авторизация должна работать корректно! 🎉
