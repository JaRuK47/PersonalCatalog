<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';

const players = ref([]);
const rounds = ref([]);
const users = ref([]);
const sessions = ref([]);
const playerToAdd = ref({ round: null, user: null, role: 'Мирный', points: 0, won: false });

async function fetchAll() {
  const [p, r, u, s] = await Promise.all([
    axios.get('/api/round-players/'),
    axios.get('/api/rounds/'),
    axios.get('/api/users/'),
    axios.get('/api/sessions/'),
  ]);
  players.value = p.data;
  rounds.value = r.data;
  users.value = u.data;
  sessions.value = s.data;
}

async function onPlayerAdd() {
  await axios.post('/api/round-players/', playerToAdd.value);
  // Очищаем форму, но оставляем выбранную партию (чтобы удобно было добавлять следующих)
  playerToAdd.value = { round: playerToAdd.value.round, user: null, role: 'Мирный', points: 0, won: false };
  await fetchAll();
}

async function onRemoveClick(player) {
  await axios.delete(`/api/round-players/${player.id}/`);
  await fetchAll();
}

function userName(id) { return users.value.find(u => u.id === id)?.username || id; }

// Красиво выводим название партии: "2026-10-25 — Партия #1"
function roundLabel(id) {
  const r = rounds.value.find(x => x.id === id);
  if (!r) return id;
  const s = sessions.value.find(x => x.id === r.session);
  const sessionDate = s ? s.date : 'Неизвестная сессия';
  return `${sessionDate} — Партия #${r.number}`;
}

onMounted(fetchAll);
</script>

<template>
  <h1>Результаты партий</h1>
  <p class="text-muted">Здесь вы вносите, кто играл в партии и с какими результатами.</p>

  <form @submit.prevent="onPlayerAdd" class="row g-2 mb-4 bg-light p-3 rounded">
    <div class="col-md-4">
      <label class="form-label">Партия</label>
      <select v-model.number="playerToAdd.round" class="form-select" required>
        <option disabled :value="null">Выберите партию</option>
        <option v-for="r in rounds" :key="r.id" :value="r.id">{{ roundLabel(r.id) }}</option>
      </select>
    </div>
    <div class="col-md-3">
      <label class="form-label">Игрок</label>
      <select v-model.number="playerToAdd.user" class="form-select" required>
        <option disabled :value="null">Кто играл?</option>
        <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
      </select>
    </div>
    <div class="col-md-2">
      <label class="form-label">Роль</label>
      <input v-model="playerToAdd.role" class="form-control" placeholder="Мафия, Шериф..." required />
    </div>
    <div class="col-md-1">
      <label class="form-label">Очки</label>
      <input v-model.number="playerToAdd.points" type="number" class="form-control" />
    </div>
    <div class="col-md-1 d-flex align-items-end pb-2">
      <div class="form-check">
        <input v-model="playerToAdd.won" class="form-check-input" type="checkbox" id="wonCheck">
        <label class="form-check-label" for="wonCheck">Победа</label>
      </div>
    </div>
    <div class="col-md-1 d-flex align-items-end">
      <button class="btn btn-primary w-100">Добавить</button>
    </div>
  </form>

  <table class="table table-striped">
    <thead>
      <tr><th>ID</th><th>Партия</th><th>Игрок</th><th>Роль</th><th>Очки</th><th>Победа</th><th></th></tr>
    </thead>
    <tbody>
      <tr v-for="p in players" :key="p.id">
        <td>{{ p.id }}</td>
        <td>{{ roundLabel(p.round) }}</td>
        <td>{{ userName(p.user) }}</td>
        <td>{{ p.role }}</td>
        <td>{{ p.points }}</td>
        <td>
          <span v-if="p.won" class="badge bg-success">Да</span>
          <span v-else class="badge bg-secondary">Нет</span>
        </td>
        <td>
          <button class="btn btn-sm btn-danger" @click="onRemoveClick(p)">Удалить</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>