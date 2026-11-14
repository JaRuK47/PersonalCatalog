<script setup>
import { onMounted, ref, watch, computed } from 'vue';
import axios from 'axios';

const bookings = ref([]);
const sessions = ref([]);
const users = ref([]);
const bookingStats = ref({ count: 0, active_count: 0, no_show_count: 0 });
const bookingToAdd = ref({ user: null, session: null, leave_time: null, status: 'active' });
const bookingToEdit = ref({});
const filterUserId = ref('');
const displayLimit = ref(50);

async function fetchUsersAndSessions() {
  const [s, u] = await Promise.all([axios.get('/api/sessions/'), axios.get('/api/users/')]);
  sessions.value = s.data; users.value = u.data;
}

async function fetchBookings() {
  const url = filterUserId.value ? `/api/bookings/?user=${filterUserId.value}` : '/api/bookings/';
  const b = await axios.get(url);
  bookings.value = b.data;
  displayLimit.value = 50;
}

async function fetchStats() {
  const url = filterUserId.value ? `/api/bookings/stats/?user=${filterUserId.value}` : '/api/bookings/stats/';
  const r = await axios.get(url);
  bookingStats.value = r.data;
}

watch(filterUserId, () => {
  fetchBookings();
  fetchStats();
});

async function onBookingAdd() {
  const payload = { ...bookingToAdd.value };
  if (!payload.leave_time) delete payload.leave_time;
  await axios.post('/api/bookings/', payload);
  bookingToAdd.value = { user: null, session: null, leave_time: null, status: 'active' };
  await fetchBookings();
  await fetchStats();
}

function onEditClick(b) { bookingToEdit.value = { ...b }; }

async function onUpdateBooking() {
  const payload = {
    user: bookingToEdit.value.user,
    session: bookingToEdit.value.session,
    status: bookingToEdit.value.status,
    leave_time: bookingToEdit.value.leave_time || null
  };
  await axios.put(`/api/bookings/${bookingToEdit.value.id}/`, payload);
  await fetchBookings();
  await fetchStats();
}

async function onRemoveClick(b) {
  if(!confirm('Удалить бронь?')) return;
  await axios.delete(`/api/bookings/${b.id}/`);
  await fetchBookings();
  await fetchStats();
}

function sessionLabel(id) {
  const s = sessions.value.find(x => x.id === id);
  return s ? `${s.date} ${s.start_time} (${s.title})` : id;
}

const displayedBookings = computed(() => bookings.value.slice(0, displayLimit.value));

onMounted(async () => {
  await fetchUsersAndSessions();
  await fetchBookings();
  await fetchStats();
});
</script>

<template>
  <h1>Управление бронями</h1>

  <div class="row mb-4">
    <div class="col-md-4">
      <div class="card bg-primary text-white shadow-sm text-center py-3">
        <h5 class="mb-0">Всего броней</h5>
        <h2 class="mb-0">{{ bookingStats.count }}</h2>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card bg-success text-white shadow-sm text-center py-3">
        <h5 class="mb-0">Активных</h5>
        <h2 class="mb-0">{{ bookingStats.active_count }}</h2>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card bg-danger text-white shadow-sm text-center py-3">
        <h5 class="mb-0">Неявок</h5>
        <h2 class="mb-0">{{ bookingStats.no_show_count }}</h2>
      </div>
    </div>
  </div>

  <div class="row g-2 mb-3 bg-white p-3 rounded shadow-sm align-items-end">
    <div class="col-md-4">
      <label class="form-label small mb-0 fw-bold">Фильтр по пользователю</label>
      <select v-model="filterUserId" class="form-select">
        <option value="">Показать всех пользователей</option>
        <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
      </select>
    </div>
  </div>

  <form @submit.prevent="onBookingAdd" class="row g-2 mb-4 bg-light p-3 rounded shadow-sm">
    <div class="col-md-3">
      <select v-model.number="bookingToAdd.user" class="form-select" required>
        <option disabled :value="null">Кто бронирует</option>
        <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
      </select>
    </div>
    <div class="col-md-4">
      <select v-model.number="bookingToAdd.session" class="form-select" required>
        <option disabled :value="null">Сессия</option>
        <option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.date }} {{ s.start_time }} ({{ s.title }})</option>
      </select>
    </div>
    <div class="col-md-3">
      <input v-model="bookingToAdd.leave_time" type="time" class="form-control" title="Время ухода" />
    </div>
    <div class="col-md-2">
      <button class="btn btn-primary w-100">Забронировать</button>
    </div>
  </form>

  <table class="table table-striped align-middle shadow-sm bg-white">
    <thead class="table-dark">
      <tr><th>Кто</th><th>Сессия</th><th>Уходит</th><th>Статус</th><th>Действия</th></tr>
    </thead>
    <tbody>
      <tr v-for="b in displayedBookings" :key="b.id">
        <td>{{ b.user_name }}</td>
        <td>
          {{ sessionLabel(b.session) }}
          <span v-if="sessions.find(s => s.id === b.session)?.is_cancelled" class="badge bg-danger ms-2">Игра отменена</span>
        </td>
        <td>{{ b.leave_time || '—' }}</td>
        <td>{{ b.status_display }}</td>
        <td>
          <button class="btn btn-sm btn-success me-1" data-bs-toggle="modal" data-bs-target="#editBookingModal" @click="onEditClick(b)">Ред.</button>
          <button class="btn btn-sm btn-danger" @click="onRemoveClick(b)">Удал.</button>
        </td>
      </tr>
    </tbody>
  </table>

  <div class="text-center mb-5" v-if="bookings.length > displayLimit">
    <button class="btn btn-outline-secondary" @click="displayLimit += 50">Показать ещё 50</button>
  </div>

  <div class="modal fade" id="editBookingModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать бронь</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <label class="form-label">Статус брони:</label>
          <select v-model="bookingToEdit.status" class="form-select mb-2">
            <option value="active">Активно (Ждем)</option>
            <option value="attended">Явился</option>
            <option value="no_show">Неявка</option>
            <option value="cancelled">Отменено</option>
          </select>
          <label class="form-label">Время ухода:</label>
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