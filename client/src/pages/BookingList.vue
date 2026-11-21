<script setup>
import { onMounted, ref, watch, computed } from 'vue';
import axios from 'axios';
import { downloadExcel } from '@/utils/excel';
import BookingTableRow from '@/components/bookings/BookingTableRow.vue';
import BookingEditModal from '@/components/modals/BookingEditModal.vue';
import Pagination from '@/components/Pagination.vue';

const bookings = ref([]);
const sessions = ref([]);
const users = ref([]);
const bookingStats = ref({ count: 0, active_count: 0, no_show_count: 0 });
const bookingToAdd = ref({ user: null, session: null, leave_time: null, status: 'active' });
const showEditModal = ref(false);
const bookingToEdit = ref({});

const filterUser = ref('');
const filterSession = ref('');
const filterStatus = ref('');

const sortKey = ref('date');
const sortOrder = ref('desc');

const currentPage = ref(1);
const itemsPerPage = ref(10);

async function fetchUsersAndSessions() {
  const [s, u] = await Promise.all([axios.get('/api/sessions/'), axios.get('/api/users/')]);
  sessions.value = s.data;
  users.value = u.data;
}

function buildQueryString() {
  const params = new URLSearchParams();
  if (filterUser.value) params.append('user', filterUser.value);
  if (filterSession.value) params.append('session', filterSession.value);
  if (filterStatus.value) params.append('status', filterStatus.value);
  return params.toString();
}

async function fetchBookings() {
  const query = buildQueryString();
  const url = `/api/bookings/${query ? '?' + query : ''}`;
  const b = await axios.get(url);
  bookings.value = b.data;
}

async function fetchStats() {
  const query = buildQueryString();
  const url = `/api/bookings/stats/${query ? '?' + query : ''}`;
  const r = await axios.get(url);
  bookingStats.value = r.data;
}

watch([filterUser, filterSession, filterStatus], () => {
  currentPage.value = 1;
  fetchBookings();
  fetchStats();
});

function resetFilters() {
  filterUser.value = '';
  filterSession.value = '';
  filterStatus.value = '';
  currentPage.value = 1;
}

function sortBy(key) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortOrder.value = 'asc';
  }
  currentPage.value = 1;
}

async function onBookingAdd() {
  const payload = { ...bookingToAdd.value };
  if (!payload.leave_time) delete payload.leave_time;
  await axios.post('/api/bookings/', payload);
  bookingToAdd.value = { user: null, session: null, leave_time: null, status: 'active' };
  await fetchBookings();
  await fetchStats();
}

function openEditModal(b) {
  bookingToEdit.value = b;
  showEditModal.value = true;
}

async function handleSaveBooking(form) {
  const payload = {
    user: form.user,
    session: form.session,
    status: form.status,
    leave_time: form.leave_time || null
  };
  await axios.put(`/api/bookings/${form.id}/`, payload);
  showEditModal.value = false;
  await fetchBookings();
  await fetchStats();
}

async function onRemoveClick(b) {
  if(!confirm('Удалить бронь?')) return;
  await axios.delete(`/api/bookings/${b.id}/`);
  await fetchBookings();
  await fetchStats();
}

function getSessionLabel(id) {
  const s = sessions.value.find(x => x.id === id);
  return s ? `${s.date} ${s.start_time} (${s.title})` : id;
}

function isSessionCancelled(id) {
  const s = sessions.value.find(x => x.id === id);
  return s ? s.is_cancelled : false;
}

const sortedBookings = computed(() => {
  let result = bookings.value.slice();
  result.sort((a, b) => {
    let valA, valB;
    if (sortKey.value === 'user') {
      valA = a.user_name.toLowerCase();
      valB = b.user_name.toLowerCase();
    } else if (sortKey.value === 'session') {
      valA = getSessionLabel(a.session);
      valB = getSessionLabel(b.session);
    } else if (sortKey.value === 'status') {
      valA = a.status_display;
      valB = b.status_display;
    }
    if (valA < valB) return sortOrder.value === 'asc' ? -1 : 1;
    if (valA > valB) return sortOrder.value === 'asc' ? 1 : -1;
    return 0;
  });
  return result;
});

const paginatedBookings = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return sortedBookings.value.slice(start, end);
});

const totalPages = computed(() => {
  return Math.ceil(sortedBookings.value.length / itemsPerPage.value);
});

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
        <h5 class="mb-0">Найдено броней</h5>
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
    <div class="col-md-3">
      <label class="form-label small mb-0 fw-bold">Пользователь</label>
      <select v-model="filterUser" class="form-select">
        <option value="">Все пользователи</option>
        <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
      </select>
    </div>
    <div class="col-md-3">
      <label class="form-label small mb-0 fw-bold">Сессия</label>
      <select v-model="filterSession" class="form-select">
        <option value="">Все сессии</option>
        <option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.date }} ({{ s.title }})</option>
      </select>
    </div>
    <div class="col-md-2">
      <label class="form-label small mb-0 fw-bold">Статус</label>
      <select v-model="filterStatus" class="form-select">
        <option value="">Все статусы</option>
        <option value="active">Активно (Игра еще не прошла)</option>
        <option value="attended">Явился (Игра прошла)</option>
        <option value="no_show">Неявка</option>
        <option value="cancelled">Отменено</option>
      </select>
    </div>
    <div class="col-md-2">
      <button class="btn btn-outline-secondary w-100" @click="resetFilters">Сбросить</button>
    </div>
    <div class="col-md-2">
      <button class="btn btn-success w-100" @click="downloadExcel(`/api/bookings/export/?${buildQueryString()}`, 'bookings_export.xlsx')">Экспорт в Excel</button>
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
      <tr>
        <th style="cursor: pointer;" @click="sortBy('user')">Кто {{ sortKey === 'user' ? (sortOrder === 'asc' ? '▲' : '▼') : '' }}</th>
        <th style="cursor: pointer;" @click="sortBy('session')">Сессия {{ sortKey === 'session' ? (sortOrder === 'asc' ? '▲' : '▼') : '' }}</th>
        <th>Уходит</th>
        <th style="cursor: pointer;" @click="sortBy('status')">Статус {{ sortKey === 'status' ? (sortOrder === 'asc' ? '▲' : '▼') : '' }}</th>
        <th>Действия</th>
      </tr>
    </thead>
    <tbody>
      <BookingTableRow
        v-for="b in paginatedBookings"
        :key="b.id"
        :booking="b"
        :session-info="getSessionLabel(b.session)"
        :is-cancelled="isSessionCancelled(b.session)"
        @edit="openEditModal"
        @remove="onRemoveClick"
      />
    </tbody>
  </table>

  <Pagination
    v-model:current-page="currentPage"
    :total-pages="totalPages"
  />

  <BookingEditModal
    v-if="showEditModal"
    :booking="bookingToEdit"
    @close="showEditModal = false"
    @save="handleSaveBooking"
  />
</template>