<template>
  <div id="app">
    <h1>Учет воинского призыва</h1>
    <hr>

    <!-- Отображение имени пользователя после входа -->
    <div v-if="user" class="auth-info">
      <p><strong @click="currentTab = 'profile'" class="username-link">{{ user.username }}</strong></p>
      <button @click="logout">Выйти</button>
    </div>

    <!-- Если пользователь не авторизован -->
    <div v-else class="auth-buttons">
      <button @click="currentTab = 'login'" :class="{ active: currentTab === 'login' }">Войти</button>
      <button @click="currentTab = 'register'" :class="{ active: currentTab === 'register' }">Зарегистрироваться</button>
    </div>

    <hr>

    <!-- Меню вкладок -->
    <div class="menu-tabs" v-if="!selectedRecruitId && currentTab !== 'profile'">
      <button @click="currentTab = 'branches'" :class="{ active: currentTab === 'branches' }">Роды войск</button>
      <button @click="currentTab = 'troops'" :class="{ active: currentTab === 'troops' }">Виды войск</button>
      <button @click="currentTab = 'recruitments'" :class="{ active: currentTab === 'recruitments' }">Призывники</button>
      <button @click="currentTab = 'recruitment_offices'" :class="{ active: currentTab === 'recruitment_offices' }">Призывные пункты</button>
    </div>

    <!-- Контент -->
    <div class="content-section">
      <BranchesList v-if="currentTab === 'branches' && !selectedRecruitId" :user="user" />
      <TroopsList v-if="currentTab === 'troops' && !selectedRecruitId" :user="user" />
      <RecruitmentsList
          v-if="currentTab === 'recruitments' && !selectedRecruitId"
          :user="user"
          @view-recruit="viewRecruit"
      />
      <RecruitmentOfficesList v-if="currentTab === 'recruitment_offices' && !selectedRecruitId" :user="user" />
      <LoginPage v-if="currentTab === 'login'" @login="handleLogin" />
      <RegisterPage v-if="currentTab === 'register'" @register="handleRegister" />

      <!-- Профиль пользователя -->
      <UserProfile v-if="currentTab === 'profile'" :user="user" @logout="logout" @go-home="currentTab = 'branches'" />

      <!-- Отдельная страница призывника -->
      <RecruitmentPage
          v-if="selectedRecruitId"
          :recruitId="selectedRecruitId"
          :user="user"
          @back="goBackToList"
      />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import BranchesList from '@/components/BranchesList.vue';
import TroopsList from '@/components/TroopsList.vue';
import RecruitmentOfficesList from '@/components/RecruitmentOfficesList.vue';
import RecruitmentsList from '@/components/RecruitmentsList.vue';
import LoginPage from '@/components/LoginPage.vue';
import RegisterPage from '@/components/RegisterPage.vue';
import RecruitmentPage from '@/components/RecruitmentPage.vue';
import UserProfile from '@/components/UserProfile.vue'; // Импортируем новый компонент

export default {
  name: 'App',
  components: {
    BranchesList,
    TroopsList,
    RecruitmentOfficesList,
    RecruitmentsList,
    LoginPage,
    RegisterPage,
    RecruitmentPage,
    UserProfile // Добавляем компонент профиля в список
  },
  data() {
    return {
      currentTab: 'branches',
      user: null,
      selectedRecruitId: null, // ID выбранного призывника
    };
  },
  methods: {
    // Получение данных о текущем пользователе
    async fetchUserProfile() {
      const token = JSON.parse(localStorage.getItem('user'))?.token;
      if (!token) {
        this.user = null;
        return;
      }

      try {
        const response = await axios.get('http://127.0.0.1:8000/auth/profile', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.user = response.data;
      } catch (error) {
        console.error('Ошибка при загрузке профиля пользователя:', error);
        this.user = null;
      }
    },
    handleLogin(responseData) {
      if (responseData.access_token) {
        localStorage.setItem('user', JSON.stringify({
          username: responseData.username,
          token: responseData.access_token,
        }));
        this.user = { username: responseData.username, token: responseData.access_token };
        this.currentTab = 'profile';
      }
    },
    handleRegister(responseData) {
      if (responseData.access_token) {
        localStorage.setItem('user', JSON.stringify({
          username: responseData.username,
          token: responseData.access_token,
        }));
        this.user = { username: responseData.username, token: responseData.access_token };
        this.currentTab = 'branches';
      }
    },
    logout() {
      localStorage.removeItem('user');
      localStorage.removeItem('page_size');
      this.user = null;
      this.currentTab = 'login';
    },
    // Метод для перехода на страницу призывника
    viewRecruit(id) {
      this.selectedRecruitId = id;
    },
    // Метод для возврата к списку призывников
    goBackToList() {
      this.selectedRecruitId = null;
      this.currentTab = 'recruitments';
    }
  },
  mounted() {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      this.user = JSON.parse(savedUser);
      this.fetchUserProfile();  // Загружаем профиль после авторизации
    }
  }
};
</script>

<style scoped>
#app {
  max-width: 900px;
  margin: auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.menu-tabs button {
  margin-right: 10px;
  padding: 10px 20px;
  border: none;
  background-color: #eee;
  border-radius: 4px;
  cursor: pointer;
}

.menu-tabs button.active {
  background-color: #007bff;
  color: white;
}

.auth-buttons button {
  margin-right: 10px;
  padding: 10px 20px;
  border: none;
  background-color: #28a745;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

.auth-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.auth-info button {
  padding: 6px 12px;
  border: none;
  background-color: #dc3545;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

.username-link {
  cursor: pointer;
  text-decoration: underline;
  color: #007bff;
}

.username-link:hover {
  color: #0056b3;
}

.content-section {
  margin-top: 20px;
}
</style>
