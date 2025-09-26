<template>
  <div class="project-dashboard">
    <div class="dashboard-header">
      <div class="project-title">
        <div class="project-icon">{{ getProjectIcon() }}</div>
        <div class="title-info">
          <h3>{{ project.name }}</h3>
          <div class="project-subtitle">
            {{ project.target.name }} × {{ project.quantity }}
          </div>
        </div>
      </div>
      <div class="project-status">
        <span :class="['status-badge', project.status]">
          {{ getStatusText(project.status) }}
        </span>
      </div>
    </div>

    <div class="dashboard-content">
      <!-- Общий прогресс -->
      <div class="section">
        <h4>■ Общий прогресс</h4>
        <div class="overall-progress">
          <div class="progress-visual">
            <div class="progress-circle-large">
              <svg width="120" height="120" viewBox="0 0 120 120">
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="8"
                  opacity="0.3"
                />
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="8"
                  stroke-dasharray="314.16"
                  :stroke-dashoffset="314.16 - (overallProgress / 100) * 314.16"
                  stroke-linecap="round"
                  transform="rotate(-90 60 60)"
                  class="progress-circle"
                />
              </svg>
              <div class="progress-text">
                <span class="progress-percent">{{ overallProgress }}%</span>
                <span class="progress-label">завершено</span>
              </div>
            </div>
          </div>
          <div class="progress-stats">
            <div class="stat-grid">
              <div class="stat-item">
                <div class="stat-value">{{ completedTasks }}</div>
                <div class="stat-label">Завершено</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ activeTasks }}</div>
                <div class="stat-label">В работе</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ pendingTasks }}</div>
                <div class="stat-label">Ожидает</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ totalTasks }}</div>
                <div class="stat-label">Всего</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Список задач с быстрыми действиями -->
      <div class="section">
        <h4>▦ Задачи проекта</h4>
        <div class="tasks-overview">
          <div
            v-for="task in project.tasks"
            :key="task.id"
            :class="['task-card', task.status]"
            @click="$emit('select-task', task)"
          >
            <div class="task-header">
              <div class="task-icon">{{ getTaskIcon(task) }}</div>
              <div class="task-info">
                <div class="task-name">{{ task.name }}</div>
                <div class="task-quantity">{{ task.quantity }}x</div>
              </div>
              <div :class="['task-status-dot', task.status]"></div>
            </div>
            <div class="task-progress-bar">
              <div
                class="task-progress-fill"
                :style="{ width: task.progress + '%' }"
              ></div>
            </div>
            <div class="task-footer">
              <span class="task-progress-text"
                >{{ Math.round(task.progress) }}%</span
              >
              <span class="task-duration">{{
                formatDuration(task.duration)
              }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Список покупок (агрегированный) -->
      <div class="section">
        <h4>🛒 Список покупок</h4>
        <div class="shopping-list">
          <div
            v-for="material in aggregatedMaterials"
            :key="material.id"
            :class="[
              'shopping-item',
              { available: material.available >= material.required },
            ]"
          >
            <div class="material-info">
              <div class="material-name">{{ material.name }}</div>
              <div class="material-type">
                {{ getMaterialTypeText(material.type) }}
              </div>
            </div>
            <div class="material-quantity">
              <span class="available">{{
                material.available.toLocaleString()
              }}</span>
              <span class="separator">/</span>
              <span class="required">{{
                material.required.toLocaleString()
              }}</span>
            </div>
            <div class="material-actions">
              <input
                type="checkbox"
                :checked="material.available >= material.required"
                @change="toggleMaterial(material, $event)"
                class="material-checkbox"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Финансы (заглушка) -->
      <div class="section">
        <h4>💰 Финансовый обзор</h4>
        <div class="financial-overview">
          <div class="financial-grid">
            <div class="financial-item">
              <div class="financial-label">Стоимость материалов</div>
              <div class="financial-value">
                {{ formatISK(estimatedMaterialCost) }}
              </div>
            </div>
            <div class="financial-item">
              <div class="financial-label">Предполагаемая прибыль</div>
              <div class="financial-value profit">
                {{ formatISK(estimatedProfit) }}
              </div>
            </div>
            <div class="financial-item">
              <div class="financial-label">Рентабельность</div>
              <div class="financial-value">{{ profitMargin }}%</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Быстрые действия -->
      <div class="section">
        <h4>🚀 Быстрые действия</h4>
        <div class="quick-actions">
          <button
            @click="startAllReadyTasks"
            :disabled="readyTasks.length === 0"
            class="quick-action-btn start"
          >
            ▶ Запустить все готовые ({{ readyTasks.length }})
          </button>
          <button
            @click="completeAllRunning"
            :disabled="runningTasks.length === 0"
            class="quick-action-btn complete"
          >
            ✓ Завершить все активные ({{ runningTasks.length }})
          </button>
          <button @click="exportShoppingList" class="quick-action-btn export">
            ▫ Экспорт списка покупок
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ProjectDashboard",
  props: {
    project: {
      type: Object,
      required: true,
    },
  },
  emits: ["select-task"],
  computed: {
    totalTasks() {
      return this.project.tasks?.length || 0;
    },
    completedTasks() {
      return (
        this.project.tasks?.filter((t) => t.status === "completed").length || 0
      );
    },
    activeTasks() {
      return (
        this.project.tasks?.filter((t) =>
          ["running", "ready"].includes(t.status)
        ).length || 0
      );
    },
    pendingTasks() {
      return (
        this.project.tasks?.filter((t) => t.status === "pending").length || 0
      );
    },
    overallProgress() {
      if (!this.project.tasks || this.project.tasks.length === 0) return 0;
      const avgProgress =
        this.project.tasks.reduce((sum, task) => sum + task.progress, 0) /
        this.project.tasks.length;
      return Math.round(avgProgress);
    },
    readyTasks() {
      return this.project.tasks?.filter((t) => t.status === "ready") || [];
    },
    runningTasks() {
      return this.project.tasks?.filter((t) => t.status === "running") || [];
    },
    aggregatedMaterials() {
      if (!this.project.tasks) return [];

      const materialMap = new Map();

      this.project.tasks.forEach((task) => {
        if (task.materials) {
          task.materials.forEach((material) => {
            if (materialMap.has(material.name)) {
              const existing = materialMap.get(material.name);
              existing.required += material.required;
              existing.available += material.available;
            } else {
              materialMap.set(material.name, { ...material });
            }
          });
        }
      });

      return Array.from(materialMap.values());
    },
    estimatedMaterialCost() {
      // Заглушка для стоимости материалов
      return this.aggregatedMaterials.reduce((sum, material) => {
        const estimatedPrice = this.getEstimatedPrice(material.name);
        return sum + material.required * estimatedPrice;
      }, 0);
    },
    estimatedProfit() {
      // Заглушка для прибыли
      const productPrice =
        this.getEstimatedPrice(this.project.target.name) *
        this.project.quantity;
      return productPrice - this.estimatedMaterialCost;
    },
    profitMargin() {
      if (this.estimatedMaterialCost === 0) return 0;
      return Math.round(
        (this.estimatedProfit / this.estimatedMaterialCost) * 100
      );
    },
  },
  methods: {
    getProjectIcon() {
      return this.project.target.icon || "🎯";
    },
    getStatusText(status) {
      const statusTexts = {
        planning: "Планирование",
        active: "Активен",
        in_progress: "В процессе",
        completed: "Завершён",
        paused: "Приостановлен",
        cancelled: "Отменён",
      };
      return statusTexts[status] || "Неизвестно";
    },
    getTaskIcon(task) {
      const typeIcons = {
        production: "🏭",
        research: "🔬",
        invention: "💡",
        copy: "📄",
        purchase: "💰",
      };
      return typeIcons[task.type] || "📋";
    },
    getMaterialTypeText(type) {
      const typeTexts = {
        raw: "Сырьё",
        component: "Компонент",
        blueprint: "Чертёж",
        purchase: "Покупка",
      };
      return typeTexts[type] || "Материал";
    },
    formatDuration(milliseconds) {
      const hours = Math.floor(milliseconds / (1000 * 60 * 60));
      const minutes = Math.floor(
        (milliseconds % (1000 * 60 * 60)) / (1000 * 60)
      );

      if (hours > 0) {
        return `${hours}ч ${minutes}м`;
      }
      return `${minutes}м`;
    },
    formatISK(amount) {
      if (amount >= 1000000000) {
        return `${(amount / 1000000000).toFixed(1)}B ISK`;
      } else if (amount >= 1000000) {
        return `${(amount / 1000000).toFixed(1)}M ISK`;
      } else if (amount >= 1000) {
        return `${(amount / 1000).toFixed(1)}K ISK`;
      }
      return `${Math.round(amount)} ISK`;
    },
    getEstimatedPrice(itemName) {
      // Заглушка для цен (в реальном приложении это будут данные из API)
      const mockPrices = {
        Tritanium: 5.5,
        Pyerite: 8.2,
        Tengu: 850000000,
        Raven: 180000000,
        Catalyst: 2500000,
      };
      return mockPrices[itemName] || 100000;
    },
    toggleMaterial(material, event) {
      if (event.target.checked) {
        material.available = material.required;
      } else {
        material.available = 0;
      }
    },
    startAllReadyTasks() {
      // Здесь была бы логика для запуска всех готовых задач
      alert(`Запуск ${this.readyTasks.length} готовых задач в разработке`);
    },
    completeAllRunning() {
      // Здесь была бы логика для завершения всех активных задач
      alert(
        `Завершение ${this.runningTasks.length} активных задач в разработке`
      );
    },
    exportShoppingList() {
      // Формируем текст для экспорта
      const shoppingText = this.aggregatedMaterials
        .filter((m) => m.available < m.required)
        .map((m) => `${m.name} ${m.required - m.available}`)
        .join("\n");

      // Копируем в буфер обмена
      navigator.clipboard
        .writeText(shoppingText)
        .then(() => {
          alert("Список покупок скопирован в буфер обмена!");
        })
        .catch(() => {
          alert("Ошибка копирования в буфер обмена");
        });
    },
  },
};
</script>

