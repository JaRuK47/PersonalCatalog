<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';

const bookings = ref([]);
const sessions = ref([]);
const users = ref([]);
const bookingToAdd = ref({ user: null, session: null, leave_time: null, status: 'active' });

async function fetchAll() {
  const [b, s, u] = await Promise.all([
    axios.get('/api/bookings/'),
    axios.get('/api/sessions/'),
    axios.get('/api/users/'),
  ]);
  bookings.value = b.data;
  sessions.value = s.data;
  users.value = u.data;
}

async function onBookingAdd() {
  const payload = { ...bookingToAdd.value };
  if (!payload.leave_time) delete payload.leave_time;
  await axios.post('/api/bookings/', payload);
  bookingToAdd.value = { user: null, session: null, leave_time: null, status: 'active' };
  await fetchAll();
}

async function onRemoveClick(booking) {
  await axios.delete(`/api/bookings/${booking.id}/`);
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
  <h1>Бронирования</h1>

  <form @submit.prevent="onBookingAdd" class="row g-2 mb-3">
    <div class="col">
      <select v-model.number="bookingToAdd.user" class="form-select" required>
        <option disabled :value="null">Пользователь</option>
        <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
      </select>
    </div>
    <div class="col">
      <select v-model.number="bookingToAdd.session" class="form-select" required>
        <option disabled :value="null">Сессия</option>
        <option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.date }} {{ s.start_time }}</option>
      </select>
    </div>
    <div class="col-auto">
      <input v-model="bookingToAdd.leave_time" type="time" class="form-control" placeholder="Уход" />
    </div>
    <div class="col-auto">
      <button class="btn btn-primary">Добавить</button>
    </div>
  </form>

  <table class="table table-striped">
    <thead>
      <tr><th>ID</th><th>Пользователь</th><th>Сессия</th><th>До</th><th>Статус</th><th></th></tr>
    </thead>
    <tbody>
      <tr v-for="b in bookings" :key="b.id">
        <td>{{ b.id }}</td>
        <td>{{ userName(b.user) }}</td>
        <td>{{ sessionLabel(b.session) }}</td>
        <td>{{ b.leave_time || 'до конца' }}</td>
        <td>{{ b.status }}</td>
        <td>
          <button class="btn btn-sm btn-danger" @click="onRemoveClick(b)">Удалить</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>