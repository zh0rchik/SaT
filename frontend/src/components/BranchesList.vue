<template>
  <div>
    <h2>Рода войск</h2>

    <table>
      <thead>
      <tr style="background: #f4f4f4">
        <th>ID</th>
        <th>Название рода войск</th>
        <th v-if="user">Действия</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="branch in branches" :key="branch.id">
        <td>{{ branch.id }}</td>
        <td>{{ branch.name }}</td>
        <td v-if="user">
          <button @click="openEditModal(branch)">Редактировать</button>
          <button class="button-delete" @click="deleteBranch(branch.id)">Удалить</button>
        </td>
      </tr>
      </tbody>
    </table>

    <!-- Модальное окно для редактирования -->
    <div v-if="isEditModalOpen" class="modal">
      <div class="modal-content">
        <h3>Редактировать род войск</h3>
        <input v-model="editBranchName" placeholder="Название рода войск" />
        <button @click="updateBranch(editBranchId)">Сохранить</button>
        <button @click="closeEditModal">Отмена</button>
      </div>
    </div>

    <!-- Модальное окно для добавления -->
    <div v-if="isAddModalOpen" class="modal">
      <div class="modal-content">
        <h3>Добавить род войск</h3>
        <input v-model="newBranchName" placeholder="Название рода войск" />
        <button @click="addBranch">Добавить</button>
        <button @click="closeAddModal">Отмена</button>
      </div>
    </div>

    <!-- Кнопка для открытия модального окна добавления -->
    <div v-if="user">
      <button @click="openAddModal">Добавить род войск</button>
    </div>
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
      editBranchName: '',
      isEditModalOpen: false,
      isAddModalOpen: false
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
        this.closeAddModal();
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
    // Открытие модального окна редактирования
    openEditModal(branch) {
      this.editBranchId = branch.id;
      this.editBranchName = branch.name;
      this.isEditModalOpen = true;
    },
    // Закрытие модального окна редактирования
    closeEditModal() {
      this.isEditModalOpen = false;
      this.editBranchId = null;
      this.editBranchName = '';
    },
    // Открытие модального окна добавления
    openAddModal() {
      this.isAddModalOpen = true;
    },
    // Закрытие модального окна добавления
    closeAddModal() {
      this.isAddModalOpen = false;
      this.newBranchName = '';
    },
    // Сохранить изменения
    async updateBranch(branchId) {
      if (!this.editBranchName.trim()) return;
      try {
        const token = JSON.parse(localStorage.getItem('user')).token;
        await axios.patch(`http://127.0.0.1:8000/branches/${branchId}?name=${encodeURIComponent(this.editBranchName)}`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.fetchBranches();
        this.closeEditModal();
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

input {
  padding: 5px;
  margin-right: 10px;
  margin-bottom: 10px;
  width: calc(100% - 12px);
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Модальное окно */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 5px;
  width: 400px;
}
</style>
