<template>
  <div id="app">
    <h1>Учет воинского призыва</h1>
    <hr>

    <!-- Отображение имени пользователя после входа -->
    <div v-if="user" class="auth-info">
      <p>Вы вошли как: <strong>{{ user.username }}</strong></p>
      <button @click="logout">Выйти</button>
    </div>

    <!-- Если пользователь не авторизован -->
    <div v-else class="auth-buttons">
      <button @click="currentTab = 'login'" :class="{ active: currentTab === 'login' }">Войти</button>
      <button @click="currentTab = 'register'" :class="{ active: currentTab === 'register' }">Зарегистрироваться</button>
    </div>

    <hr>

    <!-- Меню вкладок -->
    <div class="menu-tabs">
      <button @click="currentTab = 'branches'" :class="{ active: currentTab === 'branches' }">Роды войск</button>
      <button @click="currentTab = 'troops'" :class="{ active: currentTab === 'troops' }">Виды войск</button>
      <button @click="currentTab = 'recruitment_offices'" :class="{ active: currentTab === 'recruitment_offices' }">Призывные пункты</button>
    </div>

    <!-- Контент -->
    <div class="content-section">
      <BranchesList v-if="currentTab === 'branches'" :user="user" />
      <TroopsList v-if="currentTab === 'troops'" :user="user" />
      <RecruitmentOfficesList v-if="currentTab === 'recruitment_offices'" :user="user" />
      <LoginPage v-if="currentTab === 'login'" @login="handleLogin" />
      <RegisterPage v-if="currentTab === 'register'" @register="handleRegister" />
    </div>
  </div>
</template>

<script>
import BranchesList from '@/components/BranchesList.vue';
import TroopsList from '@/components/TroopsList.vue';
import RecruitmentOfficesList from '@/components/RecruitmentOfficesList.vue';
import LoginPage from '@/components/LoginPage.vue';
import RegisterPage from '@/components/RegisterPage.vue';

export default {
  name: 'App',
  components: {
    BranchesList,
    TroopsList,
    RecruitmentOfficesList,
    LoginPage,
    RegisterPage
  },
  data() {
    return {
      currentTab: 'branches',
      user: null
    };
  },
  methods: {
    handleLogin(responseData) {
      if (responseData.access_token) {
        localStorage.setItem('user', JSON.stringify({
          username: responseData.username,
          token: responseData.access_token
        }));
        this.user = { username: responseData.username };
        this.currentTab = 'branches';
      }
    },
    handleRegister(responseData) {
      if (responseData.access_token) {
        localStorage.setItem('user', JSON.stringify({
          username: responseData.username,
          token: responseData.access_token
        }));
        this.user = { username: responseData.username };
        this.currentTab = 'branches';
      }
    },
    logout() {
      localStorage.removeItem('user');
      this.user = null;
      this.currentTab = 'branches';
    }
  },
  mounted() {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      this.user = JSON.parse(savedUser);
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

.content-section {
  margin-top: 20px;
}
</style>


<style scoped>
/* Основной контейнер */
#app {
  max-width: 900px;
  margin: auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

/* Стили для меню вкладок */
.menu-tabs {
  margin: 20px 0;
}

.menu-tabs button {
  margin-right: 10px;
  padding: 10px 20px;
  border: none;
  background-color: #eee;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.menu-tabs button.active {
  background-color: #007bff;
  color: white;
}

/* Стили для кнопок входа/регистрации */
.auth-buttons button {
  margin-right: 10px;
  padding: 10px 20px;
  border: none;
  background-color: #28a745;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.auth-buttons button.active {
  background-color: #218838;
}

/* Информация о пользователе */
.auth-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.auth-info p {
  margin: 0;
}

.auth-info button {
  padding: 6px 12px;
  border: none;
  background-color: #dc3545;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.auth-info button:hover {
  background-color: #c82333;
}

/* Основной контент */
.content-section {
  margin-top: 20px;
}

/* Ошибки */
.error {
  color: red;
  margin-top: 10px;
  text-align: center;
  font-weight: bold;
}

table, th, td {
  border: 1px solid #ddd;
}

th, td {
  padding: 8px;
  text-align: left;
}

th {
  background-color: #f4f4f4;
}
</style>
