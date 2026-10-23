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

function openVenue(v) { selectedVenue.value = v; }

onMounted(fetchVenues);
</script>

<template>
  <h1>Наши локации</h1>

  <div v-if="profileStore.isAdmin">
    <form @submit.prevent="onVenueAdd" class="row g-2 mb-4 bg-light p-3 rounded">
      <div class="col-md-3"><input v-model="venueToAdd.name" class="form-control" placeholder="Название" required /></div>
      <div class="col-md-3"><input v-model="venueToAdd.address" class="form-control" placeholder="Адрес" required /></div>
      <div class="col-md-2"><input v-model.number="venueToAdd.capacity" type="number" class="form-control" placeholder="Вместимость" required /></div>
      <div class="col-md-2"><input v-model="venueToAdd.description" class="form-control" placeholder="Описание" /></div>
      <div class="col-md-2"><button class="btn btn-primary w-100">Добавить</button></div>
    </form>

    <table class="table table-striped">
      <thead><tr><th>Название</th><th>Адрес</th><th>Вместимость</th><th>Описание</th><th>Действия</th></tr></thead>
      <tbody>
        <tr v-for="v in venues" :key="v.id">
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

  <div v-else class="venue-carousel">
    <div class="venue-card-wrapper" v-for="v in venues" :key="v.id" @click="openVenue(v)" data-bs-toggle="modal" data-bs-target="#venueInfoModal">
      <div class="card shadow-sm">
        <div class="card-body text-center">
          <h3 class="card-title">{{ v.name }}</h3>
          <h5 class="text-muted">{{ v.address }}</h5>
          <p class="card-text">{{ v.description }}</p>
          <p class="mb-0"><b>Вместимость:</b> {{ v.capacity }} чел.</p>
        </div>
      </div>
    </div>
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
          <input v-model.number="venueToEdit.capacity" type="number" class="form-control mb-2" />
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

<style scoped>
.venue-carousel {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  gap: 20px;
  padding: 20px 10%;
}
.venue-card-wrapper {
  flex: 0 0 80%;
  scroll-snap-align: center;
  cursor: pointer;
  transition: transform 0.3s ease;
}
.venue-card-wrapper:hover { transform: scale(1.02); }
.venue-carousel::-webkit-scrollbar { height: 8px; }
.venue-carousel::-webkit-scrollbar-thumb { background: #ccc; border-radius: 4px; }
</style>