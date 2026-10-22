<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';

const profileStore = useProfileStore();
const venues = ref([]);
const venueToAdd = ref({ name: '', address: '', description: '', capacity: 11 });
const venueToEdit = ref({});
const selectedVenue = ref(null);

async function fetchVenues() {
  const r = await axios.get('/api/venues/');
  venues.value = r.data;
}

async function onVenueAdd() {
  await axios.post('/api/venues/', venueToAdd.value);
  venueToAdd.value = { name: '', address: '', description: '', capacity: 11 };
  await fetchVenues();
}

function onEditClick(v) { venueToEdit.value = { ...v }; }
async function onUpdateVenue() {
  await axios.put(`/api/venues/${venueToEdit.value.id}/`, venueToEdit.value);
  await fetchVenues();
}

async function onRemoveClick(venue) {
  if (!confirm('Удалить локацию?')) return;
  await axios.delete(`/api/venues/${venue.id}/`);
  await fetchVenues();
}

function openVenue(v) {
  selectedVenue.value = v;
}

onMounted(fetchVenues);
</script>

<template>
  <h1>Наши локации</h1>

  <form v-if="profileStore.isAdmin" @submit.prevent="onVenueAdd" class="row g-2 mb-4 bg-light p-3 rounded">
    <div class="col-md-3"><input v-model="venueToAdd.name" class="form-control" placeholder="Название" required /></div>
    <div class="col-md-3"><input v-model="venueToAdd.address" class="form-control" placeholder="Адрес" required /></div>
    <div class="col-md-4"><input v-model="venueToAdd.description" class="form-control" placeholder="Описание" /></div>
    <div class="col-md-2"><button class="btn btn-primary w-100">Добавить</button></div>
  </form>

  <div id="venueCarousel" class="carousel slide" data-bs-ride="false">
    <div class="carousel-inner">
      <div class="carousel-item" :class="{ 'active': index === 0 }" v-for="(v, index) in venues" :key="v.id">
        <div class="card mx-auto" style="width: 24rem; cursor: pointer;" @click="openVenue(v)" data-bs-toggle="modal" data-bs-target="#venueInfoModal">
          <div class="card-body text-center">
            <h3 class="card-title">{{ v.name }}</h3>
            <h5 class="text-muted">{{ v.address }}</h5>
            <p class="card-text">{{ v.description }}</p>
            <p><b>Вместимость:</b> {{ v.capacity }} чел.</p>
            <div v-if="profileStore.isAdmin" class="mt-3" @click.stop>
              <button class="btn btn-sm btn-success me-2" data-bs-toggle="modal" data-bs-target="#editVenueModal" @click="onEditClick(v)">Ред.</button>
              <button class="btn btn-sm btn-danger" @click="onRemoveClick(v)">Удал.</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <button class="carousel-control-prev" type="button" data-bs-target="#venueCarousel" data-bs-slide="prev">
      <span class="carousel-control-prev-icon bg-dark rounded-circle" aria-hidden="true"></span>
    </button>
    <button class="carousel-control-next" type="button" data-bs-target="#venueCarousel" data-bs-slide="next">
      <span class="carousel-control-next-icon bg-dark rounded-circle" aria-hidden="true"></span>
    </button>
  </div>

  <div class="modal fade" id="venueInfoModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content" v-if="selectedVenue">
        <div class="modal-header"><h5 class="modal-title">{{ selectedVenue.name }}</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <div class="modal-body">
          <h5>Адрес: {{ selectedVenue.address }}</h5>
          <p class="fs-5 mt-3">{{ selectedVenue.description || 'Описание пока отсутствует.' }}</p>
          <hr>
          <h6>Вместимость: {{ selectedVenue.capacity }} человек</h6>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="editVenueModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">Редактировать</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <div class="modal-body">
          <input v-model="venueToEdit.name" class="form-control mb-2" />
          <input v-model="venueToEdit.address" class="form-control mb-2" />
          <textarea v-model="venueToEdit.description" class="form-control mb-2"></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateVenue">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>