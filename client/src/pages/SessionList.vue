<script setup>
import { onMounted, ref, computed, watch } from 'vue';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';
import { useRouter } from 'vue-router';
import SessionCard from '@/components/sessions/SessionCard.vue';
import SessionTableRow from '@/components/sessions/SessionTableRow.vue';
import SessionEditModal from '@/components/modals/SessionEditModal.vue';
import BookingModal from '@/components/modals/BookingModal.vue';
import ImageModal from '@/components/modals/ImageModal.vue';

const router = useRouter();
const profileStore = useProfileStore();
const sessions = ref([]);
const venues = ref([]);
const users = ref([]);
const allBookings = ref([]);
const gameModes = ref([]);
const sessionStats = ref({ count: 0, cancelled_count: 0 });

const sessionToAdd = ref({ venue: null, date: '', start_time: '', title: 'Игра', game_mode: null, description: '', max_players: 11 });

const showEditModal = ref(false);
const sessionToEdit = ref({});

const showBookingModal = ref(false);
const selectedSession = ref(null);

const showImageModal = ref(false);
const selectedImageForModal = ref(null);

const filterVenue = ref('');
const filterGameMode = ref('');
const filterStatus = ref('');

const newGameModeName = ref('');
const showAddModeModal = ref(false);

const addPictureRef = ref();
const addImageUrl = ref();

async function fetchDependencies() {
  const [v, u, g] = await Promise.all([
    axios.get('/api/venues/'),
    axios.get('/api/users/'),
    axios.get('/api/game-modes/')
  ]);
  venues.value = v.data;
  users.value = u.data;
  gameModes.value = g.data;
}

function buildQueryString() {
  const params = new URLSearchParams();
  if (filterVenue.value) params.append('venue', filterVenue.value);
  if (filterGameMode.value) params.append('game_mode', filterGameMode.value);
  if (filterStatus.value) params.append('status', filterStatus.value);
  return params.toString();
}

async function fetchSessions() {
  const query = buildQueryString();
  const url = `/api/sessions/${query ? '?' + query : ''}`;
  const [s, b] = await Promise.all([
    axios.get(url),
    axios.get('/api/bookings/')
  ]);
  sessions.value = s.data;
  allBookings.value = b.data;
}

async function fetchStats() {
  const query = buildQueryString();
  const url = `/api/sessions/stats/${query ? '?' + query : ''}`;
  const r = await axios.get(url);
  sessionStats.value = r.data;
}

watch([filterVenue, filterGameMode, filterStatus], () => {
  fetchSessions();
  fetchStats();
});

function resetFilters() {
  filterVenue.value = '';
  filterGameMode.value = '';
  filterStatus.value = '';
}

async function addGameMode() {
  if (!newGameModeName.value) return;
  try {
    const r = await axios.post('/api/game-modes/', { name: newGameModeName.value });
    await fetchDependencies();
    sessionToAdd.value.game_mode = r.data.id;
    newGameModeName.value = '';
    showAddModeModal.value = false;
  } catch (e) {
    alert('Такой режим уже существует!');
  }
}

function onAddPictureChange() {
  if (addPictureRef.value.files[0]) {
    addImageUrl.value = URL.createObjectURL(addPictureRef.value.files[0]);
  }
}

