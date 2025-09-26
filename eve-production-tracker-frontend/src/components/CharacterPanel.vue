<template>
  <div class="character-panel">
    <div class="panel-header-controls">
      <h2 class="panel-title">Characters</h2>
      <button
        @click="$emit('add-character')"
        class="add-character-btn"
        title="Добавить персонажа"
      >
        <span class="add-char-icon">+</span>
        <span class="add-char-text">Add Character</span>
      </button>
    </div>
    <div class="characters-list" ref="charactersList">
      <div
        v-for="char in characters"
        :key="char.character_id"
        class="character-card"
        :class="{ 'is-active': selectedCharacterId === char.character_id }"
        @click="$emit('select-character', char.character_id)"
      >
        <div class="card-left">
          <img
            :src="getCharacterPortrait(char.character_id)"
            :alt="char.character_name"
            class="character-portrait"
          />
        </div>
        <div class="card-right">
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
          <div v-if="activities[char.character_id]" class="activity-grid">
            <div class="info-line" title="MAnufacturing">
              <img src="/icons/manufacturing.svg" class="activity-icon" /><span
                >{{ activities[char.character_id].lines.manufacturing.used }}/{{
                  activities[char.character_id].lines.manufacturing.total
                }}</span
              >
            </div>
            <div class="info-line" title="Research">
              <img src="/icons/research.svg" class="activity-icon" /><span
                >{{ activities[char.character_id].lines.research.used }}/{{
                  activities[char.character_id].lines.research.total
                }}</span
              >
            </div>
            <div class="info-line" title="Reaction">
              <img src="/icons/reactions.svg" class="activity-icon" /><span
                >{{ activities[char.character_id].lines.reactions.used }}/{{
                  activities[char.character_id].lines.reactions.total
                }}</span
              >
            </div>
            <div class="info-line" title="Planets">
              <img src="/icons/planets.svg" class="activity-icon" /><span
                >{{ activities[char.character_id].planets.used }}/{{
                  activities[char.character_id].planets.total
                }}</span
              >
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: "CharacterPanel",
  props: ["characters", "activities", "selectedCharacterId"],
  inject: ["eventBus"],
  emits: ["add-character", "remove-character", "select-character"],
  watch: {
    "eventBus.scroll": "handleExternalScroll",
  },
  methods: {
    getCharacterPortrait(characterId) {
      return `https://images.evetech.net/characters/${characterId}/portrait?size=128`;
    },
    handleExternalScroll(scrollData) {
      if (scrollData.source === "character-panel") return;
      const el = this.$refs.charactersList;
      if (el) el.scrollTop = scrollData.scrollTop;
    },
  },
};
</script>
<style scoped>
.character-panel {
  width: 350px;
  min-width: 350px;
  background-color: #20232a;
  padding: 20px 15px;
  border-right: 1px solid #3c414d;
  box-sizing: border-box;
  overflow: hidden;
  height: 100%;
}
.panel-header-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 15px 15px;
  background-color: #20232a;
  position: sticky;
  top: 0;
  z-index: 10;
  border-bottom: 1px solid #3c414d;
  margin: -20px -15px 20px;
}

.panel-title {
  margin: 0;
  color: #e0e0e0;
  font-weight: 300;
  font-size: 18px;
}
.characters-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  height: calc(100% - 95px); /* Увеличиваем высоту, так как убрали кнопку */
  overflow-y: scroll;
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
  padding-bottom: 20px; /* Уменьшаем отступ снизу */
}
.characters-list::-webkit-scrollbar {
  display: none;
}
.character-card {
  display: flex;
  background-color: #282c34;
  padding: 10px;
  border-radius: 8px;
  border: 2px solid #3c414d;
  cursor: pointer;
  transition: all 0.2s;
  height: 120px;
  min-height: 120px;
  max-height: 120px;
  box-sizing: border-box;
}
.character-card:hover {
  border-color: #61afef;
}
.character-card.is-active {
  border-color: #c678dd;
}
.card-left {
  width: 33.33%;
  flex-shrink: 0;
  padding-right: 10px;
}
.character-portrait {
  width: 100%;
  height: auto;
  border-radius: 8px;
}
.card-right {
  width: 66.66%;
  display: flex;
  flex-direction: column;
}
.name-block {
  position: relative;
  margin-bottom: 8px;
}
.character-name {
  font-size: 16px;
  font-weight: bold;
  color: #e0e0e0;
}
.remove-char-btn {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #444;
  color: #aaa;
  border: none;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  font-size: 18px;
  line-height: 22px;
  cursor: pointer;
  opacity: 0.3;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}
.character-card:hover .remove-char-btn {
  opacity: 1;
}
.remove-char-btn:hover {
  color: #fff;
  background-color: #ff6b6b;
}
.activity-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  width: 100%;
}
.info-line {
  display: flex;
  align-items: center;
  background-color: #20232a;
  padding: 5px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.activity-icon {
  width: 18px;
  height: 18px;
  margin-right: 8px;
  filter: invert(80%) sepia(10%) saturate(200%) hue-rotate(180deg)
    brightness(90%) contrast(90%);
}
.info-line span {
  color: #abb2bf;
}
.add-character-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #4e9aef;
  color: white;
  border: 2px solid transparent;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.add-character-btn:hover {
  background-color: #3a7bc8;
  transform: translateY(-1px);
  box-shadow: 0 3px 6px rgba(78, 154, 239, 0.3);
}

.add-character-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 3px rgba(78, 154, 239, 0.3);
}

.add-char-icon {
  font-size: 16px;
  font-weight: bold;
  line-height: 1;
}

.add-char-text {
  font-size: 14px;
}

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
  .panel-header-controls {
    padding: 15px 10px 10px;
    margin: -20px -15px 15px;
  }

  .add-character-btn {
    padding: 6px 12px;
    font-size: 12px;
  }

  .add-char-text {
    display: none; /* Скрываем текст на мобильных, оставляем только иконку */
  }

  .add-char-icon {
    font-size: 18px;
  }
}

@media (max-width: 480px) {
  .panel-header-controls {
    padding: 12px 8px 8px;
    margin: -20px -15px 12px;
  }

  .panel-title {
    font-size: 16px;
  }

  .add-character-btn {
    padding: 8px;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    justify-content: center;
  }
}
</style>
