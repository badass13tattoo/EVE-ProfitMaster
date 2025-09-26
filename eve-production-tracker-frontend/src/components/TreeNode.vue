<template>
  <div v-if="shouldShowTask" class="tree-node">
    <div
      :class="[
        'task-node',
        { selected: isSelected, 'has-children': hasChildren },
      ]"
      @click="selectTask"
    >
      <div class="node-content">
        <button
          v-if="hasChildren"
          @click.stop="toggleExpanded"
          class="expand-button"
        >
          {{ isExpanded ? "▼" : "▶" }}
        </button>
        <span v-else class="expand-placeholder"></span>

        <div class="task-icon">
          {{ getTaskIcon(task) }}
        </div>

        <div class="task-info">
          <div class="task-name">{{ task.name }}</div>
          <div class="task-meta">
            <span class="task-quantity">{{ task.quantity }}x</span>
            <span :class="['task-status', task.status]">
              {{ getStatusText(task.status) }}
            </span>
          </div>
        </div>

        <div class="task-progress">
          <div class="progress-ring">
            <svg width="24" height="24" viewBox="0 0 24 24">
              <circle
                cx="12"
                cy="12"
                r="10"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                opacity="0.3"
              />
              <circle
                cx="12"
                cy="12"
                r="10"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-dasharray="62.83"
                :stroke-dashoffset="62.83 - (task.progress / 100) * 62.83"
                stroke-linecap="round"
                transform="rotate(-90 12 12)"
                class="progress-circle"
              />
            </svg>
            <span class="progress-percent"
              >{{ Math.round(task.progress) }}%</span
            >
          </div>
        </div>

        <div class="task-actions">
          <button
            v-if="task.status === 'ready'"
            @click.stop="startTask"
            class="action-button start"
            title="Запустить задачу"
          >
            ▶
          </button>
          <button
            v-if="task.status === 'running'"
            @click.stop="pauseTask"
            class="action-button pause"
            title="Приостановить"
          >
            ‖
          </button>
          <button
            v-if="['pending', 'running'].includes(task.status)"
            @click.stop="completeTask"
            class="action-button complete"
            title="Отметить как завершённую"
          >
            ✓
          </button>
        </div>
      </div>

      <!-- Индикаторы состояния -->
      <div class="status-indicators">
        <span
          v-if="task.materials && getMissingMaterialsCount() > 0"
          class="indicator materials"
          :title="`Не хватает материалов: ${getMissingMaterialsCount()}`"
        >
          ■ {{ getMissingMaterialsCount() }}
        </span>
        <span
          v-if="task.skills && task.skills.length > 0"
          class="indicator skills"
          :title="`Требуемые навыки: ${task.skills.join(', ')}`"
        >
          △ {{ task.skills.length }}
        </span>
        <span
          v-if="task.duration"
          class="indicator duration"
          :title="`Время выполнения: ${formatDuration(task.duration)}`"
        >
          ○ {{ formatDuration(task.duration) }}
        </span>
      </div>
    </div>

    <!-- Дочерние задачи -->
    <div v-if="hasChildren && isExpanded" class="children-container">
      <TreeNode
        v-for="childTask in task.children"
        :key="childTask.id"
        :task="childTask"
        :project="project"
        :selected-task="selectedTask"
        :expanded="expanded"
        :filter-status="filterStatus"
        :depth="depth + 1"
        @select="$emit('select', $event)"
        @toggle="$emit('toggle', $event)"
        @update="$emit('update', $event)"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: "TreeNode",
  props: {
    task: {
      type: Object,
      required: true,
    },
    project: {
      type: Object,
      required: true,
    },
    selectedTask: {
      type: Object,
      default: null,
    },
    expanded: {
      type: Set,
      required: true,
    },
    filterStatus: {
      type: String,
      default: "",
    },
    depth: {
      type: Number,
      default: 0,
    },
  },
  emits: ["select", "toggle", "update"],
  computed: {
    isSelected() {
      return this.selectedTask && this.selectedTask.id === this.task.id;
    },
    hasChildren() {
      return this.task.children && this.task.children.length > 0;
    },
    isExpanded() {
      return this.expanded.has(this.task.id);
    },
    shouldShowTask() {
      if (!this.filterStatus) return true;
      return this.task.status === this.filterStatus;
    },
  },
  methods: {
    selectTask() {
      this.$emit("select", this.task);
    },
    toggleExpanded() {
      this.$emit("toggle", this.task.id);
    },
    startTask() {
      const updatedTask = { ...this.task, status: "running" };
      this.$emit("update", updatedTask);
    },
    pauseTask() {
      const updatedTask = { ...this.task, status: "pending" };
      this.$emit("update", updatedTask);
    },
    completeTask() {
      const updatedTask = { ...this.task, status: "completed", progress: 100 };
      this.$emit("update", updatedTask);
    },
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
        ready: "Готово",
        running: "Выполняется",
        completed: "Завершено",
        paused: "Приостановлено",
        failed: "Ошибка",
      };
      return statusTexts[status] || "Неизвестно";
    },
    getMissingMaterialsCount() {
      if (!this.task.materials) return 0;
      return this.task.materials.filter(
        (material) => material.available < material.required
      ).length;
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
  },
};
</script>

