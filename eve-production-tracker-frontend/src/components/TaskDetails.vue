<template>
  <div class="task-details">
    <div class="details-header">
      <div class="task-title">
        <div class="task-icon">{{ getTaskIcon(task) }}</div>
        <div class="title-info">
          <h3>{{ task.name }}</h3>
          <div class="task-subtitle">
            {{ task.quantity }}x {{ task.item?.name || "Предмет" }}
          </div>
        </div>
      </div>
      <div class="task-status-badge">
        <span :class="['status-badge', task.status]">
          {{ getStatusText(task.status) }}
        </span>
      </div>
    </div>

    <div class="details-content">
      <!-- Прогресс задачи -->
      <div class="section">
        <h4>Прогресс выполнения</h4>
        <div class="progress-section">
          <div class="circular-progress">
            <svg width="80" height="80" viewBox="0 0 80 80">
              <circle
                cx="40"
                cy="40"
                r="35"
                fill="none"
                stroke="currentColor"
                stroke-width="6"
                opacity="0.3"
              />
              <circle
                cx="40"
                cy="40"
                r="35"
                fill="none"
                stroke="currentColor"
                stroke-width="6"
                stroke-dasharray="219.91"
                :stroke-dashoffset="219.91 - (task.progress / 100) * 219.91"
                stroke-linecap="round"
                transform="rotate(-90 40 40)"
                class="progress-circle"
              />
            </svg>
            <div class="progress-text">
              <span class="progress-percent"
                >{{ Math.round(task.progress) }}%</span
              >
            </div>
          </div>
          <div class="progress-info">
            <div class="progress-stats">
              <div class="stat">
                <span class="stat-label">Статус:</span>
                <span :class="['stat-value', task.status]">{{
                  getStatusText(task.status)
                }}</span>
              </div>
              <div class="stat">
                <span class="stat-label">Время:</span>
                <span class="stat-value">{{
                  formatDuration(task.duration)
                }}</span>
              </div>
              <div v-if="task.status === 'running'" class="stat">
                <span class="stat-label">Осталось:</span>
                <span class="stat-value">{{ getRemainingTime() }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Материалы -->
      <div v-if="task.materials && task.materials.length > 0" class="section">
        <h4>Необходимые материалы</h4>
        <div class="materials-list">
          <div
            v-for="material in task.materials"
            :key="material.id"
            :class="[
              'material-item',
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
              <button
                v-if="material.available < material.required"
                @click="addMaterial(material)"
                class="add-material-btn"
                title="Добавить материал"
              >
                +
              </button>
              <button
                @click="buyMaterial(material)"
                class="buy-material-btn"
                title="Купить материал"
              >
                $
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Навыки -->
      <div v-if="task.skills && task.skills.length > 0" class="section">
        <h4>Требуемые навыки</h4>
        <div class="skills-list">
          <div v-for="skill in task.skills" :key="skill" class="skill-item">
            △ {{ skill }}
          </div>
        </div>
      </div>

      <!-- Зависимости -->
      <div
        v-if="task.dependencies && task.dependencies.length > 0"
        class="section"
      >
        <h4>Зависимости</h4>
        <div class="dependencies-list">
          <div
            v-for="depId in task.dependencies"
            :key="depId"
            class="dependency-item"
          >
            {{ getDependencyName(depId) }}
          </div>
        </div>
      </div>

      <!-- Действия -->
      <div class="section actions-section">
        <h4>Действия</h4>
        <div class="action-buttons">
          <button
            v-if="task.status === 'pending' && canStartTask()"
            @click="startTask"
            class="action-btn start"
          >
            ▶ Запустить работу
          </button>
          <button
            v-if="task.status === 'ready' && canStartTask()"
            @click="startTask"
            class="action-btn start"
          >
            ▶ Запустить работу
          </button>
          <button
            v-if="task.status === 'running'"
            @click="pauseTask"
            class="action-btn pause"
          >
            ‖ Приостановить
          </button>
          <button
            v-if="['pending', 'running'].includes(task.status)"
            @click="completeTask"
            class="action-btn complete"
          >
            ✓ Отметить как выполненное
          </button>
          <button
            v-if="task.status === 'completed'"
            @click="resetTask"
            class="action-btn reset"
          >
            ↻ Сбросить
          </button>
        </div>
      </div>

      <!-- Детали производства -->
      <div class="section">
        <h4>Детали производства</h4>
        <div class="production-details">
          <div class="detail-row">
            <span class="detail-label">Тип производства:</span>
            <span class="detail-value">{{ getTaskTypeText(task.type) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Количество:</span>
            <span class="detail-value">{{ task.quantity }}x</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Время выполнения:</span>
            <span class="detail-value">{{
              formatDuration(task.duration)
            }}</span>
          </div>
          <div v-if="task.item" class="detail-row">
            <span class="detail-label">Предмет:</span>
            <span class="detail-value">{{ task.item.name }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "TaskDetails",
  props: {
    task: {
      type: Object,
      required: true,
    },
    project: {
      type: Object,
      required: true,
    },
  },
  emits: ["update-task"],
  methods: {
    getTaskIcon(task) {
      const typeIcons = {
        production: "■",
        research: "△",
        invention: "◆",
        copy: "□",
        purchase: "●",
      };
      return typeIcons[task.type] || "○";
    },
    getStatusText(status) {
      const statusTexts = {
        pending: "Ожидает",
        ready: "Готово к запуску",
        running: "Выполняется",
        completed: "Завершено",
        paused: "Приостановлено",
        failed: "Ошибка",
      };
      return statusTexts[status] || "Неизвестно";
    },
    getTaskTypeText(type) {
      const typeTexts = {
        production: "Производство",
        research: "Исследование",
        invention: "Изобретение",
        copy: "Копирование",
        purchase: "Покупка",
      };
      return typeTexts[type] || "Неизвестно";
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
    getRemainingTime() {
      // Заглушка для оставшегося времени
      return this.formatDuration(
        this.task.duration * (1 - this.task.progress / 100)
      );
    },
    canStartTask() {
      // Проверяем, доступны ли все необходимые материалы
      if (!this.task.materials) return true;
      return this.task.materials.every(
        (material) => material.available >= material.required
      );
    },
    getDependencyName(depId) {
      const dependentTask = this.project.tasks.find((t) => t.id === depId);
      return dependentTask ? dependentTask.name : `Задача #${depId}`;
    },
    startTask() {
      const updatedTask = { ...this.task, status: "running" };
      this.$emit("update-task", updatedTask);
    },
    pauseTask() {
      const updatedTask = { ...this.task, status: "paused" };
      this.$emit("update-task", updatedTask);
    },
    completeTask() {
      const updatedTask = { ...this.task, status: "completed", progress: 100 };
      this.$emit("update-task", updatedTask);
    },
    resetTask() {
      const updatedTask = { ...this.task, status: "pending", progress: 0 };
      this.$emit("update-task", updatedTask);
    },
    addMaterial(material) {
      // Заглушка для добавления материала
      const needed = material.required - material.available;
      const amount = prompt(
        `Сколько единиц ${material.name} добавить? (нужно: ${needed})`
      );
      if (amount && !isNaN(amount)) {
        material.available += parseInt(amount);
        this.$emit("update-task", { ...this.task });
      }
    },
    buyMaterial(material) {
      // Заглушка для покупки материала
      alert(`Покупка материала "${material.name}" в разработке`);
    },
  },
};
</script>

<style scoped>
.task-details {
  padding: 24px;
  height: 100%;
  overflow-y: auto;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #3c4043;
}

.task-title {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.task-icon {
  font-size: 32px;
  line-height: 1;
}

.title-info h3 {
  margin: 0 0 4px 0;
  color: #e6e6e6;
  font-size: 20px;
  font-weight: 500;
}

.task-subtitle {
  color: #abb2bf;
  font-size: 14px;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background-color: #6c757d;
  color: white;
}

.status-badge.ready {
  background-color: #ffc107;
  color: black;
}

.status-badge.running {
  background-color: #17a2b8;
  color: white;
}

.status-badge.completed {
  background-color: #28a745;
  color: white;
}

.status-badge.paused {
  background-color: #fd7e14;
  color: white;
}

.details-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section h4 {
  margin: 0 0 16px 0;
  color: #e6e6e6;
  font-size: 16px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-section {
  display: flex;
  gap: 24px;
  align-items: center;
}

.circular-progress {
  position: relative;
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.circular-progress svg {
  width: 100%;
  height: 100%;
  color: #6c757d;
  transform: rotate(-90deg);
}

.progress-circle {
  transition: stroke-dashoffset 0.5s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.progress-percent {
  font-size: 16px;
  font-weight: 600;
  color: #e6e6e6;
}

.progress-info {
  flex-grow: 1;
}

.progress-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #21252b;
  border-radius: 4px;
}

.stat-label {
  color: #abb2bf;
  font-size: 14px;
}

.stat-value {
  color: #e6e6e6;
  font-weight: 500;
}

.stat-value.running {
  color: #6c757d;
}

.stat-value.completed {
  color: #5a6268;
}

.materials-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.material-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: #21252b;
  border-radius: 6px;
  border-left: 4px solid #dc3545;
}

.material-item.available {
  border-left-color: #28a745;
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

.material-actions {
  display: flex;
  gap: 4px;
}

.add-material-btn,
.buy-material-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.add-material-btn:hover,
.buy-material-btn:hover {
  background-color: #3c4043;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-item {
  padding: 6px 12px;
  background-color: #21252b;
  border-radius: 4px;
  color: #ced4da;
  font-size: 14px;
}

.dependencies-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dependency-item {
  padding: 8px 12px;
  background-color: #21252b;
  border-radius: 4px;
  color: #abb2bf;
  font-size: 14px;
}

.actions-section .action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.action-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-btn.start {
  background-color: #6c757d;
  color: white;
}

.action-btn.start:hover {
  background-color: #5a6268;
}

.action-btn.pause {
  background-color: #868e96;
  color: white;
}

.action-btn.pause:hover {
  background-color: #6c757d;
}

.action-btn.complete {
  background-color: #495057;
  color: white;
}

.action-btn.complete:hover {
  background-color: #343a40;
}

.action-btn.reset {
  background-color: #868e96;
  color: white;
}

.action-btn.reset:hover {
  background-color: #6c757d;
}

.production-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #21252b;
  border-radius: 4px;
}

.detail-label {
  color: #abb2bf;
  font-size: 14px;
}

.detail-value {
  color: #e6e6e6;
  font-weight: 500;
}
</style>
