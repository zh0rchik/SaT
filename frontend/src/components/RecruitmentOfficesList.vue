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
        <th v-if="user">Действия</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="office in recruitmentOffices" :key="office.id">
        <td>{{ office.id }}</td>
        <td>
          <div v-if="editOfficeId === office.id">
            <input v-model="editAddress" placeholder="Новый адрес" />
          </div>
          <div v-else>
            {{ office.address }}
          </div>
        </td>
        <td>
          <div v-if="editOfficeId === office.id">
            <input v-model="editChiefName" placeholder="Новый начальник" />
          </div>
          <div v-else>
            {{ office.chief_name }}
          </div>
        </td>
        <td v-if="user">
          <div v-if="editOfficeId === office.id">
            <button @click="updateOffice(office.id)">Сохранить</button>
            <button @click="cancelEdit">Отмена</button>
          </div>
          <div v-else>
            <button @click="startEdit(office)">Редактировать</button>
            <button class="button-delete" @click="deleteOffice(office.id)">Удалить</button>
          </div>
        </td>
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
      editOfficeId: null,
      editAddress: '',
      editChiefName: '',
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

    // Добавить новый пункт
    async createOffice() {
      if (!this.newAddress.trim() || !this.newChiefName.trim()) {
        alert('Заполните все поля!');
        return;
      }

      try {
        const token = JSON.parse(localStorage.getItem('user'))?.token;
        if (!token) {
          alert('Вы должны быть авторизованы!');
          return;
        }

        await axios.post(
            'http://127.0.0.1:8000/recruitment_offices/',
            { address: this.newAddress, chief_name: this.newChiefName },
            { headers: { Authorization: `Bearer ${token}` } }
        );

        this.newAddress = '';
        this.newChiefName = '';
        await this.fetchOffices();
        alert('Призывной пункт успешно добавлен');
      } catch (error) {
        console.error('Ошибка при добавлении:', error);
        alert('Ошибка при добавлении.');
      }
    },

    // Удалить пункт
    async deleteOffice(id) {
      if (!confirm('Вы уверены, что хотите удалить этот пункт?')) return;

      try {
        const token = JSON.parse(localStorage.getItem('user'))?.token;
        await axios.delete(`http://127.0.0.1:8000/recruitment_offices/${id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        await this.fetchOffices();
        alert('Призывной пункт удален');
      } catch (error) {
        console.error('Ошибка при удалении:', error);
        alert('Ошибка при удалении.');
      }
    },

    // Начать редактирование
    startEdit(office) {
      this.editOfficeId = office.id;
      this.editAddress = office.address;
      this.editChiefName = office.chief_name;
    },

    // Отмена редактирования
    cancelEdit() {
      this.editOfficeId = null;
      this.editAddress = '';
      this.editChiefName = '';
    },

    // Сохранить изменения
    async updateOffice(id) {
      if (!this.editAddress.trim() || !this.editChiefName.trim()) {
        alert('Заполните все поля!');
        return;
      }

      try {
        const token = JSON.parse(localStorage.getItem('user'))?.token;

        await axios.patch(
            `http://127.0.0.1:8000/recruitment_offices/${id}?address=${encodeURIComponent(this.editAddress)}&chief_name=${encodeURIComponent(this.editChiefName)}`,
            {}, // Тело не требуется, данные передаются через query параметры
            { headers: { Authorization: `Bearer ${token}` } }
        );

        this.cancelEdit();
        await this.fetchOffices();
        alert('Призывной пункт обновлен');
      } catch (error) {
        console.error('Ошибка при обновлении:', error);
        alert('Ошибка при обновлении.');
      }
    },
  },
  mounted() {
    this.fetchOffices();
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
  margin: 2px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}

.button-delete {
  background-color: #dc3545;
}

.button-delete:hover {
  background-color: #c82333;
}
</style>
