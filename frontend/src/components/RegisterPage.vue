<template>
  <div>
    <h2>Регистрация</h2>
    <form @submit.prevent="submitForm">
      <div>
        <label for="username">Имя пользователя<span class="required">*</span>:</label>
        <input type="text" v-model="username" id="username" required />
      </div>
      <div>
        <label for="password">Пароль<span class="required">*</span>:</label>
        <input type="password" v-model="password" id="password" required />
      </div>
      <div>
        <label for="confirmPassword">Подтверждение пароля<span class="required">*</span>:</label>
        <input type="password" v-model="confirmPassword" id="confirmPassword" required />
      </div>
      <button type="submit">Зарегистрироваться</button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
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
      // Проверка совпадения паролей
      if (this.password !== this.confirmPassword) {
        this.errorMessage = 'Пароли не совпадают';
        return;
      }

      const registerData = {
        username: this.username,
        password: this.password
      };

      try {
        // Отправка запроса на регистрацию
        const response = await axios.post('http://localhost:8000/auth/register', registerData, {
          headers: {
            'Content-Type': 'application/json'
          }
        });

        console.log('Успешная регистрация:', response.data);

        // После успешной регистрации выполняем вход
        try {
          const loginResponse = await axios.post('http://localhost:8000/auth/login', registerData, {
            headers: {
              'Content-Type': 'application/json'
            }
          });

          console.log('Автоматический вход после регистрации:', loginResponse.data);

          // Передаем данные авторизации в родительский компонент
          this.$emit('register', loginResponse.data);
          this.errorMessage = null;
        } catch (loginError) {
          console.error('Ошибка при автоматическом входе:', loginError);
          this.errorMessage = 'Регистрация успешна, но не удалось выполнить вход автоматически';
        }
      } catch (error) {
        console.error('Ошибка при регистрации:', error);

        if (error.response && error.response.data.detail) {
          this.errorMessage = error.response.data.detail;
        } else {
          this.errorMessage = error.response?.data?.message || 'Произошла ошибка при регистрации';
        }
      }
    }
  }
};
</script>

<style scoped>
.error {
  color: red;
}
</style>