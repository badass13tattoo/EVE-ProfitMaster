// Утилиты для оптимизированной загрузки данных
export class DataLoader {
  constructor(options = {}) {
    this.cache = new Map();
    this.cacheTimeout = options.cacheTimeout || 5 * 60 * 1000; // 5 минут
    this.maxCacheSize = options.maxCacheSize || 100;
    this.requestQueue = new Map();
    this.concurrentLimit = options.concurrentLimit || 3;
    this.activeRequests = 0;
  }

  // Кэшированная загрузка данных
  async load(url, options = {}) {
    const cacheKey = this.getCacheKey(url, options);

    // Проверяем кэш
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
      this.cache.delete(cacheKey);
    }

    // Проверяем очередь запросов
    if (this.requestQueue.has(cacheKey)) {
      return this.requestQueue.get(cacheKey);
    }

    // Создаем новый запрос
    const request = this.makeRequest(url, options);
    this.requestQueue.set(cacheKey, request);

    try {
      const data = await request;

      // Сохраняем в кэш
      this.setCache(cacheKey, data);

      return data;
    } finally {
      this.requestQueue.delete(cacheKey);
    }
  }

  async makeRequest(url, options = {}) {
    // Ограничиваем количество одновременных запросов
    while (this.activeRequests >= this.concurrentLimit) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }

    this.activeRequests++;

    try {
      const response = await fetch(url, {
        ...options,
        signal: AbortSignal.timeout(options.timeout || 10000),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } finally {
      this.activeRequests--;
    }
  }

  getCacheKey(url, options) {
    const params = new URLSearchParams(options.params || {});
    return `${url}?${params.toString()}`;
  }

  setCache(key, data) {
    // Ограничиваем размер кэша
    if (this.cache.size >= this.maxCacheSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  // Предзагрузка данных
  async preload(urls, options = {}) {
    const promises = urls.map((url) => this.load(url, options));
    return Promise.allSettled(promises);
  }

  // Очистка кэша
  clearCache() {
    this.cache.clear();
    this.requestQueue.clear();
  }

  // Очистка устаревших записей
  cleanup() {
    const now = Date.now();
    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp > this.cacheTimeout) {
        this.cache.delete(key);
      }
    }
  }
}

// Пагинированная загрузка данных
export class PaginatedLoader {
  constructor(loader, options = {}) {
    this.loader = loader;
    this.pageSize = options.pageSize || 20;
    this.cache = new Map();
  }

  async loadPage(url, page, options = {}) {
    const cacheKey = `${url}-page-${page}`;

    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    const params = {
      ...options.params,
      page,
      limit: this.pageSize,
    };

    const data = await this.loader.load(url, { ...options, params });
    this.cache.set(cacheKey, data);

    return data;
  }

  async loadAllPages(url, options = {}) {
    const firstPage = await this.loadPage(url, 1, options);
    const totalPages = Math.ceil(firstPage.total / this.pageSize);

    if (totalPages <= 1) {
      return firstPage;
    }

    const remainingPages = Array.from(
      { length: totalPages - 1 },
      (_, i) => i + 2
    );

    const remainingData = await Promise.all(
      remainingPages.map((page) => this.loadPage(url, page, options))
    );

    return {
      ...firstPage,
      data: [...firstPage.data, ...remainingData.flatMap((page) => page.data)],
    };
  }

  clearCache() {
    this.cache.clear();
  }
}

// Инфинити скролл
export class InfiniteScrollLoader {
  constructor(loader, options = {}) {
    this.loader = loader;
    this.pageSize = options.pageSize || 20;
    this.data = [];
    this.currentPage = 0;
    this.hasMore = true;
    this.loading = false;
  }

  async loadMore() {
    if (this.loading || !this.hasMore) {
      return this.data;
    }

    this.loading = true;
    this.currentPage++;

    try {
      const pageData = await this.loader.loadPage(
        this.loader.url,
        this.currentPage,
        this.loader.options
      );

      this.data = [...this.data, ...pageData.data];
      this.hasMore = pageData.data.length === this.pageSize;

      return this.data;
    } finally {
      this.loading = false;
    }
  }

  reset() {
    this.data = [];
    this.currentPage = 0;
    this.hasMore = true;
    this.loading = false;
  }
}

// Создаем глобальный экземпляр загрузчика
export const dataLoader = new DataLoader({
  cacheTimeout: 5 * 60 * 1000, // 5 минут
  maxCacheSize: 100,
  concurrentLimit: 3,
});

// Автоматическая очистка кэша каждые 10 минут
setInterval(() => {
  dataLoader.cleanup();
}, 10 * 60 * 1000);
