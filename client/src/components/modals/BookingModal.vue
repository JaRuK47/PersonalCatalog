<script setup>
defineProps({
  session: Object,
  bookedUsers: Array,
  isBookedByMe: Boolean,
  venueName: String,
  gameModeName: String
})

defineEmits(['close', 'book', 'cancel'])
</script>

<template>
  <div class="modal fade show d-block" style="background: rgba(0,0,0,0.6);" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-centered">
      <div class="modal-content" v-if="session">
        <div class="modal-header">
          <h5 class="modal-title">{{ session.title }} | {{ session.date }}</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <h6>Режим:</h6> <p>{{ gameModeName }}</p>
            <h6>Описание:</h6> <p>{{ session.description }}</p>
            <h6>Локация:</h6> <p>{{ venueName }}</p>
          </div>
          <h5 class="mt-4 border-top pt-3">Список игроков ({{ bookedUsers.length }}):</h5>
          <ul class="list-group">
            <li class="list-group-item" v-for="(uname, idx) in bookedUsers" :key="idx">{{ uname }}</li>
            <li class="list-group-item text-muted" v-if="bookedUsers.length === 0">Пока никого нет</li>
          </ul>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="$emit('close')">Закрыть</button>
          <button v-if="!isBookedByMe" class="btn btn-success" @click="$emit('book')">Забронировать</button>
          <button v-else class="btn btn-danger" @click="$emit('cancel')">Отменить мою бронь</button>
        </div>
      </div>
    </div>
  </div>
</template>