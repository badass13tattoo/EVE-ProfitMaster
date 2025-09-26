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
      <div v-if="isLoading" class="timeline-status loading-indicator">
        Data loading...
      </div>
      <div v-else-if="!hasJobs" class="timeline-status no-jobs-placeholder">
        No jobs.
      </div>

      <div
        v-else
        class="timeline-wrapper"
        ref="timelineWrapper"
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
            v-for="(char, index) in characters"
            :key="`border-${char.character_id}`"
            class="character-border-line"
            :class="{
              'active-character': selectedCharacterId === char.character_id,
            }"
            :style="getCharacterBorderStyle(char.character_id, index)"
          ></div>

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
                    :class="{ 'completed-job-focus': isJobCompleted(job) }"
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
              <div class="completed-jobs-indicators">
                <div
                  v-for="job in getCompletedJobs(char.character_id)"
                  :key="`completed-${job.job_id}`"
                  :data-job-id="job.job_id"
                  :data-activity-id="job.activity_id"
                  class="completed-job-indicator"
                  :style="getCompletedJobIndicatorStyle(job)"
                  @mouseover="showTooltip(job, $event)"
                  @mouseleave="hideTooltip"
                >
                  <svg class="checkmark-icon-indicator" viewBox="0 0 24 24">
                    <path
                      d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"
                      fill="white"
                    />
                  </svg>
                </div>
              </div>

              <div v-if="planets[char.character_id]" class="planets-lane">
                <div
                  v-for="planet in planets[char.character_id]"
                  :key="`planet-${planet.planet_id}`"
                  class="planet-job-lane"
                >
                  <div
                    v-for="(job, index) in getPlanetJobs(planet)"
                    :key="`planet-job-${planet.planet_id}-${index}`"
                    class="planet-job-bar"
                    :class="{
                      'planet-needs-attention': planet.needs_attention,
                    }"
                    :style="getPlanetJobStyle(job, planet)"
                    @mouseover="showPlanetTooltip(planet, $event)"
                    @mouseleave="hideTooltip"
                  >
                    <div
                      class="planet-job-fill"
                      :style="{ backgroundColor: '#ECECBB' }"
                    >
                      <div
                        v-if="planet.needs_attention"
                        class="attention-indicator"
                      >
                        ✕
                      </div>
                      <div class="planet-name">{{ planet.planet_name }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <div
                v-if="industryJobs[char.character_id]"
                class="industry-jobs-lane"
              >
                <div
                  v-for="(lane, index) in getIndustryJobLanes(
                    char.character_id
                  )"
                  :key="`industry-lane-${index}`"
                  class="industry-job-lane"
                >
                  <div
                    v-for="job in lane"
                    :key="`industry-${job.job_id}`"
                    class="industry-job-bar"
                    :class="{
                      'industry-job-completed': job.is_completed,
                      'industry-job-paused': job.is_paused,
                      'industry-job-high-priority': job.priority === 'high',
                    }"
                    :style="getIndustryJobStyle(job)"
                    @mouseover="showIndustryJobTooltip(job, $event)"
                    @mouseleave="hideTooltip"
                  >
                    <div
                      class="industry-job-fill"
                      :style="{
                        backgroundColor: getIndustryJobColor(job.activity_id),
                      }"
                    >
                      <div class="industry-job-name">
                        {{ job.product_name }}
                      </div>
                      <div
                        class="industry-job-progress"
                        v-if="!job.is_completed"
                      >
                        {{ Math.round(job.progress_percentage) }}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <template v-if="processedJobs[char.character_id]">
                <div
                  v-for="(lane, index) in processedJobs[char.character_id]"
                  :key="index"
                  class="job-lane"
                >
                  <div
                    v-for="job in lane"
                    :key="job.job_id"
                    :data-activity-id="job.activity_id"
                    class="job-bar"
                    :class="{
                      'has-overlap': job.hasOverlap,
                    }"
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
      <div
        v-if="tooltip.type === 'planet'"
        v-html="getPlanetTooltipContent(tooltip.planet)"
      ></div>

      <div
        v-else-if="tooltip.type === 'industry'"
        v-html="getIndustryJobTooltipContent(tooltip.job)"
      ></div>

      <div v-else>
        <strong>{{ tooltip.job.product_name }}</strong
        ><br />
        <small>Location: {{ tooltip.job.location_name }}</small
        ><br /><br />
        Type: {{ getJobType(tooltip.job.activity_id) }}<br />

        <span v-if="tooltip.job.activity_id === 100">
          <div v-if="tooltip.job.planet_name">
            <strong>Planet:</strong> {{ tooltip.job.planet_name }}<br />
          </div>
          <div v-if="tooltip.job.pi_type">
            <strong>PI Type:</strong> {{ tooltip.job.pi_type }}<br />
          </div>
          <div v-if="tooltip.job.cycle_time">
            <strong>Cycle Time:</strong>
            {{ Math.round(tooltip.job.cycle_time / 60) }}m<br />
          </div>
          <span
            v-if="tooltip.job.status === 'needs_attention'"
            style="color: #e06c75"
          >
            ⚠️ Needs attention
          </span>
          <span v-else-if="tooltip.job.status === 'ready'">
            ✅ Ready for collection
          </span>
          <span v-else>
            completion in: {{ getTimeRemaining(tooltip.job.end_date) }}
          </span>
        </span>

        <span v-else-if="tooltip.job.is_planet_job">
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
  </div>
