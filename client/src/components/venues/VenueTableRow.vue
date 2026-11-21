<script setup>
defineProps({
  venue: Object
})

defineEmits(['edit', 'remove', 'open-image'])
</script>

<template>
  <tr>
    <td>
      <div v-show="venue.picture">
        <img
          :src="venue.picture"
          style="max-height: 50px; cursor: pointer; border-radius: 5px;"
          @click="$emit('open-image', venue.picture)"
        />
      </div>
    </td>
    <td>{{ venue.name }}</td>
    <td>{{ venue.address }}</td>
    <td>{{ venue.capacity }}</td>
    <td>{{ venue.description }}</td>
    <td>
      <button class="btn btn-sm btn-success me-1" @click="$emit('edit', venue)">Ред.</button>
      <button class="btn btn-sm btn-danger" @click="$emit('remove', venue)">Удал.</button>
    </td>
  </tr>
</template>