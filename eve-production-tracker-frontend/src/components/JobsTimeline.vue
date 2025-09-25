<template>
  <div class="timeline-container">
    <div v-if="isLoading" class="loading-indicator">Загрузка данных...</div>
    <div v-else-if="!hasJobs" class="no-jobs-placeholder">
      Нет активных работ для отображения.
    </div>
    <div v-else class="timeline-wrapper" ref="timelineWrapper">
      <!-- Заголовки времени -->
      <div class="time-headers">
        <div
          v-for="hour in timeScale"
          :key="hour.timestamp"
          class="time-header-item"
          :style="{ left: hour.left + 'px' }"
        >
          {{ hour.label }}
        </div>
      </div>
      <!-- Группы работ по персонажам -->
      <div v-for="charId in characterIds" :key="charId" class="character-row">
        <div class="character-label">{{ getCharacterName(charId) }}</div>
        <div class="job-bars-container">
          <div
            v-for="job in jobs[charId]"
            :key="job.job_id"
            class="job-bar"
            :class="getJobClass(job.activity_id)"
            :style="getJobStyle(job)"
            @mouseover="showTooltip(job, $event)"
            @mouseleave="hideTooltip"
          >
            <span class="job-status-icon">{{ getJobStatusIcon(job) }}</span>
            <span class="job-bar-label">{{ job.product_name }}</span>
          </div>
        </div>
      </div>
    </div>
    <!-- Всплывающая подсказка -->
    <div
      v-if="tooltip.visible"
      class="tooltip"
      :style="{ top: tooltip.y + 'px', left: tooltip.x + 'px' }"
    >
      <strong>{{ tooltip.job.product_name }}</strong
      ><br />
      Тип: {{ getJobType(tooltip.job.activity_id) }}<br />
      Статус: {{ getJobStatus(tooltip.job) }}<br />
      Начало: {{ new Date(tooltip.job.start_date).toLocaleString() }}<br />
      Конец: {{ new Date(tooltip.job.end_date).toLocaleString() }}
    </div>
  </div>
</template>

<script>
export default {
  name: "JobsTimeline",
  props: {
    jobs: Object,
    characters: Array,
    isLoading: Boolean,
  },
  data() {
    return {
      timelineStart: new Date(),
      pixelsPerHour: 60,
      timeScale: [],
      tooltip: { visible: false, job: null, x: 0, y: 0 },
    };
  },
  computed: {
    characterIds() {
      return this.characters.map((c) => c.character_id);
    },
    hasJobs() {
      return Object.values(this.jobs).some((jobList) => jobList.length > 0);
    },
  },
  watch: {
    jobs: {
      handler() {
        this.calculateTimeScale();
      },
      deep: true,
      immediate: true,
    },
  },
  methods: {
    getCharacterName(charId) {
      const char = this.characters.find((c) => c.character_id == charId);
      return char ? char.character_name : `Персонаж ${charId}`;
    },
    calculateTimeScale() {
      const now = new Date();
      this.timelineStart = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        now.getHours()
      );

      const scale = [];
      const hoursToShow = 48; // Показываем 48 часов
      for (let i = 0; i < hoursToShow; i++) {
        const date = new Date(this.timelineStart.getTime() + i * 3600 * 1000);
        scale.push({
          timestamp: date.getTime(),
          label: `${String(date.getHours()).padStart(2, "0")}:00`,
          left: i * this.pixelsPerHour,
        });
      }
      this.timeScale = scale;
    },
    getJobStyle(job) {
      const startDate = new Date(job.start_date);
      const endDate = new Date(job.end_date);

      const startOffsetMs = Math.max(
        0,
        startDate.getTime() - this.timelineStart.getTime()
      );
      const durationMs = endDate.getTime() - startDate.getTime();

      const left = (startOffsetMs / (3600 * 1000)) * this.pixelsPerHour;
      const width = (durationMs / (3600 * 1000)) * this.pixelsPerHour;

      return {
        left: `${left}px`,
        width: `${width}px`,
      };
    },
    getJobClass(activityId) {
      const classes = {
        1: "job-manufacturing",
        5: "job-research-te",
        4: "job-research-me",
        8: "job-invention",
        3: "job-copying",
        6: "job-reaction",
      };
      return classes[activityId] || "job-default";
    },
    getJobStatusIcon(job) {
      if (new Date(job.end_date) < new Date()) return "✅";
      if (job.status === "paused") return "⏸️";
      return "⚙️";
    },
    getJobType(activityId) {
      const jobTypes = {
        1: "Производство",
        2: "Исследование",
        3: "Копирование",
        4: "Мат. эффективность",
        5: "Врем. эффективность",
        6: "Реакции",
        7: "Изобретение",
        8: "Изобретение",
      };
      return jobTypes[activityId] || "Неизвестно";
    },
    getJobStatus(job) {
      if (new Date(job.end_date) < new Date()) return "Завершено";
      return { active: "Идет", paused: "На паузе" }[job.status] || "Неизвестно";
    },
    showTooltip(job, event) {
      this.tooltip = {
        visible: true,
        job: job,
        x: event.clientX + 15,
        y: event.clientY + 15,
      };
    },
    hideTooltip() {
      this.tooltip.visible = false;
    },
  },
  mounted() {
    this.calculateTimeScale();
  },
};
</script>

<style scoped>
.timeline-container {
  flex-grow: 1;
  padding: 20px;
  overflow-x: auto;
  position: relative;
}
.timeline-wrapper {
  position: relative;
  min-height: 100%;
}
.time-headers {
  display: flex;
  position: sticky;
  top: 0;
  background-color: #1a1a1a;
  z-index: 2;
  height: 30px;
  border-bottom: 1px solid #444;
  padding-left: 150px; /* Отступ для имен персонажей */
}
.time-header-item {
  position: absolute;
  color: #888;
  font-size: 12px;
}
.character-row {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
  min-height: 40px;
}
.character-label {
  width: 140px;
  min-width: 140px;
  padding-right: 10px;
  text-align: right;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.job-bars-container {
  position: relative;
  width: 100%;
  height: 40px;
}
.job-bar {
  position: absolute;
  height: 28px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  color: #fff;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  cursor: pointer;
}
.job-bar-label {
  margin-left: 5px;
}
.job-manufacturing {
  background: linear-gradient(to right, #e67e22, #d35400);
}
.job-research-te,
.job-research-me {
  background: linear-gradient(to right, #3498db, #2980b9);
}
.job-invention {
  background: linear-gradient(to right, #9b59b6, #8e44ad);
}
.job-copying {
  background: linear-gradient(to right, #1abc9c, #16a085);
}
.job-reaction {
  background: linear-gradient(to right, #f1c40f, #f39c12);
}
.job-default {
  background: #7f8c8d;
}

.tooltip {
  position: fixed;
  background-color: #333;
  border: 1px solid #555;
  padding: 10px;
  border-radius: 5px;
  z-index: 100;
  pointer-events: none;
  font-size: 14px;
  white-space: nowrap;
}
.loading-indicator,
.no-jobs-placeholder {
  text-align: center;
  margin-top: 50px;
  font-size: 18px;
  color: #888;
}
</style>