</template>
<script>
export default {
  name: "JobsTimeline",
  props: [
    "jobs",
    "characters",
    "planets",
    "industryJobs",
    "isLoading",
    "selectedCharacterId",
  ],
  inject: ["eventBus"],
  emits: [],
  data: () => ({
    scaleMode: "week",
    tooltip: { visible: false, job: null, x: 0, y: 0 },
    now: new Date(),
    interval: null,
    containerWidth: 1000,
    // Константы для вертикального ритма
    CARD_HEIGHT: 120,
    GAP_HEIGHT: 15,
    TOTAL_ROW_HEIGHT: 135, // Только высота карточки, gap управляется CSS
    // Оптимизация обновлений
    _lastUpdateTime: 0,
    _updateThrottle: 5000, // Обновляем максимум раз в 5 секунд
    _resizeTimeout: null,
    // Кэш для layoutJobs
    _layoutCache: new Map(),
    _layoutCacheKey: null,
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
      // Создаем ключ кэша на основе данных
      const cacheKey = `${this.characters.length}-${
        Object.keys(this.jobs).length
      }-${this.scaleMode}-${this.now.getTime()}`;

      if (this._layoutCacheKey === cacheKey && this._layoutCache.size > 0) {
        return Object.fromEntries(this._layoutCache);
      }

      const result = {};
      for (const char of this.characters) {
        if (this.jobs[char.character_id]) {
          const jobs = this.jobs[char.character_id];
          const cacheKeyForChar = `${char.character_id}-${jobs.length}-${this.scaleMode}`;

          if (this._layoutCache.has(cacheKeyForChar)) {
            result[char.character_id] = this._layoutCache.get(cacheKeyForChar);
          } else {
            const layout = this.layoutJobs(jobs);
            result[char.character_id] = layout;
            this._layoutCache.set(cacheKeyForChar, layout);
          }
        }
      }

      this._layoutCacheKey = cacheKey;
      return result;
    },
    tooltipStyle() {
      if (!this.tooltip.visible) return {};
      return {
        top: `${this.tooltip.y}px`,
        left: `${this.tooltip.x}px`,
        "--tooltip-bg":
          this.tooltip.type === "planet"
            ? "#ECECBB"
            : this.tooltip.type === "industry"
            ? this.getIndustryJobColor(this.tooltip.job?.activity_id)
            : this.getJobColor(this.tooltip.job?.activity_id),
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
      // КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ #1: Определяем BORDER_STYLE
      const BORDER_STYLE = "1px solid #3c414d";

      if (this.selectedCharacterId === characterId) {
        return {
          height: `${this.focusRowHeight}px`,
          minHeight: `${this.focusRowHeight}px`,
          maxHeight: `${this.focusRowHeight}px`,
          borderBottom: BORDER_STYLE,
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
          borderBottom: BORDER_STYLE,
        };
      }
      // Стандартный вид:
      // КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ #1: Фиксируем высоту 120px и добавляем нижнюю границу
      return {
        height: `${this.CARD_HEIGHT}px`,
        minHeight: `${this.CARD_HEIGHT}px`,
        maxHeight: `${this.CARD_HEIGHT}px`,
        margin: "0",
        borderBottom: BORDER_STYLE, // Добавлен border-bottom для выравнивания
      };
    },

    getCharacterBorderStyle(characterId, index) {
      // Здесь BORDER_STYLE не вызывал ошибки, но используем для консистентности
      const BORDER_STYLE = "1px solid #3c414d";
      // Вычисляем позицию верхней границы таймлайна персонажа
      let topPosition = 10; // padding-top контейнера

      for (let i = 0; i < index; i++) {
        const char = this.characters[i];
        if (this.selectedCharacterId === char.character_id) {
          topPosition += this.focusRowHeight;
        } else if (
          this.selectedCharacterId &&
          this.selectedCharacterId !== char.character_id
        ) {
          // Свернутый персонаж - не добавляем высоту
          continue;
        } else {
          // Логика определения высоты строки в нормальном режиме
          // Учитываем высоту карточки (120px) и gap (15px) = 135px
          // NOTE: В стилях character-rows-container есть gap: 15px, который автоматически добавляет отступ.
          // В CharacterPanel, высота фиксирована 120px.
          topPosition += this.CARD_HEIGHT + this.GAP_HEIGHT;
          continue; // Продолжаем, не возвращаем стиль отсюда
        }
      }

      // Определяем высоту текущего персонажа
      let characterHeight = this.CARD_HEIGHT; // Используем константу
      if (this.selectedCharacterId === characterId) {
        characterHeight = this.focusRowHeight;
      } else if (
        this.selectedCharacterId &&
        this.selectedCharacterId !== characterId
      ) {
        characterHeight = 0; // Свернутый персонаж
      }

      // Создаем две линии: верхнюю и нижнюю границы таймлайна персонажа
      return {
        position: "absolute",
        top: `${topPosition}px`,
        left: "0",
        right: "0",
        height: `${characterHeight}px`,
        borderTop: BORDER_STYLE, // Верхняя граница - тонкая серая
        borderBottom: BORDER_STYLE, // Нижняя граница - тонкая серая
        backgroundColor: "rgba(60, 65, 77, 0.05)", // Легкий серый фон
        zIndex: 5,
        pointerEvents: "none",
        boxSizing: "border-box",
      };
    },
    handleScroll(event) {
      if (event.target.classList.contains("timeline-scroll-wrapper")) {
        this.eventBus.scroll = {
          source: "timeline",
          scrollTop: event.target.scrollTop,
        };
      }

      // Обновляем позиции индикаторов при горизонтальной прокрутке
      if (event.target.classList.contains("job-lanes-container")) {
        // Принудительно обновляем позиции индикаторов
        this.$nextTick(() => {
          this.updateIndicatorPositions();
        });
      }
    },

    // Обновление позиций индикаторов
    updateIndicatorPositions() {
      // КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ #2: Используем $refs вместо $el
      if (!this.$refs.timelineWrapper) return;

      // Находим все контейнеры индикаторов и обновляем их позиции
      const indicatorContainers = this.$refs.timelineWrapper.querySelectorAll(
        ".completed-jobs-indicators"
      );
      indicatorContainers.forEach((container) => {
        const indicators = container.querySelectorAll(
          ".completed-job-indicator"
        );
        indicators.forEach((indicator) => {
          // Обновляем стили индикатора
          const jobId = indicator.getAttribute("data-job-id");
          if (jobId) {
            // Находим соответствующую работу и обновляем стиль
            const job = this.findJobById(jobId);
            if (job) {
              const style = this.getCompletedJobIndicatorStyle(job);
              Object.assign(indicator.style, style);
            }
          }
        });
      });
    },

    // Методы для работы с планетами
    getPlanetJobs(planet) {
      // Создаем "работы" для планеты на основе времени до завершения
      const jobs = [];

      if (planet.jobs && planet.jobs.length > 0) {
        // Если есть реальные работы на планете, используем их
        planet.jobs.forEach((job) => {
          if (job.status === "active" && job.end_date) {
            jobs.push({
              ...job,
              planet_id: planet.planet_id,
              planet_name: planet.planet_name,
              is_planet_job: true,
            });
          }
        });
      } else {
        // Если нет активных работ, создаем виртуальную работу на основе времени до истечения экстракторов
        const now = new Date();
        const expiryTime = planet.extractor_expiry_time
          ? new Date(planet.extractor_expiry_time)
          : null;

        if (expiryTime && expiryTime > now) {
          jobs.push({
            job_id: `planet-${planet.planet_id}`,
            planet_id: planet.planet_id,
            planet_name: planet.planet_name,
            start_date: now.toISOString(),
            end_date: expiryTime.toISOString(),
            status: "active",
            is_planet_job: true,
            product_name: "Planetary Extraction",
          });
        } else {
          // Если нет времени истечения, создаем постоянную работу
          const futureTime = new Date(now.getTime() + 24 * 60 * 60 * 1000); // 24 часа
          jobs.push({
            job_id: `planet-${planet.planet_id}`,
            planet_id: planet.planet_id,
            planet_name: planet.planet_name,
            start_date: now.toISOString(),
            end_date: futureTime.toISOString(),
            status: "active",
            is_planet_job: true,
            product_name: "Planetary Extraction",
          });
        }
      }

      return jobs;
    },

    getPlanetJobStyle(job, planet) {
      // Используем тот же метод что и для обычных работ, но с толщиной 10px
      const style = this.getJobStyle(job);
      return {
        ...style,
        height: "10px",
        zIndex: 1,
      };
    },

    showPlanetTooltip(planet, event) {
      const rect = event.target.getBoundingClientRect();
      this.tooltip = {
        visible: true,
        planet: planet,
        x: rect.left + rect.width / 2,
        y: rect.top - 10,
        type: "planet",
      };
    },

    getPlanetTooltipContent(planet) {
      let content = `<strong>${planet.planet_name}</strong><br>`;
      content += `Система: ${planet.solar_system_name || "Unknown"}<br>`;
      content += `Тип планеты: ${this.getPlanetTypeName(
        planet.planet_type
      )}<br>`;
      content += `Активных экстракторов: ${planet.active_extractors || 0}<br>`;

      // Добавляем информацию о времени завершения
      if (planet.next_completion_hours !== undefined) {
        if (planet.next_completion_hours > 0) {
          const hours = Math.floor(planet.next_completion_hours);
          const minutes = Math.floor(
            (planet.next_completion_hours - hours) * 60
          );
          content += `⏰ Следующее завершение: ${hours}ч ${minutes}м<br>`;
        } else {
          content += `⏰ Работы завершены<br>`;
        }
      }

      if (planet.total_time_remaining_hours !== undefined) {
        content += `📊 Общее время работ: ${planet.total_time_remaining_hours.toFixed(
          1
        )}ч<br>`;
      }

      if (planet.extractor_expiry_time) {
        const expiryTime = new Date(planet.extractor_expiry_time);
        const timeRemaining = this.getTimeRemaining(expiryTime);
        content += `🕐 Время истечения экстрактора: ${timeRemaining}<br>`;
      }

      if (planet.needs_attention) {
        content += `<span style="color: #ff6b6b;">⚠️ Требует внимания!</span><br>`;
      }

      // Получаем все работы планеты (включая созданные виртуальные)
      const planetJobs = this.getPlanetJobs(planet);

      if (planetJobs.length > 0) {
        content += `<br><strong>Активные работы:</strong><br>`;
        planetJobs.forEach((job) => {
          if (job.status === "active" && job.end_date) {
            const timeRemaining = this.getTimeRemaining(job.end_date);
            const jobType = job.is_planet_job
              ? "Планетарная добыча"
              : job.product_name;

            // Используем вычисленное время, если доступно
            const remainingTime =
              job.time_remaining_hours !== undefined
                ? `${job.time_remaining_hours.toFixed(1)}ч`
                : timeRemaining;

            content += `• ${jobType} - ${remainingTime}`;

            // Добавляем прогресс, если доступен
            if (job.progress_percentage !== undefined) {
              content += ` (${job.progress_percentage.toFixed(1)}%)`;
            }

            content += `<br>`;

            // Дополнительная информация для планетарных работ
            if (job.is_planet_job) {
              const startTime = new Date(job.start_date);
              const endTime = new Date(job.end_date);
              const duration = Math.round(
                (endTime - startTime) / (1000 * 60 * 60)
              ); // в часах
              content += `  └─ Длительность: ${duration}ч<br>`;
            }
          }
        });
      } else {
        content += `<br><span style="color: #888;">Нет активных работ</span><br>`;
      }

      // Информация о времени истечения экстракторов
      if (planet.extractor_expiry_time) {
        const expiryTime = new Date(planet.extractor_expiry_time);
        const now = new Date();
        if (expiryTime > now) {
          const timeToExpiry = this.getTimeRemaining(
            planet.extractor_expiry_time
          );
          content += `<br><strong>Время истечения экстракторов:</strong><br>`;
          content += `• ${timeToExpiry}<br>`;
        }
      }
      return content;
    },
    getPlanetTypeName(planetType) {
      const types = {
        1: "Temperate",
        2: "Barren",
        3: "Oceanic",
        4: "Ice",
        5: "Gas",
        6: "Lava",
        7: "Storm",
        8: "Plasma",
        9: "Shattered",
        10: "Temperate (High Sec)",
        11: "Barren (High Sec)",
        12: "Oceanic (High Sec)",
        13: "Ice (High Sec)",
        14: "Gas (High Sec)",
        15: "Lava (High Sec)",
        16: "Storm (High Sec)",
        17: "Plasma (High Sec)",
        18: "Shattered (High Sec)",
      };
      return types[planetType] || "Unknown";
    },

    // Методы для работы с индустриальными работами
    getIndustryJobLanes(characterId) {
      const jobs = this.industryJobs[characterId] || [];
      if (!jobs.length) return [];
      // Сортируем работы по времени начала
      const sortedJobs = [...jobs].sort(
        (a, b) => new Date(a.start_date) - new Date(b.start_date)
      );
      const lanes = [];
      // Определяем временные границы видимой области
      const viewStart = this.now;
      const viewEnd = new Date(this.now.getTime() + this.totalDurationMs);
      for (const job of sortedJobs) {
        const jobEndDate = new Date(job.end_date);
        const jobStartDate = new Date(job.start_date);
        // Пропускаем работы за пределами видимой области
        if (
          jobEndDate < viewStart &&
          viewStart - jobEndDate > this.totalDurationMs / 4
        )
          continue;
        if (jobStartDate > viewEnd) continue;
        let placed = false;
        // Ищем подходящую линию
        for (const lane of lanes) {
          let hasOverlap = false;
          for (const existingJob of lane) {
            if (
              new Date(job.start_date) < new Date(existingJob.end_date) &&
              new Date(existingJob.start_date) < new Date(job.end_date)
            ) {
              hasOverlap = true;
              break;
            }
          }
          if (!hasOverlap) {
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
    getIndustryJobStyle(job) {
      const startOffsetMs = Math.max(
        0,
        new Date(job.start_date).getTime() - this.now.getTime()
      );
      const endOffsetMs = new Date(job.end_date).getTime() - this.now.getTime();
      const left = (startOffsetMs / 3600e3) * this.pixelsPerHour;
      const endPosition = (endOffsetMs / 3600e3) * this.pixelsPerHour;
      const width = Math.max(2, endPosition - left);
      return {
        transform: `translateX(${left}px)`,
        width: `${width}px`,
        height: "10px",
      };
    },
    getIndustryJobColor(activityId) {
      const colors = {
        1: "#E1AA36", // Manufacturing
        3: "#239BA7", // Researching Technology
        4: "#239BA7", // Researching Time Efficiency
        5: "#239BA7", // Researching Material Efficiency
        6: "#239BA7", // Copying
        7: "#239BA7", // Duplicating
        8: "#239BA7", // Reverse Engineering
        9: "#239BA7", // Invention
        11: "#7ADAA5", // Reaction
      };
      return colors[activityId] || "#7f8c8d";
    },
    showIndustryJobTooltip(job, event) {
      const rect = event.target.getBoundingClientRect();
      this.tooltip = {
        visible: true,
        job: job,
        x: rect.left + rect.width / 2,
        y: rect.top - 10,
        type: "industry",
      };
    },
    getIndustryJobTooltipContent(job) {
      let content = `<strong>${job.product_name}</strong><br>`;
      content += `Тип: ${
        job.activity_name || this.getJobType(job.activity_id)
      }<br>`;
      content += `Локация: ${job.location_name}<br>`;
      content += `Система: ${job.system_name || "Unknown"}<br>`;
      content += `Безопасность: ${
        job.system_security ? job.system_security.toFixed(2) : "Unknown"
      }<br>`;
      if (job.is_completed) {
        content += `<span style="color: #4CAF50;">✅ Завершено</span><br>`;
      } else if (job.is_paused) {
        content += `<span style="color: #FF9800;">⏸️ Приостановлено</span><br>`;
      } else {
        const timeRemaining = this.getTimeRemaining(job.end_date);
        content += `Осталось: ${timeRemaining}<br>`;
        content += `Прогресс: ${Math.round(job.progress_percentage || 0)}%<br>`;
      }
      content += `Длительность: ${job.duration_hours || 0}ч<br>`;
      content += `Стоимость: ${(job.cost || 0).toLocaleString()} ISK<br>`;
      content += `Рангов: ${job.runs || 1}<br>`;
      if (job.priority) {
        const priorityColors = {
          high: "#f44336",
          medium: "#ff9800",
          low: "#4caf50",
        };
        content += `Приоритет: <span style="color: ${
          priorityColors[job.priority]
        };">${job.priority.toUpperCase()}</span><br>`;
      }
      if (job.risk_level) {
        const riskColors = {
          high: "#f44336",
          medium: "#ff9800",
          low: "#4caf50",
        };
        content += `Риск: <span style="color: ${
          riskColors[job.risk_level]
        };">${job.risk_level.toUpperCase()}</span><br>`;
      }
      return content;
    },

    // Поиск работы по ID
    findJobById(jobId) {
      for (const characterId in this.jobs) {
        const characterJobs = this.jobs[characterId];
        if (characterJobs) {
          const job = characterJobs.find((j) => j.job_id == jobId);
          if (job) return job;
        }
      }
      return null;
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
      // Очищаем кэш при смене масштаба
      this._layoutCache.clear();
      this._layoutCacheKey = null;
      // Обновляем позиции индикаторов при смене масштаба
      this.$nextTick(() => {
        this.updateIndicatorPositions();
      });
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
          // Проверяем все работы в линии на перекрытие
          let hasOverlap = false;
          for (const existingJob of lane) {
            if (
              new Date(job.start_date) < new Date(existingJob.end_date) &&
              new Date(existingJob.start_date) < new Date(job.end_date)
            ) {
              hasOverlap = true;
              break;
            }
          }
          if (!hasOverlap) {
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
      // Определяем максимальное количество линий в зависимости от масштаба
      const MAX_LANES =
        this.scaleMode === "month" ? 15 : this.scaleMode === "week" ? 8 : 5;
      if (lanes.length > MAX_LANES) {
        const newLanes = lanes.slice(0, MAX_LANES);
        // Распределяем оставшиеся работы по существующим линиям
        for (let i = MAX_LANES; i < lanes.length; i++) {
          const jobsToPlace = lanes[i];
          for (const job of jobsToPlace) {
            let placed = false;
            // Пытаемся разместить в существующих линиях
            for (const lane of newLanes) {
              let hasOverlap = false;
              for (const existingJob of lane) {
                if (
                  new Date(job.start_date) < new Date(existingJob.end_date) &&
                  new Date(existingJob.start_date) < new Date(job.end_date)
                ) {
                  hasOverlap = true;
                  break;
                }
              }
              if (!hasOverlap) {
                lane.push(job);
                placed = true;
                break;
              }
            }
            if (!placed) {
              // Если нигде не поместилось, просто добавляем в последнюю линию (с перекрытием)
              newLanes[newLanes.length - 1].push(job);
              job.hasOverlap = true;
            }
          }
        }
        return newLanes;
      }

      return lanes;
    },

    // *** МЕТОДЫ, КОТОРЫЕ ТРЕБУЮТ РЕАЛИЗАЦИИ ВАШЕЙ ЛОГИКИ ***
    getTimeRemaining(endDate) {
      if (!endDate) return "N/A";
      const end = new Date(endDate);
      const diffMs = end.getTime() - this.now.getTime();

      if (diffMs < 0) return "Completed";

      const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      const hours = Math.floor(
        (diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
      );
      const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

      if (days > 0) return `${days}d ${hours}h`;
      if (hours > 0) return `${hours}h ${minutes}m`;
      return `${minutes}m`;
    },
    getJobStyle(job) {
      const startOffsetMs = Math.max(
        0,
        new Date(job.start_date).getTime() - this.now.getTime()
      );
      const endOffsetMs = new Date(job.end_date).getTime() - this.now.getTime();
      const left = (startOffsetMs / 3600e3) * this.pixelsPerHour;
      const endPosition = (endOffsetMs / 3600e3) * this.pixelsPerHour;
      const width = Math.max(2, endPosition - left);

      return {
        transform: `translateX(${left}px)`,
        width: `${width}px`,
        // height: job.is_planet_job ? '10px' : '12px' // ИСПОЛЬЗУЕТСЯ в getPlanetJobStyle
      };
    },
    getJobColor(activityId) {
      const colors = {
        1: "#61aef5", // Manufacturing
        3: "#8bc34a", // Researching Technology
        4: "#8bc34a", // Researching Time Efficiency
        5: "#8bc34a", // Researching Material Efficiency
        6: "#8bc34a", // Copying
        9: "#ff9800", // Invention
        100: "#f44336", // PI (виртуальный ID)
        101: "#37d8d0", // PI (виртуальный ID)
      };
      return colors[activityId] || "#7f8c8d";
    },
    getJobType(activityId) {
      const types = {
        1: "Manufacturing",
        3: "Tech Research",
        4: "Time Eff. Research",
        5: "Mat. Eff. Research",
        6: "Copying",
        9: "Invention",
        100: "Planetary Industry (PI)",
      };
      return types[activityId] || "Other";
    },
    getCompletedJobs(characterId) {
      return (this.jobs[characterId] || []).filter(
        (job) => new Date(job.end_date) < this.now
      );
    },
    isJobCompleted(job) {
      return new Date(job.end_date) < this.now;
    },
    getCompletedJobIndicatorStyle(job) {
      const jobEndDate = new Date(job.end_date);
      const offsetMs = jobEndDate.getTime() - this.now.getTime();
      const left = (offsetMs / 3600e3) * this.pixelsPerHour;

      // Рассчитываем, как далеко слева он находится
      const leftPosition = Math.max(0, left);

      return {
        transform: `translateX(${leftPosition}px)`,
        backgroundColor: this.getJobColor(job.activity_id),
      };
    },
    showTooltip(job, event) {
      const rect = event.target.getBoundingClientRect();
      this.tooltip = {
        visible: true,
        job: job,
        x: rect.left + rect.width / 2,
        y: rect.top - 10,
        type: "job",
      };
    },
    hideTooltip() {
      this.tooltip = { visible: false, job: null, x: 0, y: 0 };
    },
    // *** КОНЕЦ МЕТОДОВ, КОТОРЫЕ ТРЕБУЮТ РЕАЛИЗАЦИИ ВАШЕЙ ЛОГИКИ ***

    // *** Vue lifecycle methods ***
    updateContainerWidth() {
      // КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ #2: Используем $refs вместо $el
      if (!this.$refs.timelineWrapper) return;

      const container = this.$refs.timelineWrapper.parentNode;
      this.containerWidth = container.clientWidth;
    },
    updateTime() {
      if (Date.now() - this._lastUpdateTime < this._updateThrottle) return;
      this.now = new Date();
      this._lastUpdateTime = Date.now();
      // Вызываем обновление позиций, которое использует $refs
      this.updateIndicatorPositions();
    },
  },
  mounted() {
    this.updateContainerWidth();
    // Слушаем горизонтальный скролл на timeline-scroll-wrapper
    this.$refs.timelineWrapper?.parentNode.addEventListener(
      "scroll",
      this.handleScroll
    );
    window.addEventListener("resize", this.updateContainerWidth);
    this.interval = setInterval(this.updateTime, 5000); // Обновляем время каждые 5 сек
    // Первичное обновление позиций после отрисовки
    this.$nextTick(() => {
      this.updateIndicatorPositions();
    });
  },
  beforeUnmount() {
    clearInterval(this.interval);
    window.removeEventListener("resize", this.updateContainerWidth);
    if (this.$refs.timelineWrapper?.parentNode) {
      this.$refs.timelineWrapper.parentNode.removeEventListener(
        "scroll",
        this.handleScroll
      );
    }
    clearTimeout(this._resizeTimeout);
  },
};
</script>

<style scoped>
/* Стили для статусов */
.timeline-status {
  position: absolute; /* Позволяет ему растягиваться и быть поверх */
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #888;
  font-size: 16px;
  background-color: #1a1a1a;
  z-index: 10;
}

/* ... (Ваши оригинальные стили) ... */
.timeline-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  height: 100%;
  overflow: hidden; /* Добавлено, чтобы предотвратить двойные скроллы */
}
.timeline-controls {
  flex-shrink: 0;
  padding: 10px;
  background-color: #20232a;
  border-bottom: 1px solid #3c414d;
}
.timeline-scroll-wrapper {
  flex-grow: 1;
  overflow-x: auto;
  overflow-y: scroll; /* Для вертикальной прокрутки списка персонажей */
  position: relative;
}
.timeline-scroll-wrapper.is-locked {
  overflow-y: hidden; /* Блокируем вертикальный скролл при фокусе */
}
.timeline-wrapper {
  position: relative;
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

/* ЗАГОЛОВКИ ВРЕМЕНИ */
.time-headers {
  position: sticky;
  top: 0;
  height: 40px;
  background-color: #1a1a1a;
  border-bottom: 1px solid #3c414d;
  z-index: 2;
  flex-shrink: 0;
}
.time-header-item {
  position: absolute;
  top: 5px;
  font-size: 12px;
  color: #abb2bf;
  transform: translateX(-50%);
  text-align: center;
}

/* ЛИНИЯ ТЕКУЩЕГО ВРЕМЕНИ */
.current-time-line {
  position: absolute;
  top: 40px;
  bottom: 0;
  left: 0;
  width: 2px;
  background-color: #ff6b6b;
  z-index: 3;
  pointer-events: none;
  /* Для плавной анимации */
  transition: transform 0.3s linear;
}

/* КОНТЕЙНЕР СТРОК ПЕРСОНАЖЕЙ */
.character-rows-container {
  padding-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 15px; /* Разделение строк */
  flex-grow: 1;
  position: relative;
}

/* ГРУППА СТРОКИ ПЕРСОНАЖА */
.character-row-group {
  box-sizing: border-box;
  transition: all 0.3s ease-in-out;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  /* FIX: УДАЛЕН ЛИШНИЙ padding-top, который ломал выравнивание */
  padding: 0 10px;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
  z-index: 5;
}

.character-row-group.is-hidden {
  opacity: 0;
  pointer-events: none;
}
.character-row-group.is-selected {
  z-index: 6;
  background-color: #1a1a1a;
}
/* Бордер для разделения (вместо границы на самой группе) */
.character-border-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 135px; /* Синхронизируется с TOTAL_ROW_HEIGHT */
  border-bottom: 1px solid #3c414d;
  pointer-events: none;
  transition: all 0.3s ease-in-out;
}
.character-border-line.active-character {
  /* Бордер для активного персонажа */
  border: 1px solid #4e9aef;
  background-color: rgba(78, 154, 239, 0.1);
}

/* КОНТЕЙНЕРЫ РАБОТ */
.job-lanes-container {
  position: relative;
  flex-grow: 1;
  height: 100%;
}
.completed-jobs-indicators {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  pointer-events: none;
  z-index: 2;
}
.completed-job-indicator {
  position: absolute;
  bottom: 0px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #4caf50;
  transform: translateX(-50%);
  pointer-events: all;
  opacity: 0.8;
  cursor: pointer;
  transition: transform 0.3s linear;
}
.checkmark-icon-indicator {
  width: 8px;
  height: 8px;
}

/* Планетарные работы */
.planets-lane {
  margin-top: 5px;
  margin-bottom: 5px;
  display: flex;
  flex-direction: column;
}
.planet-job-lane {
  position: relative;
  height: 12px;
}
.planet-job-bar {
  position: absolute;
  top: 0;
  height: 10px;
  border-radius: 2px;
  box-sizing: border-box;
  overflow: hidden;
  cursor: pointer;
  z-index: 1;
}
.planet-job-fill {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-size: 10px;
  font-weight: bold;
  position: relative;
}
.planet-needs-attention {
  border: 2px solid #ff6b6b;
  animation: pulse-red 1s infinite alternate;
}
.attention-indicator {
  position: absolute;
  right: 5px;
  color: #ff6b6b;
  font-size: 12px;
  font-weight: bold;
}
.planet-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 5px;
}

/* Индустриальные работы */
.industry-jobs-lane {
  margin-bottom: 5px;
}
.industry-job-lane {
  position: relative;
  height: 12px;
  margin-bottom: 2px;
}
.industry-job-bar {
  position: absolute;
  top: 0;
  height: 10px;
  border-radius: 2px;
  box-sizing: border-box;
  overflow: hidden;
  cursor: pointer;
  z-index: 1;
}
.industry-job-fill {
  width: 100%;
  height: 100%;
  border-radius: 2px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 6px;
  box-sizing: border-box;
  overflow: hidden;
  white-space: nowrap;
}

.industry-job-name {
  color: white;
  font-size: 10px;
  font-weight: 500;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 70%;
}

.industry-job-progress {
  color: white;
  font-size: 9px;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
  flex-shrink: 0;
}

.industry-job-completed .industry-job-fill {
  opacity: 0.7;
  background-color: #4caf50 !important;
}

.industry-job-paused .industry-job-fill {
  opacity: 0.8;
  background-color: #ff9800 !important;
}

.industry-job-high-priority {
  box-shadow: 0 0 4px rgba(244, 67, 54, 0.8);
}

/* Обычные работы */
.job-lane {
  position: relative;
  height: 12px;
  margin-bottom: 2px;
}
.job-bar {
  position: absolute;
  top: 0;
  height: 12px;
  border-radius: 2px;
  box-sizing: border-box;
  overflow: hidden;
  cursor: pointer;
  z-index: 1;
  transition: box-shadow 0.2s;
}
.job-bar:hover {
  box-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
}
.job-bar.has-overlap {
  opacity: 0.7;
  border: 1px solid rgba(255, 255, 255, 0.3);
}
.job-bar-fill {
  width: 100%;
  height: 100%;
  border-radius: 2px;
  background-color: #7f8c8d;
}

/* РАСШИРЕННЫЙ ВИД */
.expanded-jobs-view {
  padding: 10px 0;
  overflow-y: auto;
  flex-grow: 1;
  max-height: 100%;
}
.focus-jobs-count {
  padding: 5px 10px;
  color: #abb2bf;
  font-size: 12px;
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
  justify-content: space-between;
}
.job-bar-focus-view .job-bar-fill.completed-job-focus {
  background-color: #4caf50 !important;
  opacity: 0.8;
  justify-content: center;
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
.checkmark-icon-expanded {
  width: 20px;
  height: 20px;
}

/* ТУЛТИП */
.tooltip {
  position: fixed;
  background-color: var(--tooltip-bg, #333);
  color: #1a1a1a;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  pointer-events: none;
  transform: translate(-50%, -100%);
  z-index: 1000;
  min-width: 250px;
  box-sizing: border-box;
  font-size: 13px;
  line-height: 1.4;
}
.tooltip strong {
  color: #1a1a1a;
  font-weight: bold;
}
.tooltip small {
  color: #444;
}

@keyframes pulse-red {
  from {
    box-shadow: 0 0 0 0px rgba(255, 0, 0, 0.4);
  }
  to {
    box-shadow: 0 0 0 6px rgba(255, 0, 0, 0);
  }
}
</style>
