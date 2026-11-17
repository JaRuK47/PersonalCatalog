<script setup>
defineProps({
  url: String
})
defineEmits(['close'])
</script>

<template>
  <div class="modal fade show d-block" style="background: rgba(0,0,0,0.8);" tabindex="-1" @click.self="$emit('close')">
    <div class="modal-dialog modal-lg modal-dialog-centered">
      <div class="modal-content bg-transparent border-0">
        <div class="modal-body text-center p-0 position-relative">
          <button type="button" class="btn-close btn-close-white position-absolute top-0 end-0 m-3" @click="$emit('close')" style="z-index: 1055;"></button>
          <img :src="url" class="img-fluid rounded shadow-lg" />
        </div>
      </div>
    </div>
  </div>
</template>