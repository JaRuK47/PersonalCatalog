<script setup>
import { onMounted, ref, computed } from 'vue';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';
import { downloadExcel } from '@/utils/excel';
import VenueCarousel from '@/components/VenueCarousel.vue';
import VenueTableRow from '@/components/venues/VenueTableRow.vue';
import VenueEditModal from '@/components/modals/VenueEditModal.vue';
import ImageModal from '@/components/modals/ImageModal.vue';
import Pagination from '@/components/Pagination.vue';

const profileStore = useProfileStore();
const venues = ref([]);
const venueStats = ref({ count: 0, avg_capacity: 0, max_capacity: 0, min_capacity: 0 });
const venueToAdd = ref({ name: '', address: '', description: '', capacity: 11 });

const showEditModal = ref(false);
const venueToEdit = ref({});
const showImageModal = ref(false);
const selectedImageForModal = ref(null);

const addPictureRef = ref();
const addImageUrl = ref();

const currentPage = ref(1);
const itemsPerPage = ref(10);

async function fetchVenues() {
  const r = await axios.get('/api/venues/');
  venues.value = r.data;
}

async function fetchStats() {
  const r = await axios.get('/api/venues/stats/');
  venueStats.value = r.data;
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
  await fetchStats();
}

function onAddPictureChange() {
  if (addPictureRef.value.files[0]) {
    addImageUrl.value = URL.createObjectURL(addPictureRef.value.files[0]);
  }
}

function openEditModal(v) {
  venueToEdit.value = v;
  showEditModal.value = true;
}

async function handleSaveVenue({ form, pictureFile }) {
  const formData = new FormData();
  formData.set('name', form.name);
  formData.set('address', form.address);
  formData.set('description', form.description || '');
  formData.set('capacity', form.capacity);

  if (pictureFile) {
    formData.append('picture', pictureFile);
  }

  await axios.patch(`/api/venues/${form.id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
  showEditModal.value = false;
  await fetchVenues();
  await fetchStats();
}

async function onRemoveClick(venue) {
  if (!confirm('Удалить локацию?')) return;
  await axios.delete(`/api/venues/${venue.id}/`);
  await fetchVenues();
  await fetchStats();
}

function openImageModal(url) {
  selectedImageForModal.value = url;
  showImageModal.value = true;
}

const paginatedVenues = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return venues.value.slice(start, end);
});

const totalPages = computed(() => {
  return Math.ceil(venues.value.length / itemsPerPage.value);
});

onMounted(() => {
  fetchVenues();
  fetchStats();
});
</script>

<template>
  <div v-if="profileStore.isAdmin">
    <h1 class="mb-4">Наши локации</h1>

    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card bg-primary text-white shadow-sm text-center py-3">
          <h5 class="mb-0">Всего локаций</h5>
          <h2 class="mb-0">{{ venueStats.count }}</h2>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-info text-white shadow-sm text-center py-3">
          <h5 class="mb-0">Средняя вместимость</h5>
          <h2 class="mb-0">{{ venueStats.avg_capacity ? venueStats.avg_capacity.toFixed(1) : 0 }}</h2>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white shadow-sm text-center py-3">
          <h5 class="mb-0">Макс. вместимость</h5>
          <h2 class="mb-0">{{ venueStats.max_capacity }}</h2>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning text-dark shadow-sm text-center py-3">
          <h5 class="mb-0">Мин. вместимость</h5>
          <h2 class="mb-0">{{ venueStats.min_capacity }}</h2>
        </div>
      </div>
    </div>

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

    <div class="d-flex justify-content-end mb-3">
      <button class="btn btn-success" @click="downloadExcel('/api/venues/export/', 'venues_export.xlsx')">Экспорт в Excel</button>
    </div>

    <table class="table table-striped shadow-sm bg-white align-middle">
      <thead class="table-dark">
        <tr><th>Фото</th><th>Название</th><th>Адрес</th><th>Мест</th><th>Описание</th><th>Действия</th></tr>
      </thead>
      <tbody>
        <VenueTableRow
          v-for="v in paginatedVenues"
          :key="v.id"
          :venue="v"
          @edit="openEditModal"
          @remove="onRemoveClick"
          @open-image="openImageModal"
        />
      </tbody>
    </table>

    <Pagination
      v-model:current-page="currentPage"
      :total-pages="totalPages"
    />
  </div>

  <div v-else>
    <VenueCarousel :venues="venues" @open="openImageModal" />
  </div>

  <VenueEditModal
    v-if="showEditModal"
    :venue="venueToEdit"
    @close="showEditModal = false"
    @save="handleSaveVenue"
  />

  <ImageModal
    v-if="showImageModal"
    :url="selectedImageForModal"
    @close="showImageModal = false"
  />
</template>