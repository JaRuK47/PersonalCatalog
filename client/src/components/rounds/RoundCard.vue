<script setup>
defineProps({
  round: Object,
  hostName: String,
  gameModeName: String,
  isManager: Boolean
})

defineEmits(['view', 'edit', 'remove'])
</script>

<template>
  <div class="card shadow-sm h-100 border-primary">
    <div class="card-body text-center d-flex flex-column">
      <h5 class="card-title">Партия #{{ round.number }}</h5>
      <p class="card-text small mb-1">Режим: <b>{{ gameModeName }}</b></p>
      <p class="card-text text-muted small mb-3">Ведущий: {{ hostName }}</p>

      <button class="btn btn-sm btn-outline-primary mt-auto" @click="$emit('view', round)">
        Статистика
      </button>

      <div v-if="isManager" class="mt-2 d-flex justify-content-between">
        <button class="btn btn-sm btn-success w-50 me-1" @click="$emit('edit', round)">Ред.</button>
        <button class="btn btn-sm btn-danger w-50" @click="$emit('remove', round)">Удал.</button>
      </div>
    </div>
  </div>
</template>