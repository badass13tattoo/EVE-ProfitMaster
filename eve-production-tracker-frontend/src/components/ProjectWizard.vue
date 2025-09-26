<template>
  <div class="wizard-overlay">
    <div class="wizard-container">
      <div class="wizard-header">
        <h2>Мастер создания проекта</h2>
        <div class="wizard-progress">
          <div class="step-indicator">
            <div
              v-for="(step, index) in steps"
              :key="index"
              :class="[
                'step',
                {
                  active: currentStep === index + 1,
                  completed: currentStep > index + 1,
                },
              ]"
            >
              {{ index + 1 }}
            </div>
          </div>
          <div class="step-title">{{ steps[currentStep - 1]?.title }}</div>
        </div>
        <button class="close-button" @click="$emit('close')">×</button>
      </div>

      <div class="wizard-content">
        <!-- Шаг 1: Выбор цели -->
        <div v-if="currentStep === 1" class="step-content">
          <h3>Выберите цель производства</h3>
          <div class="target-selection">
            <div class="search-container">
              <input
                v-model="targetSearch"
                class="target-search"
                placeholder="Поиск предмета..."
                @input="filterTargets"
              />
            </div>
            <div class="target-list">
              <div
                v-for="item in filteredTargets"
                :key="item.id"
                :class="[
                  'target-item',
                  { selected: selectedTarget?.id === item.id },
                ]"
                @click="selectTarget(item)"
              >
                <div class="item-icon">{{ item.icon }}</div>
                <div class="item-info">
                  <div class="item-name">{{ item.name }}</div>
                  <div class="item-category">{{ item.category }}</div>
                </div>
              </div>
            </div>
            <div v-if="selectedTarget" class="quantity-section">
              <label>Количество:</label>
              <input
                v-model.number="targetQuantity"
                type="number"
                min="1"
                class="quantity-input"
              />
            </div>
          </div>
        </div>

        <!-- Шаг 2: Декомпозиция -->
        <div v-if="currentStep === 2" class="step-content">
          <h3>Выберите компоненты для производства</h3>
          <div class="target-info">
            <strong>{{ selectedTarget.name }}</strong> × {{ targetQuantity }}
          </div>
          <div class="components-list">
            <div
              v-for="component in projectComponents"
              :key="component.id"
              class="component-item"
            >
              <div class="component-info">
                <div class="component-icon">{{ component.icon }}</div>
                <div class="component-details">
                  <div class="component-name">{{ component.name }}</div>
                  <div class="component-quantity">
                    Нужно: {{ component.required }}
                  </div>
                </div>
              </div>
              <div class="component-actions">
                <label class="action-option">
                  <input
                    type="radio"
                    :value="'build'"
                    v-model="component.action"
                    @change="updateComponent(component)"
                  />
                  <span class="action-label build">▶ Произвести</span>
                </label>
                <label class="action-option">
                  <input
                    type="radio"
                    :value="'buy'"
                    v-model="component.action"
                    @change="updateComponent(component)"
                  />
                  <span class="action-label buy">● Купить</span>
                </label>
              </div>

              <!-- Опции покупки -->
              <div v-if="component.action === 'buy'" class="buy-options">
                <label class="buy-method-option">
                  <input
                    type="radio"
                    :value="'sell_order'"
                    v-model="component.buyMethod"
                    @change="updateComponent(component)"
                  />
                  <span class="buy-method-label sell-order"
                    >↗ Sell ордера (быстро)</span
                  >
                </label>
                <label class="buy-method-option">
                  <input
                    type="radio"
                    :value="'buy_order'"
                    v-model="component.buyMethod"
                    @change="updateComponent(component)"
                  />
                  <span class="buy-method-label buy-order"
                    >↙ Buy ордера (дешевле)</span
                  >
                </label>
              </div>
            </div>
          </div>
          <div class="mass-actions">
            <button @click="selectAllAction('build')" class="mass-button">
              ▶ Производить всё возможное
            </button>
            <button @click="selectAllAction('buy')" class="mass-button">
              ● Купить всё (Sell ордера)
            </button>
          </div>
        </div>

        <!-- Шаг 3: Подтверждение -->
        <div v-if="currentStep === 3" class="step-content">
          <h3>Подтверждение проекта</h3>
          <div class="project-summary">
            <div class="project-name-section">
              <label>Название проекта:</label>
              <input
                v-model="projectName"
                class="project-name-input"
                placeholder="Введите название..."
              />
            </div>
            <div class="summary-section">
              <h4>Структура производства:</h4>
              <div class="production-tree">
                <div class="tree-item main-target">
                  <span class="tree-icon">►</span>
                  {{ selectedTarget.name }} × {{ targetQuantity }}
                </div>
                <div class="tree-children">
                  <div
                    v-for="component in projectComponents.filter(
                      (c) => c.action === 'build'
                    )"
                    :key="'build-' + component.id"
                    class="tree-item build-item"
                  >
                    <span class="tree-icon">▶</span>
                    {{ component.name }} × {{ component.required }}
                  </div>
                </div>
              </div>
              <h4>Список покупок:</h4>
              <div class="shopping-list">
                <div
                  v-for="component in projectComponents.filter(
                    (c) => c.action === 'buy'
                  )"
                  :key="'buy-' + component.id"
                  class="shopping-item"
                >
                  <div class="shopping-item-main">
                    <span class="shop-icon">●</span>
                    {{ component.name }} × {{ component.required }}
                  </div>
                  <div class="shopping-method">
                    {{ getBuyMethodText(component.buyMethod) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="wizard-footer">
        <button
          v-if="currentStep > 1"
          @click="previousStep"
          class="wizard-button secondary"
        >
          ← Назад
        </button>
        <button
          v-if="currentStep < 3"
          @click="nextStep"
          :disabled="!canProceed"
          class="wizard-button primary"
        >
          Далее →
        </button>
        <button
          v-if="currentStep === 3"
          @click="createProject"
          :disabled="!projectName.trim()"
          class="wizard-button success"
        >
          Создать проект
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ProjectWizard",
  emits: ["close", "create-project"],
  data() {
    return {
      currentStep: 1,
      steps: [
        { title: "Выбор цели" },
        { title: "Компоненты" },
        { title: "Подтверждение" },
      ],
      targetSearch: "",
      selectedTarget: null,
      targetQuantity: 1,
      projectName: "",
      availableTargets: [
        { id: 1, name: "Tengu", category: "Strategic Cruiser", icon: "▶" },
        { id: 2, name: "Raven", category: "Battleship", icon: "■" },
        { id: 3, name: "Catalyst", category: "Destroyer", icon: "●" },
        { id: 4, name: "Rifter", category: "Frigate", icon: "○" },
      ],
      filteredTargets: [],
      projectComponents: [],
    };
  },
  computed: {
    canProceed() {
      switch (this.currentStep) {
        case 1:
          return this.selectedTarget && this.targetQuantity > 0;
        case 2:
          return this.projectComponents.every((c) => {
            if (c.action === "buy") {
              return c.action && c.buyMethod;
            }
            return c.action;
          });
        case 3:
          return this.projectName.trim().length > 0;
        default:
          return false;
      }
    },
  },
  mounted() {
    this.filteredTargets = [...this.availableTargets];
  },
  methods: {
    filterTargets() {
      const search = this.targetSearch.toLowerCase();
      this.filteredTargets = this.availableTargets.filter(
        (target) =>
          target.name.toLowerCase().includes(search) ||
          target.category.toLowerCase().includes(search)
      );
    },
    selectTarget(target) {
      this.selectedTarget = target;
      this.projectName = `Проект: ${target.name}`;
    },
    nextStep() {
      if (!this.canProceed) return;

      if (this.currentStep === 1) {
        this.generateComponents();
      }

      this.currentStep++;
    },
    previousStep() {
      if (this.currentStep > 1) {
        this.currentStep--;
      }
    },
    generateComponents() {
      // Моковые компоненты для демонстрации
      const mockComponents = {
        1: [
          // Tengu
          {
            id: 101,
            name: "Tengu Subsystem - Defensive",
            required: 1,
            icon: "□",
            action: null,
            buyMethod: null,
          },
          {
            id: 102,
            name: "Tengu Subsystem - Electronics",
            required: 1,
            icon: "△",
            action: null,
            buyMethod: null,
          },
          {
            id: 103,
            name: "Tengu Subsystem - Engineering",
            required: 1,
            icon: "▽",
            action: null,
            buyMethod: null,
          },
          {
            id: 104,
            name: "Tengu Subsystem - Offensive",
            required: 1,
            icon: "◇",
            action: null,
            buyMethod: null,
          },
          {
            id: 105,
            name: "R.A.M. - Ship Tech",
            required: 1,
            icon: "◆",
            action: null,
            buyMethod: null,
          },
        ],
        2: [
          // Raven
          {
            id: 201,
            name: "Raven Blueprint",
            required: 1,
            icon: "▦",
            action: null,
            buyMethod: null,
          },
          {
            id: 202,
            name: "Tritanium",
            required: 100000,
            icon: "▪",
            action: null,
            buyMethod: null,
          },
          {
            id: 203,
            name: "Pyerite",
            required: 50000,
            icon: "▫",
            action: null,
            buyMethod: null,
          },
        ],
      };

      this.projectComponents = (
        mockComponents[this.selectedTarget.id] || []
      ).map((component) => ({
        ...component,
        required: component.required * this.targetQuantity,
      }));
    },
    updateComponent(component) {
      // Устанавливаем метод покупки по умолчанию при выборе "Купить"
      if (component.action === "buy" && !component.buyMethod) {
        component.buyMethod = "sell_order";
      }
    },
    selectAllAction(action) {
      this.projectComponents.forEach((component) => {
        component.action = action;
        // Устанавливаем метод покупки по умолчанию
        if (action === "buy") {
          component.buyMethod = "sell_order";
        }
      });
    },
    createProject() {
      const project = {
        id: Date.now(),
        name: this.projectName,
        target: this.selectedTarget,
        quantity: this.targetQuantity,
        components: this.projectComponents,
        createdAt: new Date(),
        status: "planning",
      };

      this.$emit("create-project", project);
      this.$emit("close");
    },
    getBuyMethodText(buyMethod) {
      const methodTexts = {
        sell_order: "↗ Sell ордера",
        buy_order: "↙ Buy ордера",
      };
      return methodTexts[buyMethod] || "Не выбран";
    },
  },
};
</script>

<style scoped>
.wizard-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.wizard-container {
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  background-color: #2c2c2c;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.wizard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background-color: #21252b;
  border-bottom: 1px solid #3c4043;
}

.wizard-header h2 {
  margin: 0;
  color: #e6e6e6;
}

.wizard-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-indicator {
  display: flex;
  gap: 12px;
}

.step {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #3c4043;
  color: #abb2bf;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  transition: all 0.2s ease;
}

.step.active {
  background-color: #495057;
  color: white;
}

.step.completed {
  background-color: #6c757d;
  color: white;
}

.step-title {
  font-size: 14px;
  color: #abb2bf;
}

.close-button {
  background: none;
  border: none;
  color: #abb2bf;
  font-size: 24px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.close-button:hover {
  background-color: #3c4043;
  color: #e6e6e6;
}

.wizard-content {
  flex-grow: 1;
  padding: 24px;
  overflow-y: auto;
}

.step-content h3 {
  margin: 0 0 24px 0;
  color: #e6e6e6;
}

.search-container {
  margin-bottom: 16px;
}

.target-search {
  width: 100%;
  padding: 12px;
  background-color: #3c4043;
  border: 1px solid #4a4a4a;
  border-radius: 6px;
  color: #e6e6e6;
  font-size: 14px;
}

.target-search::placeholder {
  color: #abb2bf;
}

.target-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.target-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: #3c4043;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.target-item:hover {
  background-color: #4a4a4a;
}

.target-item.selected {
  background-color: #495057;
  color: white;
}

.item-icon {
  font-size: 24px;
  width: 40px;
  text-align: center;
}

.item-info {
  flex-grow: 1;
}

.item-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.item-category {
  font-size: 12px;
  opacity: 0.7;
}

.quantity-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background-color: #21252b;
  border-radius: 6px;
}

