<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  booking: Object
})

const emit = defineEmits(['save', 'close'])

const formData = ref({})

watch(() => props.booking, (newVal) => {
  formData.value = { ...newVal }
}, { immediate: true })

function onSave() {
  emit('save', formData.value)
}
</script>

<template>
  <div class="modal fade show d-block" style="background: rgba(0,0,0,0.5);" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать бронь</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <label class="form-label small mb-0">Статус брони:</label>
          <select v-model="formData.status" class="form-select mb-2">
            <option value="active">Активно (Ждем)</option>
            <option value="attended">Явился</option>
            <option value="no_show">Неявка</option>
            <option value="cancelled">Отменено</option>
          </select>

          <label class="form-label small mb-0">Время ухода:</label>
          <input v-model="formData.leave_time" type="time" class="form-control" />
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="$emit('close')">Отмена</button>
          <button class="btn btn-primary" @click="onSave">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>