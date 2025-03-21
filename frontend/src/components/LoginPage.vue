<template>
  <div>
    <h2>Вход</h2>
    <form @submit.prevent="submitForm">
      <div>
        <label for="username">Имя пользователя<span class="required">*</span>:</label>
        <input type="text" v-model="username" id="username" required />
      </div>
      <div>
        <label for="password">Пароль<span class="required">*</span>:</label>
        <input type="password" v-model="password" id="password" required />
      </div>
      <button type="submit">Войти</button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script>
import axios from '@/axios'; // Путь к файлу axios

export default {
  data() {
    return {
      username: '',
      password: '',
      errorMessage: null,
    };
  },
  methods: {
    async submitForm() {
      console.log('Отправка данных: ', { username: this.username, password: this.password }); // Отладка данных

      const loginData = {
        username: this.username,
        password: this.password
      };

      try {
        // Отправляем запрос на сервер для аутентификации
        const response = await axios.post('http://localhost:8000/auth/login', loginData, {
          headers: {
            'Content-Type': 'application/json'
          }
        });

        console.log('Успешный вход, ответ от сервера: ', response.data); // Отладка ответа от сервера

        // Если аутентификация прошла успешно
        this.$emit('login', response.data); // Передаем данные ответа в родительский компонент
        this.errorMessage = null; // Очищаем ошибку

        const token = response.data.access_token;  // Получаем токен из props
        console.log(token);
        const r = await axios.get('http://127.0.0.1:8000/auth/profile', {
          headers: { Authorization: `Bearer ${token}` },  // Отправляем токен в заголовке
        });
        console.log(r);

        localStorage.setItem('page_size', Number(r.data.page_size))

      } catch (error) {
        console.log('Ошибка при входе:', error); // Отладка ошибки

        // Обработка ошибки (например, если неверные данные)
        if (error.response && error.response.data.detail) {
          this.errorMessage = error.response.data.detail;
        } else {
          this.errorMessage = error.response?.data?.message || 'Произошла ошибка при попытке войти';
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