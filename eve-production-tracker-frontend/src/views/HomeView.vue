<template>
  <div class="app-container">
    <div class="main-scroll-container">
      <!-- Глобальная навигация -->
      <div class="navigation-container">
        <nav class="global-navigation">
          <button
            v-for="navItem in navigationItems"
            :key="navItem.key"
            :class="[
              'nav-button',
              { 'nav-button-active': currentSection === navItem.key },
            ]"
            @click="switchSection(navItem.key)"
            :title="navItem.tooltip"
          >
            <i :class="navItem.icon"></i>
            <span class="nav-label">{{ navItem.label }}</span>
          </button>
        </nav>
      </div>

      <!-- Контент разделов -->
      <div class="content-container">
        <CharacterPanel
          v-if="currentSection === 'characters'"
          class="character-panel-column"
          :characters="characters"
          :activities="activities"
          @add-character="addMockCharacter"
          @remove-character="removeMockCharacter"
          @select-character="handleCharacterSelection"
          :selected-character-id="selectedCharacterId"
        />

        <!-- Раздел проектов -->
        <ProjectView
          v-if="currentSection === 'projects'"
          class="project-view-container"
        />

        <JobsTimeline
          v-if="currentSection === 'characters'"
          class="timeline-column"
          :jobs="filteredJobs"
          :characters="characters"
          :planets="planets"
          :is-loading="loading"
          :selected-character-id="selectedCharacterId"
        />
      </div>
    </div>
    <div v-if="!isLoggedIn && !loading" class="login-overlay">
      <div class="login-box">
        <h1>EVE Profit Master</h1>
        <p>Войдите через EVE Online SSO для работы с реальными данными.</p>
        <div class="login-buttons">
          <button @click="loginWithEVE" class="eve-login-button">
            <img
              src="/eve-sso-login-white-large.png"
              alt="EVE SSO Login"
              class="eve-logo"
            />
          </button>
          <button @click="loadMockData" class="mock-login-button">
            Демо режим (тестовые данные)
          </button>
          <button @click="resetDatabase" class="reset-database-button">
            Очистить базу данных
          </button>
          <button @click="clearCache" class="clear-cache-button">
            Очистить кэш
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import CharacterPanel from "@/components/CharacterPanel.vue";
import JobsTimeline from "@/components/JobsTimeline.vue";
import ProjectView from "@/components/ProjectView.vue";
import { mockCharacters, mockActivities, mockJobs } from "@/mock/mockData.js";
import { dataCache } from "@/utils/cache.js";
import { reactive } from "vue";
export default {
  name: "HomeView",
  components: { CharacterPanel, JobsTimeline, ProjectView },
  provide() {
    return {
      eventBus: this.eventBus,
    };
  },
  data: () => ({
    eventBus: reactive({}),
    jobs: {},
    piJobs: {}, // Отдельные данные о PI работах
    characters: [],
    activities: {},
    planets: {}, // Данные о планетах для каждого персонажа
    isLoggedIn: false,
    loading: false,
    selectedCharacterId: null,
    currentSection: "characters", // Текущий активный раздел
    // Автоматическое обновление
    autoUpdateInterval: null,
    lastActivityTime: Date.now(),
    isWindowActive: true,
    updateTimeout: null,
    apiBaseUrl:
      process.env.NODE_ENV === "development"
        ? "http://localhost:5000"
        : "https://eve-profitmaster.onrender.com",
    navigationItems: [
      {
        key: "characters",
        label: "Персонажи",
        icon: "nav-icon-characters",
        tooltip: "Управление персонажами и их активностями",
      },
      {
        key: "projects",
        label: "Проекты",
        icon: "nav-icon-projects",
        tooltip: "Управление проектами (в разработке)",
      },
    ],
  }),
  computed: {
    // Объединенные работы (обычные + PI)
    allJobs() {
      const combined = {};
      for (const character of this.characters) {
        const characterId = character.character_id;
        const regularJobs = this.jobs[characterId] || [];
        const piJobs = this.piJobs[characterId] || [];

        // Объединяем все работы
        combined[characterId] = [...regularJobs, ...piJobs];
      }
      return combined;
    },

    filteredJobs() {
      if (!this.selectedCharacterId) return this.allJobs;
      return {
        [this.selectedCharacterId]:
          this.allJobs[this.selectedCharacterId] || [],
      };
    },
  },
  methods: {
    switchSection(sectionKey) {
      this.currentSection = sectionKey;
      // Сбрасываем выбранного персонажа при переключении разделов
      if (sectionKey !== "characters") {
        this.selectedCharacterId = null;
      }
    },
    handleCharacterSelection(charId) {
      this.selectedCharacterId =
        this.selectedCharacterId === charId ? null : charId;
    },

    // Авторизация через EVE Online SSO
    loginWithEVE() {
      console.log("Попытка авторизации через EVE SSO...");
      console.log("API Base URL:", this.apiBaseUrl);

      // Проверяем доступность backend перед перенаправлением
      fetch(`${this.apiBaseUrl}/`)
        .then((response) => {
          if (response.ok) {
            console.log("Backend доступен, перенаправляем на авторизацию");
            window.location.href = `${this.apiBaseUrl}/login`;
          } else {
            throw new Error("Backend недоступен");
          }
        })
        .catch((error) => {
          console.error("Ошибка подключения к backend:", error);
          alert(
            "Ошибка: Backend сервер недоступен!\n\nУбедитесь что:\n1. Flask сервер запущен (python app.py)\n2. Сервер работает на http://localhost:5000\n3. .env файл настроен правильно"
          );
        });
    },

    // Загрузка тестовых данных для демо режима
    loadMockData() {
      this.loading = true;
      this.characters = mockCharacters;
      this.activities = mockActivities;
      this.jobs = mockJobs;
      this.isLoggedIn = true;
      this.loading = false;
    },

    // Загрузка кэшированных данных
    loadCachedData() {
      const cachedData = dataCache.loadFromCache();
      if (cachedData) {
        console.log("Загружаем кэшированные данные");
        this.characters = cachedData.characters || [];
        this.activities = cachedData.activities || {};
        this.jobs = cachedData.jobs || {};
        this.piJobs = cachedData.piJobs || {};
        this.planets = cachedData.planets || {};
        this.isLoggedIn = this.characters.length > 0;

        // Показываем информацию о кэше
        const cacheInfo = dataCache.getCacheInfo();
        if (cacheInfo) {
          console.log(
            `Кэш: ${cacheInfo.charactersCount} персонажей, ${cacheInfo.jobsCount} работ, возраст: ${cacheInfo.cacheAge}с`
          );
        }

        return true;
      }
      return false;
    },

    // Сохранение данных в кэш
    saveToCache() {
      dataCache.saveToCache({
        characters: this.characters,
        activities: this.activities,
        jobs: this.jobs,
        piJobs: this.piJobs,
        planets: this.planets,
      });
    },

    // Загрузка реальных данных из API
    async loadRealData(useCache = true) {
      // Сначала пытаемся загрузить из кэша
      if (useCache && this.loadCachedData()) {
        // Запускаем обновление в фоне
        this.updateDataInBackground();
        return;
      }

      this.loading = true;
      console.log("Starting loadRealData...");
      try {
        // Загружаем персонажей
        const charactersResponse = await fetch(
          `${this.apiBaseUrl}/get_characters`
        );
        if (charactersResponse.ok) {
          this.characters = await charactersResponse.json();
        }

        // Загружаем активности для каждого персонажа
        this.activities = {};
        for (const character of this.characters) {
          const detailsResponse = await fetch(
            `${this.apiBaseUrl}/get_character_details/${character.character_id}`
          );
          if (detailsResponse.ok) {
            this.activities[character.character_id] =
              await detailsResponse.json();

            // Загружаем дополнительные данные для персонажа
            await this.loadCharacterDetails(character.character_id);
          } else if (detailsResponse.status === 401) {
            const errorData = await detailsResponse.json();
            if (errorData.requires_reauth) {
              console.warn(
                `Character ${character.character_name} requires re-authentication`
              );
              // Remove character from the list and show notification
              this.characters = this.characters.filter(
                (c) => c.character_id !== character.character_id
              );
              alert(
                `Персонаж ${character.character_name} требует повторной авторизации. Пожалуйста, войдите в систему заново.`
              );
            }
          }
        }

        // Загружаем работы
        const jobsResponse = await fetch(`${this.apiBaseUrl}/get_jobs`);
        if (jobsResponse.ok) {
          this.jobs = await jobsResponse.json();
          console.log("Loaded jobs data:", this.jobs);

          // Проверяем структуру данных для каждого персонажа
          for (const character of this.characters) {
            const characterJobs = this.jobs[character.character_id];
            if (characterJobs && characterJobs.length > 0) {
              console.log(
                `Jobs for ${character.character_name}:`,
                characterJobs[0]
              );
              console.log(`Job fields:`, Object.keys(characterJobs[0]));
            }
          }
        }

        // Загружаем планеты и обрабатываем PI работы
        for (const character of this.characters) {
          try {
            const planetsResponse = await fetch(
              `${this.apiBaseUrl}/get_character_planets/${character.character_id}`
            );
            if (planetsResponse.ok) {
              const planets = await planetsResponse.json();
              console.log(
                `Planets for character ${character.character_id}:`,
                planets
              );

              // Сохраняем данные о планетах
              this.planets[character.character_id] = planets;

              // Обрабатываем PI работы отдельно
              this.piJobs[character.character_id] = [];

              for (const planet of planets) {
                if (planet.jobs && planet.jobs.length > 0) {
                  // Преобразуем работы планет в формат PI работ
                  const piJobs = planet.jobs.map((job) => ({
                    ...job,
                    activity_id: 100, // Специальный ID для PI работ
                    is_planet_job: true,
                    planet_name: planet.name,
                    planet_id: planet.planet_id,
                    // Добавляем специфичные для PI поля
                    pi_type: job.type || "extraction", // extraction, production, etc.
                    cycle_time: job.cycle_time || 3600, // Время цикла в секундах
                    is_continuous: job.is_continuous || false, // Непрерывная работа
                  }));

                  this.piJobs[character.character_id].push(...piJobs);
                  console.log(
                    `Added ${piJobs.length} PI jobs for character ${character.character_name} from planet ${planet.name}`
                  );
                }
              }

              // Анализируем планеты, требующие внимания
              const planetsNeedingAttention = planets.filter(
                (planet) => planet.needs_attention
              );
              if (planetsNeedingAttention.length > 0) {
                console.log(
                  `Planets needing attention for character ${character.character_id}:`,
                  planetsNeedingAttention
                );
              }
            }
          } catch (error) {
            console.error(
              `Error loading planets for character ${character.character_id}:`,
              error
            );
          }
        }

        console.log("Final jobs data after adding planets:", this.jobs);
        this.isLoggedIn = true;

        // Сохраняем данные в кэш
        this.saveToCache();
      } catch (error) {
        console.error("Ошибка загрузки данных:", error);
        alert("Ошибка загрузки данных. Проверьте подключение к серверу.");
      } finally {
        this.loading = false;
      }
    },

    // Фоновое обновление данных
    async updateDataInBackground() {
      console.log("Запускаем фоновое обновление данных...");
      try {
        // Загружаем персонажей
        const charactersResponse = await fetch(
          `${this.apiBaseUrl}/get_characters`
        );
        if (charactersResponse.ok) {
          const newCharacters = await charactersResponse.json();

          // Обновляем только если данные изменились
          if (
            JSON.stringify(newCharacters) !== JSON.stringify(this.characters)
          ) {
            console.log("Обнаружены изменения в персонажах, обновляем...");
            this.characters = newCharacters;
          }
        }

        // Загружаем активности для каждого персонажа
        for (const character of this.characters) {
          const detailsResponse = await fetch(
            `${this.apiBaseUrl}/get_character_details/${character.character_id}`
          );
          if (detailsResponse.ok) {
            const newActivity = await detailsResponse.json();

            // Обновляем только если данные изменились
            if (
              JSON.stringify(newActivity) !==
              JSON.stringify(this.activities[character.character_id])
            ) {
              console.log(
                `Обновляем активности для персонажа ${character.character_name}`
              );
              this.activities[character.character_id] = newActivity;
            }
          }
        }

        // Загружаем работы
        const jobsResponse = await fetch(`${this.apiBaseUrl}/get_jobs`);
        if (jobsResponse.ok) {
          const newJobs = await jobsResponse.json();

          // Обновляем только если данные изменились
          if (JSON.stringify(newJobs) !== JSON.stringify(this.jobs)) {
            console.log("Обнаружены изменения в работах, обновляем...");
            this.jobs = newJobs;
          }
        }

        // Загружаем планеты и обновляем PI работы
        for (const character of this.characters) {
          try {
            const planetsResponse = await fetch(
              `${this.apiBaseUrl}/get_character_planets/${character.character_id}`
            );
            if (planetsResponse.ok) {
              const newPlanets = await planetsResponse.json();

              // Обновляем только если данные изменились
              if (
                JSON.stringify(newPlanets) !==
                JSON.stringify(this.planets[character.character_id])
              ) {
                console.log(
                  `Обновляем планеты для персонажа ${character.character_name}`
                );
                this.planets[character.character_id] = newPlanets;

                // Обновляем PI работы
                this.piJobs[character.character_id] = [];

                for (const planet of newPlanets) {
                  if (planet.jobs && planet.jobs.length > 0) {
                    // Преобразуем работы планет в формат PI работ
                    const piJobs = planet.jobs.map((job) => ({
                      ...job,
                      activity_id: 100, // Специальный ID для PI работ
                      is_planet_job: true,
                      planet_name: planet.name,
                      planet_id: planet.planet_id,
                      pi_type: job.type || "extraction",
                      cycle_time: job.cycle_time || 3600,
                      is_continuous: job.is_continuous || false,
                    }));

                    this.piJobs[character.character_id].push(...piJobs);
                  }
                }
              }
            }
          } catch (error) {
            console.error(
              `Error loading planets for character ${character.character_id}:`,
              error
            );
          }
        }

        // Сохраняем обновленные данные в кэш
        this.saveToCache();
        console.log("Фоновое обновление завершено");
      } catch (error) {
        console.error("Ошибка фонового обновления:", error);
      }
    },

    // Добавление нового персонажа
    addMockCharacter() {
      this.loginWithEVE();
    },

    // Удаление персонажа
    async removeMockCharacter(characterId) {
      if (!confirm("Уверены что хотите удалить персонажа?")) return;

      try {
        const response = await fetch(`${this.apiBaseUrl}/remove_character`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ character_id: characterId }),
        });

        if (response.ok) {
          this.characters = this.characters.filter(
            (c) => c.character_id !== characterId
          );
          delete this.jobs[characterId];
          delete this.activities[characterId];
          if (this.characters.length === 0) {
            this.isLoggedIn = false;
          }
        } else {
          alert("Ошибка при удалении персонажа");
        }
      } catch (error) {
        console.error("Ошибка удаления персонажа:", error);
        alert("Ошибка удаления персонажа");
      }
    },

    // Загрузка дополнительных данных для персонажа
    async loadCharacterDetails(characterId) {
      try {
        // Загружаем навыки
        const skillsResponse = await fetch(
          `${this.apiBaseUrl}/get_character_skills/${characterId}`
        );
        if (skillsResponse.ok) {
          const skills = await skillsResponse.json();
          console.log(`Skills for character ${characterId}:`, skills);
        }

        // Загружаем блюпринты
        const blueprintsResponse = await fetch(
          `${this.apiBaseUrl}/get_character_blueprints/${characterId}`
        );
        if (blueprintsResponse.ok) {
          const blueprints = await blueprintsResponse.json();
          console.log(`Blueprints for character ${characterId}:`, blueprints);
        }

        // Планеты уже загружены в loadRealData

        // Загружаем портрет
        const portraitResponse = await fetch(
          `${this.apiBaseUrl}/get_character_portrait/${characterId}`
        );
        if (portraitResponse.ok) {
          const portrait = await portraitResponse.json();
          console.log(`Portrait for character ${characterId}:`, portrait);
        }
      } catch (error) {
        console.error(
          `Error loading details for character ${characterId}:`,
          error
        );
      }
    },

    // Загрузка информации о типе продукта
    async loadTypeInfo(typeId) {
      try {
        const response = await fetch(
          `${this.apiBaseUrl}/get_type_info/${typeId}`
        );
        if (response.ok) {
          const typeInfo = await response.json();
          console.log(`Type info for ${typeId}:`, typeInfo);
          return typeInfo;
        }
      } catch (error) {
        console.error(`Error loading type info for ${typeId}:`, error);
      }
      return null;
    },

    // Загрузка информации о локации
    async loadLocationInfo(locationId) {
      try {
        const response = await fetch(
          `${this.apiBaseUrl}/get_location_info/${locationId}`
        );
        if (response.ok) {
          const locationInfo = await response.json();
          console.log(`Location info for ${locationId}:`, locationInfo);
          return locationInfo;
        }
      } catch (error) {
        console.error(`Error loading location info for ${locationId}:`, error);
      }
      return null;
    },

    // Очистка кэша
    clearCache() {
      if (
        confirm(
          "Очистить кэш данных? При следующей загрузке данные будут загружены заново."
        )
      ) {
        dataCache.clearCache();
        alert("Кэш очищен");
      }
    },

    // Автоматическое обновление данных
    startAutoUpdate() {
      // Обновляем каждые 2-3 минуты (120-180 секунд)
      const updateInterval = () => {
        if (this.isWindowActive && this.isLoggedIn) {
          console.log("Автоматическое обновление данных...");
          this.updateDataInBackground();
        }

        // Планируем следующее обновление через 2-3 минуты
        const nextUpdateDelay = Math.random() * 60000 + 120000; // 2-3 минуты
        this.updateTimeout = setTimeout(updateInterval, nextUpdateDelay);
      };

      // Запускаем первое обновление через 2-3 минуты
      const initialDelay = Math.random() * 60000 + 120000;
      this.updateTimeout = setTimeout(updateInterval, initialDelay);

      // Запускаем проверку активности окна каждую минуту
      this.autoUpdateInterval = setInterval(() => {
        this.checkWindowActivity();
      }, 60000); // Каждую минуту
    },

    // Остановка автоматического обновления
    stopAutoUpdate() {
      if (this.updateTimeout) {
        clearTimeout(this.updateTimeout);
        this.updateTimeout = null;
      }
      if (this.autoUpdateInterval) {
        clearInterval(this.autoUpdateInterval);
        this.autoUpdateInterval = null;
      }
    },

    // Обработка активности окна
    handleWindowFocus() {
      this.isWindowActive = true;
      this.lastActivityTime = Date.now();
      console.log("Окно активно, возобновляем обновления");
    },

    handleWindowBlur() {
      this.isWindowActive = false;
      this.lastActivityTime = Date.now();
      console.log("Окно неактивно, приостанавливаем обновления");
    },

    // Проверка активности окна
    checkWindowActivity() {
      const now = Date.now();
      const timeSinceLastActivity = now - this.lastActivityTime;

      // Если окно неактивно более 15 минут, останавливаем обновления
      if (!this.isWindowActive && timeSinceLastActivity > 15 * 60 * 1000) {
        this.stopAutoUpdate();
        console.log("Окно неактивно более 15 минут, остановка обновлений");
      }
    },

    // Очистка базы данных
    async resetDatabase() {
      if (
        confirm(
          "Вы уверены, что хотите очистить базу данных? Все персонажи будут удалены."
        )
      ) {
        try {
          const response = await fetch(`${this.apiBaseUrl}/reset_database`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
          });

          if (response.ok) {
            const result = await response.json();
            alert(result.message);
            // Очищаем локальные данные и кэш
            this.characters = [];
            this.activities = {};
            this.jobs = {};
            this.planets = {};
            this.isLoggedIn = false;
            this.selectedCharacterId = null;
            dataCache.clearCache();
          } else {
            const error = await response.json();
            alert(`Ошибка: ${error.error}`);
          }
        } catch (error) {
          console.error("Ошибка очистки базы данных:", error);
          alert("Ошибка подключения к серверу.");
        }
      }
    },
  },

  // Проверяем авторизацию при загрузке компонента
  async mounted() {
    // Добавляем обработчики активности окна
    window.addEventListener("focus", this.handleWindowFocus);
    window.addEventListener("blur", this.handleWindowBlur);
    window.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        this.handleWindowBlur();
      } else {
        this.handleWindowFocus();
      }
    });

    // Проверяем URL параметры на успешную авторизацию
    const urlParams = new URLSearchParams(window.location.search);
    const authSuccess = urlParams.get("auth");

    if (authSuccess === "success") {
      // Убираем параметр из URL
      window.history.replaceState({}, document.title, window.location.pathname);
      // Принудительно загружаем данные после авторизации (без кэша)
      await this.loadRealData(false);
      // Запускаем автоматическое обновление
      this.startAutoUpdate();
      return;
    }

    // Сначала пытаемся загрузить из кэша
    if (this.loadCachedData()) {
      console.log(
        "Данные загружены из кэша, запускаем автоматическое обновление"
      );
      // Запускаем автоматическое обновление
      this.startAutoUpdate();
      return;
    }

    // Если кэша нет, проверяем авторизацию через API
    try {
      const charactersResponse = await fetch(
        `${this.apiBaseUrl}/get_characters`
      );
      if (charactersResponse.ok) {
        const characters = await charactersResponse.json();
        if (characters.length > 0) {
          // Пользователь авторизован, загружаем реальные данные
          await this.loadRealData();
          // Запускаем автоматическое обновление
          this.startAutoUpdate();
        }
      }
    } catch (error) {
      // Игнорируем ошибки при первом запуске - пользователь не авторизован
      console.log("Пользователь не авторизован или сервер недоступен");
    }
  },

  // Очистка при размонтировании компонента
  beforeUnmount() {
    // Останавливаем автоматическое обновление
    this.stopAutoUpdate();

    // Удаляем обработчики активности окна
    window.removeEventListener("focus", this.handleWindowFocus);
    window.removeEventListener("blur", this.handleWindowBlur);
    window.removeEventListener("visibilitychange", () => {
      if (document.hidden) {
        this.handleWindowBlur();
      } else {
        this.handleWindowFocus();
      }
    });
  },
};
</script>
<style>
body,
html {
  margin: 0;
  padding: 0;
  background-color: #1a1a1a;
  color: #f0f0f0;
  font-family: "Segoe UI", sans-serif;
}
</style>
<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
  padding-bottom: 20px; /* Добавляем отступ снизу для всего приложения */
  box-sizing: border-box;
}
.main-scroll-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  overflow: hidden;
  background-color: #282c34;
}

