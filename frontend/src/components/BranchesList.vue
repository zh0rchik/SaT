<template>
  <div>
    <h2>Рода войск</h2>
    <table>
      <thead>
      <tr>
        <th>ID</th>
        <th>Название рода войск</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="branch in branches" :key="branch.id">
        <td>{{ branch.id }}</td>
        <td>{{ branch.name }}</td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'BranchesList',
  data() {
    return {
      branches: [] // сюда загрузятся данные с API
    };
  },
  methods: {
    async fetchBranches() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/branches/');
        this.branches = response.data;
      } catch (error) {
        console.error('Ошибка при загрузке родов войск:', error);
      }
    }
  },
  mounted() {
    this.fetchBranches(); // загрузка при монтировании
  }
};
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
