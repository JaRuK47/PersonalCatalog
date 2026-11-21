<script setup>
defineProps({
  booking: Object,
  sessionInfo: String,
  isCancelled: Boolean
})

defineEmits(['edit', 'remove'])
</script>

<template>
  <tr>
    <td>{{ booking.user_name }}</td>
    <td>
      {{ sessionInfo }}
      <span v-if="isCancelled" class="badge bg-danger ms-2">Игра отменена</span>
    </td>
    <td>{{ booking.leave_time || '—' }}</td>
    <td>{{ booking.status_display }}</td>
    <td>
      <button class="btn btn-sm btn-success me-1" @click="$emit('edit', booking)">Ред.</button>
      <button class="btn btn-sm btn-danger" @click="$emit('remove', booking)">Удал.</button>
    </td>
  </tr>
</template>