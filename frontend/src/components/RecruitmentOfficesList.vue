<template>
  <div>
    <h2>Призывные пункты</h2>

    <!-- Таблица с призывными пунктами -->
    <table>
      <thead>
      <tr>
        <th>ID</th>
        <th>Адрес</th>
        <th>Начальник</th>
        <th>Действия</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="office in recruitmentOffices" :key="office.id">
        <td>{{ office.id }}</td>
        <td>{{ office.address }}</td>
        <td>{{ office.chief_name }}</td>
      </tr>
      </tbody>
    </table>
  </div>

  <!-- Форма для создания нового призывного пункта -->
  <div v-if="user">
    <h3>Добавить призывной пункт</h3>
    <form @submit.prevent="createOffice">
      <input v-model="newAddress" placeholder="Адрес" required />
      <input v-model="newChiefName" placeholder="Начальник" required />
      <button type="submit">Добавить</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'RecruitmentOfficesList',
  props: ['user'],
  data() {
    return {
      recruitmentOffices: [],
      newAddress: '',
      newChiefName: '',
    };
  },
  methods: {
    // Получаем все пункты
    async fetchOffices() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/recruitment_offices/');
        this.recruitmentOffices = response.data;

      } catch (error) {
        console.error('Ошибка при получении данных о призывных пунктах:', error);
      }
    },

    // Добавляем новый призывной пункт
    async createOffice() {
      if (!this.newAddress.trim() || !this.newChiefName.trim()) {
        alert('Заполните все поля!');
        return;
      }

      try {
        // Проверяем наличие пользователя и токена
        if (!localStorage.getItem('user')) {
          alert('Вы должны быть авторизованы для добавления пункта!');
          return;
        }

        const token = JSON.parse(localStorage.getItem('user')).token;

        await axios.post(
            'http://127.0.0.1:8000/recruitment_offices/',
            {
              address: this.newAddress,
              chief_name: this.newChiefName,
            },
            {
              headers: { Authorization: `Bearer ${token}` },
            }
        );

        // После успешного добавления очищаем форму и перезагружаем данные
        this.newAddress = '';
        this.newChiefName = '';
        await this.fetchOffices();
        alert('Призывной пункт успешно добавлен');
      } catch (error) {
        console.error('Ошибка при добавлении призывного пункта:', error);
        alert('Ошибка при добавлении. Проверьте данные и права доступа.');
      }
    },
  },
  mounted() {
    this.fetchOffices(); // Загружаем данные при инициализации компонента
  },
};
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
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

form {
  margin-bottom: 20px;
}

input {
  padding: 8px;
  margin: 5px;
  border-radius: 4px;
}

button {
  padding: 8px 16px;
  background-color: #28a745;
  color: white;
  border: none;
  cursor: pointer;
}

button[type="submit"]:hover {
  background-color: #218838;
}

ul {
  margin: 0;
  padding-left: 20px;
}
</style>