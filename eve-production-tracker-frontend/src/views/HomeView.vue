<template>
  <div class="app-container">
    <CharacterPanel
      ref="characterPanel"
      class="character-panel-column"
      :characters="characters"
      :activities="activities"
      @add-character="addMockCharacter"
      @remove-character="removeMockCharacter"
      @select-character="handleCharacterSelection"
      :selected-character-id="selectedCharacterId"
      @scroll="handlePanelScroll"
    />
    <JobsTimeline
      ref="jobsTimeline"
      class="timeline-column"
      :jobs="filteredJobs"
      :characters="characters"
      :is-loading="loading"
      :selected-character-id="selectedCharacterId"
      @scroll="handleTimelineScroll"
    />
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
import { mockCharacters, mockActivities, mockJobs } from "@/mock/mockData.js";
export default {
  name: "HomeView",
  components: { CharacterPanel, JobsTimeline },
  data: () => ({
    jobs: {},
    characters: [],
    activities: {},
    isLoggedIn: false,
    loading: false,
    selectedCharacterId: null,
    isPanelScrolling: false,
    isTimelineScrolling: false,
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
    handlePanelScroll(event) {
      if (this.selectedCharacterId || this.isTimelineScrolling) return;
      this.isPanelScrolling = true;
      this.$refs.jobsTimeline.setScrollTop(event.target.scrollTop);
      requestAnimationFrame(() => {
        this.isPanelScrolling = false;
      });
    },
    handleTimelineScroll(event) {
      if (this.selectedCharacterId || this.isPanelScrolling) return;
      this.isTimelineScrolling = true;
      this.$refs.characterPanel.setScrollTop(event.target.scrollTop);
      requestAnimationFrame(() => {
        this.isTimelineScrolling = false;
      });
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
}
.character-panel-column {
  flex-shrink: 0;
}
.timeline-column {
  flex-grow: 1;
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
