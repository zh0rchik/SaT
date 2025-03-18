<template>
  <div class="profile-container">
    <h2>Профиль пользователя</h2>
    <div class="profile-info">
      <p><strong>Имя пользователя:</strong> {{ user.username }}</p>
    </div>
    <div class="buttons">
      <button @click="goHome">На главную</button>
      <button @click="logout">Выйти</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserProfile',
  props: {
    user: Object // Получаем данные пользователя из App.vue
  },
  methods: {
    logout() {
      this.$emit('logout'); // Вызываем событие выхода
    },
    goHome() {
      this.$emit('go-home'); // Передаем правильное событие
    }
  }
};
</script>

<style scoped>
.profile-container {
  max-width: 400px;
  margin: auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
  text-align: center;
}

.profile-info {
  margin-bottom: 20px;
}

.buttons {
  display: flex;
  justify-content: space-between;
}

button {
  padding: 10px 20px;
  border: none;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

button:first-child {
  background-color: #007bff;
}

button:first-child:hover {
  background-color: #0056b3;
}

button:last-child {
  background-color: #dc3545;
}

button:last-child:hover {
  background-color: #c82333;
}
</style>