.navigation-container {
  flex-shrink: 0;
  background-color: #21252b;
  border-bottom: 1px solid #3c4043;
  z-index: 10;
}

.global-navigation {
  display: flex;
  padding: 0;
  margin: 0;
  min-height: 60px;
  align-items: center;
  padding-left: 20px;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 10px;
  background: none;
  border: none;
  color: #abb2bf;
  padding: 12px 20px;
  margin-right: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
  position: relative;
}

.nav-button:hover {
  background-color: #2c3038;
  color: #e6e6e6;
}

.nav-button-active {
  background-color: #495057;
  color: #ffffff;
}

.nav-button-active:hover {
  background-color: #343a40;
}

.nav-label {
  font-size: 14px;
  white-space: nowrap;
}

.content-container {
  display: flex;
  flex-grow: 1;
  overflow: hidden;
}

.character-panel-column {
  flex-shrink: 0;
}

.timeline-column {
  flex-grow: 1;
}

.project-view-container {
  flex-grow: 1;
  height: 100%;
}

.section-placeholder {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #282c34;
}

.placeholder-content {
  text-align: center;
  color: #abb2bf;
}

.placeholder-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.placeholder-content h3 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #e6e6e6;
}

.placeholder-content p {
  margin: 0;
  font-size: 16px;
  opacity: 0.7;
}

