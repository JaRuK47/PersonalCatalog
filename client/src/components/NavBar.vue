<script setup>
import useProfileStore from '@/stores/profileStore';
import { storeToRefs } from 'pinia';
const profileStore = useProfileStore();
const { isAuthenticated, userName, isManager } = storeToRefs(profileStore);
async function onLogoutButtonClick() { await profileStore.logout(); }
</script>

<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container-fluid">
            <router-link class="navbar-brand" to="/">Клуб Инсайд</router-link>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse w-100 justify-content-between" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item"><router-link class="nav-link" to="/about">О клубе</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/rules">Правила</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/venues">Локации</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/sessions">Сессии</router-link></li>
                    <li class="nav-item"><router-link class="nav-link" to="/rounds">Партии</router-link></li>

                    <li class="nav-item" v-if="isAuthenticated && !isManager">
                        <router-link class="nav-link" to="/my-bookings">Мои брони</router-link>
                    </li>
                    <li class="nav-item" v-if="isAuthenticated">
                      <router-link class="nav-link" to="/my-games">Мои игры</router-link>
                    </li>
                    <li class="nav-item" v-if="isManager">
                        <router-link class="nav-link" to="/bookings">Управление бронями</router-link>
                    </li>
                    <li class="nav-item" v-if="isManager">
                        <a class="nav-link" href="/admin" target="_blank">Админка</a>
                    </li>
                </ul>
                <div class="d-flex align-items-center text-white">
                    <span v-if="isAuthenticated" class="me-3">Привет, <b>{{ userName }}</b></span>
                    <span v-else class="me-3"><router-link to="/login" class="text-white text-decoration-none">Войти</router-link></span>
                    <button v-if="isAuthenticated" class="btn btn-outline-light btn-sm" @click="onLogoutButtonClick">Выйти</button>
                </div>
            </div>
        </div>
    </nav>
</template>