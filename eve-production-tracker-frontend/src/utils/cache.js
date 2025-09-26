// Утилита для работы с кэшем данных
export class DataCache {
  constructor() {
    this.CACHE_KEY = "eve_profitmaster_cache";
    this.CACHE_EXPIRY_KEY = "eve_profitmaster_cache_expiry";
    this.CACHE_DURATION = 5 * 60 * 1000; // 5 минут в миллисекундах
  }

  // Сохранить данные в кэш
  saveToCache(data) {
    try {
      const cacheData = {
        characters: data.characters || [],
        activities: data.activities || {},
        jobs: data.jobs || {},
        planets: data.planets || {},
        timestamp: Date.now(),
      };

      localStorage.setItem(this.CACHE_KEY, JSON.stringify(cacheData));
      localStorage.setItem(this.CACHE_EXPIRY_KEY, Date.now().toString());

      console.log("Данные сохранены в кэш");
    } catch (error) {
      console.error("Ошибка сохранения в кэш:", error);
    }
  }

  // Загрузить данные из кэша
  loadFromCache() {
    try {
      const cacheData = localStorage.getItem(this.CACHE_KEY);
      const expiryTime = localStorage.getItem(this.CACHE_EXPIRY_KEY);

      if (!cacheData || !expiryTime) {
        return null;
      }

      const now = Date.now();
      const cacheAge = now - parseInt(expiryTime);

      // Проверяем, не устарел ли кэш
      if (cacheAge > this.CACHE_DURATION) {
        console.log("Кэш устарел, очищаем");
        this.clearCache();
        return null;
      }

      const data = JSON.parse(cacheData);
      console.log(
        "Данные загружены из кэша, возраст:",
        Math.round(cacheAge / 1000),
        "секунд"
      );

      return data;
    } catch (error) {
      console.error("Ошибка загрузки из кэша:", error);
      this.clearCache();
      return null;
    }
  }

  // Очистить кэш
  clearCache() {
    try {
      localStorage.removeItem(this.CACHE_KEY);
      localStorage.removeItem(this.CACHE_EXPIRY_KEY);
      console.log("Кэш очищен");
    } catch (error) {
      console.error("Ошибка очистки кэша:", error);
    }
  }

  // Проверить, есть ли валидный кэш
  hasValidCache() {
    try {
      const cacheData = localStorage.getItem(this.CACHE_KEY);
      const expiryTime = localStorage.getItem(this.CACHE_EXPIRY_KEY);

      if (!cacheData || !expiryTime) {
        return false;
      }

      const now = Date.now();
      const cacheAge = now - parseInt(expiryTime);

      return cacheAge <= this.CACHE_DURATION;
    } catch (error) {
      console.error("Ошибка проверки кэша:", error);
      return false;
    }
  }

  // Получить информацию о кэше
  getCacheInfo() {
    try {
      const cacheData = localStorage.getItem(this.CACHE_KEY);
      const expiryTime = localStorage.getItem(this.CACHE_EXPIRY_KEY);

      if (!cacheData || !expiryTime) {
        return null;
      }

      const now = Date.now();
      const cacheAge = now - parseInt(expiryTime);
      const data = JSON.parse(cacheData);

      return {
        charactersCount: data.characters?.length || 0,
        jobsCount: Object.keys(data.jobs || {}).reduce(
          (total, charId) => total + (data.jobs[charId]?.length || 0),
          0
        ),
        cacheAge: Math.round(cacheAge / 1000),
        isExpired: cacheAge > this.CACHE_DURATION,
      };
    } catch (error) {
      console.error("Ошибка получения информации о кэше:", error);
      return null;
    }
  }
}

// Создаем единственный экземпляр кэша
export const dataCache = new DataCache();
