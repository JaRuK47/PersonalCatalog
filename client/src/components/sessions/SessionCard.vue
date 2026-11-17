<script setup>
defineProps({
  session: Object,
  venueName: String,
  gameModeName: String,
  isBooked: Boolean
})

defineEmits(['book', 'open-image'])
</script>

<template>
  <div class="card shadow-sm h-100" :class="{'border-danger border-2': session.is_cancelled}">
    <img
      v-if="session.picture" 
      :src="session.picture"
      class="card-img-top"
      style="height: 300px; object-fit: cover; cursor: pointer;"
      @click="$emit('open-image', session.picture)"
    />
    <div class="card-body">
      <h4 class="card-title">
        {{ session.title }}
        <span v-if="session.is_cancelled" class="badge bg-danger fs-6">Отменена</span>
      </h4>
      <h6 class="card-subtitle mb-2 text-primary">{{ gameModeName }}</h6>
      <p class="card-text text-muted mb-1"><b>{{ session.date }}</b> в {{ session.start_time }}</p>
      <p class="card-text mb-2">{{ venueName }}</p>
      <p class="card-text small">{{ session.description }}</p>
      <hr>
      <p>Статус: <b>{{ session.status }}</b></p>
      <button
        v-if="!session.is_cancelled"
        class="btn w-100"
        :class="isBooked ? 'btn-outline-danger' : 'btn-primary'"
        @click="$emit('book', session)"
      >
        {{ isBooked ? 'Вы записаны (Управление)' : 'Забронировать' }}
      </button>
    </div>
  </div>
</template>