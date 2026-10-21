<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import useProfileStore from '@/stores/profileStore';

const router = useRouter();
const profileStore = useProfileStore();

const username = ref('');
const password = ref('');
const errorMsg = ref('');

async function onSubmit() {
    try {
        await profileStore.login(username.value, password.value);
        router.push('/');
    } catch (e) {
        errorMsg.value = 'Неверный логин или пароль';
    }
}
</script>

<template>
    <div class="row justify-content-center mt-5">
        <div class="col-md-4">
            <h2 class="mb-3 text-center">Вход в систему</h2>
            <form @submit.prevent="onSubmit" class="card p-4 shadow-sm">
                <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>
                <div class="mb-3">
                    <label>Логин</label>
                    <input v-model="username" type="text" class="form-control" required />
                </div>
                <div class="mb-3">
                    <label>Пароль</label>
                    <input v-model="password" type="password" class="form-control" required />
                </div>
                <button type="submit" class="btn btn-primary w-100">Войти</button>
            </form>
        </div>
    </div>
</template>