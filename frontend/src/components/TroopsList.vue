<template>
  <div>
    <h2>Виды войск</h2>

    <table>
      <thead>
      <tr style="background: #f4f4f4">
        <th @click="sort('id')" style="cursor: pointer" :class="{'sortable': true, 'asc': sortField === 'id' && sortOrder === 'asc', 'desc': sortField === 'id' && sortOrder === 'desc'}">№</th>
        <th @click="sort('name')" style="cursor: pointer" :class="{'sortable': true, 'asc': sortField === 'name' && sortOrder === 'asc', 'desc': sortField === 'name' && sortOrder === 'desc'}">Название вида войск</th>
        <th @click="sort('branch_id')" style="cursor: pointer" :class="{'sortable': true, 'asc': sortField === 'branch_id' && sortOrder === 'asc', 'desc': sortField === 'branch_id' && sortOrder === 'desc'}">Род войск</th>
        <th v-if="user">Действия</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="troop in troops" :key="troop.id">
        <td style="text-align: center;">{{ troops.indexOf(troop) + 1 }}</td>
        <td>{{ troop.name }}</td>
        <td>{{ getBranchName(troop.branch_id) }}</td>
        <td v-if="user">
          <button @click="startEdit(troop)">Редактировать</button>
          <button class="button-delete" @click="deleteTroop(troop.id)">Удалить</button>
        </td>
      </tr>
      </tbody>
    </table>

    <div v-if="user">
      <button @click="openAddModal">Добавить вид войск</button>
    </div>

    <!-- Модальное окно для добавления -->
    <div v-if="isAddModalOpen" class="modal">
      <div class="modal-content">
        <h3>Добавить вид войск</h3>
        <input v-model="newTroopName" placeholder="Название вида войск" />
        <select v-model="selectedBranchId">
          <option disabled value="">Выберите род войск</option>
          <option v-for="branch in branches" :key="branch.id" :value="branch.id">
            {{ branch.name }}
          </option>
        </select>
        <button @click="addTroop">Добавить</button>
        <button @click="closeAddModal">Отмена</button>
      </div>
    </div>

    <!-- Модальное окно для редактирования -->
    <div v-if="isEditModalOpen" class="modal">
      <div class="modal-content">
        <h3>Редактировать вид войск</h3>
        <input v-model="editTroopName" placeholder="Название вида войск" />
        <select v-model="editBranchId">
          <option v-for="branch in branches" :key="branch.id" :value="branch.id">
            {{ branch.name }}
          </option>
        </select>
        <button @click="updateTroop(editTroopId)">Сохранить</button>
        <button @click="closeEditModal">Отмена</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'TroopsList',
  props: ['user'],
  data() {
    return {
      troops: [],
      branches: [],
      newTroopName: '',
      selectedBranchId: '',
      editTroopId: null,
      editTroopName: '',
      editBranchId: '',
      isAddModalOpen: false,
      isEditModalOpen: false,
      sortField: '',
      sortOrder: 'asc',
    };
  },
  methods: {
    async fetchData() {
      try {
        const [troopsResponse, branchesResponse] = await Promise.all([
          axios.get(`http://127.0.0.1:8000/troops/?sort_by=${this.sortField}&order=${this.sortOrder}`),
          axios.get('http://127.0.0.1:8000/branches/')
        ]);
        this.troops = troopsResponse.data;
        this.branches = branchesResponse.data;
      } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
      }
    },
    // Сортировка
    sort(field) {
      this.sortField = field;
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      this.fetchData();
    },
    // Получить название рода войск
    getBranchName(branchId) {
      const branch = this.branches.find(b => b.id === branchId);
      return branch ? branch.name : 'Не определен';
    },
    // Добавить новый вид войск
    async addTroop() {
      if (!this.newTroopName.trim() || !this.selectedBranchId) {
        alert('Заполните все поля!');
        return;
      }

      try {
        const token = JSON.parse(localStorage.getItem('user')).token;
        await axios.post('http://127.0.0.1:8000/troops/', {
          name: this.newTroopName,
          branch_id: this.selectedBranchId
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });

        // Очистить форму и закрыть модальное окно
        this.newTroopName = '';
        this.selectedBranchId = '';
        this.closeAddModal();

        // Обновить список
        this.fetchData();
      } catch (error) {
        console.error('Ошибка при добавлении:', error);
      }
    },
    // Удалить вид войск
    async deleteTroop(troopId) {
      if (confirm('Вы уверены, что хотите удалить этот вид войск?')) {
        try {
          const token = JSON.parse(localStorage.getItem('user')).token;
          await axios.delete(`http://127.0.0.1:8000/troops/${troopId}`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          this.fetchData();
        } catch (error) {
          console.error('Ошибка при удалении:', error);
        }
      }
    },
    // Открытие модального окна редактирования
    startEdit(troop) {
      this.editTroopId = troop.id;
      this.editTroopName = troop.name;
      this.editBranchId = troop.branch_id;
      this.isEditModalOpen = true;
    },
    // Закрытие модального окна редактирования
    closeEditModal() {
      this.isEditModalOpen = false;
      this.editTroopId = null;
      this.editTroopName = '';
      this.editBranchId = '';
    },
    // Открытие модального окна добавления
    openAddModal() {
      this.isAddModalOpen = true;
    },
    // Закрытие модального окна добавления
    closeAddModal() {
      this.isAddModalOpen = false;
      this.newTroopName = '';
      this.selectedBranchId = '';
    },
    // Обновить вид войск
    async updateTroop(troopId) {
      if (!this.editTroopName.trim() || !this.editBranchId) {
        alert('Заполните все поля!');
        return;
      }

      try {
        const token = JSON.parse(localStorage.getItem('user')).token;
        await axios.patch(`http://127.0.0.1:8000/troops/${troopId}`, {
          name: this.editTroopName,
          branch_id: this.editBranchId
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.fetchData();
        this.closeEditModal();
      } catch (error) {
        console.error('Ошибка при обновлении:', error);
      }
    }
  },
  mounted() {
    this.fetchData();
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
  text-align: left;
}

th {
  cursor: pointer;
  transition: background-color 0.3s ease;
}

th:hover {
  background-color: #d1e7fd;
}

th.sortable {
  position: relative;
}

th.sortable:after {
  content: '';
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
}

th.sortable.asc:after {
  content: '↑';
}

th.sortable.desc:after {
  content: '↓';
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

input, select {
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

tbody tr:nth-child(odd) {
  background-color: #f9f9f9;
}

tbody tr:nth-child(even) {
  background-color: #e6e6e6;
}

tbody tr:hover {
  background-color: #d1e7fd;
}
</style>
