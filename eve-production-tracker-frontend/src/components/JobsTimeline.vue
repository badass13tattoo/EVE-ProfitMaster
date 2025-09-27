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

        <div v-if="isLoading" class="loading-indicator">Data loading...</div>

        <div v-else-if="!hasJobs" class="no-jobs-placeholder">
          No jobs to display.
        </div>
        <div v-else class="character-rows-container"></div>
        <div class="current-time-line"></div>
        <div class="character-rows-container">
          <!-- Бордерлайны для разделения персонажей -->
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
              <!-- Контейнер для индикаторов завершенных работ -->
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

              <!-- Планеты персонажа как работы -->
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

              <!-- Индустриальные работы персонажа -->
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
      <!-- Тултип для планет -->
      <div
        v-if="tooltip.type === 'planet'"
        v-html="getPlanetTooltipContent(tooltip.planet)"
      ></div>

      <!-- Тултип для индустриальных работ -->
      <div
        v-else-if="tooltip.type === 'industry'"
        v-html="getIndustryJobTooltipContent(tooltip.job)"
      ></div>

      <!-- Тултип для обычных работ -->
      <div v-else>
        <strong>{{ tooltip.job.product_name }}</strong
        ><br />
        <small>Location: {{ tooltip.job.location_name }}</small
        ><br /><br />
        Type: {{ getJobType(tooltip.job.activity_id) }}<br />

        <!-- Специальная информация для PI работ -->
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

        <!-- Обычные планетные работы -->
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

        <!-- Обычные работы -->
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
      // Стандартный вид: разрешаем динамический рост для показа всех работ
      return {
        height: "auto", // ИЗМЕНЕНИЕ: Разрешаем динамический рост
        minHeight: `${this.TOTAL_ROW_HEIGHT}px`, // Сохраняем минимальную высоту (135px) для выравнивания
        margin: "0",
      };
    },

    getCharacterBorderStyle(characterId, index) {
      const BORDER_STYLE = "1px solid #3c414d";
      // Вычисляем позицию верхней границы таймлайна персонажа
      let topPosition = 10; // padding-top контейнера

      for (let i = 0; i < index; i++) {
        const char = this.characters[i];
        let charHeight;

        if (this.selectedCharacterId === char.character_id) {
          // 1. В режиме фокуса: используем рассчитанную высоту фокуса
          charHeight = this.focusRowHeight;
        } else if (
          this.selectedCharacterId &&
          this.selectedCharacterId !== char.character_id
        ) {
          // 2. В режиме скрытия: высота 0
          charHeight = 0;
        } else {
          // 3. В стандартном режиме: используем фактическую высоту строки.
          //    Поскольку RowStyle теперь "auto", для расчета границы используем минимальную/стандартную высоту.
          //    Синхронизируем с минимальной высотой карточки (120px) + gap (15px) = 135px
          charHeight = this.CARD_HEIGHT + this.GAP_HEIGHT;
          // Если вам нужно, чтобы граница учитывала фактический рост,
          // вам придется использовать $refs для замера высоты уже отрендеренной строки,
          // что намного сложнее. Мы используем минимальную высоту для стабильности.
        }

        // КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Мы должны продолжать цикл, а не возвращать значение!
        // Существующий код возвращал стиль для ПЕРВОГО же персонажа, если фокуса не было.
        topPosition += charHeight;
      }

      // Определяем высоту текущего персонажа
      let characterHeight = this.CARD_HEIGHT + this.GAP_HEIGHT; // Стандартная высота (135px)
      if (this.selectedCharacterId === characterId) {
        characterHeight = this.focusRowHeight;
      } else if (
        this.selectedCharacterId &&
        this.selectedCharacterId !== characterId
      ) {
        characterHeight = 0; // Свернутый персонаж
      }

      // Возвращаем стили для *текущей* границы, расположенной на topPosition
      return {
        position: "absolute",
        top: `${topPosition - this.GAP_HEIGHT / 2}px`, // Сдвигаем на половину GAP, чтобы центрировать границу
        left: "0",
        right: "0",
        height: "1px", // Сама линия границы
        borderTop: BORDER_STYLE,
        backgroundColor: "#3c414d",
        zIndex: 5,
        pointerEvents: "none",
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
      // Находим все контейнеры индикаторов и обновляем их позиции
      const indicatorContainers = this.$el.querySelectorAll(
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

            // Если не удалось разместить, добавляем в первую линию и помечаем как перекрывающуюся
            if (!placed) {
              newLanes[0].push(job);
              job.hasOverlap = true;
            }
          }
        }

        // Сортируем работы в каждой линии по времени начала
        for (const lane of newLanes) {
          lane.sort((a, b) => new Date(a.start_date) - new Date(b.start_date));
        }

        // Помечаем перекрывающиеся работы
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
    // Получить завершенные работы для персонажа
    getCompletedJobs(characterId) {
      if (!this.jobs[characterId]) return [];
      return this.jobs[characterId].filter((job) => this.isJobCompleted(job));
    },

    // Стиль для индикатора завершенной работы
    getCompletedJobIndicatorStyle(job) {
      // Позиция end_date относительно текущего времени (может быть отрицательной)
      const endOffsetMs = new Date(job.end_date).getTime() - this.now.getTime();
      const left = (endOffsetMs / 3600e3) * this.pixelsPerHour;

      // Адаптивный размер квадратика в зависимости от масштаба
      const baseSize = Math.max(12, Math.min(24, this.pixelsPerHour * 0.8));
      const size = `${baseSize}px`;

      // Получаем ширину контейнера строки персонажа
      const containerWidth = this.containerWidth || 1000;

      // Вычисляем позицию относительно левого края строки персонажа
      // Если работа завершилась в прошлом (left < 0), показываем у левого края
      // Если работа завершилась в будущем, показываем в соответствующей позиции
      let indicatorLeft = left;

      // Ограничиваем позицию границами контейнера
      const maxLeft = containerWidth - parseInt(size);
      const clampedLeft = Math.max(0, Math.min(indicatorLeft, maxLeft));

      // Определяем видимость индикатора
      const isVisible = left >= -parseInt(size) && left <= containerWidth;

      return {
        left: `${clampedLeft}px`,
        width: size,
        height: size,
        backgroundColor: this.getJobColor(job.activity_id),
        opacity: isVisible ? 1 : 0,
        // Добавляем дополнительную видимость для завершенных работ
        visibility: isVisible ? "visible" : "hidden",
        // Обеспечиваем правильное позиционирование относительно строки
        position: "absolute",
      };
    },

    getJobStyle(job) {
      // Для завершенных работ не показываем в обычных линиях
      if (this.isJobCompleted(job)) {
        return {
          display: "none",
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
          1: "#E1AA36", // Manufacturing
          3: "#239BA7", // Copying
          4: "#239BA7", // Material Efficiency
          5: "#239BA7", // Time Efficiency
          6: "#7ADAA5", // Reactions
          7: "#FF6B6B", // Planet Interaction
          8: "#239BA7", // Invention
          100: "#9B59B6", // PI Jobs - специальный цвет для планетарной индустрии
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
          100: "Planetary Industry", // PI Jobs
        }[id] || "Unknown"
      );
    },
    isJobCompleted(job) {
      // Для PI работ (activity_id: 100) проверяем статус
      if (job.activity_id === 100) {
        return (
          job.status === "needs_attention" ||
          job.status === "completed" ||
          job.status === "ready" ||
          new Date(job.end_date) <= this.now
        );
      }

      // Для планетных работ проверяем статус
      if (job.is_planet_job) {
        return (
          job.status === "needs_attention" ||
          job.status === "completed" ||
          new Date(job.end_date) <= this.now
        );
      }

      // Для обычных работ проверяем статус и время завершения
      return job.status === "completed" || new Date(job.end_date) <= this.now;
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
      const now = Date.now();
      // Throttle обновления времени
      if (now - this._lastUpdateTime < this._updateThrottle) {
        return;
      }

      this.now = new Date();
      this._lastUpdateTime = now;

      // Обновляем позиции индикаторов при изменении времени
      this.$nextTick(() => {
        this.updateIndicatorPositions();
      });
    },
    updateContainerWidth() {
      // Debounce обновления размера контейнера
      if (this._resizeTimeout) {
        clearTimeout(this._resizeTimeout);
      }

      this._resizeTimeout = setTimeout(() => {
        if (this.$el) {
          this.containerWidth = this.$el.clientWidth;
          // Обновляем позиции индикаторов при изменении размера контейнера
          this.$nextTick(() => {
            this.updateIndicatorPositions();
          });
        }
      }, 100); // 100ms debounce
    },
  },
  mounted() {
    this.interval = setInterval(this.updateTime, 5000); // Обновляем каждые 5 секунд
    this.$nextTick(() => {
      this.updateContainerWidth();
      window.addEventListener("resize", this.updateContainerWidth);
      this.$el.addEventListener("scroll", this.handleScroll, true);

      // Добавляем обработчики прокрутки для контейнеров работ
      const jobContainers = this.$el.querySelectorAll(".job-lanes-container");
      jobContainers.forEach((container) => {
        container.addEventListener("scroll", this.handleScroll, true);
      });
    });
  },
  beforeUnmount() {
    clearInterval(this.interval);
    if (this._resizeTimeout) {
      clearTimeout(this._resizeTimeout);
    }
    // Очищаем кэш
    this._layoutCache.clear();
    this._layoutCacheKey = null;

    window.removeEventListener("resize", this.updateContainerWidth);
    this.$el.removeEventListener("scroll", this.handleScroll, true);

    // Удаляем обработчики прокрутки для контейнеров работ
    const jobContainers = this.$el.querySelectorAll(".job-lanes-container");
    jobContainers.forEach((container) => {
      container.removeEventListener("scroll", this.handleScroll, true);
    });
  },
};
</script>
<style scoped>
.timeline-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
  max-width: 100%;
  width: 100%;
}
.timeline-controls {
  padding: 10px 20px;
  background-color: #20232a;
  /* border-bottom: 1px solid #3c414d; */ /* Убираем горизонтальную линию */
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
  position: relative;
  display: flex;
  flex-direction: column;
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
  overflow-y: auto;
}
.timeline-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 100%; /* Гарантирует минимальную высоту */
  flex-grow: 1; /* Если используется Flexbox в .timeline-scroll-wrapper */
}
.time-headers {
  position: sticky;
  top: 0;
  background-color: #282c34;
  z-index: 0;
  flex-shrink: 0;
  height: 40px;
  width: 100%;
  /* Убедитесь, что контейнер заголовков занимает всю ширину и является контекстом для своих элементов */
  box-sizing: border-box;
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
  flex-grow: 1;
  position: relative;
}
.character-row-group {
  /* Удалены жесткие размеры высоты для гибкого вертикального ритма */
  min-height: 120px; /* Сохраняем минимальную высоту для выравнивания */
  box-sizing: border-box;
  transition: all 0.3s ease-in-out;
  display: flex;
  flex-direction: column;
  justify-content: flex-start; /* ИЗМЕНЕНИЕ: Начинаем контент сверху, а не по центру */
  padding-top: 0px; /* Добавляем небольшой отступ сверху для выравнивания */
  /* КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Обрезаем содержимое, которое выходит за границы жесткой высоты */
  overflow: hidden;
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

/* Бордерлайны для обозначения границ таймлайнов персонажей */
.character-border-line {
  position: absolute;
  left: 0;
  right: 0;
  border-top: 1px solid #3c414d;
  border-bottom: 1px solid #3c414d;
  background-color: rgba(60, 65, 77, 0.05);
  z-index: 5;
  pointer-events: none;
  box-sizing: border-box;
  opacity: 0.8;
}

.character-border-line:first-child {
  display: block; /* Показываем первую линию */
}

/* Стили для активного персонажа */
.character-border-line.active-character {
  border-top: 1px solid #c678dd;
  border-bottom: 1px solid #c678dd;
  background-color: rgba(198, 120, 221, 0.1);
  opacity: 1;
  box-shadow: 0 0 10px rgba(198, 120, 221, 0.3);
}
.job-lanes-container {
  /* ИЗМЕНЕНИЕ: Уменьшаем или удаляем padding, который "сдвигает" полосы */
  padding: 5px 0; /* Уменьшаем вертикальный padding */
  /* max-height удален для разрешения динамического роста */
  overflow-y: visible; /* Разрешаем показ всех работ */
  position: relative;
}

.completed-jobs-indicators {
  position: sticky;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 25;
  /* Привязываем к левому краю строки персонажа */
  transform: translateX(0);
}

.completed-job-indicator {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse 2s infinite;
  pointer-events: auto;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.2);
  /* Обеспечиваем видимость поверх всех элементов */
  z-index: 30;
}

