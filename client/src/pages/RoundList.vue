<script setup>
import { onMounted, ref, computed, watch } from 'vue';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';
import { useRouter } from 'vue-router';
import RoundCard from '@/components/rounds/RoundCard.vue';
import RoundEditModal from '@/components/modals/RoundEditModal.vue';
import { downloadExcel } from '@/utils/excel';

const router = useRouter();
const profileStore = useProfileStore();

const rounds = ref([]);
const sessions = ref([]);
const users = ref([]);
const venues = ref([]);
const gameModes = ref([]);
const roundStats = ref({ count: 0, mafia_wins: 0, town_wins: 0 });

const roundToAdd = ref({ session: null, number: 1, host: null, game_mode: null, description: '' });
const showEditModal = ref(false);
const roundToEdit = ref({});

const filterSession = ref('');
const filterHost = ref('');
const filterGameMode = ref('');
const searchSessionVenue = ref('');
const searchHost = ref('');

async function fetchDependencies() {
  const [s, u, g, v] = await Promise.all([
    axios.get('/api/sessions/'),
    axios.get('/api/users/'),
    axios.get('/api/game-modes/'),
    axios.get('/api/venues/')
  ]);
  sessions.value = s.data;
  users.value = u.data;
  gameModes.value = g.data;
  venues.value = v.data;
}

function buildQueryString() {
  const params = new URLSearchParams();
  if (filterSession.value) params.append('session', filterSession.value);
  if (filterHost.value) params.append('host', filterHost.value);
  if (filterGameMode.value) params.append('game_mode', filterGameMode.value);
  return params.toString();
}

async function fetchRounds() {
  const query = buildQueryString();
  const url = `/api/rounds/${query ? '?' + query : ''}`;
  const r = await axios.get(url);
  rounds.value = r.data;
}

async function fetchStats() {
  const query = buildQueryString();
  const url = `/api/rounds/stats/${query ? '?' + query : ''}`;
  const r = await axios.get(url);
  roundStats.value = r.data;
}

watch([filterSession, filterHost, filterGameMode], () => {
  fetchRounds();
  fetchStats();
});

function resetFilters() {
  filterSession.value = '';
  filterHost.value = '';
  filterGameMode.value = '';
}

const availableSessions = computed(() => {
  const today = new Date().toISOString().split('T')[0];
  let list = sessions.value.filter(s => s.date <= today);

  if (searchSessionVenue.value) {
    list = list.filter(s => s.venue === searchSessionVenue.value);
  }

  return list.sort((a, b) => new Date(`${b.date}T${b.start_time}`) - new Date(`${a.date}T${a.start_time}`));
});

const availableHosts = computed(() => {
  if (!searchHost.value) return users.value;
  const q = searchHost.value.toLowerCase();
  return users.value.filter(u => u.username.toLowerCase().includes(q));
});

async function onRoundAdd() {
  try {
    await axios.post('/api/rounds/', roundToAdd.value);
    roundToAdd.value = { session: null, number: 1, host: null, game_mode: null, description: '' };
    await fetchRounds();
    await fetchStats();
  } catch (e) {
    alert('Ошибка! Партия с таким номером уже существует.');
  }
}

function openEditModal(r) { roundToEdit.value = r; showEditModal.value = true; }
async function handleSaveRound(form) {
  try {
    await axios.put(`/api/rounds/${form.id}/`, form);
    showEditModal.value = false;
    await fetchRounds();
    await fetchStats();
  } catch (e) {
    alert('Ошибка! Партия с таким номером уже существует.');
  }
}

async function onRemoveClick(r) {
  if(!confirm('Удалить партию?')) return;
  await axios.delete(`/api/rounds/${r.id}/`);
  await fetchRounds();
  await fetchStats();
}

function goToRound(r) { router.push('/rounds/' + r.id); }

const groupedRounds = computed(() => {
  const groups = {};
  rounds.value.forEach(r => {
    const s = sessions.value.find(x => x.id === r.session);
    const v = venues.value.find(x => x.id === s?.venue)?.name || '';
    const label = s ? `${s.date} ${s.start_time} (${s.title}) [${v}]` : 'Без сессии';
    if (!groups[label]) groups[label] = [];
    groups[label].push(r);
  });
  const result = {};
  Object.keys(groups).sort().reverse().forEach(key => {
    result[key] = groups[key].sort((a, b) => a.number - b.number);
  });
  return result;
});

function userName(id) { return users.value.find(u => u.id === id)?.username || 'Неизвестен'; }
function gameModeName(id) { return gameModes.value.find(g => g.id === id)?.name || '—'; }
function venueName(id) { return venues.value.find(v => v.id === id)?.name || '—'; }

onMounted(async () => {
  await fetchDependencies();
  await fetchRounds();
  await fetchStats();
});
</script>

