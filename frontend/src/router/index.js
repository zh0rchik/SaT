import { createRouter, createWebHistory } from 'vue-router';
import App from '@/App.vue'; // Главная страница
import LoginPage from '@/components/LoginPage.vue'; // Страница логина
import RegisterPage from '@/components/RegisterPage.vue'; // Страница регистрации

const routes = [
    { path: '/', component: App },  // Главная страница
    { path: '/login', component: LoginPage },
    { path: '/register', component: RegisterPage }
];

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
});

export default router;
