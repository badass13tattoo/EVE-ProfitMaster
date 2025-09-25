<template>
  <div class="home">
    <h1>Отслеживание производства EVE Online</h1>

    <!-- Экран входа -->
    <div v-if="!isLoggedIn && !loading">
      <p>Войдите, чтобы начать отслеживать ваши производственные работы.</p>
      <a href="#" @click.prevent="openLoginPopup">
        <img
          src="/eve-sso-login-white-large.png"
          alt="Log in with EVE Online"
        />
      </a>
    </div>

    <!-- Основной контент -->
    <div v-if="isLoggedIn && !loading">
      <div class="characters-container">
        <h2>Авторизованные персонажи:</h2>
        <div class="characters-list">
          <div
            v-for="char in characters"
            :key="char.character_id"
            class="character-item"
          >
            <!-- КНОПКА УДАЛЕНИЯ -->
            <button
              @click="removeCharacter(char.character_id)"
              class="remove-char-btn"
              title="Удалить персонажа"
            >
              ×
            </button>
            <img
              :src="getCharacterPortrait(char.character_id)"
              :alt="char.character_name"
              class="character-portrait"
            />
            <span class="character-name">{{ char.character_name }}</span>
            <!-- ИНФОРМАЦИЯ О ЛИНИЯХ -->
            <div v-if="activities[char.character_id]" class="activity-info">
              <div>
                П: {{ activities[char.character_id].manufacturing.used }} /
                {{ activities[char.character_id].manufacturing.total }}
              </div>
              <div>
                И: {{ activities[char.character_id].research.used }} /
                {{ activities[char.character_id].research.total }}
              </div>
            </div>
            <div v-else class="activity-info">
              <small>Загрузка...</small>
            </div>
          </div>
          <!-- Кнопка добавления -->
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
      activities: {}, // Для хранения данных о линиях
      isLoggedIn: false,
      loading: true,
      loginUrl: "https://eve-profitmaster.onrender.com/login",
    };
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
    openLoginPopup() {
      const width = 600;
      const height = 700;

      // Рассчитываем позицию относительно текущего окна браузера, а не всего экрана
      const left = window.top.outerWidth / 2 + window.top.screenX - width / 2;
      const top = window.top.outerHeight / 2 + window.top.screenY - height / 2;

      window.open(
        this.loginUrl,
        "eveLogin",
        `width=${width},height=${height},top=${top},left=${left}`
      );
    },
    handleAuthMessage(event) {
      if (event.data === "auth-success") {
        console.log("Авторизация прошла успешно, обновляем данные...");
        this.loadAppData();
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
          // После загрузки персонажей, получаем данные об их активностях
          this.fetchAllCharacterActivities();
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
    async fetchAllCharacterActivities() {
      const backendUrl = "https://eve-profitmaster.onrender.com";
      for (const char of this.characters) {
        try {
          const response = await axios.get(
            `${backendUrl}/get_character_activity/${char.character_id}`
          );
          // Используем Vue.set или прямое присваивание для реактивности
          this.activities = {
            ...this.activities,
            [char.character_id]: response.data,
          };
        } catch (error) {
          console.error(
            `Ошибка при получении активности для ${char.character_name}:`,
            error
          );
        }
      }
    },
    async removeCharacter(characterId) {
      if (
        !confirm(
          "Вы уверены, что хотите удалить этого персонажа? Вам придется заново авторизовать его."
        )
      ) {
        return;
      }
      const backendUrl = "https://eve-profitmaster.onrender.com";
      try {
        await axios.post(`${backendUrl}/remove_character`, {
          character_id: characterId,
        });
        // Обновляем данные после удаления
        this.loadAppData();
      } catch (error) {
        console.error("Ошибка при удалении персонажа:", error);
        alert("Не удалось удалить персонажа. Пожалуйста, попробуйте снова.");
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
        4: "Мат. эффективность",
        5: "Врем. эффективность",
        6: "Реакции",
        7: "Изобретение",
      };
      return jobTypes[activityId] || "Неизвестно";
    },
    getJobStatus(job) {
      if (job.status === "active" && new Date(job.end_date) < new Date()) {
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
/* ... (все ваши старые стили остаются здесь) ... */
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
  width: 120px;
  text-decoration: none;
  color: inherit;
  position: relative;
  background-color: #2c2c2c;
  padding: 10px;
  border-radius: 8px;
}
.add-char-item {
  cursor: pointer;
  border: 2px dashed #555;
  justify-content: center;
  transition: background-color 0.2s, border-color 0.2s;
  height: 120px;
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
/* НОВЫЕ СТИЛИ */
.remove-char-btn {
  position: absolute;
  top: 0;
  right: 0;
  background: #555;
  color: white;
  border: none;
  border-radius: 0 8px 0 50%;
  width: 24px;
  height: 24px;
  font-size: 16px;
  line-height: 24px;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.2s;
}
.character-item:hover .remove-char-btn {
  opacity: 1;
}
.activity-info {
  font-size: 12px;
  margin-top: 5px;
  color: #aaa;
}
</style>
