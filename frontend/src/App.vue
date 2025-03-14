<template>
  <div id="app">
    <h1>Учет воинского призыва</h1>
    <hr>

    <!-- Отображение имени пользователя после входа -->
    <div v-if="user" class="auth-info">
      <p>Вы вошли как: <strong>{{ user.username }}</strong></p>
      <button @click="logout">Выйти</button>
    </div>

    <!-- Если пользователь не авторизован, показываем вход/регистрацию -->
    <div v-else class="auth-buttons">
      <button @click="currentTab = 'login'" :class="{ active: currentTab === 'login' }">Войти</button>
      <button @click="currentTab = 'register'" :class="{ active: currentTab === 'register' }">Зарегистрироваться</button>
    </div>

    <hr>

    <!-- Меню для переключения вкладок -->
    <div class="menu-tabs">
      <button @click="currentTab = 'branches'" :class="{ active: currentTab === 'branches' }">Роды войск</button>
      <button @click="currentTab = 'troops'" :class="{ active: currentTab === 'troops' }">Виды войск</button>
    </div>

    <!-- Секция отображения данных -->
    <div class="content-section">
      <div v-if="currentTab === 'branches'">
        <BranchesList :user="user" />
      </div>

      <div v-if="currentTab === 'troops'">
        <TroopsList :user="user" />
      </div>

      <!-- Страницы входа и регистрации -->
      <div v-if="currentTab === 'login'">
        <LoginPage @login="handleLogin" />
      </div>

      <div v-if="currentTab === 'register'">
        <RegisterPage @register="handleRegister" />
      </div>
    </div>
  </div>
</template>

<script>
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
      currentTab: 'branches',  // Текущая активная вкладка
      user: null,              // Состояние авторизованного пользователя
      errorMessage: ''         // Сообщения об ошибках
    };
  },
  methods: {
    // Обработка успешного входа
    async handleLogin(responseData) {
      this.errorMessage = '';
      try {
        if (responseData.access_token) {
          localStorage.setItem('user', JSON.stringify({
            username: responseData.username,
            token: responseData.access_token
          }));
          this.user = { username: responseData.username };
          this.currentTab = 'branches'; // Переход на основную вкладку
        } else {
          this.errorMessage = 'Неверные данные для входа';
        }
      } catch (error) {
        console.error('Ошибка при входе:', error);
        this.errorMessage = 'Ошибка при входе. Повторите попытку.';
      }
    },

    // Обработка успешной регистрации
    async handleRegister(responseData) {
      this.errorMessage = '';
      try {
        if (responseData.access_token) {
          localStorage.setItem('user', JSON.stringify({
            username: responseData.username,
            token: responseData.access_token
          }));
          this.user = { username: responseData.username };
          this.currentTab = 'branches'; // Переход на основную вкладку
        } else {
          this.errorMessage = 'Ошибка при входе после регистрации';
        }
      } catch (error) {
        console.error('Ошибка при регистрации:', error);
        this.errorMessage = 'Ошибка при регистрации. Повторите попытку.';
      }
    },

    // Выход из системы
    logout() {
      localStorage.removeItem('user');
      this.user = null;
      this.currentTab = 'branches'; // Возвращаемся на главную вкладку
    }
  },
  mounted() {
    // Проверяем наличие сохраненного пользователя
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      this.user = JSON.parse(savedUser);
    }
  }
};
</script>

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
}

/* Основной контент */
.content-section {
  margin-top: 20px;
}

/* Ошибки */
.error {
  color: red;
  margin-top: 10px;
}
</style>
