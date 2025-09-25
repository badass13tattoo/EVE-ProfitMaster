<template>
  <div class="character-panel">
    <h2 class="panel-title">Персонажи</h2>
    <div class.characters-list>
      <div
        v-for="char in characters"
        :key="char.character_id"
        class="character-card"
        :class="{ 'is-active': selectedCharacterId === char.character_id }"
        @click="$emit('select-character', char.character_id)"
      >
        <div class="card-main-info">
          <img
            :src="getCharacterPortrait(char.character_id)"
            :alt="char.character_name"
            class="character-portrait"
          />
          <div class="name-block">
            <span class="character-name">{{ char.character_name }}</span>
            <button
              @click.stop="$emit('remove-character', char.character_id)"
              class="remove-char-btn"
              title="Удалить персонажа"
            >
              ×
            </button>
          </div>
        </div>
        <div v-if="activities[char.character_id]" class="activity-grid">
          <div class="info-line" title="Производство">
            🏭
            <span
              >{{ activities[char.character_id].lines.manufacturing.used }} /
              {{
                activities[char.character_id].lines.manufacturing.total
              }}</span
            >
          </div>
          <div class="info-line" title="Исследования">
            🔬
            <span
              >{{ activities[char.character_id].lines.research.used }} /
              {{ activities[char.character_id].lines.research.total }}</span
            >
          </div>
          <div class="info-line" title="Реакции">
            💠
            <span
              >{{ activities[char.character_id].reactions.used }} /
              {{ activities[char.character_id].reactions.total }}</span
            >
          </div>
          <div class="info-line" title="Планеты">
            🪐
            <span
              >{{ activities[char.character_id].planets.used }} /
              {{ activities[char.character_id].planets.total }}</span
            >
          </div>
        </div>
        <div v-else class="activity-grid">
          <small>Загрузка...</small>
        </div>
      </div>
      <div @click="$emit('add-character')" class="add-char-card">
        <div class="add-char-icon">+</div>
        <span class="character-name">Добавить персонажа</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "CharacterPanel",
  props: ["characters", "activities", "selectedCharacterId"],
  emits: ["add-character", "remove-character", "select-character"],
  methods: {
    getCharacterPortrait(characterId) {
      return `https://images.evetech.net/characters/${characterId}/portrait?size=64`;
    },
  },
};
</script>

<style scoped>
.character-panel {
  width: 320px;
  min-width: 320px;
  background-color: #252525;
  padding: 20px;
  height: 100vh;
  overflow-y: auto;
  border-right: 1px solid #444;
  box-sizing: border-box;
}
.panel-title {
  text-align: center;
  margin-top: 0;
  margin-bottom: 20px;
  color: #ddd;
}
.characters-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.character-card,
.add-char-card {
  display: flex;
  flex-direction: column;
  color: inherit;
  position: relative;
  background-color: #2c2c2c;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #444;
  cursor: pointer;
  transition: all 0.2s;
}
.character-card.is-active {
  border-color: #4e9aef;
  background-color: #3a4a5f;
}
.add-char-card {
  flex-direction: row;
  align-items: center;
  justify-content: center;
  border-style: dashed;
  color: #888;
}
.add-char-card:hover {
  background-color: #333;
  border-color: #777;
  color: #fff;
}
.add-char-icon {
  font-size: 24px;
  margin-right: 10px;
}
.card-main-info {
  display: flex;
  align-items: center;
  width: 100%;
}
.character-portrait {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  margin-right: 15px;
}
.name-block {
  flex-grow: 1;
  position: relative;
}
.character-name {
  font-size: 16px;
  font-weight: bold;
  color: #fff;
}
.remove-char-btn {
  position: absolute;
  top: -5px;
  right: -5px;
  background: transparent;
  color: #888;
  border: none;
  width: 24px;
  height: 24px;
  font-size: 20px;
  line-height: 24px;
  cursor: pointer;
  opacity: 0.3;
  transition: all 0.2s;
}
.character-card:hover .remove-char-btn {
  opacity: 1;
}
.remove-char-btn:hover {
  color: #ff6b6b;
}
.activity-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  width: 100%;
  margin-top: 15px;
  font-size: 14px;
  color: #aaa;
}
.info-line {
  display: flex;
  justify-content: space-between;
  background-color: #252525;
  padding: 4px 8px;
  border-radius: 4px;
}
.info-line span {
  font-weight: bold;
  color: #fff;
}
</style>
