<template>
  <div class="timeline-container" ref="container">
    <div v-if="isLoading" class="loading-indicator">Загрузка данных...</div>
    <div v-else-if="!hasJobs" class="no-jobs-placeholder">
      Нет активных работ для отображения.
    </div>
    <div v-else class="timeline-wrapper">
      <!-- Заголовки времени -->
      <div class="time-headers" :style="{ 'padding-left': labelWidth + 'px' }">
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
      <div
        v-for="charId in characterIds"
        :key="charId"
        class="character-row-group"
      >
        <div class="character-label" :style="{ width: labelWidth + 'px' }">
          {{ getCharacterName(charId) }}
        </div>
        <div class="job-lanes-container">
          <div
            v-for="(lane, index) in processedJobs[charId]"
            :key="index"
            class="job-lane"
          >
            <div
              v-for="job in lane"
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
  props: ["jobs", "characters", "isLoading"],
  data() {
    return {
      timelineStart: new Date(),
      pixelsPerHour: 100,
      timeScale: [],
      tooltip: { visible: false, job: null, x: 0, y: 0 },
      labelWidth: 150,
    };
  },
  computed: {
    characterIds() {
      return this.characters.map((c) => c.character_id);
    },
    hasJobs() {
      return this.characterIds.some(
        (id) => this.jobs[id] && this.jobs[id].length > 0
      );
    },
    processedJobs() {
      const result = {};
      for (const charId of this.characterIds) {
        const charJobs = this.jobs[charId] || [];
        result[charId] = this.layoutJobs(charJobs);
      }
      return result;
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
    layoutJobs(jobs) {
      const lanes = [];
      const sortedJobs = [...jobs].sort(
        (a, b) => new Date(a.start_date) - new Date(b.start_date)
      );

      for (const job of sortedJobs) {
        let placed = false;
        for (const lane of lanes) {
          const lastJobInLane = lane[lane.length - 1];
          if (new Date(lastJobInLane.end_date) <= new Date(job.start_date)) {
            lane.push(job);
            placed = true;
            break;
          }
        }
        if (!placed) {
          lanes.push([job]);
        }
      }
      return lanes;
    },
    getCharacterName(charId) {
      const char = this.characters.find((c) => c.character_id == charId);
      return char ? char.character_name : `ID: ${charId}`;
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
      const containerWidth = this.$refs.container
        ? this.$refs.container.scrollWidth
        : 2000;
      const hoursToShow = Math.ceil(containerWidth / this.pixelsPerHour);

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
      return { left: `${left}px`, width: `${width}px` };
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
      return "⚙️";
    },
    getJobType(activityId) {
      const jobTypes = {
        1: "Производство",
        3: "Копирование",
        4: "Мат. эффективность",
        5: "Врем. эффективность",
        6: "Реакции",
        8: "Изобретение",
      };
      return jobTypes[activityId] || "Неизвестно";
    },
    getJobStatus(job) {
      if (new Date(job.end_date) < new Date()) return "Завершено";
      return { active: "Идет" }[job.status] || "Неизвестно";
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
    window.addEventListener("resize", this.calculateTimeScale);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.calculateTimeScale);
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
}
.time-header-item {
  position: absolute;
  color: #888;
  font-size: 12px;
}
.character-row-group {
  display: flex;
  align-items: flex-start;
  border-bottom: 1px solid #333;
  padding: 10px 0;
}
.character-label {
  padding-right: 10px;
  text-align: right;
  font-weight: bold;
  color: #ddd;
  padding-top: 5px;
}
.job-lanes-container {
  flex-grow: 1;
}
.job-lane {
  position: relative;
  height: 32px;
  margin-bottom: 2px;
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
  border: 1px solid rgba(0, 0, 0, 0.3);
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
  background-color: #222;
  border: 1px solid #555;
  padding: 10px;
  border-radius: 5px;
  z-index: 1000;
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
