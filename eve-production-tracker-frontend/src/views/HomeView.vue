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
    characters: [],
    activities: {},
    isLoggedIn: false,
    loading: false,
    selectedCharacterId: null,
    currentSection: "characters", // Текущий активный раздел
    apiBaseUrl:
      process.env.NODE_ENV === "development" ? "http://localhost:5000" : "",
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
    filteredJobs() {
      if (!this.selectedCharacterId) return this.jobs;
      return {
        [this.selectedCharacterId]: this.jobs[this.selectedCharacterId] || [],
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
      console.log('Попытка авторизации через EVE SSO...');
      console.log('API Base URL:', this.apiBaseUrl);
      
      // Проверяем доступность backend перед перенаправлением
      fetch(`${this.apiBaseUrl}/`)
        .then(response => {
          if (response.ok) {
            console.log('Backend доступен, перенаправляем на авторизацию');
            window.location.href = `${this.apiBaseUrl}/login`;
          } else {
            throw new Error('Backend недоступен');
          }
        })
        .catch(error => {
          console.error('Ошибка подключения к backend:', error);
          alert('Ошибка: Backend сервер недоступен!\n\nУбедитесь что:\n1. Flask сервер запущен (python app.py)\n2. Сервер работает на http://localhost:5000\n3. .env файл настроен правильно');
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

    // Загрузка реальных данных из API
    async loadRealData() {
      this.loading = true;
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
          }
        }

        // Загружаем работы
        const jobsResponse = await fetch(`${this.apiBaseUrl}/get_jobs`);
        if (jobsResponse.ok) {
          this.jobs = await jobsResponse.json();
        }

        this.isLoggedIn = true;
      } catch (error) {
        console.error("Ошибка загрузки данных:", error);
        alert("Ошибка загрузки данных. Проверьте подключение к серверу.");
      } finally {
        this.loading = false;
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
  },

  // Проверяем авторизацию при загрузке компонента
  async mounted() {
    // Проверяем URL параметры на успешную авторизацию
    const urlParams = new URLSearchParams(window.location.search);
    const authSuccess = urlParams.get("auth");

    if (authSuccess === "success") {
      // Убираем параметр из URL
      window.history.replaceState({}, document.title, window.location.pathname);
      // Принудительно загружаем данные после авторизации
      await this.loadRealData();
      return;
    }

    // Проверяем, есть ли персонажи в системе (значит пользователь авторизован)
    try {
      const charactersResponse = await fetch(
        `${this.apiBaseUrl}/get_characters`
      );
      if (charactersResponse.ok) {
        const characters = await charactersResponse.json();
        if (characters.length > 0) {
          // Пользователь авторизован, загружаем реальные данные
          await this.loadRealData();
        }
      }
    } catch (error) {
      // Игнорируем ошибки при первом запуске - пользователь не авторизован
      console.log("Пользователь не авторизован или сервер недоступен");
    }
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
</style>
