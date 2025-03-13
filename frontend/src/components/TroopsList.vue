<template>
  <div>
    <h2>Виды войск</h2>
    <table>
      <thead>
      <tr>
        <th>ID</th>
        <th>Название вида войск</th>
        <th>Род войск</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="troop in troops" :key="troop.id">
        <td>{{ troop.id }}</td>
        <td>{{ troop.name }}</td>
        <td>{{ getBranchName(troop.branch_id) }}</td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'TroopsList',
  data() {
    return {
      troops: [],
      branches: []
    }
  },
  methods: {
    async fetchData() {
      try {
        const [troopsResponse, branchesResponse] = await Promise.all([
          axios.get('http://127.0.0.1:8000/troops/'),     // Виды войск
          axios.get('http://127.0.0.1:8000/branches/')   // Роды войск
        ]);
        this.troops = troopsResponse.data;
        this.branches = branchesResponse.data;
      } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
      }
    },
    getBranchName(branch_id) {
      const branch = this.branches.find(b => b.id === branch_id);
      return branch ? branch.name : 'Не определен';
    }
  },
  mounted() {
    this.fetchData();
  }
}
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  padding: 8px;
  border: 1px solid #ccc;
}
</style>
