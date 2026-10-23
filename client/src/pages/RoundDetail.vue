<script setup>
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';

const route = useRoute();
const router = useRouter();
const profileStore = useProfileStore();
const players = ref([]);
const users = ref([]);
const roundInfo = ref({});

const newPlayer = ref({ user: null, role: 'Мирный', points: 0.0, won: false, description: '' });
const playerToEdit = ref({});

async function fetchData() {
  const roundId = route.params.id;
  const [r, p, u] = await Promise.all([
    axios.get(`/api/rounds/${roundId}/`),
    axios.get(`/api/round-players/`),
    axios.get('/api/users/')
  ]);
  roundInfo.value = r.data;
  players.value = p.data.filter(x => x.round == roundId);
  users.value = u.data;
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
    await fetchData();
  } catch (e) {
    alert('Ошибка при добавлении игрока');
  }
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
    <h5 class="text-muted">{{ roundInfo.game_mode }}</h5>
    <p>{{ roundInfo.description }}</p>

    <form v-if="profileStore.isManager" @submit.prevent="addPlayer" class="row g-2 mb-4 bg-light p-3 rounded shadow-sm">
      <div class="col-md-3">
        <select v-model.number="newPlayer.user" class="form-select" required>
          <option disabled :value="null">Игрок</option>
          <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
        </select>
      </div>
      <div class="col-md-2"><input v-model="newPlayer.role" class="form-control" placeholder="Роль" required /></div>
      <div class="col-md-2"><input v-model.number="newPlayer.points" type="number" step="0.1" class="form-control" placeholder="Очки" /></div>
      <div class="col-md-3"><input v-model="newPlayer.description" class="form-control" placeholder="За что баллы?" /></div>
      <div class="col-md-1 form-check mt-2">
        <input v-model="newPlayer.won" class="form-check-input" type="checkbox" id="newWon">
        <label class="form-check-label" for="newWon">Победа</label>
      </div>
      <div class="col-md-1"><button class="btn btn-primary w-100">Доб.</button></div>
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
          <input v-model="playerToEdit.role" class="form-control mb-2" />
          <input v-model.number="playerToEdit.points" type="number" step="0.1" class="form-control mb-2" />
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