<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';

const venues = ref([]);
const venueToAdd = ref({ name: '', address: '', capacity: 10 });
const venueToEdit = ref({});

async function fetchVenues() {
  const r = await axios.get('/api/venues/');
  venues.value = r.data;
}

async function onVenueAdd() {
  await axios.post('/api/venues/', venueToAdd.value);
  venueToAdd.value = { name: '', address: '', capacity: 10 };
  await fetchVenues();
}

function onVenueEditClick(venue) {
  venueToEdit.value = { ...venue };
}

async function onUpdateVenue() {
  await axios.put(`/api/venues/${venueToEdit.value.id}/`, venueToEdit.value);
  await fetchVenues();
}

async function onRemoveClick(venue) {
  await axios.delete(`/api/venues/${venue.id}/`);
  await fetchVenues();
}

onMounted(fetchVenues);
</script>

<template>
  <h1>Локации</h1>

  <form @submit.prevent="onVenueAdd" class="row g-2 mb-3">
    <div class="col">
      <input v-model="venueToAdd.name" class="form-control" placeholder="Название" required />
    </div>
    <div class="col">
      <input v-model="venueToAdd.address" class="form-control" placeholder="Адрес" required />
    </div>
    <div class="col-auto">
      <input v-model.number="venueToAdd.capacity" type="number" class="form-control" placeholder="Мест" required />
    </div>
    <div class="col-auto">
      <button class="btn btn-primary">Добавить</button>
    </div>
  </form>

  <table class="table table-striped">
    <thead>
      <tr><th>ID</th><th>Название</th><th>Адрес</th><th>Мест</th><th></th></tr>
    </thead>
    <tbody>
      <tr v-for="v in venues" :key="v.id">
        <td>{{ v.id }}</td>
        <td>{{ v.name }}</td>
        <td>{{ v.address }}</td>
        <td>{{ v.capacity }}</td>
        <td>
          <button class="btn btn-sm btn-success me-1"
                  data-bs-toggle="modal"
                  data-bs-target="#editVenueModal"
                  @click="onVenueEditClick(v)">
            Изменить
          </button>
          <button class="btn btn-sm btn-danger" @click="onRemoveClick(v)">Удалить</button>
        </td>
      </tr>
    </tbody>
  </table>

  <div class="modal fade" id="editVenueModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать локацию</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input v-model="venueToEdit.name" class="form-control mb-2" placeholder="Название" />
          <input v-model="venueToEdit.address" class="form-control mb-2" placeholder="Адрес" />
          <input v-model.number="venueToEdit.capacity" type="number" class="form-control" placeholder="Мест" />
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateVenue">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>