<template>
  <h1>Партии</h1>

  <div class="row mb-4">
    <div class="col-md-4">
      <div class="card bg-primary text-white shadow-sm text-center py-3">
        <h5 class="mb-0">Найдено партий</h5>
        <h2 class="mb-0">{{ roundStats.count }}</h2>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card bg-dark text-white shadow-sm text-center py-3">
        <h5 class="mb-0">Побед Мафии</h5>
        <h2 class="mb-0">{{ roundStats.mafia_wins }}</h2>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card bg-success text-white shadow-sm text-center py-3">
        <h5 class="mb-0">Побед Мирных</h5>
        <h2 class="mb-0">{{ roundStats.town_wins }}</h2>
      </div>
    </div>
  </div>

  <div class="row g-2 mb-3 bg-white p-3 rounded shadow-sm align-items-end">
    <div class="col-md-3">
      <label class="form-label small mb-0 fw-bold">Сессия</label>
      <select v-model="filterSession" class="form-select">
        <option value="">Все сессии</option>
        <option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.date }} ({{ s.title }}) - {{ venueName(s.venue) }}</option>
      </select>
    </div>
    <div class="col-md-3">
      <label class="form-label small mb-0 fw-bold">Ведущий</label>
      <select v-model="filterHost" class="form-select">
        <option value="">Все ведущие</option>
        <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
      </select>
    </div>
    <div class="col-md-3">
      <label class="form-label small mb-0 fw-bold">Режим</label>
      <select v-model="filterGameMode" class="form-select">
        <option value="">Все режимы</option>
        <option v-for="g in gameModes" :key="g.id" :value="g.id">{{ g.name }}</option>
      </select>
    </div>
    <div class="col-md-3">
      <button class="btn btn-outline-secondary w-100" @click="resetFilters">Сбросить фильтры</button>
    </div>
    <div class="col-md-2">
      <button class="btn btn-success w-100" @click="downloadExcel(`/api/rounds/export/?${buildQueryString()}`, 'rounds_export.xlsx')">Экспорт в Excel</button>
    </div>
  </div>

  <form v-if="profileStore.isManager" @submit.prevent="onRoundAdd" class="row g-2 mb-4 bg-light p-3 rounded shadow-sm align-items-end">
    <div class="col-md-3">
      <label class="form-label small mb-0">Фильтр по локации</label>
      <select v-model="searchSessionVenue" class="form-select">
        <option value="">Все локации</option>
        <option v-for="v in venues" :key="v.id" :value="v.id">{{ v.name }}</option>
      </select>
    </div>
    <div class="col-md-3">
      <label class="form-label small mb-0">Сессия</label>
      <select v-model.number="roundToAdd.session" class="form-select" required>
        <option disabled :value="null">Выбрать</option>
        <option v-for="s in availableSessions" :key="s.id" :value="s.id">
          {{ s.date }} {{ s.start_time }} - {{ venueName(s.venue) }}
        </option>
      </select>
    </div>
    <div class="col-md-1">
      <label class="form-label small mb-0">Номер</label>
      <input v-model.number="roundToAdd.number" type="number" class="form-control" required />
    </div>
    <div class="col-md-2">
      <label class="form-label small mb-0">Поиск ведущего</label>
      <input v-model="searchHost" type="text" class="form-control" placeholder="Имя..." />
    </div>
    <div class="col-md-3">
      <label class="form-label small mb-0">Ведущий</label>
      <select v-model.number="roundToAdd.host" class="form-select" required>
        <option disabled :value="null">Выбрать</option>
        <option v-for="u in availableHosts" :key="u.id" :value="u.id">{{ u.username }}</option>
      </select>
    </div>
    <div class="col-md-4 mt-2">
      <label class="form-label small mb-0">Режим</label>
      <select v-model.number="roundToAdd.game_mode" class="form-select" required>
        <option disabled :value="null">Выбрать</option>
        <option v-for="g in gameModes" :key="g.id" :value="g.id">{{ g.name }}</option>
      </select>
    </div>
    <div class="col-md-6 mt-2">
      <label class="form-label small mb-0">Описание</label>
      <input v-model="roundToAdd.description" class="form-control" />
    </div>
    <div class="col-md-2 mt-2">
      <button class="btn btn-primary w-100">Добавить</button>
    </div>
  </form>

  <div v-for="(sessionRounds, sessionName) in groupedRounds" :key="sessionName" class="mb-5">
    <h4 class="border-bottom pb-2 text-secondary">Сессия: {{ sessionName }}</h4>
    <div class="row">
      <div class="col-md-3 mb-3" v-for="r in sessionRounds" :key="r.id">
        <RoundCard
          :round="r"
          :host-name="userName(r.host)"
          :game-mode-name="gameModeName(r.game_mode)"
          :is-manager="profileStore.isManager"
          @view="goToRound"
          @edit="openEditModal"
          @remove="onRemoveClick"
        />
      </div>
    </div>
  </div>

  <RoundEditModal
    v-if="showEditModal"
    :round="roundToEdit"
    :sessions="sessions"
    :users="users"
    :game-modes="gameModes"
    @close="showEditModal = false"
    @save="handleSaveRound"
  />
</template>