<style scoped>
.project-dashboard {
  padding: 24px;
  height: 100%;
  overflow-y: auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 1px solid #3c4043;
}

.project-title {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.project-icon {
  font-size: 40px;
  line-height: 1;
}

.title-info h3 {
  margin: 0 0 6px 0;
  color: #e6e6e6;
  font-size: 24px;
  font-weight: 500;
}

.project-subtitle {
  color: #abb2bf;
  font-size: 16px;
}

.status-badge {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
}

.status-badge.planning {
  background-color: #6c757d;
  color: white;
}

.status-badge.active {
  background-color: #28a745;
  color: white;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.section h4 {
  margin: 0 0 20px 0;
  color: #e6e6e6;
  font-size: 18px;
  font-weight: 500;
}

.overall-progress {
  display: flex;
  gap: 32px;
  align-items: center;
}

.progress-circle-large {
  position: relative;
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}

.progress-circle-large svg {
  width: 100%;
  height: 100%;
  color: #6c757d;
}

.progress-circle {
  transition: stroke-dashoffset 0.8s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.progress-percent {
  display: block;
  font-size: 24px;
  font-weight: 600;
  color: #e6e6e6;
}

.progress-label {
  font-size: 12px;
  color: #abb2bf;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background-color: #21252b;
  border-radius: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #6c757d;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #abb2bf;
}

.tasks-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.task-card {
  padding: 16px;
  background-color: #21252b;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 4px solid #6c757d;
}

.task-card:hover {
  background-color: #2c3038;
  transform: translateY(-2px);
}

.task-card.pending {
  border-left-color: #6c757d;
}

.task-card.ready {
  border-left-color: #6f7071;
}

.task-card.running {
  border-left-color: #495057;
}

.task-card.completed {
  border-left-color: #5a6268;
}

.task-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.task-icon {
  font-size: 18px;
}

.task-info {
  flex-grow: 1;
}

.task-name {
  color: #e6e6e6;
  font-weight: 500;
  margin-bottom: 2px;
}

.task-quantity {
  color: #abb2bf;
  font-size: 12px;
}

.task-status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.task-status-dot.pending {
  background-color: #6c757d;
}

.task-status-dot.ready {
  background-color: #6f7071;
}

.task-status-dot.running {
  background-color: #495057;
}

.task-status-dot.completed {
  background-color: #5a6268;
}

.task-progress-bar {
  height: 4px;
  background-color: #3c4043;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 8px;
}

.task-progress-fill {
  height: 100%;
  background-color: #6c757d;
  transition: width 0.3s ease;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-progress-text {
  color: #6c757d;
  font-size: 12px;
  font-weight: 500;
}

.task-duration {
  color: #abb2bf;
  font-size: 12px;
}

.shopping-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.shopping-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: #21252b;
  border-radius: 6px;
  border-left: 4px solid #868e96;
}

.shopping-item.available {
  border-left-color: #6c757d;
  opacity: 0.7;
}

.material-info {
  flex-grow: 1;
}

.material-name {
  color: #e6e6e6;
  font-weight: 500;
  margin-bottom: 2px;
}

.material-type {
  color: #abb2bf;
  font-size: 12px;
}

.material-quantity {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 0 16px;
}

.available {
  color: #6c757d;
  font-weight: 500;
}

.separator {
  color: #abb2bf;
}

.required {
  color: #abb2bf;
}

.material-checkbox {
  accent-color: #6c757d;
  transform: scale(1.2);
}

.financial-overview {
  background-color: #21252b;
  border-radius: 8px;
  padding: 20px;
}

.financial-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
}

.financial-item {
  text-align: center;
}

.financial-label {
  color: #abb2bf;
  font-size: 12px;
  margin-bottom: 8px;
}

.financial-value {
  color: #e6e6e6;
  font-size: 18px;
  font-weight: 600;
}

.financial-value.profit {
  color: #6c757d;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.quick-action-btn {
  padding: 12px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.quick-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quick-action-btn.start {
  background-color: #6c757d;
  color: white;
}

.quick-action-btn.start:hover:not(:disabled) {
  background-color: #5a6268;
}

.quick-action-btn.complete {
  background-color: #495057;
  color: white;
}

.quick-action-btn.complete:hover:not(:disabled) {
  background-color: #343a40;
}

.quick-action-btn.export {
  background-color: #6c757d;
  color: white;
}

.quick-action-btn.export:hover:not(:disabled) {
  background-color: #5a6268;
}
</style>
