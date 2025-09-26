<template>
  <div class="project-view">
    <!-- Заголовок с действиями -->
    <div class="project-header">
      <div class="header-left">
        <h2>Управление проектами</h2>
        <div class="project-stats" v-if="projects.length > 0">
          <span class="stat-item">
            {{ projects.length }} проект{{ projects.length > 1 ? "ов" : "" }}
          </span>
          <span class="stat-item"> {{ activeProjects.length }} активных </span>
        </div>
      </div>
      <div class="header-actions">
        <button @click="showWizard = true" class="create-button">
          + Создать проект
        </button>
        <div class="view-controls">
          <button
            :class="['view-button', { active: currentView === 'list' }]"
            @click="currentView = 'list'"
            title="Список проектов"
          >
            ▦
          </button>
          <button
            :class="['view-button', { active: currentView === 'tree' }]"
            @click="currentView = 'tree'"
            title="Дерево задач"
          >
            ⧨
          </button>
        </div>
      </div>
    </div>

    <!-- Основной контент -->
    <div class="project-content">
      <!-- Левая панель -->
      <div class="left-panel">
        <!-- Список проектов -->
        <div v-if="currentView === 'list'" class="projects-list">
          <div v-if="projects.length === 0" class="empty-state">
            <div class="empty-icon">▦</div>
            <h3>Нет проектов</h3>
            <p>Создайте первый проект для начала работы</p>
          </div>
          <div
            v-for="project in projects"
            :key="project.id"
            :class="[
              'project-item',
              { selected: selectedProject?.id === project.id },
            ]"
            @click="selectProject(project)"
          >
            <div class="project-icon">
              {{ getProjectIcon(project) }}
            </div>
            <div class="project-info">
              <div class="project-name">{{ project.name }}</div>
              <div class="project-meta">
                <span class="project-target"
                  >{{ project.target.name }} × {{ project.quantity }}</span
                >
                <span :class="['project-status', project.status]">
                  {{ getStatusText(project.status) }}
                </span>
              </div>
              <div class="project-progress">
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: getProjectProgress(project) + '%' }"
                  ></div>
                </div>
                <span class="progress-text"
                  >{{ getProjectProgress(project) }}%</span
                >
              </div>
            </div>
            <div class="project-actions">
              <button @click.stop="editProject(project)" title="Редактировать">
                ⚙
              </button>
              <button @click.stop="deleteProject(project)" title="Удалить">
                ×
              </button>
            </div>
          </div>
        </div>

        <!-- Дерево задач -->
        <div
          v-if="currentView === 'tree' && selectedProject"
          class="project-tree"
        >
          <ProjectTree
            :project="selectedProject"
            :selected-task="selectedTask"
            @select-task="selectTask"
            @update-task="updateTask"
          />
        </div>

        <!-- Заглушка для дерева без выбранного проекта -->
        <div
          v-if="currentView === 'tree' && !selectedProject"
          class="empty-state"
        >
          <div class="empty-icon">⧨</div>
          <h3>Выберите проект</h3>
          <p>Выберите проект из списка, чтобы увидеть дерево задач</p>
        </div>
      </div>

      <!-- Правая панель -->
      <div class="right-panel">
        <TaskDetails
          v-if="selectedProject && selectedTask"
          :project="selectedProject"
          :task="selectedTask"
          @update-task="updateTask"
        />
        <div
          v-else-if="selectedProject && !selectedTask"
          class="project-dashboard"
        >
          <ProjectDashboard
            :project="selectedProject"
            @select-task="selectTask"
          />
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">▢</div>
          <h3>Выберите проект</h3>
          <p>Выберите проект или задачу для просмотра деталей</p>
        </div>
      </div>
    </div>

    <!-- Мастер создания проекта -->
    <ProjectWizard
      v-if="showWizard"
      @close="showWizard = false"
      @create-project="createProject"
    />
  </div>
</template>

<script>
import ProjectWizard from "./ProjectWizard.vue";
import ProjectTree from "./ProjectTree.vue";
import TaskDetails from "./TaskDetails.vue";
import ProjectDashboard from "./ProjectDashboard.vue";