<style scoped>
.tree-node {
  margin-bottom: 4px;
}

.task-node {
  padding: 12px;
  background-color: #3c4043;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.task-node:hover {
  background-color: #4a4a4a;
}

.task-node.selected {
  border-color: #6c757d;
  background-color: #495057;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.expand-button {
  background: none;
  border: none;
  color: #abb2bf;
  cursor: pointer;
  font-size: 14px;
  padding: 2px;
  border-radius: 2px;
  transition: all 0.2s ease;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.expand-button:hover {
  background-color: #2c3038;
  color: #e6e6e6;
}

.expand-placeholder {
  width: 20px;
  height: 20px;
}

.task-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.task-info {
  flex-grow: 1;
  min-width: 0;
}

.task-name {
  font-weight: 500;
  color: #e6e6e6;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.task-quantity {
  color: #abb2bf;
}

.task-status {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
}

.task-status.pending {
  background-color: #6c757d;
  color: white;
}

.task-status.ready {
  background-color: #6f7071;
  color: white;
}

.task-status.running {
  background-color: #495057;
  color: white;
}

.task-status.completed {
  background-color: #5a6268;
  color: white;
}

.task-status.paused {
  background-color: #6c757d;
  color: white;
}

.task-status.failed {
  background-color: #868e96;
  color: white;
}

.task-progress {
  display: flex;
  align-items: center;
}

.progress-ring {
  position: relative;
  width: 24px;
  height: 24px;
}

.progress-ring svg {
  width: 100%;
  height: 100%;
  color: #6c757d;
}

.progress-circle {
  transition: stroke-dashoffset 0.3s ease;
}

.progress-percent {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 8px;
  font-weight: 500;
  color: #e6e6e6;
}

.task-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.task-node:hover .task-actions {
  opacity: 1;
}

.action-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  font-size: 12px;
  transition: all 0.2s ease;
}

.action-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.action-button.start {
  color: #adb5bd;
}

.action-button.pause {
  color: #adb5bd;
}

.action-button.complete {
  color: #adb5bd;
}

.status-indicators {
  display: flex;
  gap: 6px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.indicator {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 3px;
  background-color: #21252b;
  color: #abb2bf;
  display: flex;
  align-items: center;
  gap: 2px;
}

.indicator.materials {
  background-color: #495057;
  color: #ced4da;
}

.indicator.skills {
  background-color: #495057;
  color: #ced4da;
}

.indicator.duration {
  background-color: #495057;
  color: #ced4da;
}

.children-container {
  margin-left: 30px;
  margin-top: 8px;
  border-left: 2px solid #3c4043;
  padding-left: 12px;
}
</style>