.quantity-section label {
  color: #e6e6e6;
  font-weight: 500;
}

.quantity-input {
  width: 80px;
  padding: 8px;
  background-color: #3c4043;
  border: 1px solid #4a4a4a;
  border-radius: 4px;
  color: #e6e6e6;
  text-align: center;
}

.target-info {
  background-color: #21252b;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 24px;
  color: #e6e6e6;
  text-align: center;
}

.components-list {
  margin-bottom: 24px;
}

.component-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #3c4043;
  border-radius: 6px;
  margin-bottom: 12px;
}

.component-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.component-icon {
  font-size: 20px;
  width: 32px;
  text-align: center;
}

.component-details {
  color: #e6e6e6;
}

.component-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.component-quantity {
  font-size: 12px;
  color: #abb2bf;
}

.component-actions {
  display: flex;
  gap: 16px;
}

.action-option {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #abb2bf;
}

.action-option input[type="radio"] {
  accent-color: #6c757d;
}

.action-label.build {
  color: #ced4da;
}

.action-label.buy {
  color: #adb5bd;
}

.buy-options {
  margin-top: 12px;
  padding: 12px;
  background-color: #21252b;
  border-radius: 6px;
  border-left: 3px solid #6c757d;
}

.buy-method-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #abb2bf;
  margin-bottom: 8px;
}

