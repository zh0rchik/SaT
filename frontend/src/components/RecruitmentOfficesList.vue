<template>
  <div>
    <h2>Призывные пункты</h2>

    <!-- Таблица -->
    <table>
      <thead>
      <tr>
        <th>ID</th> <!-- Добавлен столбец для ID -->
        <th>Адрес</th>
        <th>Начальник</th>
        <th v-if="user">Действия</th>
        <th>Режим работы</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="office in recruitmentOffices" :key="office.id">
        <td>{{ office.id }}</td> <!-- Отображение ID -->
        <td>
          <div v-if="editOfficeId === office.id">
            <input v-model="editAddress" placeholder="Новый адрес" />
          </div>
          <div v-else>
            {{ office.address }}
          </div>
        </td>
        <td>
          <div v-if="editOfficeId === office.id">
            <input v-model="editChiefName" placeholder="Новый начальник" />
          </div>
          <div v-else>
            {{ office.chief_name }}
          </div>
        </td>
        <td v-if="user">
          <div v-if="editOfficeId === office.id">
            <button @click="updateOffice(office.id)">Сохранить</button>
            <button @click="cancelEdit">Отмена</button>
          </div>
          <div v-else>
            <button @click="startEdit(office)">Редактировать</button>
            <button class="button-delete" @click="deleteOffice(office.id)">Удалить</button>
          </div>
        </td>
        <td class="work-hours-cell">
          <ul v-if="office.modes_work.length">
            <li v-for="mode in office.modes_work" :key="mode.id">
              <!-- Режим работы -->
              {{ mode.day }}: {{ mode.work_start }} - {{ mode.work_end }}
              <span v-if="user">
                <button class="button-delete" @click="deleteMode(mode.id)">Удалить</button>
              </span>
            </li>
          </ul>
          <div v-else>Нет данных</div>
        </td>
      </tr>
      </tbody>
    </table>

    <!-- Форма добавления нового призывного пункта -->
    <div v-if="user && editOfficeId == null">
      <h3>Добавить новый призывный пункт</h3>
      <input v-model="newAddress" placeholder="Адрес" />
      <input v-model="newChiefName" placeholder="Начальник" />
      <button @click="addOffice">Добавить</button>
    </div>

    <!-- Форма добавления режима работы -->
    <div v-if="editOfficeId !== null && user">
      <h3>Добавить режим работы</h3>
      <input v-model="newWorkDay" placeholder="День" />
      <input v-model="newWorkStart" placeholder="Начало работы" />
      <input v-model="newWorkEnd" placeholder="Конец работы" />
      <button @click="addWorkMode">Добавить режим работы</button>
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
      newAddress: '',
      newChiefName: '',
      editOfficeId: null,
      editAddress: '',
      editChiefName: '',
      newWorkDay: '',
      newWorkStart: '',
      newWorkEnd: '',
    };
  },
  methods: {
    async fetchOffices() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/recruitment_offices/');
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

    startEdit(office) {
      this.editOfficeId = office.id;
      this.editAddress = office.address;
      this.editChiefName = office.chief_name;
    },

    cancelEdit() {
      this.editOfficeId = null;
      this.editAddress = '';
      this.editChiefName = '';
    },

    async updateOffice(id) {
      if (!this.editAddress.trim() || !this.editChiefName.trim()) {
        alert('Заполните все поля!');
        return;
      }

      try {
        const token = JSON.parse(localStorage.getItem('user'))?.token;
        await axios.patch(
            `http://127.0.0.1:8000/recruitment_offices/${id}?address=${encodeURIComponent(this.editAddress)}&chief_name=${encodeURIComponent(this.editChiefName)}`,
            {},
            { headers: { Authorization: `Bearer ${token}` } }
        );
        this.cancelEdit();
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

        this.newAddress = '';
        this.newChiefName = '';
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
        await axios.post(`http://127.0.0.1:8000/work_hours_office/${this.editOfficeId}`, {
          day: this.newWorkDay,
          work_start: this.newWorkStart,
          work_end: this.newWorkEnd,
        }, {
          headers: { Authorization: `Bearer ${token}` },
        });

        this.newWorkDay = '';
        this.newWorkStart = '';
        this.newWorkEnd = '';
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
}

table, th, td {
  border: 1px solid #ddd;
}

th, td {
  padding: 8px;
  text-align: left;
}

th {
  background-color: #f4f4f4;
}

form {
  margin-bottom: 20px;
}

input {
  padding: 8px;
  margin: 5px;
  border-radius: 4px;
}

button {
  padding: 8px 16px;
  margin: 2px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
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

ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

li {
  margin: 2px 0;
}

.work-hours-cell {
  min-width: 350px;
  white-space: normal;
  vertical-align: top;
}
</style>
