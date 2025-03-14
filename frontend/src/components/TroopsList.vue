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
        <td>{{ troop.name }}</td>
        <td>{{ getBranchName(troop.branch_id) }}</td>
        <td v-if="user">
          <button class="button-delete" @click="deleteTroop(troop.id)">Удалить</button>
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
      selectedBranchId: ''
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
  width: calc(50% - 12px);
}

button {
  padding: 5px 10px;
  border: none;
  background: #007bff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
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