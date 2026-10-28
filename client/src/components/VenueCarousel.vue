<script setup>
import { ref } from 'vue';

const props = defineProps({ venues: Array });
const emit = defineEmits(['open']);

const activeIndex = ref(0);

const prev = () => {
  activeIndex.value = (activeIndex.value - 1 + props.venues.length) % props.venues.length;
};

const next = () => {
  activeIndex.value = (activeIndex.value + 1) % props.venues.length;
};

const getPositionClass = (index) => {
  const total = props.venues.length;
  if (index === activeIndex.value) return 'active';
  if (index === (activeIndex.value - 1 + total) % total) return 'left';
  if (index === (activeIndex.value + 1) % total) return 'right';
  return 'hidden';
};
</script>

<template>
  <div class="venue-carousel-container">
    <h1 class="text-center display-4 mb-5 fw-bold text-dark">Наши локации</h1>

    <div class="carousel-track-container">
      <div
        v-for="(v, index) in venues"
        :key="v.id"
        class="carousel-card"
        :class="getPositionClass(index)"
      >
        <div class="card venue-card shadow-lg" @click="index === activeIndex ? emit('open', v) : activeIndex = index">
          <div class="photo-placeholder bg-secondary d-flex align-items-center justify-content-center">
            <img v-if="v.picture" :src="v.picture" class="carousel-img" />
            <span v-else class="text-white fs-4">Фото скоро</span>
          </div>
          <div class="text-box p-4">
            <h3 class="fw-bold mb-3">{{ v.name }}</h3>
            <p class="text-muted small mb-3">{{ v.address }}</p>
            <p class="mb-0 fs-5">{{ v.description }}</p>
          </div>
        </div>
      </div>

      <button class="carousel-btn prev" @click="prev">&#10094;</button>
      <button class="carousel-btn next" @click="next">&#10095;</button>
    </div>
  </div>
</template>

<style scoped>
.venue-carousel-container {
  width: 100%;
  overflow: hidden;
  padding-bottom: 50px;
}
.carousel-track-container {
  position: relative;
  height: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.carousel-card {
  position: absolute;
  width: 400px;
  transition: all 0.5s ease-in-out;
  cursor: pointer;
  opacity: 0;
  pointer-events: none;
  z-index: 1;
  filter: brightness(0.5);
}
.carousel-card.active {
  transform: translateX(0) scale(1);
  opacity: 1;
  pointer-events: auto;
  z-index: 3;
  filter: brightness(1);
}
.carousel-card.left {
  transform: translateX(-110%) scale(0.85);
  opacity: 0.7;
  pointer-events: auto;
  z-index: 2;
}
.carousel-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.carousel-card.right {
  transform: translateX(110%) scale(0.85);
  opacity: 0.7;
  pointer-events: auto;
  z-index: 2;
}
.carousel-card.hidden {
  transform: translateX(0) scale(0.5);
}
.venue-card {
  height: 100%;
  border: none;
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.photo-placeholder {
  height: 250px;
  width: 100%;
}
.text-box {
  background: white;
  border-radius: 20px 20px 0 0;
  margin-top: -20px;
  z-index: 1;
  flex-grow: 1;
}
.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  font-size: 30px;
  padding: 10px 20px;
  border-radius: 50%;
  z-index: 10;
  cursor: pointer;
  transition: background 0.3s;
}
.carousel-btn:hover { background: rgba(0, 0, 0, 0.8); }
.carousel-btn.prev { left: 10%; }
.carousel-btn.next { right: 10%; }
</style>