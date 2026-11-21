<script setup>
import { onMounted, ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';
import RoundPlayerCard from '@/components/rounds/RoundPlayerCard.vue';
import RoundPlayerEditModal from '@/components/modals/RoundPlayerEditModal.vue';
import { downloadExcel } from '@/utils/excel';

const route = useRoute();
const router = useRouter();
const profileStore = useProfileStore();

const players = ref([]);
const users = ref([]);
const roundInfo = ref({});
const allBookings = ref([]);
const allRounds = ref([]);
const allRoundPlayers = ref([]);

const newPlayer = ref({ user: null, role: 'Мирный', points: 0.0, description: '' });
const showEditModal = ref(false);
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
    axios.get('/api/round-players/'),
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

async function updateWinningTeam(event) {
  const team = event.target.value;
  await axios.patch(`/api/rounds/${roundInfo.value.id}/`, { winning_team: team });
  await fetchData();
}

function isWinner(player) {
  if (!roundInfo.value.winning_team) return null;

  const mafiaRoles = ['Мафия', 'Дон'];
  const isMafia = mafiaRoles.includes(player.role);

  if (roundInfo.value.winning_team === 'mafia' && isMafia) return true;
  if (roundInfo.value.winning_team === 'town' && !isMafia) return true;
  return false;
}

async function addPlayer() {
  const isAlreadyAdded = players.value.some(p => p.user === newPlayer.value.user);
  if (isAlreadyAdded) {
    alert('Этот игрок уже добавлен в партию!');
    return;
  }

  try {
    await axios.post('/api/round-players/', { ...newPlayer.value, round: route.params.id });
    newPlayer.value = { user: null, role: 'Мирный', points: 0.0, description: '' };
    searchQuery.value = '';
    await fetchData();
  } catch (e) {
    alert('Ошибка при добавлении игрока');
  }
}

async function addFromBookings() {
  if (!confirm('Добавить всех игроков, забронировавших эту сессию?')) return;
  const sessionBookings = allBookings.value.filter(b => b.session === roundInfo.value.session && (b.status === 'active' || b.status === 'attended'));
  const playersToAdd = sessionBookings.filter(b => !players.value.some(p => p.user === b.user));
  if (playersToAdd.length === 0) { alert('Все уже добавлены!'); return; }

  for (let b of playersToAdd) {
    await axios.post('/api/round-players/', { round: route.params.id, user: b.user, role: 'Мирный', points: 0 });
  }
  await fetchData();
}

async function copyFromPreviousRound() {
  const currentNumber = roundInfo.value.number;
  if (currentNumber <= 1) { alert('Это первая партия.'); return; }
  const prevRound = allRounds.value.find(r => r.session === roundInfo.value.session && r.number === currentNumber - 1);
  if (!prevRound) { alert('Предыдущая не найдена.'); return; }
  if (!confirm(`Скопировать игроков из Партии #${prevRound.number}?`)) return;

  const prevPlayers = allRoundPlayers.value.filter(rp => rp.round === prevRound.id);
  const playersToAdd = prevPlayers.filter(pp => !players.value.some(p => p.user === pp.user));
  if (playersToAdd.length === 0) { alert('Все уже добавлены!'); return; }

  for (let p of playersToAdd) {
    await axios.post('/api/round-players/', { round: route.params.id, user: p.user, role: 'Мирный', points: 0 });
  }
  await fetchData();
}

function openEditModal(p) {
  playerToEdit.value = p;
  showEditModal.value = true;
}

async function handleSavePlayer(form) {
  await axios.put(`/api/round-players/${form.id}/`, form);
  showEditModal.value = false;
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

    <div class="mb-4 bg-white p-3 rounded shadow-sm border d-inline-block" v-if="profileStore.isManager">
      <label class="fw-bold me-2">Победившая сторона:</label>
      <select :value="roundInfo.winning_team" @change="updateWinningTeam" class="form-select d-inline-block w-auto">
        <option :value="null">Не выбрана</option>
        <option value="town">Победа Мирных (Шериф, Доктор, Мирные)</option>
        <option value="mafia">Победа Мафии (Мафия, Дон)</option>
      </select>
    </div>

    <div v-if="profileStore.isManager" class="mb-3">
      <button class="btn btn-info text-white me-2" @click="addFromBookings">Взять из броней сессии</button>
      <button class="btn btn-secondary" @click="copyFromPreviousRound">Скопировать из партии #{{ roundInfo.number - 1 }}</button>
      <button class="btn btn-success" @click="downloadExcel(`/api/round-players/export/?round=${route.params.id}`, 'round_players_export.xlsx')">Скачать Excel</button>
    </div>

    <form v-if="profileStore.isManager" @submit.prevent="addPlayer" class="row g-2 mb-4 bg-light p-3 rounded shadow-sm align-items-end">
      <div class="col-md-2">
        <label class="form-label small mb-0">Поиск игрока</label>
        <input v-model="searchQuery" type="text" class="form-control" placeholder="Имя..." />
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
        <select v-model="newPlayer.role" class="form-select" required>
          <option value="Мирный">Мирный</option>
          <option value="Мафия">Мафия</option>
          <option value="Дон">Дон</option>
          <option value="Шериф">Шериф</option>
          <option value="Доктор">Доктор</option>
        </select>
      </div>
      <div class="col-md-2">
        <label class="form-label small mb-0">Очки</label>
        <input v-model.number="newPlayer.points" type="number" step="0.1" class="form-control" />
      </div>
      <div class="col-md-3">
        <label class="form-label small mb-0">За что баллы?</label>
        <input v-model="newPlayer.description" class="form-control" />
      </div>
      <div class="col-md-1">
        <button class="btn btn-primary w-100">Доб.</button>
      </div>
    </form>

    <div class="row">
      <div class="col-md-6" v-for="p in players" :key="p.id">
        <RoundPlayerCard
          :player="p"
          :user-name="userName(p.user)"
          :is-manager="profileStore.isManager"
          :win-status="isWinner(p)"
          @edit="openEditModal"
          @remove="removePlayer"
        />
      </div>
    </div>
  </div>

  <RoundPlayerEditModal
    v-if="showEditModal"
    :player="playerToEdit"
    @close="showEditModal = false"
    @save="handleSavePlayer"
  />
</template>