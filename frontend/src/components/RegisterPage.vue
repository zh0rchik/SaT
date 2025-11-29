<template>
  <div class="page-wrapper">
    <div class="login-card">
      <h2 class="title">Регистрация</h2>

      <form @submit.prevent="submitForm" class="login-form">

        <div class="input-group">
          <label for="username">Имя пользователя<span class="required">*</span></label>
          <input
            type="text"
            v-model="username"
            id="username"
            required
            placeholder="Введите имя"
          />
        </div>

        <div class="input-group">
          <label for="password">Пароль<span class="required">*</span></label>
          <input
            type="password"
            v-model="password"
            id="password"
            required
            placeholder="Введите пароль"
          />
        </div>

        <div class="input-group">
          <label for="confirmPassword">Подтверждение пароля<span class="required">*</span></label>
          <input
            type="password"
            v-model="confirmPassword"
            id="confirmPassword"
            required
            placeholder="Повторите пароль"
          />
        </div>

        <button type="submit" class="btn">Зарегистрироваться</button>
      </form>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
import axios from '@/axios';

export default {
  data() {
    return {
      username: '',
      password: '',
      confirmPassword: '',
      errorMessage: null,
    };
  },
  methods: {
    async submitForm() {
      if (this.password !== this.confirmPassword) {
        this.errorMessage = 'Пароли не совпадают';
        return;
      }

      try {
        // Регистрация пользователя
        await axios.post(
          'http://localhost:8000/auth/register',
          { username: this.username, password: this.password },
          { headers: { 'Content-Type': 'application/json' } }
        );

        // Автоматический вход после успешной регистрации
        const loginResponse = await axios.post(
          'http://localhost:8000/auth/login',
          { username: this.username, password: this.password },
          { headers: { 'Content-Type': 'application/json' } }
        );

        this.$emit('register', loginResponse.data);
        this.errorMessage = null;

      } catch (error) {
        this.errorMessage =
          error.response?.data?.detail ||
          error.response?.data?.message ||
          'Произошла ошибка при регистрации';
      }
    }
  }
};
</script>

<style scoped>
.page-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.login-card {
  width: 360px;
  background: #fff;
  padding: 35px 32px;
  border-radius: 16px;
  box-shadow: 0 12px 35px rgba(0,0,0,0.15);
  animation: fadeIn 0.5s ease;
}

.title {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 25px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.input-group {
  display: flex;
  flex-direction: column;
}

label {
  font-weight: 600;
  margin-bottom: 6px;
}

input {
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid #ccc;
  font-size: 15px;
  transition: 0.25s ease;
}

input:focus {
  border-color: #6a4df5;
  box-shadow: 0 0 4px rgba(106,77,245,0.4);
  outline: none;
}

.btn {
  padding: 12px;
  background: #6a4df5;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.25s ease;
}

.btn:hover {
  background: #5536e4;
  transform: translateY(-2px);
}

.error {
  margin-top: 15px;
  color: #d63031;
  font-weight: 600;
  text-align: center;
}

.required {
  color: red;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(15px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