export default {
  name: "ProjectView",
  components: {
    ProjectWizard,
    ProjectTree,
    TaskDetails,
    ProjectDashboard,
  },
  data() {
    return {
      projects: [],
      selectedProject: null,
      selectedTask: null,
      showWizard: false,
      currentView: "list", // 'list' или 'tree'
    };
  },
  computed: {
    activeProjects() {
      return this.projects.filter((p) =>
        ["active", "in_progress"].includes(p.status)
      );
    },
  },
  methods: {
    selectProject(project) {
      this.selectedProject = project;
      this.selectedTask = null;
      // Не переключаемся автоматически на дерево, оставляем текущий вид
    },
    selectTask(task) {
      this.selectedTask = task;
    },
    createProject(project) {
      // Преобразуем структуру проекта в дерево задач
      const projectWithTasks = {
        ...project,
        tasks: this.generateProjectTasks(project),
      };

      this.projects.push(projectWithTasks);
      this.selectProject(projectWithTasks);
      this.showWizard = false;
    },
    generateProjectTasks(project) {
      const tasks = [];

      // Основная задача
      const mainTask = {
        id: `task_${Date.now()}`,
        name: `Произвести ${project.target.name}`,
        type: "production",
        status: "pending",
        quantity: project.quantity,
        item: project.target,
        dependencies: [],
        children: [],
        materials: [],
        skills: [],
        duration: 3600000, // 1 час в миллисекундах
        progress: 0,
      };

      // Создаем задачи для каждого компонента
      project.components.forEach((component) => {
        if (component.action === "build") {
          const componentTask = {
            id: `task_${Date.now()}_${component.id}`,
            name: `Произвести ${component.name}`,
            type: "production",
            status: "pending",
            quantity: component.required,
            item: component,
            dependencies: [],
            children: [],
            materials: this.generateMaterialsForComponent(component),
            skills: ["Industry", "Production Efficiency"],
            duration: 1800000, // 30 минут
            progress: 0,
          };

          mainTask.children.push(componentTask);
          mainTask.dependencies.push(componentTask.id);
          tasks.push(componentTask);
        } else {
          // Добавляем материалы для покупки в основную задачу
          mainTask.materials.push({
            id: component.id,
            name: component.name,
            required: component.required,
            available: 0,
            type: "purchase",
          });
        }
      });

      tasks.unshift(mainTask);
      return tasks;
    },
    generateMaterialsForComponent(component) {
      // Заглушка для материалов
      return [
        {
          id: `mat_${component.id}_1`,
          name: "Tritanium",
          required: Math.floor(component.required * 1000),
          available: 0,
          type: "raw",
        },
        {
          id: `mat_${component.id}_2`,
          name: "Pyerite",
          required: Math.floor(component.required * 500),
          available: 0,
          type: "raw",
        },
      ];
    },
    updateTask(task) {
      // Обновляем задачу в проекте
      if (this.selectedProject) {
        const taskIndex = this.selectedProject.tasks.findIndex(
          (t) => t.id === task.id
        );
        if (taskIndex !== -1) {
          this.selectedProject.tasks[taskIndex] = { ...task };
        }
      }
    },
    editProject(project) {
      // TODO: Реализовать редактирование проекта
      alert("Редактирование проекта в разработке");
    },
    deleteProject(project) {
      if (confirm(`Удалить проект "${project.name}"?`)) {
        const index = this.projects.findIndex((p) => p.id === project.id);
        if (index !== -1) {
          this.projects.splice(index, 1);
          if (this.selectedProject?.id === project.id) {
            this.selectedProject = null;
            this.selectedTask = null;
          }
        }
      }
    },
    getProjectIcon(project) {
      const statusIcons = {
        planning: "○",
        active: "▶",
        in_progress: "●",
        completed: "■",
        paused: "‖",
        cancelled: "×",
      };
      return statusIcons[project.status] || "○";
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
    getProjectProgress(project) {
      if (!project.tasks || project.tasks.length === 0) return 0;

      const totalTasks = project.tasks.length;
      const completedTasks = project.tasks.filter(
        (t) => t.status === "completed"
      ).length;

      return Math.round((completedTasks / totalTasks) * 100);
    },
  },
};
</script>

<style scoped>
.project-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background-color: #21252b;
  border-bottom: 1px solid #3c4043;
}

.header-left h2 {
  margin: 0 0 8px 0;
  color: #e6e6e6;
  font-size: 24px;
}

.project-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  font-size: 14px;
  color: #abb2bf;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.create-button {
  padding: 10px 20px;
  background-color: #495057;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.create-button:hover {
  background-color: #6c757d;
}

.view-controls {
  display: flex;
  gap: 4px;
  background-color: #3c4043;
  border-radius: 6px;
  padding: 2px;
}

.view-button {
  padding: 8px 12px;
  background: none;
  border: none;
  color: #abb2bf;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s ease;
}

.view-button:hover {
  color: #e6e6e6;
}

.view-button.active {
  background-color: #495057;
  color: white;
}

.project-content {
  display: flex;
  flex-grow: 1;
  overflow: hidden;
}

.left-panel {
  width: 400px;
  flex-shrink: 0;
  background-color: #2c2c2c;
  border-right: 1px solid #3c4043;
  overflow-y: auto;
}

.right-panel {
  flex-grow: 1;
  background-color: #282c34;
  overflow-y: auto;
}

.projects-list {
  padding: 16px;
}

.project-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background-color: #3c4043;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.project-item:hover {
  background-color: #4a4a4a;
}

.project-item.selected {
  background-color: #495057;
  color: white;
}

.project-item.selected .project-meta span {
  color: rgba(255, 255, 255, 0.8);
}

.project-icon {
  font-size: 24px;
  width: 40px;
  text-align: center;
}

.project-info {
  flex-grow: 1;
  min-width: 0;
}

.project-name {
  font-weight: 500;
  font-size: 16px;
  margin-bottom: 4px;
  color: inherit;
}

.project-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
}

.project-target {
  color: #abb2bf;
}

.project-status {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.project-status.planning {
  background-color: #6c757d;
  color: white;
}

.project-status.active {
  background-color: #495057;
  color: white;
}

.project-status.in_progress {
  background-color: #6f7071;
  color: white;
}

.project-status.completed {
  background-color: #5a6268;
  color: white;
}

.project-status.paused {
  background-color: #6c757d;
  color: white;
}

.project-status.cancelled {
  background-color: #868e96;
  color: white;
}

.project-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  flex-grow: 1;
  height: 4px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #6c757d;
  transition: width 0.3s ease;
}

.project-item.selected .progress-bar {
  background-color: rgba(255, 255, 255, 0.3);
}

.progress-text {
  font-size: 11px;
  color: #abb2bf;
  min-width: 30px;
}

.project-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.project-item:hover .project-actions {
  opacity: 1;
}

.project-actions button {
  background: none;
  border: none;
  color: #abb2bf;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.project-actions button:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #e6e6e6;
}

.project-tree {
  padding: 16px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: #abb2bf;
  height: 100%;
  min-height: 300px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  color: #e6e6e6;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  opacity: 0.7;
}
</style>