/* Иконки для навигации */
.nav-icon-characters::before,
.nav-icon-projects::before {
  content: "";
  display: inline-block;
  width: 16px;
  height: 16px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

/* Иконка персонажей */
.nav-icon-characters::before {
  background-image: url('data:image/svg+xml;charset=UTF-8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>');
}

/* Иконка проектов */
.nav-icon-projects::before {
  background-image: url('data:image/svg+xml;charset=UTF-8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>');
}
.login-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.login-box {
  text-align: center;
  padding: 40px;
  background-color: #2c2c2c;
  border-radius: 10px;
  max-width: 450px;
}

.login-buttons {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.eve-login-button {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #1a1a1a;
  color: white;
  border: 2px solid #e67e00;
  padding: 20px 40px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 18px;
  font-weight: 600;
  transition: all 0.3s ease;
  min-width: 200px;
  min-height: 60px;
}

.eve-login-button:hover {
  background-color: #e67e00;
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(230, 126, 0, 0.4);
}

.eve-logo {
  height: 40px;
  width: auto;
  max-width: 100%;
}

.mock-login-button {
  background-color: #4e9aef;
  color: white;
  border: 2px solid transparent;
  padding: 15px 30px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.mock-login-button:hover {
  background-color: #3a7bc8;
  transform: translateY(-1px);
  box-shadow: 0 3px 6px rgba(78, 154, 239, 0.3);
}

.reset-database-button {
  background-color: #dc3545;
  color: white;
  border: 2px solid transparent;
  padding: 15px 30px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.reset-database-button:hover {
  background-color: #c82333;
  transform: translateY(-1px);
  box-shadow: 0 3px 6px rgba(220, 53, 69, 0.3);
}

.clear-cache-button {
  background-color: #ffc107;
  color: #212529;
  border: 2px solid transparent;
  padding: 15px 30px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.clear-cache-button:hover {
  background-color: #e0a800;
  transform: translateY(-1px);
  box-shadow: 0 3px 6px rgba(255, 193, 7, 0.3);
}
</style>
