<template>
  <div class="timeline-container">
    <div class="timeline-controls">
      <button @click="setScale('day')" :class="{ active: scaleMode === 'day' }">
        День
      </button>
      <button
        @click="setScale('week')"
        :class="{ active: scaleMode === 'week' }"
      >
        Неделя
      </button>
      <button
        @click="setScale('month')"
        :class="{ active: scaleMode === 'month' }"
      >
        Месяц
      </button>
    </div>
    <div
      class="timeline-scroll-wrapper"
      ref="timelineScrollWrapper"
      @scroll="$emit('scroll', $event)"
      :class="{ 'is-locked': selectedCharacterId }"
    >
      <div v-if="isLoading" class="loading-indicator">Загрузка данных...</div>
      <div v-else-if="!hasJobs" class="no-jobs-placeholder">
        Нет активных работ для отображения.
      </div>
      <div
        v-else
        class="timeline-wrapper"
        :style="{ width: timelineWidth + 'px' }"
      >
        <div class="time-headers">
          <div
            v-for="marker in timeScale"
            :key="marker.timestamp"
            class="time-header-item"
            :style="{ left: marker.left + 'px' }"
          >
            <span>{{ marker.label }}</span>
          </div>
        </div>
        <div class="current-time-line"></div>
        <div class="character-rows-container">
          <div
            v-for="char in characters"
            :key="char.character_id"
            class="character-row-group"
            :class="getRowClass(char.character_id)"
          >
            <div
              v-if="
                selectedCharacterId &&
                selectedCharacterId === char.character_id
              "
              class="expanded-jobs-view"
            >
              <div
                v-for="job in jobs[char.character_id]"
                :key="job.job_id"
                class="expanded-job-item"
              >
                <span class="job-name">{{ job.product_name }}</span>
                <span class="job-time">{{
                  getTimeRemaining(job.end_date)
                }}</span>
              </div>
            </div>
            <div v-else class="job-lanes-container">
              <template v-if="processedJobs[char.character_id]">
                <div
                  v-for="(lane, index) in processedJobs[char.character_id]"
                  :key="index"
                  class="job-lane"
                >
                  <div
                    v-for="job in lane"
                    :key="job.job_id"
                    class="job-bar"
                    :style="getJobStyle(job)"
                    @mouseover="showTooltip(job, $event)"
                    @mouseleave="hideTooltip"
                  >
                    <div
                      class="job-bar-fill"
                      :style="{ backgroundColor: getJobColor(job.activity_id) }"
                    ></div>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="tooltip.visible" class="tooltip" :style="tooltipStyle">
      <strong>{{ tooltip.job.product_name }}</strong
      ><br />
      <small>Локация: {{ tooltip.job.location_name }}</small
      ><br /><br />
      Тип: {{ getJobType(tooltip.job.activity_id) }}<br />
      Завершится через: {{ getTimeRemaining(tooltip.job.end_date) }}
    </div>
  </div>
