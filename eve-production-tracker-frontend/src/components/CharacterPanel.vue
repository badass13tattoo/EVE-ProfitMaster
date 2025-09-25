<template>
  <div class="character-panel">
    <h2 class="panel-title">Персонажи</h2>
    <div class="characters-list">
      <div
        v-for="char in characters"
        :key="char.character_id"
        class="character-card"
        :class="{ 'is-active': selectedCharacterId === char.character_id }"
        @click="$emit('select-character', char.character_id)"
      >
        <button
          @click.stop="$emit('remove-character', char.character_id)"
          class="remove-char-btn"
          title="Удалить персонажа"
        >
          ×
        </button>
        <img
          :src="getCharacterPortrait(char.character_id)"
          :alt="char.character_name"
          class="character-portrait"
        />
        <span class="character-name">{{ char.character_name }}</span>
        <div v-if="activities[char.character_id]" class="activity-info">
          <div class="info-line" title="Производство">
            🏭 {{ activities[char.character_id].lines.manufacturing.used }} /
            {{ activities[char.character_id].lines.manufacturing.total }}
          </div>
          <div class="info-line" title="Исследования">
            🔬 {{ activities[char.character_id].lines.research.used }} /
            {{ activities[char.character_id].lines.research.total }}
          </div>
          <div class="info-line" title="Планеты">
            🪐 {{ activities[char.character_id].planets.used }} /
            {{ activities[char.character_id].planets.total }}
          </div>
        </div>
        <div v-else class="activity-info">
          <small>Загрузка...</small>
        </div>
      </div>
      <div @click="$emit('add-character')" class="add-char-card">
        <div class="add-char-icon">+</div>
        <span class="character-name">Добавить</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "CharacterPanel",
  props: {
    characters: Array,
    activities: Object,
    selectedCharacterId: Number,
  },
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
  width: 280px;
  min-width: 280px;
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
  align-items: center;
  text-decoration: none;
  color: inherit;
  position: relative;
  background-color: #2c2c2c;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #444;
  cursor: pointer;
  transition: border-color 0.2s, background-color 0.2s;
}
.character-card.is-active {
  border-color: #4e9aef;
  background-color: #3a4a5f;
}
.add-char-card {
  border-style: dashed;
}
.add-char-card:hover {
  background-color: #333;
  border-color: #777;
}
.add-char-icon {
  font-size: 32px;
  color: #777;
}
.character-portrait {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 2px solid #555;
  margin-bottom: 10px;
}
.character-name {
  font-size: 16px;
  font-weight: bold;
  word-break: break-word;
  color: #fff;
}
.remove-char-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: transparent;
  color: #888;
  border: none;
  width: 24px;
  height: 24px;
  font-size: 20px;
  line-height: 24px;
  cursor: pointer;
  opacity: 0.3;
  transition: opacity 0.2s, color 0.2s;
}
.character-card:hover .remove-char-btn {
  opacity: 1;
}
.remove-char-btn:hover {
  color: #ff6b6b;
}
.activity-info {
  font-size: 14px;
  margin-top: 10px;
  color: #aaa;
  width: 100%;
}
.info-line {
  display: flex;
  justify-content: space-between;
  padding: 2px 5px;
}
</style>
