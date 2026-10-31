<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';
import VenueCarousel from '@/components/VenueCarousel.vue';

const profileStore = useProfileStore();
const venues = ref([]);
const venueToAdd = ref({ name: '', address: '', description: '', capacity: 11 });
const venueToEdit = ref({});

const addPictureRef = ref();
const addImageUrl = ref();
const editPictureRef = ref();
const editImageUrl = ref();
const selectedImageForModal = ref(null);

async function fetchVenues() {
  const r = await axios.get('/api/venues/');
  venues.value = r.data;
}

function onAddPictureChange() {
  if (addPictureRef.value.files[0]) {
    addImageUrl.value = URL.createObjectURL(addPictureRef.value.files[0]);
  }
}

async function onVenueAdd() {
  const formData = new FormData();
  formData.set('name', venueToAdd.value.name);
  formData.set('address', venueToAdd.value.address);
  formData.set('description', venueToAdd.value.description || '');
  formData.set('capacity', venueToAdd.value.capacity);

  if (addPictureRef.value.files[0]) {
    formData.append('picture', addPictureRef.value.files[0]);
  }

  await axios.post('/api/venues/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
  venueToAdd.value = { name: '', address: '', description: '', capacity: 11 };
  addImageUrl.value = null;
  addPictureRef.value.value = '';
  await fetchVenues();
}

function onEditClick(v) {
  venueToEdit.value = { ...v };
  editImageUrl.value = v.picture;
}

function onEditPictureChange() {
  if (editPictureRef.value.files[0]) {
    editImageUrl.value = URL.createObjectURL(editPictureRef.value.files[0]);
  }
}

async function onUpdateVenue() {
  const formData = new FormData();
  formData.set('name', venueToEdit.value.name);
  formData.set('address', venueToEdit.value.address);
  formData.set('description', venueToEdit.value.description || '');
  formData.set('capacity', venueToEdit.value.capacity);

  if (editPictureRef.value.files[0]) {
    formData.append('picture', editPictureRef.value.files[0]);
  }

  await axios.patch(`/api/venues/${venueToEdit.value.id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
  await fetchVenues();
}

async function onRemoveClick(venue) {
  if (!confirm('Удалить локацию?')) return;
  await axios.delete(`/api/venues/${venue.id}/`);
  await fetchVenues();
}

function openModal(url) {
  selectedImageForModal.value = url;
  const modal = new window.bootstrap.Modal(document.getElementById('imageModal'));
  modal.show();
}

onMounted(fetchVenues);
</script>

<template>
  <div v-if="profileStore.isAdmin">
    <h1 class="mb-4">Наши локации</h1>

    <form @submit.prevent="onVenueAdd" class="row g-2 mb-4 bg-light p-3 rounded shadow-sm align-items-end">
      <div class="col-md-3">
        <label class="form-label small mb-0">Название</label>
        <input v-model="venueToAdd.name" class="form-control" required />
      </div>
      <div class="col-md-3">
        <label class="form-label small mb-0">Адрес</label>
        <input v-model="venueToAdd.address" class="form-control" required />
      </div>
      <div class="col-md-2">
        <label class="form-label small mb-0">Макс. вместимость (чел.)</label>
        <input v-model.number="venueToAdd.capacity" type="number" class="form-control" required />
      </div>
      <div class="col-md-4">
        <label class="form-label small mb-0">Описание</label>
        <input v-model="venueToAdd.description" class="form-control" />
      </div>
      <div class="col-md-4 mt-2">
        <label class="form-label small mb-0">Фотография</label>
        <input class="form-control" type="file" ref="addPictureRef" @change="onAddPictureChange" />
      </div>
      <div class="col-md-2 mt-2" v-show="addImageUrl">
        <img :src="addImageUrl" style="max-height: 40px; border-radius: 5px;" />
      </div>
      <div class="col-md-2 mt-2">
        <button class="btn btn-primary w-100">Добавить</button>
      </div>
    </form>

    <table class="table table-striped shadow-sm bg-white align-middle">
      <thead class="table-dark">
        <tr><th>Фото</th><th>Название</th><th>Адрес</th><th>Мест</th><th>Описание</th><th>Действия</th></tr>
      </thead>
      <tbody>
        <tr v-for="v in venues" :key="v.id">
          <td>
            <div v-show="v.picture">
              <img :src="v.picture" style="max-height: 50px; cursor: pointer; border-radius: 5px;" @click="openModal(v.picture)" />
            </div>
          </td>
          <td>{{ v.name }}</td>
          <td>{{ v.address }}</td>
          <td>{{ v.capacity }}</td>
          <td>{{ v.description }}</td>
          <td>
            <button class="btn btn-sm btn-success me-1" data-bs-toggle="modal" data-bs-target="#editVenueModal" @click="onEditClick(v)">Ред.</button>
            <button class="btn btn-sm btn-danger" @click="onRemoveClick(v)">Удал.</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-else>
    <VenueCarousel :venues="venues" @open="openModal" />
  </div>

  <div class="modal fade" id="editVenueModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">Редактировать</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <div class="modal-body">
          <label class="form-label small mb-0">Название</label>
          <input v-model="venueToEdit.name" class="form-control mb-2" />
          <label class="form-label small mb-0">Адрес</label>
          <input v-model="venueToEdit.address" class="form-control mb-2" />
          <label class="form-label small mb-0">Макс. вместимость</label>
          <input v-model.number="venueToEdit.capacity" type="number" class="form-control mb-2" />
          <label class="form-label small mb-0">Описание</label>
          <textarea v-model="venueToEdit.description" class="form-control mb-2"></textarea>
          <label class="form-label small mb-0">Обновить фото</label>
          <input class="form-control mb-2" type="file" ref="editPictureRef" @change="onEditPictureChange" />
          <div class="text-center" v-show="editImageUrl">
            <img :src="editImageUrl" style="max-height: 100px; border-radius: 5px;" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateVenue">Сохранить</button>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="imageModal" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-centered">
      <div class="modal-content bg-transparent border-0">
        <div class="modal-body text-center p-0 position-relative">
          <button type="button" class="btn-close btn-close-white position-absolute top-0 end-0 m-3" data-bs-dismiss="modal" style="z-index: 1055;"></button>
          <img :src="selectedImageForModal" class="img-fluid rounded shadow-lg" />
        </div>
      </div>
    </div>
  </div>
</template>