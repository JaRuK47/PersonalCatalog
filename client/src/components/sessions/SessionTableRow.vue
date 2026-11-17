<script setup>
defineProps({
  session: Object,
  venueName: String,
  gameModeName: String,
  isPast: Boolean
})

defineEmits(['edit', 'cancel', 'remove', 'open-image'])
</script>

<template>
  <tr :class="{'table-danger': session.is_cancelled}">
    <td>
      <div v-show="session.picture">
        <img
          :src="session.picture"
          style="width: 80px; height: 50px; object-fit: cover; border-radius: 5px; cursor: pointer;"
          @click="$emit('open-image', session.picture)"
        />
      </div>
    </td>
    <td>{{ session.date }} в {{ session.start_time }}</td>
    <td><b>{{ session.title }}</b> <br><small class="text-muted">{{ gameModeName }}</small></td>
    <td>{{ venueName }}</td>
    <td>
      <span class="badge" :class="{
        'bg-danger': session.status === 'Отменена',
        'bg-success': session.status === 'Идёт набор',
        'bg-warning text-dark': session.status === 'Активно',
        'bg-secondary': session.status === 'Завершена'
      }">{{ session.status }}</span>
    </td>
    <td>
      <button class="btn btn-sm btn-success me-1" @click="$emit('edit', session)">Ред.</button>
      <button v-if="!session.is_cancelled && !isPast" class="btn btn-sm btn-warning me-1" @click="$emit('cancel', session)">Отменить</button>
      <button class="btn btn-sm btn-danger" @click="$emit('remove', session)">Удалить</button>
    </td>
  </tr>
</template>