.completed-job-indicator:hover {
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  border-color: rgba(255, 255, 255, 0.4);
}

.checkmark-icon-indicator {
  width: 60%;
  height: 60%;
  filter: drop-shadow(1px 1px 2px rgba(0, 0, 0, 0.5));
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

/* Скроллбары убраны - контейнеры теперь без скроллинга */

.expanded-jobs-view {
  padding: 20px;
  color: #e0e0e0;
  height: 100%;
  position: relative;
  overflow: visible;
}

/* Скроллбары убраны - контейнеры теперь без скроллинга */

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

.job-bar-focus-view .completed-job-focus {
  width: 30px !important;
  height: 30px !important;
  border-radius: 6px !important;
  animation: pulse 2s infinite;
  display: flex;
  align-items: center;
  justify-content: center;
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

/* Специальные стили для PI работ */
.job-bar[data-activity-id="100"] {
  border: 2px solid rgba(155, 89, 182, 0.3);
  box-shadow: 0 0 4px rgba(155, 89, 182, 0.2);
}

.job-bar[data-activity-id="100"]:hover {
  border-color: rgba(155, 89, 182, 0.6);
  box-shadow: 0 0 8px rgba(155, 89, 182, 0.4);
}

/* Стили для завершенных PI работ */
.completed-job-indicator[data-activity-id="100"] {
  border: 2px solid rgba(155, 89, 182, 0.4);
  box-shadow: 0 2px 8px rgba(155, 89, 182, 0.3);
}

.completed-job-indicator[data-activity-id="100"]:hover {
  border-color: rgba(155, 89, 182, 0.7);
  box-shadow: 0 4px 12px rgba(155, 89, 182, 0.5);
}
.job-bar-fill {
  height: 100%;
  width: 100%;
  border-radius: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
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
  flex-grow: 1;
  text-align: center;
  padding-top: 50px;
  font-size: 18px;
  color: #888;
}

/* Стили для планет */
.planets-lane {
  position: relative;
  margin-bottom: 4px;
  /* border-bottom: 1px solid #3c414d; */ /* Убираем горизонтальную линию */
  padding-bottom: 2px;
}

.planet-job-lane {
  position: relative;
  height: 10px;
  margin-bottom: 2px;
}

.planet-job-bar {
  position: absolute;
  height: 10px;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.1s ease-in-out;
  z-index: 1;
}

.planet-job-bar:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(236, 236, 187, 0.3);
}

.planet-job-fill {
  position: absolute;
  height: 100%;
  width: 100%;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
  box-sizing: border-box;
  overflow: hidden;
  white-space: nowrap;
}

.planet-name {
  color: #ececbb;
  font-size: 11px;
  font-weight: 500;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 80%;
}

.attention-indicator {
  width: 12px;
  height: 12px;
  background-color: #ff6b6b;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 8px;
  font-weight: bold;
  animation: blink 1s infinite;
  box-shadow: 0 0 6px rgba(255, 107, 107, 0.5);
  flex-shrink: 0;
}

.planet-needs-attention .planet-job-fill {
  box-shadow: 0 0 4px rgba(255, 107, 107, 0.3);
}

/* Стили для индустриальных работ */
.industry-jobs-lane {
  position: relative;
  margin-bottom: 4px;
  /* border-bottom: 1px solid #3c414d; */ /* Убираем горизонтальную линию */
  padding-bottom: 2px;
}

.industry-job-lane {
  position: relative;
  height: 10px;
  margin-bottom: 2px;
}

.industry-job-bar {
  position: absolute;
  height: 10px;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  z-index: 1;
}

.industry-job-bar:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.industry-job-fill {
  position: absolute;
  height: 100%;
  width: 100%;
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
  box-shadow: 0 0 4px rgba(244, 67, 54, 0.5);
  border: 1px solid rgba(244, 67, 54, 0.3);
}

/* Анимация мигания для индикатора внимания */
@keyframes blink {
  0%,
  50% {
    opacity: 1;
    transform: scale(1);
  }
  25%,
  75% {
    opacity: 0.3;
    transform: scale(0.8);
  }
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
