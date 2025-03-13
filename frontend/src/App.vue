<template>
  <div id="app">
    <h1>Учет воинского призыва</h1>
    <hr>

    <!-- Отображение имени пользователя после входа -->
    <div v-if="user">
      <p>{{ user.username }}</p>
      <button @click="logout">Выйти</button>
    </div>

    <!-- Если пользователя нет, показываем кнопки входа и регистрации -->
    <div v-else>
      <button @click="currentTab = 'login'" :class="{ active: currentTab === 'login' }">Войти</button>
      <button @click="currentTab = 'register'" :class="{ active: currentTab === 'register' }">Зарегистрироваться</button>
    </div>

    <hr>

    <!-- Переключение вкладок -->
    <div>
      <button @click="currentTab = 'branches'" :class="{ active: currentTab === 'branches' }">Роды войск</button>
      <button @click="currentTab = 'troops'" :class="{ active: currentTab === 'troops' }">Виды войск</button>
    </div>

    <!-- Данные -->
    <div class="table" v-if="currentTab === 'branches'">
      <BranchesList />
    </div>

    <div class="table" v-if="currentTab === 'troops'">
      <TroopsList />
    </div>

    <!-- Компоненты входа и регистрации -->
    <div v-if="currentTab === 'login'">
      <LoginPage @login="handleLogin" />
    </div>
    <div v-if="currentTab === 'register'">
      <RegisterPage @register="handleRegister" />
    </div>
  </div>
</template>

<script>
//import axios from '@/axios';
import BranchesList from '@/components/BranchesList.vue';
import TroopsList from '@/components/TroopsList.vue';
import LoginPage from '@/components/LoginPage.vue';
import RegisterPage from '@/components/RegisterPage.vue';

export default {
  name: 'App',
  components: {
    BranchesList,
    TroopsList,
    LoginPage,
    RegisterPage
  },
  data() {
    return {
      currentTab: 'branches',  // Начальная вкладка
      user: null,               // Состояние текущего пользователя
      errorMessage: ''          // Сообщение об ошибке
    };
  },
  methods: {
    async handleLogin(responseData) {
      this.errorMessage = ''; // Очистка предыдущих ошибок
      try {
        // Используем данные, которые уже получены в LoginPage
        if (responseData.access_token) {
          // Сохранение пользователя в localStorage
          localStorage.setItem('user', JSON.stringify({
            username: responseData.username,
            token: responseData.access_token
          }));
          this.user = { username: responseData.username };  // Сохраняем текущего пользователя
          this.currentTab = 'branches';  // Переключаем на вкладку с данными
        } else {
          this.errorMessage = 'Неверные данные для входа';
        }
      } catch (error) {
        console.error('Ошибка при входе:', error);
        this.errorMessage = 'Неверные данные для входа';
      }
    },

    async handleRegister(responseData) {
      this.errorMessage = ''; // Очистка предыдущих ошибок
      try {
        // Используем данные, которые уже получены в RegisterPage
        if (responseData.access_token) {
          // Сохранение пользователя в localStorage
          localStorage.setItem('user', JSON.stringify({
            username: responseData.username,
            token: responseData.access_token
          }));
          this.user = { username: responseData.username };  // Сохраняем текущего пользователя
          this.currentTab = 'branches';  // Переключаем на вкладку с данными
        } else {
          this.errorMessage = 'Ошибка при входе после регистрации';
        }
      } catch (error) {
        console.error('Ошибка при обработке регистрации:', error);
        this.errorMessage = 'Ошибка при обработке регистрации';
      }
    },

    logout() {
      localStorage.removeItem('user');
      this.user = null;
    }
  },
  mounted() {
    // Проверка на наличие сохраненного пользователя в localStorage
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      this.user = JSON.parse(savedUser);
    }
  }
};
</script>

<style scoped>
/* Ваши стили */
.error {
  color: red;
}
</style>