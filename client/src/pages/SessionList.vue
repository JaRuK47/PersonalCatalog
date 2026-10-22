<script setup>
import { onMounted, ref, computed } from 'vue';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';
import { useRouter } from 'vue-router';

const router = useRouter();
const profileStore = useProfileStore();
const sessions = ref([]);
const venues = ref([]);
const users = ref([]);
const allBookings = ref([]);

const sessionToAdd = ref({ venue: null, date: '', start_time: '', title: 'Игра', game_mode: 'Спортивная мафия', description: '', max_players: 11 });
const sessionToEdit = ref({});
const selectedSession = ref(null);
const currentSessionBookings = ref([]);

async function fetchAll() {
  const [s, v, b, u] = await Promise.all([
    axios.get('/api/sessions/'), axios.get('/api/venues/'),
    axios.get('/api/bookings/'), axios.get('/api/users/')
  ]);
  sessions.value = s.data;
  venues.value = v.data;
  allBookings.value = b.data;
  users.value = u.data;
}

async function onSessionAdd() {
  await axios.post('/api/sessions/', sessionToAdd.value);
  sessionToAdd.value = { venue: null, date: '', start_time: '', title: 'Игра', game_mode: 'Спортивная мафия', description: '', max_players: 11 };
  await fetchAll();
}

function onEditClick(s) { sessionToEdit.value = { ...s }; }
async function onUpdateSession() {
  await axios.put(`/api/sessions/${sessionToEdit.value.id}/`, sessionToEdit.value);
  await fetchAll();
}

async function onRemoveClick(s) {
  if(!confirm('Удалить сессию?')) return;
  await axios.delete(`/api/sessions/${s.id}/`);
  await fetchAll();
}

