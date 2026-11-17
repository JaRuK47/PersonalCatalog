<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  session: Object,
  venues: Array,
  gameModes: Array
})

const emit = defineEmits(['save', 'close'])

const editPictureRef = ref()
const editImageUrl = ref()
const formData = ref({})

watch(() => props.session, (newVal) => {
  formData.value = { ...newVal }
  editImageUrl.value = newVal?.picture || null
}, { immediate: true })

function onEditPictureChange() {
  if (editPictureRef.value.files[0]) {
    editImageUrl.value = URL.createObjectURL(editPictureRef.value.files[0])
  }
}

function onSave() {
  emit('save', { form: formData.value, pictureFile: editPictureRef.value?.files[0] })
  if (editPictureRef.value) editPictureRef.value.value = ''
}
</script>

<template>
  <div class="modal fade show d-block" style="background: rgba(0,0,0,0.5);" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать сессию</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <label class="form-label small mb-0">Место</label>
          <select v-model.number="formData.venue" class="form-select mb-2">
            <option v-for="v in venues" :key="v.id" :value="v.id">{{ v.name }}</option>
          </select>
          <label class="form-label small mb-0">Дата</label>
          <input v-model="formData.date" type="date" class="form-control mb-2" />
          <label class="form-label small mb-0">Время</label>
          <input v-model="formData.start_time" type="time" class="form-control mb-2" />
          <label class="form-label small mb-0">Название</label>
          <input v-model="formData.title" class="form-control mb-2" />
          <label class="form-label small mb-0">Режим</label>
          <select v-model.number="formData.game_mode" class="form-select mb-2">
            <option v-for="g in gameModes" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
          <label class="form-label small mb-0">Описание</label>
          <textarea v-model="formData.description" class="form-control mb-2"></textarea>
          <label class="form-label small mb-0">Обновить постер</label>
          <input class="form-control mb-2" type="file" ref="editPictureRef" @change="onEditPictureChange" />
          <div class="text-center" v-show="editImageUrl">
            <img :src="editImageUrl" style="max-height: 100px; border-radius: 5px;" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="$emit('close')">Отмена</button>
          <button class="btn btn-primary" @click="onSave">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>