<template>
  <div class="page-wrapper">
    <div class="login-card">
      <h2 class="title">Вход в систему</h2>

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

        <button type="submit" class="btn">Войти</button>
      </form>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
import api from '@/axios';

export default {
  data() {
    return {
      username: "",
      password: "",
      errorMessage: null,
    };
  },

  methods: {
    async submitForm() {
      try {
        const response = await api.post("/auth/login", {
          username: this.username,
          password: this.password
        });

        this.errorMessage = null;
        this.$emit("login", response.data);

        const token = response.data.access_token;

        const profile = await api.get("/auth/profile", {
          headers: { Authorization: `Bearer ${token}` }
        });

        localStorage.setItem("page_size", Number(profile.data.page_size));

      } catch (error) {
        this.errorMessage =
            error.response?.data?.detail ||
            "Произошла ошибка при входе";
      }
    }
  }
};
</script>

<style scoped>
/* Контейнер страницы — центрирование */
.page-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

/* Карточка */
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

/* Форма */
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

/* Кнопка */
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

/* Ошибка */
.error {
  margin-top: 15px;
  color: #d63031;
  font-weight: 600;
  text-align: center;
}

.required {
  color: red;
}

/* Анимация */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(15px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
