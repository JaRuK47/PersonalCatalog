<script setup>
import { onMounted, ref, watch } from 'vue';
import axios from 'axios';

const rounds = ref([]);
const sessions = ref([]);
const users = ref([]); // Нам понадобятся пользователи для добавления в партию

// Данные новой партии
const roundToAdd = ref({ session: null, number: 1, start_time: '' });

// Массив игроков, которых мы добавляем прямо в форме
const playersToAdd = ref([]);

async function fetchAll() {
  const [r, s, u] = await Promise.all([
    axios.get('/api/rounds/'),
    axios.get('/api/sessions/'),
    axios.get('/api/users/'),
  ]);
  rounds.value = r.data;
  sessions.value = s.data;
  users.value = u.data;
}

// Автонумерация партии
watch(() => roundToAdd.value.session, (newSessionId) => {
  if (!newSessionId) return;
  const sessionRounds = rounds.value.filter(r => r.session === newSessionId);
  if (sessionRounds.length > 0) {
    const maxNumber = Math.max(...sessionRounds.map(r => r.number));
    roundToAdd.value.number = maxNumber + 1;
  } else {
    roundToAdd.value.number = 1;
  }
});

// Добавить пустую строку для ввода нового игрока
function addPlayerRow() {
  playersToAdd.value.push({ user: null, role: 'Мирный', points: 0, won: false });
}

// Удалить игрока из формы (если ошиблись)
function removePlayerRow(index) {
  playersToAdd.value.splice(index, 1);
}

async function onRoundAdd() {
  try {
    // 1. Создаем саму партию
    // Если время не выбрано (пустая строка), отправляем null, чтобы Django не ругался
    const roundPayload = { ...roundToAdd.value };
    if (!roundPayload.start_time) roundPayload.start_time = null;

    const roundResponse = await axios.post('/api/rounds/', roundPayload);
    const newRoundId = roundResponse.data.id;

    // 2. Если в форме есть игроки, создаем их по очереди
    // (Используем Promise.all, чтобы они отправлялись одновременно)
    if (playersToAdd.value.length > 0) {
      const playerPromises = playersToAdd.value.map(player => {
        return axios.post('/api/round-players/', {
          ...player,
          round: newRoundId // Привязываем к только что созданной партии
        });
      });
      await Promise.all(playerPromises);
    }

    // 3. Очищаем форму и обновляем список
    roundToAdd.value = { session: null, number: 1, start_time: '' };
    playersToAdd.value = [];
    await fetchAll();
    alert('Партия и игроки успешно сохранены!');

  } catch (e) {
    // ПРАВИЛЬНАЯ ОБРАБОТКА ОШИБОК
    if (e.response && e.response.data) {
      const errors = e.response.data;
      // Если ошибка в полях session или number — значит это дубликат
      if (errors.session || errors.number || errors.non_field_errors) {
        alert('Ошибка: Партия с таким номером уже существует в этой сессии!');
      } else {
        // Если другие поля (например, время или роль) — выводим текст ошибки
        alert('Ошибка валидации: ' + JSON.stringify(errors));
      }
    } else {
      alert('Произошла неизвестная ошибка');
    }
  }
}

async function onRemoveClick(round) {
  if (!confirm(`Удалить партию #${round.number}? Все результаты игроков тоже удалятся.`)) return;
  await axios.delete(`/api/rounds/${round.id}/`);
  await fetchAll();
}

function sessionLabel(id) {
  const s = sessions.value.find(x => x.id === id);
  return s ? `${s.date} ${s.start_time}` : id;
}

onMounted(fetchAll);
</script>

<template>
  <h1>Партии</h1>

  <div class="card mb-4 shadow-sm">
    <div class="card-header bg-primary text-white">
      Создание новой партии
    </div>
    <div class="card-body">
      <form @submit.prevent="onRoundAdd">
        <!-- Основные данные партии -->
        <div class="row g-2 mb-3 align-items-end">
          <div class="col-md-5">
            <label class="form-label">Сессия</label>
            <select v-model.number="roundToAdd.session" class="form-select" required>
              <option disabled :value="null">Выберите сессию</option>
              <option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.date }} {{ s.start_time }}</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Номер партии</label>
            <input v-model.number="roundToAdd.number" type="number" class="form-control" required />
          </div>
          <div class="col-md-3">
            <label class="form-label">Время начала (необязательно)</label>
            <input v-model="roundToAdd.start_time" type="time" class="form-control" />
          </div>
        </div>

        <hr>
        <h5>Игроки в этой партии</h5>

        <div v-if="playersToAdd.length === 0" class="text-muted mb-2">
          Пока никто не добавлен. Нажмите кнопку ниже.
        </div>

        <!-- Строки с игроками -->
        <div v-for="(p, index) in playersToAdd" :key="index" class="row g-2 mb-2 align-items-center">
          <div class="col-md-3">
            <select v-model.number="p.user" class="form-select" required>
              <option disabled :value="null">Игрок</option>
              <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
            </select>
          </div>
          <div class="col-md-3">
            <input v-model="p.role" class="form-control" placeholder="Роль (Мафия, Шериф)" required />
          </div>
          <div class="col-md-2">
            <input v-model.number="p.points" type="number" class="form-control" placeholder="Очки" />
          </div>
          <div class="col-md-2 form-check ms-2">
            <input v-model="p.won" class="form-check-input" type="checkbox" :id="'won_' + index">
            <label class="form-check-label" :for="'won_' + index">Победа</label>
          </div>
          <div class="col-md-1">
            <button type="button" class="btn btn-outline-danger btn-sm w-100" @click="removePlayerRow(index)">
              ✕
            </button>
          </div>
        </div>

        <div class="mt-3">
          <button type="button" class="btn btn-outline-secondary me-2" @click="addPlayerRow">
            + Добавить игрока
          </button>
          <button type="submit" class="btn btn-success">
            Сохранить партию
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Таблица созданных партий -->
  <h3>Сыгранные партии</h3>
  <table class="table table-striped">
    <thead>
      <tr><th>ID</th><th>Сессия</th><th>Номер партии</th><th>Время</th><th></th></tr>
    </thead>
    <tbody>
      <tr v-for="r in rounds" :key="r.id">
        <td>{{ r.id }}</td>
        <td>{{ sessionLabel(r.session) }}</td>
        <td><b>Партия #{{ r.number }}</b></td>
        <td>{{ r.start_time || '—' }}</td>
        <td>
          <button class="btn btn-sm btn-danger" @click="onRemoveClick(r)">Удалить</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>