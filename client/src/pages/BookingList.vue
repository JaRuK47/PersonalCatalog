<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';

const bookings = ref([]);
const sessions = ref([]);
const users = ref([]);
const bookingToAdd = ref({ user: null, session: null, leave_time: null, status: 'active' });
const bookingToEdit = ref({});

async function fetchAll() {
  const [b, s, u] = await Promise.all([
    axios.get('/api/bookings/'), axios.get('/api/sessions/'), axios.get('/api/users/')
  ]);
  bookings.value = b.data; sessions.value = s.data; users.value = u.data;
}

async function onBookingAdd() {
  const payload = { ...bookingToAdd.value };
  if (!payload.leave_time) delete payload.leave_time;
  await axios.post('/api/bookings/', payload);
  await fetchAll();
}

function onEditClick(b) { bookingToEdit.value = { ...b }; }
async function onUpdateBooking() {
  const payload = { ...bookingToEdit.value };
  if (!payload.leave_time) payload.leave_time = null;
  await axios.put(`/api/bookings/${bookingToEdit.value.id}/`, payload);
  await fetchAll();
}

async function onRemoveClick(b) {
  if(!confirm('Удалить бронь?')) return;
  await axios.delete(`/api/bookings/${b.id}/`);
  await fetchAll();
}

function userName(id) { return users.value.find(u => u.id === id)?.username || id; }
function sessionLabel(id) {
  const s = sessions.value.find(x => x.id === id);
  return s ? `${s.date} ${s.start_time}` : id;
}

onMounted(fetchAll);
</script>

<template>
  <h1>Управление бронями</h1>

  <form @submit.prevent="onBookingAdd" class="row g-2 mb-4 bg-light p-3 rounded">
    <div class="col-md-3">
      <select v-model.number="bookingToAdd.user" class="form-select" required>
        <option disabled :value="null">Кто бронирует</option>
        <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
      </select>
    </div>
    <div class="col-md-4">
      <select v-model.number="bookingToAdd.session" class="form-select" required>
        <option disabled :value="null">Сессия</option>
        <option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.date }} {{ s.start_time }}</option>
      </select>
    </div>
    <div class="col-md-3">
      <input v-model="bookingToAdd.leave_time" type="time" class="form-control" title="Время ухода" />
    </div>
    <div class="col-md-2"><button class="btn btn-primary w-100">Забронировать</button></div>
  </form>

  <table class="table table-striped align-middle">
    <thead><tr><th>Кто</th><th>Сессия</th><th>Уходит в</th><th>Статус</th><th>Действия</th></tr></thead>
    <tbody>
      <tr v-for="b in bookings" :key="b.id">
        <td>{{ userName(b.user) }}</td>
        <td>{{ sessionLabel(b.session) }}</td>
        <td>{{ b.leave_time || '—' }}</td>
        <td>{{ b.status }}</td>
        <td>
          <button class="btn btn-sm btn-success me-1" data-bs-toggle="modal" data-bs-target="#editBookingModal" @click="onEditClick(b)">Ред.</button>
          <button class="btn btn-sm btn-danger" @click="onRemoveClick(b)">Удал.</button>
        </td>
      </tr>
    </tbody>
  </table>

  <div class="modal fade" id="editBookingModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">Редактировать бронь</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <div class="modal-body">
          <select v-model="bookingToEdit.status" class="form-select mb-2">
            <option value="active">Активно</option>
            <option value="cancelled">Отменено</option>
            <option value="no_show">Неявка</option>
          </select>
          <input v-model="bookingToEdit.leave_time" type="time" class="form-control" />
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateBooking">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>