.buy-method-option:last-child {
  margin-bottom: 0;
}

.buy-method-option input[type="radio"] {
  accent-color: #6c757d;
}

.buy-method-label {
  font-size: 13px;
}

.buy-method-label.sell-order {
  color: #dc7633;
}

.buy-method-label.buy-order {
  color: #52c41a;
}

.mass-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.mass-button {
  padding: 10px 20px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.mass-button:hover {
  background-color: #5a6268;
}

.project-summary {
  color: #e6e6e6;
}

.project-name-section {
  margin-bottom: 24px;
}

.project-name-section label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.project-name-input {
  width: 100%;
  padding: 12px;
  background-color: #3c4043;
  border: 1px solid #4a4a4a;
  border-radius: 6px;
  color: #e6e6e6;
  font-size: 14px;
}

.summary-section h4 {
  margin: 20px 0 12px 0;
  color: #e6e6e6;
}

.production-tree,
.shopping-list {
  background-color: #21252b;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 16px;
}

.tree-item,
.shopping-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  color: #e6e6e6;
}

.tree-item.main-target {
  font-weight: 500;
  font-size: 16px;
  border-bottom: 1px solid #3c4043;
  margin-bottom: 8px;
  padding-bottom: 8px;
}

.tree-children {
  padding-left: 24px;
}

.tree-item.build-item {
  color: #ced4da;
}

.shopping-item {
  color: #adb5bd;
}

.shopping-item-main {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.shopping-method {
  font-size: 12px;
  color: #6c757d;
  margin-left: 24px;
  font-style: italic;
}

.tree-icon,
.shop-icon {
  font-size: 16px;
}

.wizard-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background-color: #21252b;
  border-top: 1px solid #3c4043;
}

.wizard-button {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.wizard-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.wizard-button.secondary {
  background-color: #3c4043;
  color: #abb2bf;
}

.wizard-button.secondary:hover:not(:disabled) {
  background-color: #4a4a4a;
}

.wizard-button.primary {
  background-color: #6c757d;
  color: white;
}

.wizard-button.primary:hover:not(:disabled) {
  background-color: #5a6268;
}

.wizard-button.success {
  background-color: #495057;
  color: white;
}

.wizard-button.success:hover:not(:disabled) {
  background-color: #343a40;
}
</style>
