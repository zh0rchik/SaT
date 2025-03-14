<template>
  <div>
    <h2>Виды войск</h2>

    <!-- Таблица -->
    <table>
      <thead>
      <tr>
        <th>ID</th>
        <th>Название вида войск</th>
        <th>Род войск</th>
        <th v-if="user">Действия</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="troop in troops" :key="troop.id">
        <td>{{ troop.id }}</td>
        <td>
          <!-- Если сейчас редактируем этот вид войск -->
          <div v-if="editTroopId === troop.id">
            <input v-model="editTroopName" />
          </div>
          <!-- Если не редактируем -->
          <div v-else>
            {{ troop.name }}
          </div>
        </td>
        <td>
          <!-- Если сейчас редактируем этот вид войск -->
          <div v-if="editTroopId === troop.id">
            <select v-model="editBranchId">
              <option v-for="branch in branches" :key="branch.id" :value="branch.id">
                {{ branch.name }}
              </option>
            </select>
          </div>
          <!-- Если не редактируем -->
          <div v-else>
            {{ getBranchName(troop.branch_id) }}
          </div>
        </td>
        <td v-if="user">
          <!-- Если редактируем -->
          <div v-if="editTroopId === troop.id">
            <button @click="updateTroop(troop.id)">Сохранить</button>
            <button @click="cancelEdit">Отмена</button>
          </div>
          <!-- Если не редактируем -->
          <div v-else>
            <button @click="startEdit(troop)">Редактировать</button>
            <button class="button-delete" @click="deleteTroop(troop.id)">Удалить</button>
          </div>
        </td>
      </tr>
      </tbody>
    </table>
  </div>

  <!-- Форма добавления вида войск -->
  <div v-if="user">
    <h3>Добавить вид войск</h3>
    <input v-model="newTroopName" placeholder="Название вида войск" />
    <select v-model="selectedBranchId">
      <option disabled value="">Выберите род войск</option>
      <option v-for="branch in branches" :key="branch.id" :value="branch.id">
        {{ branch.name }}
      </option>
    </select>
    <button @click="addTroop">Добавить</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'TroopsList',
  props: ['user'],  // Проверяем авторизацию
  data() {
    return {
      troops: [],
      branches: [],
      newTroopName: '',
      selectedBranchId: '',
      editTroopId: null,
      editTroopName: '',
      editBranchId: ''
    };
  },
  methods: {
    // Получаем виды войск и рода войск
    async fetchData() {
      try {
        const [troopsResponse, branchesResponse] = await Promise.all([
          axios.get('http://127.0.0.1:8000/troops/'),
          axios.get('http://127.0.0.1:8000/branches/')
        ]);
        this.troops = troopsResponse.data;
        this.branches = branchesResponse.data;
      } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
      }
    },
    // Получить название рода войск по ID
    getBranchName(branch_id) {
      const branch = this.branches.find(b => b.id === branch_id);
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

        // Очистить форму
        this.newTroopName = '';
        this.selectedBranchId = '';

        // Перезагрузить список
        this.fetchData();

      } catch (error) {
        console.error('Ошибка при добавлении вида войск:', error);
        alert('Ошибка при добавлении. Проверьте данные и права доступа.');
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
          // После удаления обновить список
          this.fetchData();
        } catch (error) {
          console.error('Ошибка при удалении вида войск:', error);
          alert('Ошибка при удалении. Проверьте права доступа.');
        }
      }
    },
    // Начать редактирование
    startEdit(troop) {
      this.editTroopId = troop.id;
      this.editTroopName = troop.name;
      this.editBranchId = troop.branch_id;
    },
    // Отмена редактирования
    cancelEdit() {
      this.editTroopId = null;
      this.editTroopName = '';
      this.editBranchId = '';
    },
    // Обновить вид войск
    async updateTroop(troopId) {
      if (!this.editTroopName.trim() || !this.editBranchId) {
        alert('Заполните все поля!');
        return;
      }

      try {
        const token = JSON.parse(localStorage.getItem('user')).token;

        // Используем query параметры как в примере
        const params = new URLSearchParams();
        params.append('name', this.editTroopName);
        params.append('branch_id', this.editBranchId);

        await axios.patch(`http://127.0.0.1:8000/troops/${troopId}?${params.toString()}`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });

        // Сбросить состояние редактирования
        this.editTroopId = null;
        this.editTroopName = '';
        this.editBranchId = '';

        // Перезагрузить список
        this.fetchData();

      } catch (error) {
        console.error('Ошибка при редактировании вида войск:', error);
        alert('Ошибка при редактировании. Проверьте данные и права доступа.');
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
  padding: 10px;
  border: 1px solid #ccc;
  text-align: left;
}

input, select {
  padding: 5px;
  margin-right: 10px;
  margin-bottom: 10px;
  width: calc(100% - 12px);
}

button {
  padding: 5px 10px;
  border: none;
  background: #007bff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  margin: 4px 2px;
}

button:hover {
  background: #0056b3;
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
  background: #ccc;
  cursor: not-allowed;
}
</style>