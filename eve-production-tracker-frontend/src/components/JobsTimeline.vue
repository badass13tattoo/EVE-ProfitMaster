<template>
  <div class="timeline-container">
    <div class="timeline-controls">
      <button @click="setScale('day')" :class="{ active: scaleMode === 'day' }">
        Day
      </button>
      <button
        @click="setScale('week')"
        :class="{ active: scaleMode === 'week' }"
      >
        Week
      </button>
      <button
        @click="setScale('month')"
        :class="{ active: scaleMode === 'month' }"
      >
        Month
      </button>
    </div>
    <div
      class="timeline-scroll-wrapper"
      :class="{ 'is-locked': selectedCharacterId }"
    >
      <div v-if="isLoading" class="loading-indicator">Data loading...</div>
      <div v-else-if="!hasJobs" class="no-jobs-placeholder">No jobs.</div>
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
            :style="getCharacterRowStyle(char.character_id)"
          >
            <div
              v-if="
                selectedCharacterId && selectedCharacterId === char.character_id
              "
              class="expanded-jobs-view"
            >
              <div
                v-if="
                  jobs[char.character_id] && jobs[char.character_id].length > 10
                "
                class="focus-jobs-count"
              >
                {{ jobs[char.character_id].length }} работ - прокрутка доступна
              </div>
              <div
                v-for="job in jobs[char.character_id]"
                :key="job.job_id"
                class="expanded-job-item"
              >
                <div
                  class="job-bar-focus-view"
                  @mouseover="showTooltip(job, $event)"
                  @mouseleave="hideTooltip"
                >
                  <div
                    class="job-bar-fill"
                    :class="{ 'completed-job': isJobCompleted(job) }"
                    :style="{
                      width: getJobStyle(job).width,
                      transform: getJobStyle(job).transform,
                      backgroundColor: getJobColor(job.activity_id),
                    }"
                  >
                    <span
                      class="job-name-in-bar"
                      v-if="
                        parseInt(getJobStyle(job).width) > 100 &&
                        !isJobCompleted(job)
                      "
                      >{{ job.product_name }}</span
                    >
                    <svg
                      v-if="isJobCompleted(job)"
                      class="checkmark-icon-expanded"
                      viewBox="0 0 24 24"
                    >
                      <path
                        d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"
                        fill="white"
                      />
                    </svg>
                  </div>
                </div>
                <span class="job-time">{{
                  isJobCompleted(job)
                    ? "Завершено"
                    : getTimeRemaining(job.end_date)
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
                    :class="{
                      'has-overlap': job.hasOverlap,
                      'completed-job-bar': isJobCompleted(job),
                    }"
                    :style="getJobStyle(job)"
                    @mouseover="showTooltip(job, $event)"
                    @mouseleave="hideTooltip"
                  >
                    <div
                      class="job-bar-fill"
                      :class="{ 'completed-job': isJobCompleted(job) }"
                      :style="{ backgroundColor: getJobColor(job.activity_id) }"
                    >
                      <svg
                        v-if="isJobCompleted(job)"
                        class="checkmark-icon"
                        viewBox="0 0 24 24"
                      >
                        <path
                          d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"
                          fill="white"
                        />
                      </svg>
                    </div>
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
      <small>Location: {{ tooltip.job.location_name }}</small
      ><br /><br />
      Type: {{ getJobType(tooltip.job.activity_id) }}<br />
      <span v-if="tooltip.job.is_planet_job">
        <span
          v-if="tooltip.job.status === 'needs_attention'"
          style="color: #e06c75"
        >
          ⚠️ Needs attention
        </span>
        <span v-else>
          completion in: {{ getTimeRemaining(tooltip.job.end_date) }}
        </span>
      </span>
      <span v-else>
        completion in: {{ getTimeRemaining(tooltip.job.end_date) }}
      </span>
    </div>
  </div>
</template>
<script>
export default {
  name: "JobsTimeline",
  props: ["jobs", "characters", "planets", "isLoading", "selectedCharacterId"],
  inject: ["eventBus"],
  emits: [],
  data: () => ({
    scaleMode: "week",
    tooltip: { visible: false, job: null, x: 0, y: 0 },
    now: new Date(),
    interval: null,
    containerWidth: 1000,
  }),
  watch: {
    "eventBus.scroll": "handleExternalScroll",
  },
  computed: {
    totalDurationMs() {
      const hoursToMs = (h) => h * 3600 * 1000;
      switch (this.scaleMode) {
        case "day":
          return hoursToMs(24);
        case "week":
          return hoursToMs(24 * 7);
        case "month": {
          const now = new Date();
          const year = now.getFullYear();
          const month = now.getMonth();
          const daysInMonth = new Date(year, month + 1, 0).getDate();
          return hoursToMs(24 * daysInMonth);
        }
        default:
          return hoursToMs(24 * 7);
      }
    },
    basePixelsPerHour() {
      switch (this.scaleMode) {
        case "day":
          return 80;
        case "week":
          return 40;
        case "month":
          return 15;
        default:
          return 40;
      }
    },
    timelineWidth() {
      const totalHours = this.totalDurationMs / (3600 * 1000);
      if (totalHours <= 0) {
        return this.containerWidth;
      }

      const idealWidth = totalHours * this.basePixelsPerHour;
      const availableWidth = this.containerWidth || 1000;

      // Ограничиваем ширину таймлайна размерами контейнера
      return Math.min(idealWidth, availableWidth);
    },
    pixelsPerHour() {
      if (!this.totalDurationMs) return 1;
      const totalHours = this.totalDurationMs / (3600 * 1000);
      if (totalHours <= 0) {
        return 1;
      }
      return this.timelineWidth / totalHours;
    },
    timeScale() {
      const scale = [];
      const viewStart = this.now;
      const pph = this.pixelsPerHour;
      if (!pph || pph <= 0) return [];

      let timeCursor, stepMs, formatFn, labelStep;

      switch (this.scaleMode) {
        case "day":
          timeCursor = new Date(viewStart);
          timeCursor.setMinutes(0, 0, 0);
          stepMs = 1 * 3600e3;
          labelStep = this.containerWidth < 700 ? 3 : 1;
          formatFn = (d) => `${String(d.getHours()).padStart(2, "0")}:00`;
          break;
        case "week":
          timeCursor = new Date(viewStart);
          timeCursor.setHours(0, 0, 0, 0);
          stepMs = 24 * 3600e3;
          labelStep = 1;
          formatFn = (d) =>
            d.toLocaleDateString("ru-RU", {
              day: "numeric",
              month: "short",
            });
          break;
        default: // month
          timeCursor = new Date(viewStart);
          timeCursor.setHours(0, 0, 0, 0);
          stepMs = 24 * 3600e3;
          labelStep =
            this.containerWidth < 700 ? 7 : this.containerWidth < 1200 ? 2 : 1;
          formatFn = (d) => d.getDate();
          break;
      }

      const viewEnd = new Date(viewStart.getTime() + this.totalDurationMs);
      let count = 0;
      while (timeCursor < viewEnd) {
        if (timeCursor >= viewStart) {
          if (count % labelStep === 0) {
            const offsetMs = timeCursor.getTime() - viewStart.getTime();
            scale.push({
              timestamp: timeCursor.getTime(),
              label: formatFn(timeCursor),
              left: (offsetMs / 3600e3) * pph,
            });
          }
        }
        timeCursor.setTime(timeCursor.getTime() + stepMs);
        count++;
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
    focusRowHeight() {
      if (!this.selectedCharacterId) return 0;
      const jobsCount = this.jobs[this.selectedCharacterId]?.length || 0;
      const calculatedHeight = jobsCount * 35 + 40;
      // Ограничиваем максимальную высоту чтобы активировать прокрутку
      const maxHeight = window.innerHeight * 0.7; // 70% высоты экрана
      return Math.min(calculatedHeight, maxHeight);
    },
  },
  methods: {
    getCharacterRowStyle(characterId) {
      if (this.selectedCharacterId === characterId) {
        return {
          height: `${this.focusRowHeight}px`,
          minHeight: `${this.focusRowHeight}px`,
        };
      }
      if (
        this.selectedCharacterId &&
        this.selectedCharacterId !== characterId
      ) {
        return {
          height: "0px",
          minHeight: "0px",
          padding: "0",
          border: "none",
        };
      }
      return {
        height: "120px",
        minHeight: "120px",
        maxHeight: "120px",
      };
    },
    handleScroll(event) {
      if (event.target.classList.contains("timeline-scroll-wrapper")) {
        this.eventBus.scroll = {
          source: "timeline",
          scrollTop: event.target.scrollTop,
        };
      }
    },
    handleExternalScroll(scrollData) {
      if (scrollData.source === "timeline") return;
      if (this.$refs.timelineScrollWrapper) {
        this.$refs.timelineScrollWrapper.scrollTop = scrollData.scrollTop;
      }
    },
    getRowClass(characterId) {
      if (!this.selectedCharacterId) return "";
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

      const sortedJobs = [...jobs]
        .map((j) => ({ ...j, hasOverlap: false }))
        .sort((a, b) => new Date(a.start_date) - new Date(b.start_date));

      const lanes = [];

      // Определяем временные границы видимой области
      const viewStart = this.now;
      const viewEnd = new Date(this.now.getTime() + this.totalDurationMs);

      for (const job of sortedJobs) {
        // Показываем работы которые:
        // 1. Еще не завершились (активные)
        // 2. Завершились недавно и еще видны в области просмотра
        const jobEndDate = new Date(job.end_date);
        const jobStartDate = new Date(job.start_date);

        // Пропускаем работы которые завершились слишком давно (за пределами видимой области слева)
        if (
          jobEndDate < viewStart &&
          viewStart - jobEndDate > this.totalDurationMs / 4
        )
          continue;

        // Пропускаем работы которые начнутся слишком поздно (за пределами видимой области справа)
        if (jobStartDate > viewEnd) continue;

        let placed = false;
        // Попробуем найти подходящую линию для работы
        for (const lane of lanes) {
          const lastJobInLane = lane[lane.length - 1];
          // Проверяем есть ли достаточно места между концом последней работы и началом новой
          if (new Date(lastJobInLane.end_date) <= new Date(job.start_date)) {
            lane.push(job);
            placed = true;
            break;
          }
        }

        // Если не удалось разместить в существующих линиях, создаем новую
        if (!placed) {
          lanes.push([job]);
        }
      }

      if (this.selectedCharacterId) {
        return lanes;
      }

      const MAX_LANES = 10; // Ограничиваем для включения вертикальной прокрутки
      if (lanes.length > MAX_LANES) {
        const newLanes = lanes.slice(0, MAX_LANES);
        for (let i = MAX_LANES; i < lanes.length; i++) {
          const targetLaneIndex = i % MAX_LANES;
          newLanes[targetLaneIndex].push(...lanes[i]);
          newLanes[targetLaneIndex].sort(
            (a, b) => new Date(a.start_date) - new Date(b.start_date)
          );
        }

        for (const lane of newLanes) {
          for (let i = 0; i < lane.length; i++) {
            for (let j = i + 1; j < lane.length; j++) {
              const job1 = lane[i];
              const job2 = lane[j];
              if (
                new Date(job1.start_date) < new Date(job2.end_date) &&
                new Date(job2.start_date) < new Date(job1.end_date)
              ) {
                job1.hasOverlap = true;
                job2.hasOverlap = true;
              }
            }
          }
        }
        return newLanes;
      }

      return lanes;
    },
    getJobStyle(job) {
      // Если работа завершена, показываем квадратик в позиции завершения
      if (this.isJobCompleted(job)) {
        // Позиция end_date относительно текущего времени (может быть отрицательной)
        const endOffsetMs =
          new Date(job.end_date).getTime() - this.now.getTime();
        const left = (endOffsetMs / 3600e3) * this.pixelsPerHour;
        return {
          transform: `translateX(${left}px)`,
          width: "10px",
          height: "10px",
          borderRadius: "2px",
        };
      }

      // Для активных работ показываем линию
      const startOffsetMs = Math.max(
        0,
        new Date(job.start_date).getTime() - this.now.getTime()
      );
      const endOffsetMs = new Date(job.end_date).getTime() - this.now.getTime();

      // Если работа уже началась, but not completed, показываем только оставшуюся часть
      const left =
        startOffsetMs === 0 ? 0 : (startOffsetMs / 3600e3) * this.pixelsPerHour;
      const endPosition = (endOffsetMs / 3600e3) * this.pixelsPerHour;
      const width = Math.max(2, endPosition - left);

      return {
        transform: `translateX(${left}px)`,
        width: `${width}px`,
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
          7: "#FF6B6B", // Planet Interaction
        }[id] || "#7f8c8d"
      );
    },
    getJobType(id) {
      return (
        {
          1: "Manufacturing",
          3: "Copying",
          4: "Material Efficiency",
          5: "Time Efficiency",
          6: "Reactions",
          7: "Planet Interaction",
          8: "Invention",
        }[id] || "Unknown"
      );
    },
    isJobCompleted(job) {
      // Для планетных работ проверяем статус
      if (job.is_planet_job) {
        return (
          job.status === "needs_attention" || new Date(job.end_date) <= this.now
        );
      }
      return new Date(job.end_date) <= this.now;
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
      if (this.$el) {
        this.containerWidth = this.$el.clientWidth;
      }
    },
  },
  mounted() {
    this.interval = setInterval(this.updateTime, 1000);
    this.$nextTick(() => {
      this.updateContainerWidth();
      window.addEventListener("resize", this.updateContainerWidth);
      this.$el.addEventListener("scroll", this.handleScroll, true);
    });
  },
  beforeUnmount() {
    clearInterval(this.interval);
    window.removeEventListener("resize", this.updateContainerWidth);
    this.$el.removeEventListener("scroll", this.handleScroll, true);
  },
};
</script>
<style scoped>
.timeline-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  max-width: 100%;
  width: 100%;
}
.timeline-controls {
  padding: 10px 20px;
  background-color: #20232a;
  border-bottom: 1px solid #3c414d;
  flex-shrink: 0;
  text-align: right;
  position: sticky;
  top: 0;
  z-index: 3;
  height: 51px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: flex-end;
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
  box-sizing: border-box;
  overflow: auto;
  width: 100%;
}

.timeline-scroll-wrapper::-webkit-scrollbar {
  width: 8px;
}
.timeline-scroll-wrapper::-webkit-scrollbar-track {
  background: #20232a;
}
.timeline-scroll-wrapper::-webkit-scrollbar-thumb {
  background-color: #4f5b6b;
  border-radius: 4px;
}

.timeline-scroll-wrapper.is-locked {
  overflow-y: hidden;
}
.timeline-wrapper {
  position: relative;
  min-height: 100%;
  gap: 15px;
  max-width: 100%;
  box-sizing: border-box;
}
.time-headers {
  position: sticky;
  top: 0;
  background-color: #282c34;
  z-index: 2;
  height: 20px;
  border-bottom: 1px solid #444;
  top: 0px;
  width: 100%;
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
  z-index: 1;
}
.character-rows-container {
  padding-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  flex-grow: 1;
}
.character-row-group {
  height: 120px;
  min-height: 120px;
  max-height: 120px;
  box-sizing: border-box;
  border-bottom: 1px solid #3c414d;
  transition: all 0.3s ease-in-out;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.character-row-group.is-selected {
  background-color: #32363e;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.character-row-group.is-hidden {
  height: 0px;
  min-height: 0px !important;
  overflow: hidden;
  padding-top: 0;
  padding-bottom: 0;
  border: none;
}
.job-lanes-container {
  padding: 15px 0;
  max-height: 90px;
  overflow-y: auto;
  overflow-x: auto;
  position: relative;
}

.job-lanes-container::before {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  width: 20px;
  height: 100%;
  background: linear-gradient(
    to left,
    rgba(40, 44, 52, 0.8) 0%,
    transparent 100%
  );
  pointer-events: none;
  z-index: 1;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.job-lanes-container:hover::before {
  opacity: 1;
}

.job-lanes-container::-webkit-scrollbar {
  height: 6px;
  width: 6px;
}

.job-lanes-container::-webkit-scrollbar-track {
  background: transparent;
}

.job-lanes-container::-webkit-scrollbar-thumb {
  background-color: #4f5b6b;
  border-radius: 3px;
}

.job-lanes-container::-webkit-scrollbar-corner {
  background: transparent;
}

.expanded-jobs-view {
  padding: 20px;
  color: #e0e0e0;
  height: 100%;
  position: relative;
  overflow-y: auto;
  overflow-x: hidden;
}

.expanded-jobs-view::-webkit-scrollbar {
  width: 8px;
}

.expanded-jobs-view::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.expanded-jobs-view::-webkit-scrollbar-thumb {
  background-color: #4f5b6b;
  border-radius: 4px;
}

.expanded-jobs-view::-webkit-scrollbar-thumb:hover {
  background-color: #61afef;
}

.focus-jobs-count {
  position: sticky;
  top: -100px;
  background: linear-gradient(135deg, #32363e 0%, #2a2e36 100%);
  color: #abb2bf;
  font-size: 12px;
  font-weight: 600;
  padding: 8px 12px;
  margin: -110px -10px 10px -10px;
  border-radius: 6px;
  text-align: center;
  z-index: 2;
  border: 1px solid #4a5160;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}
.expanded-job-item {
  display: grid;
  grid-template-columns: 1fr 100px;
  gap: 15px;
  align-items: center;
  margin-bottom: 5px;
}
.job-bar-focus-view {
  position: relative;
  width: 100%;
  height: 30px;
  background-color: #20232a;
  border-radius: 4px;
}

.job-bar-focus-view .completed-job {
  width: 30px !important;
  height: 30px !important;
  border-radius: 6px !important;
}
.job-bar-focus-view .job-bar-fill {
  position: absolute;
  height: 100%;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  box-sizing: border-box;
  overflow: hidden;
  white-space: nowrap;
}
.job-name-in-bar {
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}
.job-time {
  font-family: monospace;
  color: #abb2bf;
}
.job-lane {
  position: relative;
  height: 12px;
  margin-bottom: 2px;
}
.job-bar {
  position: absolute;
  height: 10px;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.1s ease-in-out;
}

.job-bar.completed-job-bar {
  height: 10px !important;
  width: 10px !important;
  animation: pulse 2s infinite;
}

.job-bar .completed-job {
  width: 10px !important;
  height: 10px !important;
  border-radius: 2px !important;
  animation: pulse 2s infinite;
}
.job-bar.has-overlap {
  box-shadow: 0 0 8px 1px rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.job-bar-fill {
  height: 100%;
  width: 100%;
  border-radius: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.job-bar-fill.completed-job {
  animation: pulse 2s infinite;
  border-radius: 4px;
}

.checkmark-icon {
  width: 12px;
  height: 12px;
  filter: drop-shadow(1px 1px 2px rgba(0, 0, 0, 0.5));
}

.checkmark-icon-expanded {
  width: 16px;
  height: 16px;
  filter: drop-shadow(1px 1px 2px rgba(0, 0, 0, 0.5));
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

/* Анимация пульсации для завершенных работ */
@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.7);
  }
  50% {
    transform: scale(1.1);
    opacity: 0.9;
    box-shadow: 0 0 0 8px rgba(255, 255, 255, 0);
  }
  100% {
    transform: scale(1);
    opacity: 1;
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
  }
}
</style>