</template>
<script>
export default {
  name: "JobsTimeline",
  props: ["jobs", "characters", "isLoading", "selectedCharacterId"],
  emits: ["scroll"],
  data: () => ({
    scaleMode: "week",
    tooltip: { visible: false, job: null, x: 0, y: 0 },
    now: new Date(),
    interval: null,
    containerWidth: 1000,
  }),
  computed: {
    pixelsPerHour() {
      return { day: 120, week: 30, month: 8 }[this.scaleMode];
    },
    timelineDurationMs() {
      const allJobs = Object.values(this.jobs).flat();
      if (allJobs.length === 0) return 24 * 3600e3;
      const maxEnd = Math.max(
        ...allJobs.map((j) => new Date(j.end_date).getTime())
      );
      return Math.max(0, maxEnd - this.now.getTime());
    },
    timelineWidth() {
      return (
        (this.timelineDurationMs / 3600e3) * this.pixelsPerHour +
        this.containerWidth
      );
    },
    timeScale() {
      const scale = [];
      const units = {
        day: {
          step: 3600e3 * 3,
          format: (d) => `${String(d.getHours()).padStart(2, "0")}:00`,
        },
        week: {
          step: 3600e3 * 24,
          format: (d) =>
            d.toLocaleDateString("ru-RU", { day: "2-digit", month: "short" }),
        },
        month: {
          step: 3600e3 * 24 * 7,
          format: (d) =>
            d.toLocaleDateString("ru-RU", { day: "2-digit", month: "short" }),
        },
      };
      const current = units[this.scaleMode];
      for (
        let i = 0;
        i * current.step < this.timelineDurationMs + 48 * 3600e3;
        i++
      ) {
        const date = new Date(this.now.getTime() + i * current.step);
        const left =
          ((date.getTime() - this.now.getTime()) / 3600e3) * this.pixelsPerHour;
        if (left > 8000) break;
        scale.push({ label: current.format(date), left });
      }
      return scale;
    },
    hasJobs() {
      return this.characters.some((c) => this.jobs[c.character_id]?.length > 0);
    },
    processedJobs() {
      const result = {};
      for (const char of this.characters) {
        if (this.jobs[char.character_id])
          result[char.character_id] = this.layoutJobs(
            this.jobs[char.character_id]
          );
      }
      return result;
    },
    tooltipStyle() {
      if (!this.tooltip.visible) return {};
      return {
        top: `${this.tooltip.y}px`,
        left: `${this.tooltip.x}px`,
        "--tooltip-bg": this.getJobColor(this.tooltip.job.activity_id),
      };
    },
  },
  methods: {
    getRowClass(characterId) {
      if (!this.selectedCharacterId) return {};
      return {
        "is-selected": this.selectedCharacterId === characterId,
        "is-hidden": this.selectedCharacterId !== characterId,
      };
    },
    setScale(mode) {
      this.scaleMode = mode;
    },
    layoutJobs(jobs) {
      if (!jobs?.length) return [];
      const lanes = [];
      const sortedJobs = [...jobs].sort(
        (a, b) => new Date(a.start_date) - new Date(b.start_date)
      );
      for (const job of sortedJobs) {
        if (new Date(job.end_date) < this.now) continue;
        let placed = false;
        for (const lane of lanes) {
          if (
            new Date(lane[lane.length - 1].end_date) <= new Date(job.start_date)
          ) {
            lane.push(job);
            placed = true;
            break;
          }
        }
        if (!placed) lanes.push([job]);
      }
      return lanes;
    },
    getJobStyle(job) {
      const startOffsetMs = Math.max(
        0,
        new Date(job.start_date).getTime() - this.now.getTime()
      );
      const durationMs =
        new Date(job.end_date).getTime() - new Date(job.start_date).getTime();
      const left = (startOffsetMs / 3600e3) * this.pixelsPerHour;
      const width = (durationMs / 3600e3) * this.pixelsPerHour;
      return {
        transform: `translateX(${left}px)`,
        width: `${Math.max(2, width)}px`,
      };
    },
    getJobColor(id) {
      return (
        {
          1: "#E1AA36",
          4: "#239BA7",
          5: "#239BA7",
          3: "#239BA7",
          8: "#239BA7",
          6: "#7ADAA5",
        }[id] || "#7f8c8d"
      );
    },
    getJobType(id) {
      return (
        {
          1: "Производство",
          3: "Копирование",
          4: "Мат. эффективность",
          5: "Врем. эффективность",
          6: "Реакции",
          8: "Изобретение",
        }[id] || "Неизвестно"
      );
    },
    getTimeRemaining(endDate) {
      const s = Math.max(0, (new Date(endDate) - this.now) / 1000);
      const d = Math.floor(s / 86400);
      const h = Math.floor(s / 3600) % 24;
      const m = Math.floor(s / 60) % 60;
      if (d > 0) return `${d}д ${h}ч`;
      return `${h}ч ${m}м`;
    },
    showTooltip(job, e) {
      this.tooltip = {
        visible: true,
        job,
        x: e.clientX + 15,
        y: e.clientY + 15,
      };
    },
    hideTooltip() {
      this.tooltip.visible = false;
    },
    updateTime() {
      this.now = new Date();
    },
    updateContainerWidth() {
      if (this.$refs.container)
        this.containerWidth = this.$refs.container.clientWidth;
    },
    setScrollTop(scrollTop) {
      this.$refs.timelineScrollWrapper.scrollTop = scrollTop;
    },
  },
  mounted() {
    this.interval = setInterval(this.updateTime, 1000);
    this.updateContainerWidth();
    window.addEventListener("resize", this.updateContainerWidth);
  },
  beforeUnmount() {
    clearInterval(this.interval);
    window.removeEventListener("resize", this.updateContainerWidth);
  },
};
</script>
<style scoped>
.timeline-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #282c34;
}
.timeline-controls {
  padding: 10px 20px;
  background-color: #20232a;
  border-bottom: 1px solid #3c414d;
  flex-shrink: 0;
  text-align: right;
}
.timeline-controls button {
  background-color: #3a3f4b;
  color: #ddd;
  border: 1px solid #555;
  padding: 5px 15px;
  margin-left: 10px;
  border-radius: 5px;
  cursor: pointer;
}
.timeline-controls button.active {
  background-color: #61afef;
  color: #fff;
  border-color: #61afef;
}
.timeline-scroll-wrapper {
  flex-grow: 1;
  overflow: auto;
}
.timeline-scroll-wrapper.is-locked {
  overflow-y: hidden;
}
.timeline-wrapper {
  position: relative;
  min-height: 100%;
}
.time-headers {
  position: sticky;
  top: 0;
  background-color: #282c34;
  z-index: 2;
  height: 20px;
  border-bottom: 1px solid #444;
}
.time-header-item {
  position: absolute;
  color: #888;
  font-size: 12px;
  transform: translateX(-50%);
  border-left: 1px solid #444;
  height: 100%;
  padding-left: 4px;
}
.current-time-line {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 2px;
  background-color: #ff6b6b;
  z-index: 3;
}
.character-rows-container {
  padding-top: 10px;
}
.character-row-group {
  min-height: 120px;
  box-sizing: border-box;
  border-bottom: 1px solid #3c414d;
  transition: all 0.3s ease-in-out;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.character-row-group.is-selected {
  min-height: 250px;
  background-color: #32363e;
}
.character-row-group.is-hidden {
  min-height: 50px;
  overflow: hidden;
}
.job-lanes-container {
  padding: 15px 0;
}
.expanded-jobs-view {
  padding: 20px;
  color: #e0e0e0;
  height: 100%;
  overflow-y: auto;
}
.expanded-job-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #4a4f58;
}
.expanded-job-item:last-child {
  border-bottom: none;
}
.job-name {
  font-weight: 500;
}
.job-time {
  font-family: monospace;
  color: #abb2bf;
}
.job-lane {
  position: relative;
  height: 8px;
  margin-bottom: 2px;
}
.job-bar {
  position: absolute;
  height: 7px;
  border-radius: 2px;
  cursor: pointer;
}
.job-bar-fill {
  height: 100%;
  width: 100%;
  border-radius: 2px;
}
.tooltip {
  position: fixed;
  background-color: var(--tooltip-bg, #222);
  color: #fff;
  border: 1px solid #555;
  padding: 10px;
  border-radius: 5px;
  z-index: 1000;
  pointer-events: none;
  font-size: 14px;
  white-space: nowrap;
  backdrop-filter: blur(2px);
}
.loading-indicator,
.no-jobs-placeholder {
  text-align: center;
  padding-top: 50px;
  font-size: 18px;
  color: #888;
}
</style>
