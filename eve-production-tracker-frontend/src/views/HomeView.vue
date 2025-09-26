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
        <p>Для начала работы, нажмите кнопку ниже.</p>
        <button @click="loadAppData" class="mock-login-button">
          Начать с тестовыми данными
        </button>
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
    _getMockData() {},
    loadAppData() {
      this.loading = true;
      const mockData = this._getMockData();
      this.characters = mockCharacters;
      this.activities = mockActivities;
      this.jobs = mockJobs;
      this.isLoggedIn = true;
      this.loading = false;
    },
    addMockCharacter() {
      alert("Добавление 'болванки' в разработке.");
    },
    removeMockCharacter(characterId) {
      if (!confirm("Уверены?")) return;
      this.characters = this.characters.filter(
        (c) => c.character_id !== characterId
      );
      delete this.jobs[characterId];
      delete this.activities[characterId];
      if (this.characters.length === 0) this.isLoggedIn = false;
    },
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
}
.mock-login-button {
  background-color: #4e9aef;
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 18px;
  margin-top: 20px;
}
</style>
