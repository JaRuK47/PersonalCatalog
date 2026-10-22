<script setup>
import { onMounted, ref, computed } from 'vue';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';
import { useRouter } from 'vue-router';

const router = useRouter();
const profileStore = useProfileStore();
const rounds = ref([]);
const sessions = ref([]);
const roundToAdd = ref({ session: null, number: 1, description: '' });
const roundToEdit = ref({});

async function fetchAll() {
  const [r, s] = await Promise.all([axios.get('/api/rounds/'), axios.get('/api/sessions/')]);
  rounds.value = r.data;
  sessions.value = s.data;
}

async function onRoundAdd() {
  try {
    await axios.post('/api/rounds/', roundToAdd.value);
    roundToAdd.value = { session: null, number: 1, description: '' };
    await fetchAll();
  } catch (e) {
    alert('Ошибка: Партия с таким номером уже существует в этой сессии!');
  }
}

function onEditClick(r) { roundToEdit.value = { ...r }; }
async function onUpdateRound() {
  try {
    await axios.put(`/api/rounds/${roundToEdit.value.id}/`, roundToEdit.value);
    await fetchAll();
  } catch (e) {
    alert('Ошибка: Партия с таким номером уже существует!');
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
    const label = s ? `${s.date} ${s.start_time}` : 'Без сессии';
    if (!groups[label]) groups[label] = [];
    groups[label].push(r);
  });
  return groups;
});

onMounted(fetchAll);
</script>

<template>
  <h1>Партии</h1>
  <form v-if="profileStore.isManager" @submit.prevent="onRoundAdd" class="row g-2 mb-4 bg-light p-3 rounded">
    <div class="col-md-4">
      <select v-model.number="roundToAdd.session" class="form-select" required>
        <option disabled :value="null">Сессия</option>
        <option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.date }}</option>
      </select>
    </div>
    <div class="col-md-2"><input v-model.number="roundToAdd.number" type="number" class="form-control" required /></div>
    <div class="col-md-4"><input v-model="roundToAdd.description" class="form-control" placeholder="Описание" /></div>
    <div class="col-md-2"><button class="btn btn-primary w-100">Добавить</button></div>
  </form>

  <div v-for="(sessionRounds, sessionName) in groupedRounds" :key="sessionName" class="mb-4">
    <h4 class="border-bottom pb-2">Сессия: {{ sessionName }}</h4>
    <div class="row">
      <div class="col-md-3 mb-3" v-for="r in sessionRounds" :key="r.id">
        <div class="card shadow-sm h-100 border-primary">
          <div class="card-body text-center">
            <h5 class="card-title">Партия #{{ r.number }}</h5>
            <button class="btn btn-sm btn-outline-primary mt-2" @click="router.push('/rounds/' + r.id)">Статистика</button>
            <div v-if="profileStore.isManager" class="mt-2">
              <button class="btn btn-sm btn-success me-1" data-bs-toggle="modal" data-bs-target="#editRoundModal" @click="onEditClick(r)">Ред.</button>
              <button class="btn btn-sm btn-danger" @click="onRemoveClick(r)">Удал.</button>
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
            <option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.date }}</option>
          </select>
          <input v-model.number="roundToEdit.number" type="number" class="form-control mb-2" />
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