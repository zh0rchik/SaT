<template>
  <div>
    <h2>Список призывников</h2>

    <!-- Фильтрация -->
    <div class="filters">
      <div class="filter-group">
        <input v-model="filters.name" placeholder="Фильтр по имени" @input="applyFilters" />
        <input v-model="filters.address" placeholder="Фильтр по адресу" @input="applyFilters" />
        <input type="date" v-model="filters.date_of_birth" placeholder="Дата рождения" @input="applyFilters" />
        <select v-model="filters.recruitment_office_id" @change="applyFilters">
          <option value="">Все призывные пункты</option>
          <option v-for="office in recruitmentOffices" :key="office.id" :value="office.id">
            {{ office.address }}
          </option>
        </select>

        <select v-model="filters.marital_status" @change="applyFilters">
          <option value="">Все с/п</option>
          <option value="true">Женат</option>
          <option value="false">Холост</option>
        </select>

        <select v-model="filters.troop_id" @change="applyFilters">
          <option value="">Все рода войск</option>
          <option v-for="troop in troops" :key="troop.id" :value="troop.id">
            {{ troop.name }}
          </option>
        </select>
        <button @click="clearFilters" class="button-clear">Сбросить фильтры</button>
      </div>
    </div>

    <div>По Вашему запросу найдено {{ countRecords }} записи(ей)</div>

    <!-- Таблица призывников -->
    <div v-if="loading" class="loading">
      Загрузка данных...
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="fetchRecruitments" class="retry-button">Попробовать снова</button>
    </div>
    <div v-else class="table-container">
      <table>
        <thead>
        <tr>
          <th>№</th>
          <th @click="sort('name')" class="sortable" :class="{'asc': sortField === 'name' && sortOrder === 'asc', 'desc': sortField === 'name' && sortOrder === 'desc'}">
            Имя
          </th>
          <th @click="sort('address')" class="sortable" :class="{'asc': sortField === 'address' && sortOrder === 'asc', 'desc': sortField === 'address' && sortOrder === 'desc'}">
            Адрес
          </th>
          <th @click="sort('date_of_birth')" class="sortable" :class="{'asc': sortField === 'date_of_birth' && sortOrder === 'asc', 'desc': sortField === 'date_of_birth' && sortOrder === 'desc'}">
            Дата рождения
          </th>
          <th @click="sort('marital_status')" class="sortable" :class="{'asc': sortField === 'marital_status' && sortOrder === 'asc', 'desc': sortField === 'marital_status' && sortOrder === 'desc'}">
            Семейное положение
          </th>
          <th @click="sort('recruitment_office_id')" class="sortable" :class="{'asc': sortField === 'recruitment_office_id' && sortOrder === 'asc', 'desc': sortField === 'recruitment_office_id' && sortOrder === 'desc'}">
            Призывной пункт
          </th>
          <th @click="sort('troop_id')" class="sortable" :class="{'asc': sortField === 'troop_id' && sortOrder === 'asc', 'desc': sortField === 'troop_id' && sortOrder === 'desc'}">
            Род войск
          </th>
          <th v-if="user">Действия</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="recruit in recruitments" :key="recruit.id">
          <td style="text-align: center;">{{ recruitments.indexOf(recruit) + 1 }}</td>
          <td>
            <a href="#" @click.prevent="viewRecruit(recruit.id)" class="recruit-link">
              {{ recruit.name || 'Не указано' }}
            </a>
          </td>
          <td>{{ recruit.address || 'Не указано' }}</td>
          <td>{{ formatDate(recruit.date_of_birth) }}</td>
          <td>{{ recruit.marital_status ? 'Женат' : 'Холост' }}</td>
          <td>{{ getRecruitmentOfficeInfo(recruit.recruitment_office_id) }}</td>
          <td>{{ getTroopInfo(recruit.troop_id) }}</td>
          <td v-if="user">
            <button @click="deleteRecruit(recruit.id)" class="delete-button">
              Удалить
            </button>
          </td>
        </tr>
        <tr v-if="recruitments.length === 0">
          <td colspan="8" class="no-data">Нет данных</td>
        </tr>
        </tbody>
      </table>

      <!-- Пагинация -->
      <div class="pagination">
        <button @click="prevPage" :disabled="currentPage === 0">Предыдущая</button>
        <span>Страница {{ currentPage + 1 }}</span>
        <button @click="nextPage" :disabled="recruitments.length < pageSize">Следующая</button>
      </div>
    </div>

    <div class="table-header">
      <button v-if="user" @click="openModal" class="add-button">
        Добавить призывника
      </button>
    </div>
  </div>

  <!-- Модальное окно добавления призывника -->
  <div v-if="showModal" class="modal-backdrop" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>Добавить призывника</h3>
        <button @click="closeModal" class="close-button">&times;</button>
      </div>
      <form @submit.prevent="submitForm" class="add-form">
        <div class="form-group">
          <label for="name">ФИО:</label>
          <input
              id="name"
              v-model="newRecruit.name"
              type="text"
              required
              placeholder="Введите ФИО призывника"
          />
        </div>

        <div class="form-group">
          <label for="date_of_birth">Дата рождения:</label>
          <input
              id="date_of_birth"
              v-model="newRecruit.date_of_birth"
              type="date"
              required
          />
        </div>

        <div class="form-group">
          <label for="address">Адрес:</label>
          <input
              id="address"
              v-model="newRecruit.address"
              type="text"
              required
              placeholder="Введите адрес призывника"
          />
        </div>

        <div class="form-group checkbox">
          <input
              id="marital_status"
              v-model="newRecruit.marital_status"
              type="checkbox"
          />
          <label for="marital_status">Женат</label>
        </div>

        <div class="form-group">
          <label for="recruitment_office_id">Призывной пункт:</label>
          <select
              id="recruitment_office_id"
              v-model="newRecruit.recruitment_office_id"
          >
            <option :value="null">Не выбрано</option>
            <option
                v-for="office in recruitmentOffices"
                :key="office.id"
                :value="office.id"
            >
              {{ office.address }} ({{ office.chief_name }})
            </option>
          </select>
        </div>

        <div class="form-actions">
          <button type="submit" :disabled="submitting" class="submit-button">
            {{ submitting ? 'Добавление...' : 'Добавить призывника' }}
          </button>
          <button type="button" @click="resetForm" :disabled="submitting" class="reset-button">
            Очистить форму
          </button>
        </div>

        <div v-if="formError" class="error">
          {{ formError }}
        </div>
        <div v-if="formSuccess" class="success">
          {{ formSuccess }}
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'RecruitmentsList',
  props: ['user'],
  emit: ['view-recruit'],
  data() {
    return {
      recruitments: [],
      recruitmentOffices: [],
      troops: [],
      loading: true,
      error: null,
      showModal: false,
      submitting: false,
      formError: null,
      formSuccess: null,
      newRecruit: {
        name: '',
        date_of_birth: '',
        address: '',
        marital_status: false,
        recruitment_office_id: null,
        troop_id: null
      },
      // Пагинация и сортировка
      currentPage: 0,
      pageSize: 3, // поменять
      sortField: 'name',
      sortOrder: 'asc',
      // Фильтры
      filters: {
        name: '',
        address: '',
        date_of_birth: '',
        recruitment_office_id: '',
        troop_id: '',
        marital_status: ''
      },
      countRecords: 0
    };
  },
  methods: {
    // Методы для получения данных
    async fetchRecruitments() {
      this.loading = true;
      this.error = null;
      this.pageSize = this.user ? Number(localStorage.getItem('page_size')) : 5

      try {
        let url = `http://127.0.0.1:8000/recruitments/?sort_by=${this.sortField}&order=${this.sortOrder}`;

        // Добавляем параметры фильтрации в URL
        if (this.filters.name) {
          url += `&name=${encodeURIComponent(this.filters.name)}`;
        }

        if (this.filters.address) {
          url += `&address=${encodeURIComponent(this.filters.address)}`;
        }

        if (this.filters.date_of_birth) {
          url += `&date_of_birth=${this.filters.date_of_birth}`;
        }

        if (this.filters.recruitment_office_id) {
          url += `&recruitment_office_id=${this.filters.recruitment_office_id}`;
        }

        if (this.filters.troop_id) {
          url += `&troop_id=${this.filters.troop_id}`;
        }

        if (this.filters.marital_status !== '') {
          url += `&marital_status=${this.filters.marital_status}`;
        }

        // количество записей
        const responseForCount = await axios.get(url);
        this.countRecords = responseForCount.data.length;

        url += `&skip=${this.currentPage * this.pageSize}&limit=${this.pageSize}`

        const response = await axios.get(url);
        this.recruitments = response.data;

      } catch (error) {
        console.error('Ошибка при загрузке призывников:', error);
        this.error = 'Не удалось загрузить данные. Пожалуйста, попробуйте еще раз.';
      } finally {
        this.loading = false;
      }
    },

    async fetchRecruitmentOffices() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/recruitment_offices/');
        this.recruitmentOffices = response.data;
      } catch (error) {
        console.error('Ошибка при загрузке призывных пунктов:', error);
      }
    },

    async fetchTroops() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/troops/');
        this.troops = response.data;
      } catch (error) {
        console.error('Ошибка при загрузке родов войск:', error);
      }
    },

    // Методы сортировки
    sort(field) {
      if (this.sortField === field) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortField = field;
        this.sortOrder = 'asc';
      }
      this.fetchRecruitments();
    },

    // Методы пагинации
    prevPage() {
      if (this.currentPage > 0) {
        this.currentPage--;
        this.fetchRecruitments();
      }
    },

    nextPage() {
      this.currentPage++;
      this.fetchRecruitments();
    },

    // Методы фильтрации
    applyFilters() {
      this.currentPage = 0; // Сбрасываем на первую страницу при изменении фильтров
      this.fetchRecruitments();
    },

    clearFilters() {
      this.filters = {
        name: '',
        address: '',
        date_of_birth: '',
        recruitment_office_id: '',
        troop_id: '',
        marital_status: ''  // Добавить это поле
      };
      this.applyFilters();
    },

    // Вспомогательные методы и форматирование
    formatDate(dateString) {
      if (!dateString) return 'Не указано';
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU');
    },

    getRecruitmentOfficeInfo(officeId) {
      if (!officeId) return 'Не указано';
      const office = this.recruitmentOffices.find(o => o.id === officeId);
      return office ? office.address : 'Не найдено';
    },

    getTroopInfo(troopId) {
      if (!troopId) return 'Не указано';
      const troop = this.troops.find(t => t.id === troopId);
      return troop ? troop.name : 'Не найдено';
    },

    // Методы работы с призывниками
    viewRecruit(id) {
      // Можно добавить переход на детальный просмотр призывника
      console.log('Просмотр призывника', id);
      this.$router.push(`/recruit/${id}`);
      this.$emit('view-recruit', id);
    },

    async deleteRecruit(id) {
      if (!confirm('Вы уверены, что хотите удалить этого призывника?')) return;

      try {
        const token = JSON.parse(localStorage.getItem('user'))?.token;
        await axios.delete(`http://127.0.0.1:8000/recruitments/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.fetchRecruitments();
      } catch (error) {
        console.error('Ошибка при удалении призывника:', error);
        alert('Не удалось удалить призывника. Пожалуйста, попробуйте еще раз.');
      }
    },

    // Методы работы с модальным окном
    openModal() {
      this.showModal = true;
      this.resetForm();
    },

    closeModal() {
      this.showModal = false;
      this.resetForm();
    },

    resetForm() {
      this.newRecruit = {
        name: '',
        date_of_birth: '',
        address: '',
        marital_status: false,
        recruitment_office_id: null,
        troop_id: null
      };
      this.formError = null;
      this.formSuccess = null;
    },

    async submitForm() {
      if (!this.newRecruit.name || !this.newRecruit.date_of_birth || !this.newRecruit.address) {
        this.formError = 'Пожалуйста, заполните все обязательные поля';
        return;
      }

      this.submitting = true;
      this.formError = null;
      this.formSuccess = null;

      try {
        const token = JSON.parse(localStorage.getItem('user'))?.token;
        await axios.post('http://127.0.0.1:8000/recruitments/', this.newRecruit, {
          headers: { Authorization: `Bearer ${token}` }
        });

        this.formSuccess = 'Призывник успешно добавлен';
        this.fetchRecruitments();
        setTimeout(() => {
          this.closeModal();
        }, 1500);
      } catch (error) {
        console.error('Ошибка при добавлении призывника:', error);
        this.formError = 'Не удалось добавить призывника. Пожалуйста, попробуйте еще раз.';
      } finally {
        this.submitting = false;
      }
    }
  },
  mounted() {
    this.fetchRecruitments();
    this.fetchRecruitmentOffices();
    this.fetchTroops();
  }
};
</script>

<style scoped>
/* Основные стили таблицы */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  padding: 10px;
  border: 1px solid #ddd;
  text-align: left;
}

th {
  background-color: #f4f4f4;
}

/* Сортировка */
th.sortable {
  cursor: pointer;
  position: relative;
  padding-right: 20px;
  transition: background-color 0.3s;
}

th.sortable:hover {
  background-color: #d1e7fd;
}

th.sortable:after {
  content: '';
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
}

th.sortable.asc:after {
  content: '↑';
}

th.sortable.desc:after {
  content: '↓';
}

/* Стили строк таблицы */
tbody tr:nth-child(odd) {
  background-color: #f9f9f9;
}

tbody tr:nth-child(even) {
  background-color: #e6e6e6;
}

tbody tr:hover {
  background-color: #d1e7fd;
}

/* Фильтры */
.filters {
  margin: 20px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 5px;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-group input, .filter-group select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.button-clear {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.button-clear:hover {
  background-color: #5a6268;
}

/* Пагинация */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 20px 0;
}

.pagination button {
  margin: 0 10px;
  padding: 8px 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.pagination span {
  margin: 0 10px;
}

/* Кнопки */
button {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-button {
  background-color: #28a745;
  color: white;
  padding: 10px 15px;
  margin-bottom: 10px;
}

.add-button:hover {
  background-color: #218838;
}

.delete-button {
  background-color: #dc3545;
  color: white;
}

.delete-button:hover {
  background-color: #c82333;
}

.submit-button {
  background-color: #007bff;
  color: white;
}

.submit-button:hover:not(:disabled) {
  background-color: #0069d9;
}

.reset-button {
  background-color: #6c757d;
  color: white;
}

.reset-button:hover:not(:disabled) {
  background-color: #5a6268;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Модальное окно */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

/* Форма */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input[type="text"],
.form-group input[type="date"],
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.form-group.checkbox {
  display: flex;
  align-items: center;
}

.form-group.checkbox input {
  margin-right: 10px;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

/* Сообщения */
.error {
  color: #721c24;
  background-color: #f8d7da;
  padding: 10px;
  border-radius: 4px;
  margin-top: 15px;
}

.success {
  color: #155724;
  background-color: #d4edda;
  padding: 10px;
  border-radius: 4px;
  margin-top: 15px;
}

.loading {
  text-align: center;
  padding: 20px;
  font-style: italic;
}

.no-data {
  text-align: center;
  padding: 15px;
  font-style: italic;
  color: #6c757d;
}

.recruit-link {
  color: #007bff;
  text-decoration: none;
}

.recruit-link:hover {
  text-decoration: underline;
}

.table-container {
  overflow-x: auto;
}
</style>