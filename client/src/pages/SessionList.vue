<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';

const sessions = ref([]);
const venues = ref([]);
const sessionToAdd = ref({ venue: null, date: '', start_time: '', status: 'Идёт набор', max_players: 11 });
const sessionToEdit = ref({});

async function fetchAll() {
  const [s, v] = await Promise.all([
    axios.get('/api/sessions/'),
    axios.get('/api/venues/'),
  ]);
  sessions.value = s.data;
  venues.value = v.data;
}

async function onSessionAdd() {
  await axios.post('/api/sessions/', sessionToAdd.value);
  sessionToAdd.value = { venue: null, date: '', start_time: '', status: 'Идёт набор', max_players: 11 };
  await fetchAll();
}

function onSessionEditClick(session) {
  sessionToEdit.value = { ...session };
}

async function onUpdateSession() {
  await axios.put(`/api/sessions/${sessionToEdit.value.id}/`, sessionToEdit.value);
  await fetchAll();
}

async function onRemoveClick(session) {
  await axios.delete(`/api/sessions/${session.id}/`);
  await fetchAll();
}

function venueName(id) {
  return venues.value.find(v => v.id === id)?.name || '—';
}

onMounted(fetchAll);
</script>

<template>
  <h1>Игровые сессии</h1>

  <form @submit.prevent="onSessionAdd" class="row g-2 mb-3">
    <div class="col">
      <select v-model.number="sessionToAdd.venue" class="form-select" required>
        <option disabled :value="null">Место</option>
        <option v-for="v in venues" :key="v.id" :value="v.id">{{ v.name }}</option>
      </select>
    </div>
    <div class="col">
      <input v-model="sessionToAdd.date" type="date" class="form-control" required />
    </div>
    <div class="col">
      <input v-model="sessionToAdd.start_time" type="time" class="form-control" required />
    </div>
    <div class="col-auto">
      <input v-model.number="sessionToAdd.max_players" type="number" class="form-control" placeholder="Игроков" />
    </div>
    <div class="col-auto">
      <button class="btn btn-primary">Добавить</button>
    </div>
  </form>

  <table class="table table-striped">
    <thead>
      <tr><th>ID</th><th>Дата</th><th>Время</th><th>Место</th><th>Статус</th><th>Игроков</th><th></th></tr>
    </thead>
    <tbody>
      <tr v-for="s in sessions" :key="s.id">
        <td>{{ s.id }}</td>
        <td>{{ s.date }}</td>
        <td>{{ s.start_time }}</td>
        <td>{{ venueName(s.venue) }}</td>
        <td>{{ s.status }}</td>
        <td>{{ s.max_players }}</td>
        <td>
          <button class="btn btn-sm btn-success me-1"
                  data-bs-toggle="modal"
                  data-bs-target="#editSessionModal"
                  @click="onSessionEditClick(s)">
            Изменить
          </button>
          <button class="btn btn-sm btn-danger" @click="onRemoveClick(s)">Удалить</button>
        </td>
      </tr>
    </tbody>
  </table>

  <div class="modal fade" id="editSessionModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать сессию</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <select v-model.number="sessionToEdit.venue" class="form-select mb-2">
            <option v-for="v in venues" :key="v.id" :value="v.id">{{ v.name }}</option>
          </select>
          <input v-model="sessionToEdit.date" type="date" class="form-control mb-2" />
          <input v-model="sessionToEdit.start_time" type="time" class="form-control mb-2" />
          <input v-model="sessionToEdit.status" class="form-control mb-2" placeholder="Статус" />
          <input v-model.number="sessionToEdit.max_players" type="number" class="form-control" placeholder="Игроков" />
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateSession">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>