async function onSessionAdd() {
  const formData = new FormData();
  formData.set('venue', sessionToAdd.value.venue);
  formData.set('date', sessionToAdd.value.date);
  formData.set('start_time', sessionToAdd.value.start_time);
  formData.set('title', sessionToAdd.value.title);
  formData.set('game_mode', sessionToAdd.value.game_mode);
  formData.set('description', sessionToAdd.value.description || '');
  formData.set('max_players', sessionToAdd.value.max_players);

  if (addPictureRef.value.files[0]) {
    formData.append('picture', addPictureRef.value.files[0]);
  }

  await axios.post('/api/sessions/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });

  sessionToAdd.value = { venue: null, date: '', start_time: '', title: 'Игра', game_mode: null, description: '', max_players: 11 };
  addImageUrl.value = null;
  addPictureRef.value.value = '';
  await fetchSessions();
  await fetchStats();
}

function openEditModal(s) {
  sessionToEdit.value = s;
  showEditModal.value = true;
}

async function handleSaveSession({ form, pictureFile }) {
  const formData = new FormData();
  formData.set('venue', form.venue);
  formData.set('date', form.date);
  formData.set('start_time', form.start_time);
  formData.set('title', form.title);
  formData.set('game_mode', form.game_mode);
  formData.set('description', form.description || '');
  formData.set('max_players', form.max_players);

  if (pictureFile) {
    formData.append('picture', pictureFile);
  }

  await axios.patch(`/api/sessions/${form.id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
  showEditModal.value = false;
  await fetchSessions();
  await fetchStats();
}

async function onRemoveClick(s) {
  if(!confirm('Удалить сессию полностью?')) return;
  await axios.delete(`/api/sessions/${s.id}/`);
  await fetchSessions();
  await fetchStats();
}

async function cancelSession(s) {
  if(!confirm('Отменить сессию?')) return;
  await axios.patch(`/api/sessions/${s.id}/`, { is_cancelled: true });
  await fetchSessions();
  await fetchStats();
}

function handleBookClick(s) {
  if (!profileStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  selectedSession.value = s;
  showBookingModal.value = true;
}

function myBooking(sessionId) {
  return allBookings.value.find(b => b.session === sessionId && (b.status === 'active' || b.status === 'attended'));
}

async function bookPlace() {
  await axios.post('/api/bookings/', { session: selectedSession.value.id, status: 'active' });
  alert('Вы успешно забронировали место!');
  await fetchSessions();
}

async function cancelBooking() {
  const b = myBooking(selectedSession.value.id);
  if (!b) return;
  if(!confirm('Отменить бронь?')) return;
  await axios.delete(`/api/bookings/${b.id}/`);
  await fetchSessions();
  showBookingModal.value = false;
}

const sortedSessions = computed(() => {
  let result = sessions.value.slice();
  if (!profileStore.isManager) {
    const twoDaysAgo = new Date();
    twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);
    result = result.filter(s => {
      if (s.is_cancelled) return true;
      if (s.status !== 'Завершена') return true;
      return new Date(`${s.date}T${s.start_time}`) >= twoDaysAgo;
    });
    result.sort((a, b) => {
      if (a.is_cancelled && !b.is_cancelled) return -1;
      if (!a.is_cancelled && b.is_cancelled) return 1;
      return new Date(`${b.date}T${b.start_time}`) - new Date(`${a.date}T${a.start_time}`);
    });
  } else {
    result.sort((a, b) => new Date(`${b.date}T${b.start_time}`) - new Date(`${a.date}T${a.start_time}`));
  }
  return result;
});

function venueName(id) { return venues.value.find(v => v.id === id)?.name || '—'; }
function gameModeName(id) { return gameModes.value.find(g => g.id === id)?.name || '—'; }
function isPast(s) { return new Date(`${s.date}T${s.start_time}`) < new Date(); }

function openImageModal(url) {
  selectedImageForModal.value = url;
  showImageModal.value = true;
}

onMounted(async () => {
  await fetchDependencies();
  await fetchSessions();
  await fetchStats();
});
</script>

<template>
  <h1>Расписание сессий</h1>

  <div class="row mb-4">
    <div class="col-md-6">
      <div class="card bg-primary text-white shadow-sm text-center py-3">
        <h5 class="mb-0">Найдено сессий</h5>
        <h2 class="mb-0">{{ sessionStats.count }}</h2>
      </div>
    </div>
    <div class="col-md-6">
      <div class="card bg-danger text-white shadow-sm text-center py-3">
        <h5 class="mb-0">Отмененных игр</h5>
        <h2 class="mb-0">{{ sessionStats.cancelled_count }}</h2>
      </div>
    </div>
  </div>

  <div class="row g-2 mb-3 bg-white p-3 rounded shadow-sm align-items-end">
    <div class="col-md-3">
      <label class="form-label small mb-0 fw-bold">Локация</label>
      <select v-model="filterVenue" class="form-select">
        <option value="">Все локации</option>
        <option v-for="v in venues" :key="v.id" :value="v.id">{{ v.name }}</option>
      </select>
    </div>
    <div class="col-md-3">
      <label class="form-label small mb-0 fw-bold">Режим игры</label>
      <select v-model="filterGameMode" class="form-select">
        <option value="">Все режимы</option>
        <option v-for="g in gameModes" :key="g.id" :value="g.id">{{ g.name }}</option>
      </select>
    </div>
    <div class="col-md-2">
      <label class="form-label small mb-0 fw-bold">Статус</label>
      <select v-model="filterStatus" class="form-select">
        <option value="">Все сессии</option>
        <option value="active">Активные (не отменены)</option>
        <option value="cancelled">Только отмененные</option>
      </select>
    </div>
    <div class="col-md-2">
      <button class="btn btn-outline-secondary w-100" @click="resetFilters">Сбросить</button>
    </div>
  </div>

  <form v-if="profileStore.isManager" @submit.prevent="onSessionAdd" class="row g-2 mb-4 bg-light p-3 rounded shadow-sm align-items-end">
    <div class="col-md-3">
      <label class="form-label small mb-0">Место</label>
      <select v-model.number="sessionToAdd.venue" class="form-select" required>
        <option disabled :value="null">Выбрать</option>
        <option v-for="v in venues" :key="v.id" :value="v.id">{{ v.name }}</option>
      </select>
    </div>
    <div class="col-md-2">
      <label class="form-label small mb-0">Дата</label>
      <input v-model="sessionToAdd.date" type="date" class="form-control" required />
    </div>
    <div class="col-md-2">
      <label class="form-label small mb-0">Время</label>
      <input v-model="sessionToAdd.start_time" type="time" class="form-control" required />
    </div>
    <div class="col-md-2">
      <label class="form-label small mb-0">Название</label>
      <input v-model="sessionToAdd.title" class="form-control" required />
    </div>
    <div class="col-md-3">
      <label class="form-label small mb-0">Режим</label>
      <div class="input-group">
        <select v-model.number="sessionToAdd.game_mode" class="form-select" required>
          <option disabled :value="null">Выбрать</option>
          <option v-for="g in gameModes" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
        <button class="btn btn-outline-secondary" type="button" @click="showAddModeModal = true" title="Добавить новый режим">+</button>
      </div>
    </div>
    <div class="col-md-4 mt-2">
      <input v-model="sessionToAdd.description" class="form-control" placeholder="Описание" />
    </div>
    <div class="col-md-3 mt-2">
      <input class="form-control" type="file" ref="addPictureRef" @change="onAddPictureChange" />
    </div>
    <div class="col-md-2 mt-2" v-show="addImageUrl">
      <img :src="addImageUrl" style="max-height: 40px; border-radius: 5px;" />
    </div>
    <div class="col-md-3 mt-2">
      <button class="btn btn-primary w-100">Создать</button>
    </div>
  </form>

  <div v-if="profileStore.isManager">
    <table class="table table-hover align-middle shadow-sm bg-white">
      <thead class="table-dark">
        <tr>
          <th>Постер</th>
          <th>Дата</th>
          <th>Игра</th>
          <th>Место</th>
          <th>Статус</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <SessionTableRow
          v-for="s in sortedSessions"
          :key="s.id"
          :session="s"
          :venue-name="venueName(s.venue)"
          :game-mode-name="gameModeName(s.game_mode)"
          :is-past="isPast(s)"
          @edit="openEditModal"
          @cancel="cancelSession"
          @remove="onRemoveClick"
          @open-image="openImageModal"
        />
      </tbody>
    </table>
  </div>

  <div v-else class="row">
    <div class="col-md-4 mb-3" v-for="s in sortedSessions" :key="s.id">
      <SessionCard
        :session="s"
        :venue-name="venueName(s.venue)"
        :game-mode-name="gameModeName(s.game_mode)"
        :is-booked="!!myBooking(s.id)"
        @book="handleBookClick"
        @open-image="openImageModal"
      />
    </div>
  </div>

  <BookingModal
    v-if="showBookingModal"
    :session="selectedSession"
    :booked-users="selectedSession?.booked_users || []"
    :is-booked-by-me="!!myBooking(selectedSession?.id)"
    :venue-name="venueName(selectedSession?.venue)"
    :game-mode-name="gameModeName(selectedSession?.game_mode)"
    @close="showBookingModal = false"
    @book="bookPlace"
    @cancel="cancelBooking"
  />

  <SessionEditModal
    v-if="showEditModal"
    :session="sessionToEdit"
    :venues="venues"
    :game-modes="gameModes"
    @close="showEditModal = false"
    @save="handleSaveSession"
  />

  <ImageModal
    v-if="showImageModal"
    :url="selectedImageForModal"
    @close="showImageModal = false"
  />

  <div v-if="showAddModeModal" class="modal fade show d-block" style="background: rgba(0,0,0,0.5);" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Новый режим игры</h5>
          <button type="button" class="btn-close" @click="showAddModeModal = false"></button>
        </div>
        <div class="modal-body">
          <label class="form-label">Название режима</label>
          <input v-model="newGameModeName" class="form-control" placeholder="Например: Городская мафия" />
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showAddModeModal = false">Отмена</button>
          <button class="btn btn-primary" @click="addGameMode">Добавить</button>
        </div>
      </div>
    </div>
  </div>
</template>