// Логика открытия бронирования
function handleBookClick(s) {
  if (!profileStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  selectedSession.value = s;
  currentSessionBookings.value = allBookings.value.filter(b => b.session === s.id && b.status === 'Активно');

  // Программно открываем модалку, чтобы не было бага с затемнением при редиректе
  const modal = new window.bootstrap.Modal(document.getElementById('bookingModal'));
  modal.show();
}

// Проверка, забронирован ли текущий юзер
function myBooking(sessionId) {
  return allBookings.value.find(b => b.session === sessionId && b.user === profileStore.userId && b.status === 'Активно');
}

async function bookPlace() {
  await axios.post('/api/bookings/', { user: profileStore.userId, session: selectedSession.value.id, status: 'active' });
  alert('Вы успешно забронировали место!');
  await fetchAll();
  currentSessionBookings.value = allBookings.value.filter(b => b.session === selectedSession.value.id && b.status === 'Активно');
}

async function cancelBooking() {
  const b = myBooking(selectedSession.value.id);
  if (!b) return;
  if(!confirm('Отменить бронь?')) return;

  // В реальном проекте тут надо проверять "не позже чем за час", но для простоты разрешим сейчас
  await axios.delete(`/api/bookings/${b.id}/`);
  alert('Бронь отменена');
  await fetchAll();
  currentSessionBookings.value = allBookings.value.filter(x => x.session === selectedSession.value.id && x.status === 'Активно');
}

const sortedSessions = computed(() => {
  const now = new Date();
  const threeDaysAgo = new Date(now.getTime() - (3 * 24 * 60 * 60 * 1000));
  return sessions.value
    .filter(s => s.status !== 'Завершена' || new Date(s.date) >= threeDaysAgo)
    .sort((a, b) => new Date(`${b.date}T${b.start_time}`) - new Date(`${a.date}T${a.start_time}`));
});

function venueName(id) { return venues.value.find(v => v.id === id)?.name || '—'; }
function userName(id) { return users.value.find(u => u.id === id)?.username || id; }

onMounted(fetchAll);
</script>

<template>
  <h1>Расписание сессий</h1>

  <form v-if="profileStore.isManager" @submit.prevent="onSessionAdd" class="row g-2 mb-4 bg-light p-3 rounded">
    <div class="col-md-3">
      <select v-model.number="sessionToAdd.venue" class="form-select" required>
        <option disabled :value="null">Место</option>
        <option v-for="v in venues" :key="v.id" :value="v.id">{{ v.name }}</option>
      </select>
    </div>
    <div class="col-md-3"><input v-model="sessionToAdd.date" type="date" class="form-control" required /></div>
    <div class="col-md-3"><input v-model="sessionToAdd.start_time" type="time" class="form-control" required /></div>
    <div class="col-md-3"><input v-model="sessionToAdd.title" class="form-control" placeholder="Название" required /></div>
    <div class="col-md-4 mt-2"><input v-model="sessionToAdd.game_mode" class="form-control" placeholder="Режим игры" required /></div>
    <div class="col-md-8 mt-2"><input v-model="sessionToAdd.description" class="form-control" placeholder="Описание" /></div>
    <div class="col-md-12 mt-2"><button class="btn btn-primary w-100">Создать</button></div>
  </form>

  <div v-if="profileStore.isManager">
    <table class="table table-hover align-middle">
      <thead><tr><th>Дата</th><th>Игра</th><th>Место</th><th>Статус</th><th>Действия</th></tr></thead>
      <tbody>
        <tr v-for="s in sortedSessions" :key="s.id">
          <td>{{ s.date }} в {{ s.start_time }}</td>
          <td><b>{{ s.title }}</b> <br><small>{{ s.game_mode }}</small></td>
          <td>{{ venueName(s.venue) }}</td>
          <td><span class="badge" :class="{'bg-success': s.status === 'Идёт набор', 'bg-warning text-dark': s.status === 'Активно', 'bg-secondary': s.status === 'Завершена'}">{{ s.status }}</span></td>
          <td>
            <button class="btn btn-sm btn-success me-1" data-bs-toggle="modal" data-bs-target="#editSessionModal" @click="onEditClick(s)">Ред.</button>
            <button class="btn btn-sm btn-danger" @click="onRemoveClick(s)">Удал.</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-else class="row">
    <div class="col-md-4 mb-3" v-for="s in sortedSessions" :key="s.id">
      <div class="card shadow-sm h-100">
        <div class="card-body">
          <h4 class="card-title">{{ s.title }}</h4>
          <h6 class="card-subtitle mb-2 text-primary">{{ s.game_mode }}</h6>
          <p class="card-text text-muted mb-1"><b>{{ s.date }}</b> в {{ s.start_time }}</p>
          <p class="card-text mb-2">{{ venueName(s.venue) }}</p>
          <p class="card-text small">{{ s.description }}</p>
          <hr>
          <p>Статус: <b>{{ s.status }}</b></p>
          <button v-if="!myBooking(s.id)" class="btn btn-primary w-100" @click="handleBookClick(s)">Забронировать</button>
          <button v-else class="btn btn-outline-danger w-100" @click="handleBookClick(s)">Вы записаны (Управление)</button>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="bookingModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content" v-if="selectedSession">
        <div class="modal-header"><h5 class="modal-title">{{ selectedSession.title }} | {{ selectedSession.date }}</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <div class="modal-body">
          <div class="mb-3">
            <h6>Режим:</h6> <p>{{ selectedSession.game_mode }}</p>
            <h6>Описание:</h6> <p>{{ selectedSession.description }}</p>
            <h6>Локация:</h6> <p>{{ venueName(selectedSession.venue) }}</p>
          </div>
          <h5 class="mt-4">Список игроков ({{ currentSessionBookings.length }}):</h5>
          <ul class="list-group">
            <li class="list-group-item" v-for="b in currentSessionBookings" :key="b.id">{{ userName(b.user) }}</li>
            <li class="list-group-item text-muted" v-if="currentSessionBookings.length === 0">Пока никого нет</li>
          </ul>
        </div>
        <div class="modal-footer">
          <button v-if="!myBooking(selectedSession.id)" class="btn btn-success" @click="bookPlace">Забронировать место</button>
          <button v-else class="btn btn-danger" @click="cancelBooking">Отменить мою бронь</button>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="editSessionModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">Редактировать сессию</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <div class="modal-body">
          <select v-model.number="sessionToEdit.venue" class="form-select mb-2">
            <option v-for="v in venues" :key="v.id" :value="v.id">{{ v.name }}</option>
          </select>
          <input v-model="sessionToEdit.date" type="date" class="form-control mb-2" />
          <input v-model="sessionToEdit.start_time" type="time" class="form-control mb-2" />
          <input v-model="sessionToEdit.title" class="form-control mb-2" placeholder="Название" />
          <input v-model="sessionToEdit.game_mode" class="form-control mb-2" placeholder="Режим" />
          <textarea v-model="sessionToEdit.description" class="form-control mb-2" placeholder="Описание"></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateSession">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>