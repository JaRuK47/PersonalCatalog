<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  round: Object,
  sessions: Array,
  users: Array,
  gameModes: Array
})

const emit = defineEmits(['save', 'close'])

const formData = ref({})

watch(() => props.round, (newVal) => {
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
          <h5 class="modal-title">Редактировать партию</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <label class="form-label small mb-0">Сессия</label>
          <select v-model.number="formData.session" class="form-select mb-2">
            <option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.date }} ({{ s.title }})</option>
          </select>

          <label class="form-label small mb-0">Номер партии</label>
          <input v-model.number="formData.number" type="number" class="form-control mb-2" />

          <label class="form-label small mb-0">Ведущий</label>
          <select v-model.number="formData.host" class="form-select mb-2">
            <option :value="null">Без ведущего</option>
            <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
          </select>

          <label class="form-label small mb-0">Режим игры</label>
          <select v-model.number="formData.game_mode" class="form-select mb-2">
            <option v-for="g in gameModes" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>

          <label class="form-label small mb-0">Описание</label>
          <textarea v-model="formData.description" class="form-control" placeholder="Описание"></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="$emit('close')">Отмена</button>
          <button class="btn btn-primary" @click="onSave">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>