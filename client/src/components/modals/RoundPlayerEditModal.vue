<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  player: Object
})

const emit = defineEmits(['save', 'close'])

const formData = ref({})

watch(() => props.player, (newVal) => {
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
          <h5 class="modal-title">Редактировать игрока</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <label class="form-label small mb-0">Роль</label>
          <select v-model="formData.role" class="form-select mb-2">
            <option value="Мирный">Мирный</option>
            <option value="Мафия">Мафия</option>
            <option value="Дон">Дон</option>
            <option value="Шериф">Шериф</option>
            <option value="Доктор">Доктор</option>
          </select>

          <label class="form-label small mb-0">Очки</label>
          <input v-model.number="formData.points" type="number" step="0.1" class="form-control mb-2" />

          <label class="form-label small mb-0">Описание (за что баллы)</label>
          <textarea v-model="formData.description" class="form-control mb-2"></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="$emit('close')">Отмена</button>
          <button class="btn btn-primary" @click="onSave">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>