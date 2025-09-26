# Обновление EVE SSO для работы с продакшеном

## 🚨 ВАЖНО: Обновите callback URL в EVE приложении

### Шаг 1: Обновите EVE приложение

1. Перейдите на https://developers.eveonline.com/
2. Войдите в ваш аккаунт
3. Найдите приложение "EVE Profit Master"
4. **Измените callback URL на:**
   ```
   https://eve-profitmaster.onrender.com/callback
   ```

### Шаг 2: Проверьте настройки

Убедитесь что в приложении указаны правильные разрешения:

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

### Шаг 3: Тестирование

После обновления callback URL:

1. Откройте https://eve-profitmaster.onrender.com
2. Нажмите на кнопку авторизации EVE
3. Авторизуйтесь в EVE Online
4. Вы будете перенаправлены обратно в приложение с реальными данными

## Текущий статус

✅ **Backend**: Работает на https://eve-profitmaster.onrender.com
✅ **Frontend**: Работает локально на http://localhost:8080
✅ **База данных**: Подключена к PostgreSQL
✅ **EVE SSO**: Настроен (требует обновления callback URL)

## Проблема с пустой страницей

Проблема была в том, что:

1. Frontend пытался подключиться к localhost:5000
2. Но backend работает на продакшене
3. Callback URL указывал на неправильный адрес

**Исправлено:**

- Frontend теперь подключается к продакшен backend
- Callback URL обновлен для перенаправления на фронтенд
- Добавлена проверка доступности backend перед авторизацией

## Следующие шаги

1. **Обновите callback URL** в EVE приложении
2. **Протестируйте авторизацию** на https://eve-profitmaster.onrender.com
3. **Проверьте загрузку данных** после авторизации

После обновления callback URL авторизация будет работать корректно! 🚀
