<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h2>Добавить новую работу</h2>
      <form @submit.prevent="submitJob">
        <div class="form-group">
          <label for="character">Персонаж</label>
          <select id="character" v-model="job.character_id" required>
            <option
              v-for="char in characters"
              :key="char.character_id"
              :value="char.character_id"
            >
              {{ char.character_name }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label for="productName">Название продукта</label>
          <input
            type="text"
            id="productName"
            v-model="job.product_name"
            required
          />
        </div>
        <div class="form-group">
          <label for="activity">Тип работы</label>
          <select id="activity" v-model="job.activity_id" required>
            <option value="1">Производство</option>
            <option value="3">Копирование</option>
            <option value="4">Мат. эффективность</option>
            <option value="5">Врем. эффективность</option>
            <option value="6">Реакции</option>
            <option value="8">Изобретение</option>
          </select>
        </div>
        <div class="form-group">
          <label for="duration">Длительность (в часах)</label>
          <input
            type="number"
            id="duration"
            v-model.number="durationHours"
            min="1"
            required
          />
        </div>
        <div class="form-actions">
          <button type="button" @click="$emit('close')">Отмена</button>
          <button type="submit">Добавить</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: "AddJobModal",
  props: ["characters"],
  emits: ["close", "add-job"],
  data() {
    return {
      job: {
        character_id: this.characters[0]?.character_id || null,
        product_name: "",
        activity_id: 1,
      },
      durationHours: 24,
    };
  },
  methods: {
    submitJob() {
      const now = new Date();
      const newJob = {
        ...this.job,
        job_id: Date.now(),
        start_date: now,
        end_date: new Date(now.getTime() + this.durationHours * 3600 * 1000),
        status: "in-progress",
        location_name: "Не указана",
      };
      this.$emit("add-job", newJob);
      this.$emit("close");
    },
  },
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
}
.modal-content {
  background-color: #2c3e50;
  padding: 30px;
  border-radius: 10px;
  width: 400px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
}
h2 {
  margin-top: 0;
  color: #ecf0f1;
  text-align: center;
}
.form-group {
  margin-bottom: 20px;
}
label {
  display: block;
  margin-bottom: 8px;
  color: #bdc3c7;
}
input,
select {
  width: 100%;
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #34495e;
  background-color: #34495e;
  color: #ecf0f1;
  box-sizing: border-box;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
}
button {
  padding: 10px 20px;
  border-radius: 5px;
  border: none;
  cursor: pointer;
  font-weight: bold;
}
button[type="submit"] {
  background-color: #27ae60;
  color: white;
}
button[type="button"] {
  background-color: #c0392b;
  color: white;
}
</style>