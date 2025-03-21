<template>
  <div>
    <h2>Рода войск</h2>

    <!-- Панель фильтров -->
    <div class="filters">
      <input
          v-model="filterName"
          placeholder="Поиск по названию рода войск"
          @input="debounceSearch"
      />
      <button @click="resetFilters">Сбросить</button>
    </div>

    <div>По Вашему запросу найдено {{ countRecords }} записи(ей)</div>

    <table>
      <thead>
      <tr style="background: #f4f4f4">
        <th>№</th>
        <th @click="sortTable('name')">
          Название рода войск
          <span v-if="sortBy === 'name'">
            <i :class="sortOrder === 'asc' ? 'arrow-up' : 'arrow-down'"></i>
          </span>
        </th>
        <th v-if="user">Действия</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(branch, index) in sortedBranches" :key="branch.id">
        <td style="text-align: center;">{{ skip + index + 1 }}</td>
        <td>{{ branch.name }}</td>
        <td v-if="user">
          <button @click="openEditModal(branch)">Редактировать</button>
          <button class="button-delete" @click="deleteBranch(branch.id)">Удалить</button>
        </td>
      </tr>
      </tbody>
    </table>

    <!-- Пагинация -->
    <div class="pagination">
      <button :disabled="skip === 0" @click="prevPage">Предыдущая</button>
      <span>Страница {{ Math.floor(skip / limit) + 1 }}</span>
      <button :disabled="branches.length < limit" @click="nextPage">Следующая</button>
    </div>

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
    <div v-if="user" class="add-button">
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
      isAddModalOpen: false,
      sortBy: 'name',  // по умолчанию сортируем по имени
      sortOrder: 'asc',  // по умолчанию порядок сортировки - по возрастанию
      filterName: '',    // фильтр по названию
      skip: 0,           // для пагинации
      limit: 3,         // элементов на странице
      searchTimeout: null, // для дебаунса поиска
      countRecords: 0
    };
  },
  computed: {
    // Используем уже отсортированные данные с сервера
    sortedBranches() {
      return this.branches;
    }
  },
  methods: {
    // Дебаунс поиска для предотвращения частых запросов
    debounceSearch() {
      clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        this.applyFilters();
      }, 500);
    },

    // Применить фильтры и загрузить данные
    applyFilters() {
      this.skip = 0; // Сбрасываем страницу при применении нового фильтра
      this.fetchBranches();
    },

    // Сбросить фильтры
    resetFilters() {
      this.filterName = '';
      this.sortBy = 'name';
      this.sortOrder = 'asc';
      this.skip = 0;
      this.fetchBranches();
    },

    // Пагинация - предыдущая страница
    prevPage() {
      if (this.skip > 0) {
        this.skip -= this.limit;
        this.fetchBranches();
      }
    },

    // Пагинация - следующая страница
    nextPage() {
      if (this.branches.length === this.limit) {
        this.skip += this.limit;
        this.fetchBranches();
      }
    },

    async fetchBranches() {
      try {
        // Формируем URL с параметрами фильтрации, сортировки и пагинации
        const params = new URLSearchParams();

        if (this.sortBy) {
          params.append('sort_by', this.sortBy);
          params.append('order', this.sortOrder);
        }

        if (this.filterName.trim()) {
          params.append('name', this.filterName.trim());
        }

        // Для получения количества
        const responseForCount = await axios.get(`http://127.0.0.1:8000/branches/?${params.toString()}`);
        this.countRecords = responseForCount.data.length;

        params.append('skip', this.skip);
        params.append('limit', this.limit);

        const response = await axios.get(`http://127.0.0.1:8000/branches/?${params.toString()}`);
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
    },

    // Сортировка таблицы
    sortTable(column) {
      if (this.sortBy === column) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortBy = column;
        this.sortOrder = 'asc';
      }
      this.fetchBranches(); // Загружаем отсортированные данные с сервера
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

th {
  cursor: pointer; /* Указатель на столбцы для сортировки */
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

/* Стили для строк таблицы */
tbody tr:nth-child(odd) {
  background-color: #f9f9f9;
}

tbody tr:nth-child(even) {
  background-color: #e6e6e6;
}

tbody tr:hover {
  background-color: #d1e7fd;
}

/* Стиль стрелочек */
.arrow-up::before {
  content: "↑";
  font-size: 12px;
  margin-left: 5px;
}

.arrow-down::before {
  content: "↓";
  font-size: 12px;
  margin-left: 5px;
}

th:hover {
  background-color: #d1e7fd; /* Голубой оттенок при наведении */
}

/* Стили для панели фильтров */
.filters {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 5px;
}

.filters input {
  flex: 1;
  margin-bottom: 0;
}

/* Стили для пагинации */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
}

.pagination span {
  margin: 0 10px;
}

/* Стиль для кнопки добавления */
.add-button {
  margin-top: 20px;
  text-align: right;
}
</style>