<template>
  <div>
    <h2>Призывные пункты</h2>

    <!-- Фильтрация -->
    <div class="filters">
      <div class="filter-group">
        <input v-model="filters.address" placeholder="Фильтр по адресу" @input="applyFilters" />
        <input v-model="filters.chief_name" placeholder="Фильтр по начальнику" @input="applyFilters" />
        <button @click="clearFilters" class="button-clear">Сбросить фильтры</button>
      </div>
    </div>

    <div>По Вашему запросу найдено {{ countRecords }} записи(ей)</div>

    <!-- Таблица -->
    <table>
      <thead>
      <tr style="background: #f4f4f4">
        <th>№</th>
        <th @click="sort('address')" class="sortable" :class="{'asc': sortField === 'address' && sortOrder === 'asc', 'desc': sortField === 'address' && sortOrder === 'desc'}">
          Адрес
        </th>
        <th @click="sort('chief_name')" class="sortable" :class="{'asc': sortField === 'chief_name' && sortOrder === 'asc', 'desc': sortField === 'chief_name' && sortOrder === 'desc'}">
          Начальник
        </th>
        <th v-if="user">Действия</th>
        <th>Режим работы</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(office, index) in recruitmentOffices" :key="office.id">
        <td style="text-align: center;">{{ currentPage * pageSize + index + 1 }}</td>
        <td>{{ office.address }}</td>
        <td>{{ office.chief_name }}</td>
        <td v-if="user">
          <button @click="openEditModal(office)">Редактировать</button>
          <button class="button-delete" @click="deleteOffice(office.id)">Удалить</button>
          <button @click="openWorkModeModal(office)">Добавить режим</button>
        </td>
        <td class="work-hours-cell">
          <ul v-if="office.modes_work.length">
            <li v-for="mode in office.modes_work" :key="mode.id">
              {{ mode.day }}: {{ mode.work_start }} - {{ mode.work_end }}
              <span v-if="user">
                <button class="button-delete" @click="deleteMode(mode.id)">Удалить</button>
              </span>
            </li>
          </ul>
          <div v-else>Нет данных</div>
        </td>
      </tr>
      <tr v-if="recruitmentOffices.length === 0">
        <td colspan="5" style="text-align: center;">Нет данных</td>
      </tr>
      </tbody>
    </table>

    <!-- Пагинация -->
    <div class="pagination">
      <button @click="prevPage" :disabled="currentPage === 0">Предыдущая</button>
      <span>Страница {{ currentPage + 1 }}</span>
      <button @click="nextPage" :disabled="recruitmentOffices.length < pageSize">Следующая</button>
    </div>

    <!-- Кнопка добавления нового призывного пункта -->
    <div v-if="user" class="add-button-container">
      <button @click="openAddModal" class="add-button">Добавить новый призывный пункт</button>
    </div>

    <!-- Модальное окно для добавления нового призывного пункта -->
    <div v-if="showAddModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeAddModal">&times;</span>
        <h3>Добавить новый призывный пункт</h3>
        <div class="form-group">
          <label>Адрес:</label>
          <input v-model="newAddress" placeholder="Адрес" />
        </div>
        <div class="form-group">
          <label>Начальник:</label>
          <input v-model="newChiefName" placeholder="Начальник" />
        </div>
        <div class="form-actions">
          <button @click="addOffice">Добавить</button>
          <button @click="closeAddModal" class="button-cancel">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно для редактирования призывного пункта -->
    <div v-if="showEditModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeEditModal">&times;</span>
        <h3>Редактировать призывный пункт</h3>
        <div class="form-group">
          <label>Адрес:</label>
          <input v-model="editAddress" placeholder="Новый адрес" />
        </div>
        <div class="form-group">
          <label>Начальник:</label>
          <input v-model="editChiefName" placeholder="Новый начальник" />
        </div>
        <div class="form-actions">
          <button @click="updateOffice">Сохранить</button>
          <button @click="closeEditModal" class="button-cancel">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно для добавления режима работы -->
    <div v-if="showWorkModeModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeWorkModeModal">&times;</span>
        <h3>Добавить режим работы</h3>
        <div class="form-group">
          <label>День недели:</label>
          <select v-model="newWorkDay">
            <option value="">Выберите день</option>
            <option value="Пн">Понедельник</option>
            <option value="Вт">Вторник</option>
            <option value="Ср">Среда</option>
            <option value="Чт">Четверг</option>
            <option value="Пт">Пятница</option>
            <option value="Сб">Суббота</option>
          </select>
        </div>
        <div class="form-group">
          <label>Время начала:</label>
          <input type="time" v-model="newWorkStart" />
        </div>
        <div class="form-group">
          <label>Время окончания:</label>
          <input type="time" v-model="newWorkEnd" />
        </div>
        <div class="form-actions">
          <button @click="addWorkMode">Добавить режим работы</button>
          <button @click="closeWorkModeModal" class="button-cancel">Отмена</button>
        </div>
      </div>
    </div>
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
      // Данные для нового призывного пункта
      newAddress: '',
      newChiefName: '',
      // Данные для редактирования
      editOfficeId: null,
      editAddress: '',
      editChiefName: '',
      // Данные для режима работы
      selectedOfficeId: null,
      newWorkDay: '',
      newWorkStart: '',
      newWorkEnd: '',
      // Состояния модальных окон
      showAddModal: false,
      showEditModal: false,
      showWorkModeModal: false,
      // Переменные для сортировки
      sortField: 'address',
      sortOrder: 'asc',
      // Переменные для пагинации
      currentPage: 0,
      pageSize: 3,  // поменять
      // Переменные для фильтрации
      filters: {
        address: '',
        chief_name: ''
      },
      countRecords: 0
    };
  },
  methods: {
    // Функция для сортировки
    sort(field) {
      if (this.sortField === field) {
        // Если уже сортируем по этому полю, меняем порядок
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        // Если новое поле, устанавливаем его и сбрасываем порядок на 'asc'
        this.sortField = field;
        this.sortOrder = 'asc';
      }

      // Перезагружаем данные с новыми параметрами сортировки
      this.fetchOffices();
    },

    // Функции для пагинации
    prevPage() {
      if (this.currentPage > 0) {
        this.currentPage--;
        this.fetchOffices();
      }
    },

    nextPage() {
      this.currentPage++;
      this.fetchOffices();
    },

    // Функции для фильтрации
    applyFilters() {
      this.currentPage = 0;
      this.fetchOffices();
    },

    clearFilters() {
      this.filters = { address: '', chief_name: '' };
      this.applyFilters();
    },

    async fetchOffices() {
      this.pageSize = this.user ? Number(localStorage.getItem('page_size')) : 5
      try {
        // Формируем URL с параметрами сортировки, пагинации и фильтрации
        let url = `http://127.0.0.1:8000/recruitment_offices/?sort_by=${this.sortField}&order=${this.sortOrder}`;

        // Добавляем параметры фильтрации
        if (this.filters.address) {
          url += `&address=${encodeURIComponent(this.filters.address)}`;
        }
        if (this.filters.chief_name) {
          url += `&chief_name=${encodeURIComponent(this.filters.chief_name)}`;
        }

        // количество записей
        const responseForCount = await axios.get(url);
        this.countRecords = responseForCount.data.length;

        url += `&skip=${this.currentPage * this.pageSize}&limit=${this.pageSize}`

        const response = await axios.get(url);
        const offices = response.data;

        // Запрашиваем режимы работы для каждого офиса
        for (const office of offices) {
          const modesResponse = await axios.get(`http://127.0.0.1:8000/work_hours_office/${office.id}`);
          office.modes_work = modesResponse.data;
        }

        this.recruitmentOffices = offices;
      } catch (error) {
        console.error('Ошибка при получении данных:', error);
      }
    },

    // Методы для модальных окон
    openAddModal() {
      this.showAddModal = true;
      this.newAddress = '';
      this.newChiefName = '';
    },

    closeAddModal() {
      this.showAddModal = false;
    },

    openEditModal(office) {
      this.editOfficeId = office.id;
      this.editAddress = office.address;
      this.editChiefName = office.chief_name;
      this.showEditModal = true;
    },

    closeEditModal() {
      this.showEditModal = false;
    },

    openWorkModeModal(office) {
      this.selectedOfficeId = office.id;
      this.newWorkDay = '';
      this.newWorkStart = '';
      this.newWorkEnd = '';
      this.showWorkModeModal = true;
    },

    closeWorkModeModal() {
      this.showWorkModeModal = false;
    },

    // Методы для управления данными
    async deleteMode(modeId) {
      if (!confirm('Вы уверены, что хотите удалить этот режим работы?')) return;

      try {
        const token = JSON.parse(localStorage.getItem('user'))?.token;
        await axios.delete(`http://127.0.0.1:8000/work_hours_office/${modeId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        await this.fetchOffices();
      } catch (error) {
        console.error('Ошибка при удалении режима работы:', error);
      }
    },

    async deleteOffice(id) {
      if (!confirm('Удалить этот пункт?')) return;
      try {
        const token = JSON.parse(localStorage.getItem('user'))?.token;
        await axios.delete(`http://127.0.0.1:8000/recruitment_offices/${id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        await this.fetchOffices();
      } catch (error) {
        console.error('Ошибка при удалении:', error);
      }
    },

    async updateOffice() {
      if (!this.editAddress.trim() || !this.editChiefName.trim()) {
        alert('Заполните все поля!');
        return;
      }

      try {
        const token = JSON.parse(localStorage.getItem('user'))?.token;
        await axios.patch(
            `http://127.0.0.1:8000/recruitment_offices/${this.editOfficeId}?address=${encodeURIComponent(this.editAddress)}&chief_name=${encodeURIComponent(this.editChiefName)}`,
            {},
            { headers: { Authorization: `Bearer ${token}` } }
        );
        this.closeEditModal();
        await this.fetchOffices();
      } catch (error) {
        console.error('Ошибка при обновлении данных:', error);
      }
    },

    async addOffice() {
      if (!this.newAddress.trim() || !this.newChiefName.trim()) {
        alert('Заполните все поля!');
        return;
      }

      try {
        const token = JSON.parse(localStorage.getItem('user'))?.token;
        await axios.post('http://127.0.0.1:8000/recruitment_offices/', {
          address: this.newAddress,
          chief_name: this.newChiefName,
        }, {
          headers: { Authorization: `Bearer ${token}` },
        });

        this.closeAddModal();
        await this.fetchOffices();
      } catch (error) {
        console.error('Ошибка при добавлении призывного пункта:', error);
      }
    },

    async addWorkMode() {
      if (!this.newWorkDay.trim() || !this.newWorkStart.trim() || !this.newWorkEnd.trim()) {
        alert('Заполните все поля!');
        return;
      }

      try {
        const token = JSON.parse(localStorage.getItem('user'))?.token;
        await axios.post(`http://127.0.0.1:8000/work_hours_office/${this.selectedOfficeId}`, {
          day: this.newWorkDay,
          work_start: this.newWorkStart,
          work_end: this.newWorkEnd,
        }, {
          headers: { Authorization: `Bearer ${token}` },
        });

        this.closeWorkModeModal();
        await this.fetchOffices();
      } catch (error) {
        console.error('Ошибка при добавлении режима работы:', error);
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
  border-collapse: collapse;
  margin-top: 20px;
  width: 100%;
}

table, th, td {
  border: 1px solid #ddd;
}

th, td {
  padding: 8px;
  text-align: left;
}

input, select {
  padding: 8px;
  margin: 5px 0;
  border-radius: 4px;
  border: 1px solid #ccc;
  width: 100%;
}

button {
  padding: 8px 16px;
  margin: 2px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 4px;
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

.button-cancel {
  background-color: #6c757d;
}

.button-cancel:hover {
  background-color: #5a6268;
}

.button-clear {
  background-color: #6c757d;
}

.button-clear:hover {
  background-color: #5a6268;
}

ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

li {
  margin: 2px 0;
  padding: 4px;
  border-bottom: 1px solid #eee;
}

.work-hours-cell {
  min-width: 300px;
  white-space: normal;
  vertical-align: top;
}

/* Стили для модальных окон */
.modal {
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background-color: #fefefe;
  padding: 20px;
  border-radius: 8px;
  width: 80%;
  max-width: 500px;
  position: relative;
}

.close {
  color: #aaa;
  position: absolute;
  right: 15px;
  top: 10px;
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
}

.close:hover,
.close:focus {
  color: #000;
  text-decoration: none;
  cursor: pointer;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 10px;
}

.add-button-container {
  margin: 20px 0;
  text-align: right;
}

.add-button {
  font-size: 16px;
  padding: 10px 20px;
}

tbody tr:nth-child(odd) {
  background-color: #f9f9f9; /* Светлый фон для нечетных строк */
}

tbody tr:nth-child(even) {
  background-color: #e6e6e6; /* Чуть темнее для четных строк */
}
tbody tr:hover {
  background-color: #d1e7fd; /* Голубой оттенок при наведении */
}

/* Стили для сортируемых заголовков */
th.sortable {
  cursor: pointer;
  position: relative;
  padding-right: 20px; /* Место для стрелки */
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

/* Стили для фильтров */
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
  flex-direction: column;
  gap: 10px; /* Расстояние между инпутами */
  max-width: 300px; /* Чтобы не растягивалось на всю ширину */
}

.filter-group input, .filter-group select {
  margin-right: 10px;
  margin-bottom: 0;
  width: auto;
}

/* Стили для пагинации */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 20px 0;
}

.pagination button {
  margin: 0 10px;
}

.pagination span {
  margin: 0 10px;
}
</style>