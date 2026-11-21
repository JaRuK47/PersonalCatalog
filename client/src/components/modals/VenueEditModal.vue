<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  venue: Object
})

const emit = defineEmits(['save', 'close'])

const editPictureRef = ref()
const editImageUrl = ref()
const formData = ref({})

watch(() => props.venue, (newVal) => {
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
          <h5 class="modal-title">Редактировать локацию</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <label class="form-label small mb-0">Название</label>
          <input v-model="formData.name" class="form-control mb-2" />

          <label class="form-label small mb-0">Адрес</label>
          <input v-model="formData.address" class="form-control mb-2" />

          <label class="form-label small mb-0">Макс. вместимость</label>
          <input v-model.number="formData.capacity" type="number" class="form-control mb-2" />

          <label class="form-label small mb-0">Описание</label>
          <textarea v-model="formData.description" class="form-control mb-2"></textarea>

          <label class="form-label small mb-0">Обновить фото</label>
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