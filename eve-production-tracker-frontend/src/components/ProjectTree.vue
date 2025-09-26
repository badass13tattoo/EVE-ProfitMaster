<template>
  <div class="project-tree">
    <div class="tree-header">
      <h3>{{ project.name }}</h3>
      <div class="tree-controls">
        <button @click="expandAll" title="Развернуть все">▼</button>
        <button @click="collapseAll" title="Свернуть все">▶</button>
        <select v-model="filterStatus" class="status-filter">
          <option value="">Все задачи</option>
          <option value="pending">Ожидает</option>
          <option value="ready">Готово к запуску</option>
          <option value="running">Выполняется</option>
          <option value="completed">Завершено</option>
        </select>
      </div>
    </div>

    <div class="tree-content">
      <div class="task-tree">
        <TreeNode
          v-for="task in rootTasks"
          :key="task.id"
          :task="task"
          :project="project"
          :selected-task="selectedTask"
          :expanded="expandedNodes"
          :filter-status="filterStatus"
          @select="$emit('select-task', $event)"
          @toggle="toggleNode"
          @update="$emit('update-task', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import TreeNode from "./TreeNode.vue";

export default {
  name: "ProjectTree",
  components: {
    TreeNode,
  },
  props: {
    project: {
      type: Object,
      required: true,
    },
    selectedTask: {
      type: Object,
      default: null,
    },
  },
  emits: ["select-task", "update-task"],
  data() {
    return {
      expandedNodes: new Set(),
      filterStatus: "",
    };
  },
  computed: {
    rootTasks() {
      if (!this.project.tasks) return [];

      // Находим корневые задачи (те, которые не являются children других задач)
      const allChildrenIds = new Set();
      this.project.tasks.forEach((task) => {
        if (task.children) {
          task.children.forEach((child) => allChildrenIds.add(child.id));
        }
      });

      return this.project.tasks.filter((task) => !allChildrenIds.has(task.id));
    },
  },
  mounted() {
    // По умолчанию разворачиваем первый уровень
    this.rootTasks.forEach((task) => {
      this.expandedNodes.add(task.id);
    });
  },
  methods: {
    toggleNode(nodeId) {
      if (this.expandedNodes.has(nodeId)) {
        this.expandedNodes.delete(nodeId);
      } else {
        this.expandedNodes.add(nodeId);
      }
    },
    expandAll() {
      this.project.tasks.forEach((task) => {
        this.expandedNodes.add(task.id);
      });
    },
    collapseAll() {
      this.expandedNodes.clear();
    },
  },
};
</script>

<style scoped>
.project-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #3c4043;
  margin-bottom: 16px;
}

.tree-header h3 {
  margin: 0;
  color: #e6e6e6;
  font-size: 18px;
}

.tree-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tree-controls button {
  background: none;
  border: none;
  color: #abb2bf;
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.tree-controls button:hover {
  background-color: #3c4043;
  color: #e6e6e6;
}

.status-filter {
  padding: 6px 10px;
  background-color: #3c4043;
  border: 1px solid #4a4a4a;
  border-radius: 4px;
  color: #e6e6e6;
  font-size: 12px;
}

.tree-content {
  flex-grow: 1;
  overflow-y: auto;
}

.task-tree {
  padding-bottom: 20px;
}
</style>
