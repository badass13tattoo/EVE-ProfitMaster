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
                    :style="{
                      width: getJobStyle(job).width,
                      transform: getJobStyle(job).transform,
                      backgroundColor: getJobColor(job.activity_id),
                    }"
                  >
                    <span
                      class="job-name-in-bar"
                      v-if="parseInt(getJobStyle(job).width) > 100"
                      >{{ job.product_name }}</span
                    >
                  </div>
                </div>
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
                    :class="{ 'has-overlap': job.hasOverlap }"
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
      <small>Location: {{ tooltip.job.location_name }}</small
      ><br /><br />
      Type: {{ getJobType(tooltip.job.activity_id) }}<br />
      completion in: {{ getTimeRemaining(tooltip.job.end_date) }}
    </div>
  </div>
</template>
<script>
export default {
  name: "JobsTimeline",
  props: ["jobs", "characters", "isLoading", "selectedCharacterId"],
  emits: [],
  data: () => ({
    scaleMode: "week",
    tooltip: { visible: false, job: null, x: 0, y: 0 },
    now: new Date(),
    interval: null,
    containerWidth: 1000,
  }),
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
    pixelsPerHour() {
      if (!this.containerWidth || !this.totalDurationMs) return 1;
      const availableWidth = this.containerWidth;
      const totalHours = this.totalDurationMs / (3600 * 1000);
      return availableWidth / totalHours;
    },
    timelineWidth() {
      return this.containerWidth;
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
      return jobsCount * 35 + 40;
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
      for (const job of sortedJobs) {
        if (new Date(job.end_date) < this.now) continue;

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

      if (this.selectedCharacterId) {
        return lanes;
      }

      const MAX_LANES = 10;
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
          1: "Manufacturing",
          3: "Copying",
          4: "Material Efficiency",
          5: "Time Efficiency",
          6: "Reactions",
          8: "Invention",
        }[id] || "Unknown"
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
      if (this.$refs.timelineScrollWrapper)
        this.containerWidth = this.$refs.timelineScrollWrapper.clientWidth;
    },
  },
  mounted() {
    this.interval = setInterval(this.updateTime, 1000);
    this.$nextTick(() => {
      this.updateContainerWidth();
      window.addEventListener("resize", this.updateContainerWidth);
    });
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
  padding-left: 20px;
  box-sizing: border-box;
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
  background-color: #32363e;
  overflow: hidden;
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
  max-height: 90px; /* Исправленное значение */
  overflow-y: hidden;
}
.expanded-jobs-view {
  padding: 20px;
  color: #e0e0e0;
  height: 100%;
  overflow-y: auto;
  position: relative;
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
.job-bar.has-overlap {
  box-shadow: 0 0 8px 1px rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
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