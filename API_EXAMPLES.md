# Примеры использования EVE Profit Master API

## Аутентификация

### 1. Инициация входа

```javascript
// Перенаправление на EVE SSO
window.location.href = 'https://your-api-url.com/login';
```

### 2. Обработка callback

```javascript
// После успешной авторизации пользователь перенаправляется на:
// https://your-frontend-url.com/?auth=success

// Проверка успешной авторизации
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('auth') === 'success') {
    console.log('Авторизация успешна!');
    // Загружаем данные пользователя
    loadUserData();
}
```

## Работа с персонажами

### 1. Получение списка персонажей

```javascript
async function getCharacters() {
    try {
        const response = await fetch('https://your-api-url.com/api/characters');
        const characters = await response.json();
        console.log('Персонажи:', characters);
        return characters;
    } catch (error) {
        console.error('Ошибка получения персонажей:', error);
    }
}
```

### 2. Получение детальной информации о персонаже

```javascript
async function getCharacterDetails(characterId) {
    try {
        const response = await fetch(`https://your-api-url.com/api/characters/${characterId}/details`);
        const details = await response.json();
        console.log('Детали персонажа:', details);
        return details;
    } catch (error) {
        console.error('Ошибка получения деталей персонажа:', error);
    }
}
```

### 3. Получение работ персонажа

```javascript
async function getCharacterJobs(characterId) {
    try {
        const response = await fetch(`https://your-api-url.com/api/characters/${characterId}/jobs`);
        const jobs = await response.json();
        console.log('Работы персонажа:', jobs);
        return jobs;
    } catch (error) {
        console.error('Ошибка получения работ:', error);
    }
}
```

### 4. Получение планет персонажа

```javascript
async function getCharacterPlanets(characterId) {
    try {
        const response = await fetch(`https://your-api-url.com/api/characters/${characterId}/planets`);
        const planets = await response.json();
        console.log('Планеты персонажа:', planets);
        return planets;
    } catch (error) {
        console.error('Ошибка получения планет:', error);
    }
}
```

## Рыночные данные

### 1. Получение цен на предмет

```javascript
async function getItemPrices(typeId, regionId = 10000002) {
    try {
        const response = await fetch(`https://your-api-url.com/api/market/types/${typeId}/prices?region_id=${regionId}`);
        const prices = await response.json();
        console.log('Цены на предмет:', prices);
        return prices;
    } catch (error) {
        console.error('Ошибка получения цен:', error);
    }
}
```

### 2. Расчет рыночной стоимости

```javascript
async function calculateMarketValue(typeId, quantity, regionId = 10000002) {
    try {
        const response = await fetch(`https://your-api-url.com/api/market/calculate-value?type_id=${typeId}&quantity=${quantity}&region_id=${regionId}`);
        const value = await response.json();
        console.log('Рыночная стоимость:', value);
        return value;
    } catch (error) {
        console.error('Ошибка расчета стоимости:', error);
    }
}
```

### 3. Получение рыночных ордеров

```javascript
async function getMarketOrders(regionId, typeId = null) {
    try {
        let url = `https://your-api-url.com/api/market/regions/${regionId}/orders`;
        if (typeId) {
            url += `?type_id=${typeId}`;
        }
        const response = await fetch(url);
        const orders = await response.json();
        console.log('Рыночные ордера:', orders);
        return orders;
    } catch (error) {
        console.error('Ошибка получения ордеров:', error);
    }
}
```

## Утилиты

### 1. Получение информации о типе предмета

```javascript
async function getTypeInfo(typeId) {
    try {
        const response = await fetch(`https://your-api-url.com/api/types/${typeId}`);
        const typeInfo = await response.json();
        console.log('Информация о типе:', typeInfo);
        return typeInfo;
    } catch (error) {
        console.error('Ошибка получения информации о типе:', error);
    }
}
```

### 2. Получение информации о локации

```javascript
async function getLocationInfo(locationId) {
    try {
        const response = await fetch(`https://your-api-url.com/api/locations/${locationId}`);
        const locationInfo = await response.json();
        console.log('Информация о локации:', locationInfo);
        return locationInfo;
    } catch (error) {
        console.error('Ошибка получения информации о локации:', error);
    }
}
```

## Полный пример приложения

```javascript
class EVEProfitMasterAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Персонажи
    async getCharacters() {
        return this.request('/api/characters');
    }

    async getCharacterDetails(characterId) {
        return this.request(`/api/characters/${characterId}/details`);
    }

    async getCharacterJobs(characterId) {
        return this.request(`/api/characters/${characterId}/jobs`);
    }

    async getCharacterPlanets(characterId) {
        return this.request(`/api/characters/${characterId}/planets`);
    }

    async getCharacterSkills(characterId) {
        return this.request(`/api/characters/${characterId}/skills`);
    }

    async getCharacterBlueprints(characterId) {
        return this.request(`/api/characters/${characterId}/blueprints`);
    }

    async getCharacterAssets(characterId) {
        return this.request(`/api/characters/${characterId}/assets`);
    }

    // Рыночные данные
    async getItemPrices(typeId, regionId = 10000002) {
        return this.request(`/api/market/types/${typeId}/prices?region_id=${regionId}`);
    }

    async calculateMarketValue(typeId, quantity, regionId = 10000002) {
        return this.request(`/api/market/calculate-value?type_id=${typeId}&quantity=${quantity}&region_id=${regionId}`);
    }

    async getMarketOrders(regionId, typeId = null) {
        const url = typeId 
            ? `/api/market/regions/${regionId}/orders?type_id=${typeId}`
            : `/api/market/regions/${regionId}/orders`;
        return this.request(url);
    }

    // Утилиты
    async getTypeInfo(typeId) {
        return this.request(`/api/types/${typeId}`);
    }

    async getLocationInfo(locationId) {
        return this.request(`/api/locations/${locationId}`);
    }

    // Проверка состояния
    async getHealth() {
        return this.request('/health');
    }
}

