<script setup>
import { onMounted, ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';

const route = useRoute();
const router = useRouter();
const profileStore = useProfileStore();

const players = ref([]);
const users = ref([]);
const roundInfo = ref({});
const allBookings = ref([]);
const allRounds = ref([]);
const allRoundPlayers = ref([]);

const newPlayer = ref({ user: null, role: 'Мирный', points: 0.0, won: false, description: '' });
const playerToEdit = ref({});
const searchQuery = ref('');

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value;
  return users.value.filter(u =>
    u.username.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

async function fetchData() {
  const roundId = route.params.id;
  const [r, p, u, b, ar, arp] = await Promise.all([
    axios.get(`/api/rounds/${roundId}/`),
    axios.get(`/api/round-players/`),
    axios.get('/api/users/'),
    axios.get('/api/bookings/'),
    axios.get('/api/rounds/'),
    axios.get('/api/round-players/')
  ]);

  roundInfo.value = r.data;
  players.value = p.data.filter(x => x.round == roundId);
  users.value = u.data;
  allBookings.value = b.data;
  allRounds.value = ar.data;
  allRoundPlayers.value = arp.data;
}

async function addPlayer() {
  const isAlreadyAdded = players.value.some(p => p.user === newPlayer.value.user);
  if (isAlreadyAdded) {
    alert('Этот игрок уже добавлен в партию!');
    return;
  }

  try {
    await axios.post('/api/round-players/', { ...newPlayer.value, round: route.params.id });
    newPlayer.value = { user: null, role: 'Мирный', points: 0.0, won: false, description: '' };
    searchQuery.value = '';
    await fetchData();
  } catch (e) {
    alert('Ошибка при добавлении игрока');
  }
}

async function addFromBookings() {
  if (!confirm('Добавить всех игроков, забронировавших эту сессию?')) return;

  const sessionBookings = allBookings.value.filter(
    b => b.session === roundInfo.value.session && (b.status === 'active' || b.status === 'attended')
  );

  const playersToAdd = sessionBookings.filter(
    b => !players.value.some(p => p.user === b.user)
  );

  if (playersToAdd.length === 0) {
    alert('Все забронированные игроки уже добавлены в партию!');
    return;
  }

  for (let b of playersToAdd) {
    await axios.post('/api/round-players/', {
      round: route.params.id, user: b.user, role: 'Мирный', points: 0, won: false
    });
  }
  await fetchData();
}

async function copyFromPreviousRound() {
  const currentNumber = roundInfo.value.number;
  if (currentNumber <= 1) {
    alert('Это первая партия в сессии, копировать нечего.');
    return;
  }

  const prevRound = allRounds.value.find(
    r => r.session === roundInfo.value.session && r.number === currentNumber - 1
  );

  if (!prevRound) {
    alert('Предыдущая партия не найдена.');
    return;
  }

  if (!confirm(`Скопировать игроков из Партии #${prevRound.number}?`)) return;

  const prevPlayers = allRoundPlayers.value.filter(rp => rp.round === prevRound.id);
  const playersToAdd = prevPlayers.filter(
    pp => !players.value.some(p => p.user === pp.user)
  );

  if (playersToAdd.length === 0) {
    alert('Все игроки из прошлой партии уже добавлены!');
    return;
  }

  for (let p of playersToAdd) {
    await axios.post('/api/round-players/', {
      round: route.params.id, user: p.user, role: 'Мирный', points: 0, won: false
    });
  }
  await fetchData();
}

function onEditClick(p) { playerToEdit.value = { ...p }; }
async function updatePlayer() {
  await axios.put(`/api/round-players/${playerToEdit.value.id}/`, playerToEdit.value);
  await fetchData();
}

async function removePlayer(id) {
  if(!confirm('Удалить игрока?')) return;
  await axios.delete(`/api/round-players/${id}/`);
  await fetchData();
}

function userName(id) { return users.value.find(u => u.id === id)?.username || id; }

onMounted(fetchData);
</script>

<template>
  <div>
    <button @click="router.push('/rounds')" class="btn btn-sm btn-outline-secondary mb-3">← Назад к партиям</button>
    <h1>Партия #{{ roundInfo.number }}</h1>
    <p>{{ roundInfo.description }}</p>

    <div v-if="profileStore.isManager" class="mb-3">
      <button class="btn btn-info text-white me-2" @click="addFromBookings">➕ Взять из броней сессии</button>
      <button class="btn btn-secondary" @click="copyFromPreviousRound">📋 Скопировать из партии #{{ roundInfo.number - 1 }}</button>
    </div>

    <form v-if="profileStore.isManager" @submit.prevent="addPlayer" class="row g-2 mb-4 bg-light p-3 rounded shadow-sm align-items-end">
      <div class="col-md-2">
        <label class="form-label small mb-0">Поиск игрока</label>
        <input v-model="searchQuery" type="text" class="form-control" placeholder="Начните вводить..." />
      </div>
      <div class="col-md-2">
        <label class="form-label small mb-0">Игрок</label>
        <select v-model.number="newPlayer.user" class="form-select" required>
          <option disabled :value="null">Выбрать</option>
          <option v-for="u in filteredUsers" :key="u.id" :value="u.id">{{ u.username }}</option>
        </select>
      </div>
      <div class="col-md-2">
        <label class="form-label small mb-0">Роль</label>
        <input v-model="newPlayer.role" class="form-control" required />
      </div>
      <div class="col-md-2">
        <label class="form-label small mb-0">Очки</label>
        <input v-model.number="newPlayer.points" type="number" step="0.1" class="form-control" />
      </div>
      <div class="col-md-2">
        <label class="form-label small mb-0">За что баллы?</label>
        <input v-model="newPlayer.description" class="form-control" />
      </div>
      <div class="col-md-1 form-check ms-2 mb-2">
        <input v-model="newPlayer.won" class="form-check-input" type="checkbox" id="newWon">
        <label class="form-check-label" for="newWon">Победа</label>
      </div>
      <div class="col-md-1">
        <button class="btn btn-primary w-100">Доб.</button>
      </div>
    </form>

    <div class="row">
      <div class="col-md-6" v-for="p in players" :key="p.id">
        <div class="card mb-2 shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h5 class="mb-0">{{ userName(p.user) }}</h5>
                <small class="text-muted">Роль: {{ p.role }}</small>
                <p class="mb-0 mt-1 small">{{ p.description }}</p>
              </div>
              <div class="text-end">
                <span class="badge bg-primary fs-6">{{ p.points }} очков</span>
                <span v-if="p.won" class="badge bg-success ms-2">Победа</span>
                <span v-else class="badge bg-secondary ms-2">Проигрыш</span>
                <div v-if="profileStore.isManager" class="mt-2">
                  <button class="btn btn-sm btn-success me-1" data-bs-toggle="modal" data-bs-target="#editPlayerModal" @click="onEditClick(p)">Ред.</button>
                  <button class="btn btn-sm btn-danger" @click="removePlayer(p.id)">Удал.</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="editPlayerModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">Редактировать игрока</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <div class="modal-body">
          <input v-model="playerToEdit.role" class="form-control mb-2" placeholder="Роль" />
          <input v-model.number="playerToEdit.points" type="number" step="0.1" class="form-control mb-2" placeholder="Очки" />
          <textarea v-model="playerToEdit.description" class="form-control mb-2" placeholder="Описание"></textarea>
          <div class="form-check">
            <input v-model="playerToEdit.won" class="form-check-input" type="checkbox" id="editWon">
            <label class="form-check-label" for="editWon">Победа</label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button class="btn btn-primary" data-bs-dismiss="modal" @click="updatePlayer">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>