<template>
  <div class="home">
    <h1>Отслеживание производства EVE Online</h1>

    <div v-if="!isLoggedIn && !loading">
      <p>Войдите, чтобы начать отслеживать ваши производственные работы.</p>
      <a :href="loginUrl">
        <img
          src="/eve-sso-login-white-large.png"
          alt="Log in with EVE Online"
        />
      </a>
    </div>

    <div v-if="isLoggedIn && !loading">
      <h2>Ваши текущие работы:</h2>

      <a :href="loginUrl">
        <button class="add-char-button">Добавить персонажа</button>
      </a>

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
      isLoggedIn: false,
      loading: false,
      loginUrl: "https://eve-profitmaster.onrender.com/login",
    };
  },
  async created() {
    this.fetchJobs();
  },
  methods: {
    async fetchJobs() {
      const backendUrl = "https://eve-profitmaster.onrender.com";
      this.loading = true;
      try {
        const response = await axios.get(`${backendUrl}/get_jobs`);

        const jobsData = response.data;

        // Теперь мы знаем, что пользователь вошел в систему, если данные получены
        this.isLoggedIn = true;

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
      } finally {
        this.loading = false;
      }
    },

    async fetchTypeNames(ids) {
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
pre {
  background-color: #f4f4f4;
  border: 1px solid #ddd;
  padding: 15px;
  text-align: left;
  overflow-x: auto;
}
.add-char-button {
  background-color: #3e3e3e;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  margin-bottom: 20px;
}
.add-char-button:hover {
  background-color: #555555;
}
</style>
