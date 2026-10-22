<script setup>
import { onMounted, ref, computed } from 'vue';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';

const profileStore = useProfileStore();
const myBookings = ref([]);
const sessions = ref([]);
const venues = ref([]);

async function fetchData() {
  const [b, s, v] = await Promise.all([
    axios.get('/api/bookings/'),
    axios.get('/api/sessions/'),
    axios.get('/api/venues/')
  ]);
  myBookings.value = b.data.filter(x => x.user === profileStore.userId);
  sessions.value = s.data;
  venues.value = v.data;
}

async function cancelBooking(id) {
  if(!confirm('Вы уверены, что хотите отменить бронь?')) return;
  await axios.delete(`/api/bookings/${id}/`);
  await fetchData();
}

function getSession(id) { return sessions.value.find(s => s.id === id) || {}; }
function getVenue(id) { return venues.value.find(v => v.id === id)?.name || '—'; }

onMounted(fetchData);
</script>

<template>
  <h1>Мои брони</h1>
  <div class="row">
    <div class="col-md-4 mb-3" v-for="b in myBookings" :key="b.id">
      <div class="card shadow-sm">
        <div class="card-body">
          <h5 class="card-title">{{ getSession(b.session).title }}</h5>
          <h6 class="text-muted">{{ getSession(b.session).date }} в {{ getSession(b.session).start_time }}</h6>
          <p>Место: {{ getVenue(getSession(b.session).venue) }}</p>
          <p>Статус: <b>{{ b.status }}</b></p>
          <button class="btn btn-outline-danger w-100" @click="cancelBooking(b.id)" v-if="b.status === 'Активно'">
            Отменить бронь
          </button>
        </div>
      </div>
    </div>
  </div>
  <p v-if="myBookings.length === 0" class="text-muted">У вас пока нет броней.</p>
</template>