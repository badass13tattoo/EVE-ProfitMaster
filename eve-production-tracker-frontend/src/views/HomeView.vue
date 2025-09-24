<template>
  <div class="home">
    <h1>Отслеживание производства EVE Online</h1>

    <!-- Экран входа -->
    <div v-if="!isLoggedIn && !loading">
      <p>Войдите, чтобы начать отслеживать ваши производственные работы.</p>
      <!-- ИЗМЕНЕНИЕ: Кнопка теперь вызывает метод, а не является ссылкой -->
      <a href="#" @click.prevent="openLoginPopup">
        <img
          src="/eve-sso-login-white-large.png"
          alt="Log in with EVE Online"
        />
      </a>
    </div>

    <!-- Основной контент -->
    <div v-if="isLoggedIn && !loading">
      <!-- Список персонажей -->
      <div class="characters-container">
        <h2>Авторизованные персонажи:</h2>
        <div class="characters-list">
          <div
            v-for="char in characters"
            :key="char.character_id"
            class="character-item"
          >
            <img
              :src="getCharacterPortrait(char.character_id)"
              :alt="char.character_name"
              class="character-portrait"
            />
            <span class="character-name">{{ char.character_name }}</span>
          </div>
          <!-- ИЗМЕНЕНИЕ: Кнопка добавления также вызывает метод -->
          <a href="#" @click.prevent="openLoginPopup" class="add-char-item">
            <div class="add-char-icon">+</div>
            <span class="character-name">Добавить</span>
          </a>
        </div>
      </div>

      <!-- Производственные работы -->
      <h2>Ваши текущие работы:</h2>
      <div v-if="jobs.length > 0">
        <ul>
          <li v-for="job in jobs" :key="job.job_id">
            <strong>Персонаж:</strong> {{ job.character_name }} <br />
            <strong>Продукт:</strong> {{ job.product_name || "Загрузка..." }}
            <br />
            <strong>Название работы:</strong> {{ getJobType(job.activity_id) }}
            <br />
            <strong>Статус:</strong> {{ getJobStatus(job) }} <br />
            <strong>Дата завершения:</strong>
            {{ new Date(job.end_date).toLocaleString() }}
          </li>
        </ul>
      </div>
      <div v-else>
        <p>У вас нет активных или завершенных работ.</p>
      </div>
    </div>

    <!-- Индикатор загрузки -->
    <div v-if="loading">
      <p>Загрузка данных...</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "HomeView",
  data() {
    return {
      jobs: [],
      characters: [],
      isLoggedIn: false,
      loading: true,
      loginUrl: "https://eve-profitmaster.onrender.com/login",
    };
  },
  // ИЗМЕНЕНИЕ: Добавлены mounted и beforeUnmount для слушателя событий
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
    // НОВЫЙ МЕТОД: Открывает всплывающее окно для логина
    openLoginPopup() {
      const width = 600;
      const height = 700;
      const left = window.screen.width / 2 - width / 2;
      const top = window.screen.height / 2 - height / 2;
      window.open(
        this.loginUrl,
        "eveLogin",
        `width=${width},height=${height},top=${top},left=${left}`
      );
    },
    // НОВЫЙ МЕТОД: Обрабатывает сообщение от всплывающего окна
    handleAuthMessage(event) {
      // Для безопасности можно добавить проверку event.origin
      if (event.data === "auth-success") {
        console.log("Авторизация прошла успешно, обновляем данные...");
        this.loadAppData(); // Перезагружаем все данные
      }
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

    async fetchJobs() {
      const backendUrl = "https://eve-profitmaster.onrender.com";
      try {
        const response = await axios.get(`${backendUrl}/get_jobs`);
        const jobsData = response.data;
        if (!jobsData || jobsData.error) {
          this.jobs = [];
          return;
        }
        const productIds = [
          ...new Set(jobsData.map((job) => job.product_type_id)),
        ];
        const itemNames = await this.fetchTypeNames(productIds);
        this.jobs = jobsData.map((job) => ({
          ...job,
          product_name: itemNames[job.product_type_id],
        }));
      } catch (error) {
        console.error("Ошибка при получении данных о работах:", error);
        this.jobs = [];
      }
    },

    async fetchTypeNames(ids) {
      if (!ids || ids.length === 0) {
        return {};
      }
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
        console.error("Ошибка при получении названий предметов:", error);
        return {};
      }
    },

    getCharacterPortrait(characterId) {
      return `https://images.evetech.net/characters/${characterId}/portrait?size=64`;
    },

    getJobType(activityId) {
      const jobTypes = {
        1: "Производство",
        2: "Научные исследования",
        3: "Копирование",
        4: "Материальная эффективность",
        5: "Временная эффективность",
        6: "Реакции",
        7: "Изобретение",
      };
      return jobTypes[activityId] || "Неизвестно";
    },

    getJobStatus(job) {
      const currentTime = new Date();
      const endTime = new Date(job.end_date);
      if (job.status === "active" && endTime < currentTime) {
        return "Готово к доставке";
      }
      const jobStatuses = {
        active: "Идет",
        finished: "Завершено",
        delivered: "Выполнено",
        paused: "На паузе",
        ready: "Готово",
      };
      return jobStatuses[job.status] || "Неизвестно";
    },
  },
};
</script>

<style scoped>
.home {
  text-align: center;
  margin-top: 50px;
}
img {
  cursor: pointer;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  background-color: #2c2c2c;
  border: 1px solid #444;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 5px;
  text-align: left;
}
.characters-container {
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid #444;
}
.characters-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
}
.character-item,
.add-char-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100px;
  text-decoration: none;
  color: inherit;
}
.add-char-item {
  cursor: pointer;
  border: 2px dashed #555;
  border-radius: 8px;
  justify-content: center;
  transition: background-color 0.2s, border-color 0.2s;
  height: 100px;
}
.add-char-item:hover {
  background-color: #333;
  border-color: #777;
}
.add-char-icon {
  font-size: 48px;
  line-height: 64px;
  width: 64px;
  height: 64px;
  color: #777;
}
.character-portrait {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 2px solid #555;
  margin-bottom: 8px;
}
.character-name {
  font-size: 14px;
  text-align: center;
  word-break: break-word;
}
</style>
