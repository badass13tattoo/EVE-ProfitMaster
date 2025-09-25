<template>
  <div class="app-container">
    <CharacterPanel
      :characters="characters"
      :activities="activities"
      @add-character="openLoginPopup"
      @remove-character="removeCharacter"
      @select-character="handleCharacterSelection"
      :selected-character-id="selectedCharacterId"
    />

    <JobsTimeline
      :jobs="filteredJobs"
      :characters="characters"
      :is-loading="loading"
    />

    <div v-if="!isLoggedIn && !loading" class="login-overlay">
      <div class="login-box">
        <h1>EVE Profit Master</h1>
        <p>Войдите, чтобы начать отслеживать ваши производственные работы.</p>
        <a href="#" @click.prevent="openLoginPopup">
          <img
            src="/eve-sso-login-white-large.png"
            alt="Log in with EVE Online"
          />
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import CharacterPanel from "@/components/CharacterPanel.vue";
import JobsTimeline from "@/components/JobsTimeline.vue";

export default {
  name: "HomeView",
  components: { CharacterPanel, JobsTimeline },
  data() {
    return {
      jobs: {},
      characters: [],
      activities: {},
      isLoggedIn: false,
      loading: true,
      selectedCharacterId: null,
      loginUrl: "https://eve-profitmaster.onrender.com/login",
    };
  },
  computed: {
    filteredJobs() {
      if (!this.selectedCharacterId) {
        return this.jobs;
      }
      return {
        [this.selectedCharacterId]: this.jobs[this.selectedCharacterId] || [],
      };
    },
  },
  mounted() {
    window.addEventListener("message", this.handleAuthMessage);
  },
  beforeUnmount() {
    window.removeEventListener("message", this.handleAuthMessage);
  },
  async created() {
    this.loadAppData();
  },
  methods: {
    handleCharacterSelection(charId) {
      this.selectedCharacterId =
        this.selectedCharacterId === charId ? null : charId;
    },
    openLoginPopup() {
      const width = 600,
        height = 700;
      const left = window.top.outerWidth / 2 + window.top.screenX - width / 2;
      const top = window.top.outerHeight / 2 + window.top.screenY - height / 2;
      window.open(
        this.loginUrl,
        "eveLogin",
        `width=${width},height=${height},top=${top},left=${left}`
      );
    },
    handleAuthMessage(event) {
      if (event.data === "auth-success") this.loadAppData();
    },
    async loadAppData() {
      this.loading = true;
      const backendUrl = "https://eve-profitmaster.onrender.com";
      try {
        const charsResponse = await axios.get(`${backendUrl}/get_characters`);
        this.characters = charsResponse.data;
        if (this.characters && this.characters.length > 0) {
          this.isLoggedIn = true;
          await this.fetchJobs();
          this.fetchAllCharacterDetails();
        } else {
          this.isLoggedIn = false;
        }
      } catch (error) {
        console.error("Ошибка при начальной загрузке данных:", error);
        this.isLoggedIn = false;
      } finally {
        this.loading = false;
      }
    },
    async fetchAllCharacterDetails() {
      const backendUrl = "https://eve-profitmaster.onrender.com";
      const promises = this.characters.map((char) =>
        axios
          .get(`${backendUrl}/get_character_details/${char.character_id}`)
          .then((response) => {
            this.activities = {
              ...this.activities,
              [char.character_id]: response.data,
            };
          })
          .catch((error) =>
            console.error(`Ошибка деталей для ${char.character_name}:`, error)
          )
      );
      await Promise.all(promises);
    },
    async removeCharacter(characterId) {
      if (!confirm("Вы уверены, что хотите удалить этого персонажа?")) return;
      const backendUrl = "https://eve-profitmaster.onrender.com";
      try {
        await axios.post(`${backendUrl}/remove_character`, {
          character_id: characterId,
        });
        this.loadAppData();
      } catch (error) {
        alert("Не удалось удалить персонажа.");
      }
    },
    async fetchJobs() {
      const backendUrl = "https://eve-profitmaster.onrender.com";
      try {
        const response = await axios.get(`${backendUrl}/get_jobs`);
        const jobsByChar = response.data;
        const allProductIds = Object.values(jobsByChar)
          .flat()
          .map((job) => job.product_type_id);
        const uniqueProductIds = [...new Set(allProductIds)];
        const itemNames = await this.fetchTypeNames(uniqueProductIds);
        for (const charId in jobsByChar) {
          jobsByChar[charId].forEach((job) => {
            job.product_name = itemNames[job.product_type_id] || "Unknown Item";
          });
        }
        this.jobs = jobsByChar;
      } catch (error) {
        console.error("Ошибка при получении данных о работах:", error);
        this.jobs = {};
      }
    },
    async fetchTypeNames(ids) {
      if (!ids || ids.length === 0) return {};
      try {
        const response = await axios.post(
          "https://esi.evetech.net/latest/universe/names/",
          ids
        );
        const itemNames = {};
        response.data.forEach((item) => {
          itemNames[item.id] = item.name;
        });
        return itemNames;
      } catch (error) {
        return {};
      }
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
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}
</style>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
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
</style>
