import { defineStore } from "pinia";
import { ref, computed } from 'vue';
import axios from 'axios';
import Cookies from "js-cookie";

const useProfileStore = defineStore('profileStore', () => {
    const isAuthenticated = ref(false);
    const userName = ref(null);
    const role = ref(null);

    const isAdmin = computed(() => role.value === 'Администратор');
    const isManager = computed(() => role.value === 'Организатор' || isAdmin.value);

    async function fetchMe() {
        axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
        const r = await axios.get("/api/profile/me/");
        isAuthenticated.value = r.data.is_authenticated;
        userName.value = r.data.is_authenticated ? r.data.username : null;
        role.value = r.data.is_authenticated ? r.data.role : null;
    }

    async function login(username, password) {
        await axios.post('/api/profile/login/', { username, password });
        await fetchMe();
    }

    async function logout() {
        await axios.post("/api/profile/logout/");
        await fetchMe();
    }

    return { isAuthenticated, userName, role, isAdmin, isManager, fetchMe, login, logout };
});

export default useProfileStore;