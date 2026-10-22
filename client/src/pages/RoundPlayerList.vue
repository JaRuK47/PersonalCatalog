<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';

const profileStore = useProfileStore();
const players = ref([]);
const rounds = ref([]);
const users = ref([]);
const playerToAdd = ref({ round: null, user: null, role: 'Мирный', points: 0, won: false });

async function fetchAll() {
  const [p, r, u] = await Promise.all([
    axios.get('/api/round-players/'),
    axios.get('/api/rounds/'),
    axios.get('/api/users/'),
  ]);
  players.value = p.data; rounds.value = r.data; users.value = u.data;
}

async function onPlayerAdd() {
  await axios.post('/api/round-players/', playerToAdd.value);
  playerToAdd.value = { ...playerToAdd.value, user: null, role: 'Мирный', points: 0, won: false };
  await fetchAll();
}

function userName(id) { return users.value.find(u => u.id === id)?.username || id; }
function roundLabel(id) { const r = rounds.value.find(x => x.id === id); return r ? `Партия #${r.number}` : id; }

onMounted(fetchAll);
</script>

<template>
  <div v-if="profileStore.isManager">
    <h1>Результаты партий</h1>

    <form @submit.prevent="onPlayerAdd" class="row g-2 mb-4 bg-light p-3 rounded">
      <div class="col-md-4">
        <select v-model.number="playerToAdd.round" class="form-select" required>
          <option disabled :value="null">Выберите партию</option>
          <option v-for="r in rounds" :key="r.id" :value="r.id">{{ roundLabel(r.id) }}</option>
        </select>
      </div>
      <div class="col-md-3">
        <select v-model.number="playerToAdd.user" class="form-select" required>
          <option disabled :value="null">Игрок</option>
          <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
        </select>
      </div>
      <div class="col-md-2"><input v-model="playerToAdd.role" class="form-control" required /></div>
      <div class="col-md-1"><input v-model.number="playerToAdd.points" type="number" class="form-control" /></div>
      <div class="col-md-2"><button class="btn btn-primary w-100">Добавить</button></div>
    </form>

    <table class="table table-striped">
      <thead><tr><th>Партия</th><th>Игрок</th><th>Роль</th><th>Очки</th><th>Победа</th></tr></thead>
      <tbody>
        <tr v-for="p in players" :key="p.id">
          <td>{{ roundLabel(p.round) }}</td>
          <td>{{ userName(p.user) }}</td>
          <td>{{ p.role }}</td>
          <td>{{ p.points }}</td>
          <td>{{ p.won ? 'Да' : 'Нет' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>