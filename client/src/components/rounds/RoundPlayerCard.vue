<script setup>
defineProps({
  player: Object,
  userName: String,
  isManager: Boolean,
  winStatus: Boolean
})

defineEmits(['edit', 'remove'])
</script>

<template>
  <div class="card mb-2 shadow-sm" :class="{'border-success': winStatus === true, 'border-danger': winStatus === false}">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <h5 class="mb-0">{{ userName }}</h5>
          <small class="text-muted">Роль: {{ player.role }}</small>
          <p class="mb-0 mt-1 small">{{ player.description }}</p>
        </div>
        <div class="text-end">
          <span class="badge bg-primary fs-6">{{ player.points }} очков</span>

          <span v-if="winStatus === true" class="badge bg-success ms-2">Победа</span>
          <span v-if="winStatus === false" class="badge bg-secondary ms-2">Проигрыш</span>
          <span v-if="winStatus === null" class="badge bg-warning text-dark ms-2">Не определено</span>

          <div v-if="isManager" class="mt-2">
            <button class="btn btn-sm btn-success me-1" @click="$emit('edit', player)">Ред.</button>
            <button class="btn btn-sm btn-danger" @click="$emit('remove', player.id)">Удал.</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>