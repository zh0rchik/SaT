<template>
  <div>
    <h2>Рода войск</h2>

    <table>
      <thead>
      <tr>
        <th>ID</th>
        <th>Название рода войск</th>
        <th v-if="user">Действия</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="branch in branches" :key="branch.id">
        <td>{{ branch.id }}</td>
        <td>
          <!-- Если сейчас редактируем этот род -->
          <div v-if="editBranchId === branch.id">
            <input v-model="editBranchName" />
          </div>
          <!-- Если не редактируем -->
          <div v-else>
            {{ branch.name }}
          </div>
        </td>
        <td v-if="user">
          <!-- Если редактируем -->
          <div v-if="editBranchId === branch.id">
            <button @click="updateBranch(branch.id)">Сохранить</button>
            <button @click="cancelEdit">Отмена</button>
          </div>
          <!-- Если не редактируем -->
          <div v-else>
            <button @click="startEdit(branch)">Редактировать</button>
            <button class="button-delete" @click="deleteBranch(branch.id)">Удалить</button>
          </div>
        </td>
      </tr>
      </tbody>
    </table>
  </div>


  <!-- Форма добавления (если есть токен) -->
  <div v-if="user">
    <input v-model="newBranchName" placeholder="Название рода войск" />
    <button @click="addBranch">Добавить</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'BranchesList',
  props: ['user'],
  data() {
    return {
      branches: [],
      newBranchName: '',
      editBranchId: null,
      editBranchName: ''
    };
  },
  methods: {
    async fetchBranches() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/branches/');
        this.branches = response.data;
      } catch (error) {
        console.error('Ошибка при загрузке:', error);
      }
    },
    // Добавление
    async addBranch() {
      if (!this.newBranchName.trim()) return;
      try {
        const token = JSON.parse(localStorage.getItem('user')).token;
        await axios.post('http://127.0.0.1:8000/branches/', { name: this.newBranchName }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.newBranchName = '';
        this.fetchBranches();
      } catch (error) {
        console.error('Ошибка при добавлении:', error);
      }
    },
    // Удаление
    async deleteBranch(branchId) {
      if (!confirm('Вы уверены, что хотите удалить?')) return;
      try {
        const token = JSON.parse(localStorage.getItem('user')).token;
        await axios.delete(`http://127.0.0.1:8000/branches/${branchId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.fetchBranches();
      } catch (error) {
        console.error('Ошибка при удалении:', error);
      }
    },
    // Начать редактирование
    startEdit(branch) {
      this.editBranchId = branch.id;
      this.editBranchName = branch.name;
    },
    // Отмена редактирования
    cancelEdit() {
      this.editBranchId = null;
      this.editBranchName = '';
    },
    // Сохранить изменения
    async updateBranch(branchId) {
      if (!this.editBranchName.trim()) return;
      try {
        const token = JSON.parse(localStorage.getItem('user')).token;
        await axios.patch(`http://127.0.0.1:8000/branches/${branchId}?name=${encodeURIComponent(this.editBranchName)}`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.editBranchId = null;
        this.editBranchName = '';
        this.fetchBranches();
      } catch (error) {
        console.error('Ошибка при обновлении:', error);
      }
    }
  },
  mounted() {
    this.fetchBranches();
  }
};
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  padding: 8px;
  border: 1px solid #ccc;
  text-align: center;
}

.add-form {
  margin-bottom: 20px;
}

.add-form input {
  padding: 6px;
  margin-right: 8px;
  width: 300px;
}

button {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  margin: 4px 2px;
}

button:hover {
  background-color: #0056b3;
}

.button-delete {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background-color: #ff0000;
  color: white;
  cursor: pointer;
}

.button-delete:hover {
  background-color: #960000;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
