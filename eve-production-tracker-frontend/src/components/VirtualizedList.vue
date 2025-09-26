<template>
  <div class="virtualized-list" ref="container" @scroll="handleScroll">
    <div class="virtualized-content" :style="{ height: totalHeight + 'px' }">
      <div
        class="virtualized-items"
        :style="{ transform: `translateY(${offsetY}px)` }"
      >
        <div
          v-for="(item, index) in visibleItems"
          :key="getItemKey(item, startIndex + index)"
          :style="{ height: itemHeight + 'px' }"
          class="virtualized-item"
        >
          <slot
            :item="item"
            :index="startIndex + index"
            :isVisible="true"
          ></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "VirtualizedList",
  props: {
    items: {
      type: Array,
      required: true,
    },
    itemHeight: {
      type: Number,
      default: 120,
    },
    overscan: {
      type: Number,
      default: 5,
    },
    getItemKey: {
      type: Function,
      default: (item, index) => index,
    },
  },
  data() {
    return {
      scrollTop: 0,
      containerHeight: 0,
      _scrollTimeout: null,
    };
  },
  computed: {
    totalHeight() {
      return this.items.length * this.itemHeight;
    },
    startIndex() {
      return Math.max(
        0,
        Math.floor(this.scrollTop / this.itemHeight) - this.overscan
      );
    },
    endIndex() {
      const visibleCount = Math.ceil(this.containerHeight / this.itemHeight);
      return Math.min(
        this.items.length - 1,
        this.startIndex + visibleCount + this.overscan * 2
      );
    },
    visibleItems() {
      return this.items.slice(this.startIndex, this.endIndex + 1);
    },
    offsetY() {
      return this.startIndex * this.itemHeight;
    },
  },
  methods: {
    handleScroll(event) {
      // Debounce обработки прокрутки
      if (this._scrollTimeout) {
        clearTimeout(this._scrollTimeout);
      }

      this._scrollTimeout = setTimeout(() => {
        this.scrollTop = event.target.scrollTop;
      }, 16); // ~60fps
    },
    updateContainerHeight() {
      if (this.$refs.container) {
        this.containerHeight = this.$refs.container.clientHeight;
      }
    },
  },
  mounted() {
    this.updateContainerHeight();
    window.addEventListener("resize", this.updateContainerHeight);
  },
  beforeUnmount() {
    if (this._scrollTimeout) {
      clearTimeout(this._scrollTimeout);
    }
    window.removeEventListener("resize", this.updateContainerHeight);
  },
};
</script>

<style scoped>
.virtualized-list {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  /* Скрываем скроллбар для всех браузеров */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* Internet Explorer 10+ */
}

.virtualized-list::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.virtualized-content {
  position: relative;
}

.virtualized-items {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
}

.virtualized-item {
  display: block;
  width: 100%;
  box-sizing: border-box;
}
</style>