// Использование
const api = new EVEProfitMasterAPI('https://your-api-url.com');

// Пример использования
async function loadCharacterData(characterId) {
    try {
        // Получаем детальную информацию
        const details = await api.getCharacterDetails(characterId);
        console.log('Лимиты активности:', details);

        // Получаем работы
        const jobs = await api.getCharacterJobs(characterId);
        console.log('Работы:', jobs);

        // Получаем планеты
        const planets = await api.getCharacterPlanets(characterId);
        console.log('Планеты:', planets);

        // Получаем навыки
        const skills = await api.getCharacterSkills(characterId);
        console.log('Навыки:', skills);

        return {
            details,
            jobs,
            planets,
            skills
        };
    } catch (error) {
        console.error('Ошибка загрузки данных персонажа:', error);
        throw error;
    }
}

// Пример работы с рыночными данными
async function analyzeMarket(typeId, quantity = 1000) {
    try {
        // Получаем цены
        const prices = await api.getItemPrices(typeId);
        console.log('Цены:', prices);

        // Рассчитываем стоимость
        const value = await api.calculateMarketValue(typeId, quantity);
        console.log('Стоимость:', value);

        // Получаем информацию о типе
        const typeInfo = await api.getTypeInfo(typeId);
        console.log('Информация о типе:', typeInfo);

        return {
            prices,
            value,
            typeInfo
        };
    } catch (error) {
        console.error('Ошибка анализа рынка:', error);
        throw error;
    }
}
```

## Обработка ошибок

```javascript
async function handleAPIError(error) {
    if (error.message.includes('401')) {
        // Токен истек, требуется повторная авторизация
        console.log('Требуется повторная авторизация');
        window.location.href = 'https://your-api-url.com/login';
    } else if (error.message.includes('404')) {
        // Ресурс не найден
        console.log('Ресурс не найден');
    } else if (error.message.includes('500')) {
        // Внутренняя ошибка сервера
        console.log('Ошибка сервера');
    } else {
        // Другие ошибки
        console.log('Неизвестная ошибка:', error);
    }
}
```

## Кэширование на клиенте

```javascript
class CachedEVEAPI extends EVEProfitMasterAPI {
    constructor(baseUrl, cacheTime = 300000) { // 5 минут по умолчанию
        super(baseUrl);
        this.cache = new Map();
        this.cacheTime = cacheTime;
    }

    async request(endpoint, options = {}) {
        const cacheKey = `${endpoint}_${JSON.stringify(options)}`;
        const now = Date.now();
        
        // Проверяем кэш
        if (this.cache.has(cacheKey)) {
            const { data, timestamp } = this.cache.get(cacheKey);
            if (now - timestamp < this.cacheTime) {
                console.log('Используем кэшированные данные');
                return data;
            }
        }

        // Запрашиваем данные
        const data = await super.request(endpoint, options);
        
        // Сохраняем в кэш
        this.cache.set(cacheKey, {
            data,
            timestamp: now
        });

        return data;
    }

    clearCache() {
        this.cache.clear();
    }
}
```

## React Hook для API

```javascript
import { useState, useEffect } from 'react';

function useEVEAPI(baseUrl) {
    const [api] = useState(() => new EVEProfitMasterAPI(baseUrl));
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const request = async (endpoint, options = {}) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await api.request(endpoint, options);
            return result;
        } catch (err) {
            setError(err);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    return { api, request, loading, error };
}

// Использование в компоненте
function CharacterList() {
    const { request, loading, error } = useEVEAPI('https://your-api-url.com');
    const [characters, setCharacters] = useState([]);

    useEffect(() => {
        const loadCharacters = async () => {
            try {
                const data = await request('/api/characters');
                setCharacters(data);
            } catch (err) {
                console.error('Ошибка загрузки персонажей:', err);
            }
        };

        loadCharacters();
    }, [request]);

    if (loading) return <div>Загрузка...</div>;
    if (error) return <div>Ошибка: {error.message}</div>;

    return (
        <div>
            {characters.map(character => (
                <div key={character.character_id}>
                    {character.character_name}
                </div>
            ))}
        </div>
    );
}
```
