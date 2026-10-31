<script setup>
import { onMounted, ref, computed } from 'vue';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';
import { useRouter } from 'vue-router';

const router = useRouter();
const profileStore = useProfileStore();
const rounds = ref([]);
const sessions = ref([]);
const users = ref([]);
const gameModes = ref([]);

const roundToAdd = ref({ session: null, number: 1, host: null, game_mode: null, description: '' });
const roundToEdit = ref({});

const searchSession = ref('');
const searchHost = ref('');

async function fetchAll() {
  const [r, s, u, g] = await Promise.all([
    axios.get('/api/rounds/'),
    axios.get('/api/sessions/'),
    axios.get('/api/users/'),
    axios.get('/api/game-modes/')
  ]);
  rounds.value = r.data;
  sessions.value = s.data;
  users.value = u.data;
  gameModes.value = g.data;
}

const availableSessions = computed(() => {
  const today = new Date().toISOString().split('T')[0];
  let list = sessions.value.filter(s => s.date <= today);

  if (searchSession.value) {
    const q = searchSession.value.toLowerCase();
    list = list.filter(s => s.date.includes(q) || s.title.toLowerCase().includes(q));
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
    await fetchAll();
  } catch (e) {
    alert('Ошибка! Партия с таким номером уже существует.');
  }
}

function onEditClick(r) { roundToEdit.value = { ...r }; }
async function onUpdateRound() {
  try {
    await axios.put(`/api/rounds/${roundToEdit.value.id}/`, roundToEdit.value);
    await fetchAll();
  } catch (e) {
    alert('Ошибка! Партия с таким номером уже существует.');
  }
}

async function onRemoveClick(r) {
  if(!confirm('Удалить партию?')) return;
  await axios.delete(`/api/rounds/${r.id}/`);
  await fetchAll();
}

const groupedRounds = computed(() => {
  const groups = {};
  rounds.value.forEach(r => {
    const s = sessions.value.find(x => x.id === r.session);
    const label = s ? `${s.date} ${s.start_time} (${s.title})` : 'Без сессии';
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

onMounted(fetchAll);
</script>

<template>
  <h1>Партии</h1>

  <form v-if="profileStore.isManager" @submit.prevent="onRoundAdd" class="row g-2 mb-4 bg-light p-3 rounded shadow-sm align-items-end">
    <div class="col-md-2">
      <label class="form-label small mb-0">Поиск сессии</label>
      <input v-model="searchSession" type="text" class="form-control" placeholder="Дата..." />
    </div>
    <div class="col-md-3">
      <label class="form-label small mb-0">Сессия</label>
      <select v-model.number="roundToAdd.session" class="form-select" required>
        <option disabled :value="null">Выбрать</option>
        <option v-for="s in availableSessions" :key="s.id" :value="s.id">{{ s.date }} ({{ s.title }})</option>
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
    <div class="col-md-2">
      <label class="form-label small mb-0">Ведущий</label>
      <select v-model.number="roundToAdd.host" class="form-select" required>
        <option disabled :value="null">Выбрать</option>
        <option v-for="u in availableHosts" :key="u.id" :value="u.id">{{ u.username }}</option>
      </select>
    </div>
    <div class="col-md-2">
      <label class="form-label small mb-0">Режим</label>
      <select v-model.number="roundToAdd.game_mode" class="form-select" required>
        <option disabled :value="null">Выбрать</option>
        <option v-for="g in gameModes" :key="g.id" :value="g.id">{{ g.name }}</option>
      </select>
    </div>
    <div class="col-md-10 mt-2">
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
        <div class="card shadow-sm h-100 border-primary">
          <div class="card-body text-center d-flex flex-column">
            <h5 class="card-title">Партия #{{ r.number }}</h5>
            <p class="card-text small mb-1">Режим: <b>{{ gameModeName(r.game_mode) }}</b></p>
            <p class="card-text text-muted small mb-3">Ведущий: {{ userName(r.host) }}</p>
            <button class="btn btn-sm btn-outline-primary mt-auto" @click="router.push('/rounds/' + r.id)">Статистика</button>
            <div v-if="profileStore.isManager" class="mt-2 d-flex justify-content-between">
              <button class="btn btn-sm btn-success w-50 me-1" data-bs-toggle="modal" data-bs-target="#editRoundModal" @click="onEditClick(r)">Ред.</button>
              <button class="btn btn-sm btn-danger w-50" @click="onRemoveClick(r)">Удал.</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="editRoundModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">Редактировать партию</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <div class="modal-body">
          <select v-model.number="roundToEdit.session" class="form-select mb-2">
            <option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.date }} ({{ s.title }})</option>
          </select>
          <input v-model.number="roundToEdit.number" type="number" class="form-control mb-2" />
          <select v-model.number="roundToEdit.host" class="form-select mb-2">
            <option :value="null">Без ведущего</option>
            <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
          </select>
          <select v-model.number="roundToEdit.game_mode" class="form-select mb-2">
            <option v-for="g in gameModes" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
          <textarea v-model="roundToEdit.description" class="form-control" placeholder="Описание"></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateRound">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>