import { defineStore } from "pinia";
import { ref } from 'vue';
import axios from 'axios';
import Cookies from "js-cookie";

const useProfileStore = defineStore('profileStore', () => {

    const isAuthenticated = ref(false);
    const userName = ref(null);

    async function fetchMe() {
        axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");

        const r = await axios.get("/api/profile/me/");
        isAuthenticated.value = r.data.is_authenticated;
        userName.value = r.data.is_authenticated ? r.data.username : null;
    }

    async function login(username, password) {
        await axios.post('/api/profile/login/', {
            username: username,
            password: password,
        });
        await fetchMe();
    }

    async function logout() {
        await axios.post("/api/profile/logout/");
        await fetchMe();
    }

    return {
        isAuthenticated,
        userName,
        fetchMe,
        login,
        logout,
    }
})

export default useProfileStore;