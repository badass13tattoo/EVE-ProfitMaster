<template>
  <div
    class="lazy-image-container"
    :style="{ width: width + 'px', height: height + 'px' }"
  >
    <img
      v-if="loaded"
      :src="src"
      :alt="alt"
      :style="{ width: width + 'px', height: height + 'px' }"
      class="lazy-image-loaded"
      @load="onLoad"
      @error="onError"
    />
    <div
      v-else
      class="lazy-image-placeholder"
      :style="{ width: width + 'px', height: height + 'px' }"
    >
      <div class="loading-spinner" v-if="!error"></div>
      <div class="error-placeholder" v-else>?</div>
    </div>
  </div>
</template>

<script>
export default {
  name: "LazyImage",
  props: {
    src: {
      type: String,
      required: true,
    },
    alt: {
      type: String,
      default: "",
    },
    width: {
      type: Number,
      default: 128,
    },
    height: {
      type: Number,
      default: 128,
    },
    rootMargin: {
      type: String,
      default: "50px",
    },
  },
  data() {
    return {
      loaded: false,
      error: false,
      observer: null,
    };
  },
  mounted() {
    this.setupIntersectionObserver();
  },
  beforeUnmount() {
    if (this.observer) {
      this.observer.disconnect();
    }
  },
  methods: {
    setupIntersectionObserver() {
      if (!window.IntersectionObserver) {
        // Fallback для старых браузеров
        this.loadImage();
        return;
      }

      this.observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              this.loadImage();
              this.observer.disconnect();
            }
          });
        },
        {
          rootMargin: this.rootMargin,
        }
      );

      this.observer.observe(this.$el);
    },
    loadImage() {
      const img = new Image();
      img.onload = () => {
        this.loaded = true;
        this.error = false;
      };
      img.onerror = () => {
        this.error = true;
        this.loaded = false;
      };
      img.src = this.src;
    },
    onLoad() {
      this.loaded = true;
      this.error = false;
    },
    onError() {
      this.error = true;
      this.loaded = false;
    },
  },
};
</script>

<style scoped>
.lazy-image-container {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2c2c2c;
  border-radius: 8px;
  overflow: hidden;
}

.lazy-image-loaded {
  object-fit: cover;
  border-radius: 8px;
}

.lazy-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2c2c2c;
  border-radius: 8px;
  color: #666;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #444;
  border-top: 2px solid #61afef;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error-placeholder {
  font-size: 24px;
  color: #666;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
