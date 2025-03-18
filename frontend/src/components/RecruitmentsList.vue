<template>
  <div>
    <h2>Список призывников</h2>

    <!-- Таблица призывников -->
    <div v-if="loading" class="loading">
      Загрузка данных...
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="fetchRecruitments" class="retry-button">Попробовать снова</button>
    </div>
    <div v-else class="table-container">
      <div class="table-header">
        <button v-if="user" @click="openModal" class="add-button">
          Добавить призывника
        </button>
      </div>
      <table>
        <thead>
        <tr>
          <th>ID</th>
          <th>Имя</th>
          <th>Адрес</th>
          <th>Дата рождения</th>
          <th>Семейное положение</th>
          <th>Призывной пункт</th>
          <th>Род войск</th>
          <th>Действия</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="recruit in recruitments" :key="recruit.id">
          <td>{{ recruit.id }}</td>
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
          <td>
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
import { ref, reactive, onMounted } from 'vue';

export default {
  name: 'RecruitmentsList',
  props: ['user'],
  emits: ['view-recruit'],
  setup(props, { emit }) {
    const recruitments = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const officesCache = reactive({});
    const troopsCache = reactive({});
    const recruitmentOffices = ref([]);
    const submitting = ref(false);
    const formError = ref(null);
    const formSuccess = ref(null);
    const showModal = ref(false);

    // Новый объект для формы добавления призывника
    const newRecruit = reactive({
      name: '',
      date_of_birth: '',
      address: '',
      marital_status: false,
      recruitment_office_id: null
    });

    // Функция для открытия модального окна
    const openModal = () => {
      showModal.value = true;
      resetForm();
    };

    // Функция для закрытия модального окна
    const closeModal = () => {
      showModal.value = false;
      resetForm();
    };

    // Функция для перехода на страницу призывника
    const viewRecruit = (id) => {
      emit('view-recruit', id);
    };

    // Функция получения токена
    const getToken = () => {
      try {
        if (props.user) {
          return props.user.token;
        }
        const userData = localStorage.getItem('user');
        if (userData) {
          return JSON.parse(userData).token;
        }
        return null;
      } catch (err) {
        console.error('Ошибка при получении токена:', err);
        return null;
      }
    };

    // Функция сброса формы
    const resetForm = () => {
      newRecruit.name = '';
      newRecruit.date_of_birth = '';
      newRecruit.address = '';
      newRecruit.marital_status = false;
      newRecruit.recruitment_office_id = null;
      formError.value = null;
      formSuccess.value = null;
    };

    // Функция отправки формы
    const submitForm = async () => {
      formError.value = null;
      formSuccess.value = null;
      submitting.value = true;

      const token = getToken();
      if (!token) {
        formError.value = 'Необходима авторизация';
        submitting.value = false;
        return;
      }

      try {
        const response = await axios.post('http://127.0.0.1:8000/recruitments/', newRecruit, {
          timeout: 5000,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        });

        // Добавляем новый элемент в начало списка
        recruitments.value.unshift(response.data);
        formSuccess.value = 'Призывник успешно добавлен';

        // Автоматически закрываем модальное окно через 1.5 секунды после успешного добавления
        setTimeout(() => {
          closeModal();
        }, 1500);

        // Загружаем дополнительную информацию для нового призывника
        if (response.data.recruitment_office_id) {
          fetchRecruitmentOffice(response.data.recruitment_office_id);
        }
        if (response.data.troop_id) {
          fetchTroop(response.data.troop_id);
        }

      } catch (err) {
        console.error('Ошибка при добавлении призывника:', err);

        if (err.response && err.response.status === 401) {
          formError.value = 'Ошибка авторизации. Пожалуйста, войдите снова.';
        } else if (err.code === 'ECONNABORTED') {
          formError.value = 'Превышено время ожидания ответа от сервера';
        } else if (err.response) {
          // Проверяем, есть ли подробная информация об ошибке валидации
          if (err.response.data?.detail && Array.isArray(err.response.data.detail)) {
            const errors = err.response.data.detail.map(e => `${e.loc[1]}: ${e.msg}`).join('; ');
            formError.value = `Ошибка валидации: ${errors}`;
          } else {
            formError.value = `Ошибка сервера: ${err.response.status} - ${err.response.data?.detail || 'Неизвестная ошибка'}`;
          }
        } else if (err.request) {
          formError.value = 'Не удалось соединиться с сервером. Проверьте, что сервер запущен и доступен.';
        } else {
          formError.value = `Ошибка: ${err.message}`;
        }
      } finally {
        submitting.value = false;
      }
    };

    const fetchRecruitments = async () => {
      loading.value = true;
      error.value = null;

      try {
        // Добавляем обработку timeout для предотвращения вечной загрузки
        const response = await axios.get('http://127.0.0.1:8000/recruitments/', {
          timeout: 5000,
        });

        recruitments.value = response.data || [];

        // Проверяем, что данные в ожидаемом формате
        if (!Array.isArray(recruitments.value)) {
          throw new Error('Неверный формат данных');
        }

        // Загружаем информацию о призывных пунктах и родах войск
        for (const recruit of recruitments.value) {
          if (recruit.recruitment_office_id !== null && recruit.recruitment_office_id !== undefined) {
            fetchRecruitmentOffice(recruit.recruitment_office_id);
          }

          if (recruit.troop_id !== null && recruit.troop_id !== undefined) {
            fetchTroop(recruit.troop_id);
          }
        }

      } catch (err) {
        console.error('Ошибка при загрузке данных:', err);

        if (err.code === 'ECONNABORTED') {
          error.value = 'Превышено время ожидания ответа от сервера';
        } else if (err.response) {
          // Ошибка с ответом от сервера
          error.value = `Ошибка сервера: ${err.response.status} - ${err.response.data?.detail || 'Неизвестная ошибка'}`;
        } else if (err.request) {
          // Ошибка без ответа от сервера
          error.value = 'Не удалось соединиться с сервером. Проверьте, что сервер запущен и доступен.';
        } else {
          // Другие ошибки
          error.value = `Ошибка: ${err.message}`;
        }
      } finally {
        loading.value = false;
      }
    };

    // Получение списка всех призывных пунктов для выпадающего списка
    const fetchAllRecruitmentOffices = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/recruitment_offices/', {
          timeout: 5000,
        });

        if (Array.isArray(response.data)) {
          recruitmentOffices.value = response.data;

          // Также добавляем в кэш для отображения в таблице
          response.data.forEach(office => {
            officesCache[office.id] = office;
          });
        }
      } catch (err) {
        console.error('Ошибка при загрузке призывных пунктов:', err);
      }
    };

    const fetchRecruitmentOffice = async (id) => {
      if (officesCache[id]) return;
      if (id === null || id === undefined) return;

      try {
        const response = await axios.get(`http://127.0.0.1:8000/recruitment_offices/${id}`, {
          timeout: 3000,
        });
        officesCache[id] = response.data;
      } catch (err) {
        console.error(`Ошибка при загрузке данных о призывном пункте ${id}:`, err);
        officesCache[id] = { error: true, message: err.message };
      }
    };

    const fetchTroop = async (id) => {
      if (troopsCache[id]) return;
      if (id === null || id === undefined) return;

      try {
        const response = await axios.get(`http://127.0.0.1:8000/troops/${id}`, {
          timeout: 3000,
        });
        troopsCache[id] = response.data;
      } catch (err) {
        console.error(`Ошибка при загрузке данных о роде войск ${id}:`, err);
        troopsCache[id] = { error: true, message: err.message };
      }
    };

    // Функция удаления призывника
    const deleteRecruit = async (id) => {
      const token = getToken();
      if (!token) {
        alert('Необходима авторизация для удаления');
        return;
      }

      try {
        await axios.delete(`http://127.0.0.1:8000/recruitments/${id}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        // Удаляем призывника из списка после успешного запроса
        recruitments.value = recruitments.value.filter(r => r.id !== id);

      } catch (err) {
        console.error(`Ошибка при удалении призывника ID=${id}:`, err);
        alert('Ошибка при удалении призывника');
      }
    };

    const getRecruitmentOfficeInfo = (id) => {
      if (id === null || id === undefined) return 'Не прикреплён';
      if (!officesCache[id]) return 'Загрузка...';
      if (officesCache[id].error) return 'Ошибка загрузки';

      const office = officesCache[id];
      return `${office.address || 'Адрес не указан'} (${office.chief_name || 'Начальник не указан'})`;
    };

    const getTroopInfo = (id) => {
      if (id === null || id === undefined) return 'Не определён';
      if (!troopsCache[id]) return 'Загрузка...';
      if (troopsCache[id].error) return 'Ошибка загрузки';

      return troopsCache[id].name || 'Название не указано';
    };

    const formatDate = (dateString) => {
      if (!dateString) return 'Не указана';

      try {
        const date = new Date(dateString);

        if (isNaN(date.getTime())) {
          return 'Некорректная дата';
        }

        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();

        return `${day}.${month}.${year}`;
      } catch (err) {
        console.error('Ошибка форматирования даты:', err);
        return 'Ошибка формата';
      }
    };

    onMounted(() => {
      fetchRecruitments();
      fetchAllRecruitmentOffices();
    });

    return {
      recruitments,
      loading,
      error,
      fetchRecruitments,
      getRecruitmentOfficeInfo,
      getTroopInfo,
      formatDate,
      newRecruit,
      submitForm,
      resetForm,
      formError,
      formSuccess,
      submitting,
      recruitmentOffices,
      viewRecruit,
      deleteRecruit,
      showModal,
      openModal,
      closeModal
    };
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
  background-color: #f4f4f4;
}

.loading, .error {
  margin: 20px 0;
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 4px;
}

.error {
  color: #e74c3c;
  border-left: 4px solid #e74c3c;
}

.success {
  color: #27ae60;
  border-left: 4px solid #27ae60;
  margin: 20px 0;
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 4px;
}

.no-data {
  text-align: center;
  color: #7f8c8d;
  padding: 20px 0;
}

.retry-button {
  margin-top: 10px;
  padding: 5px 10px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-button:hover {
  background-color: #2980b9;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input, .form-group select {
  padding: 8px;
  width: calc(100% - 18px);
  border: 1px solid #ccc;
  border-radius: 4px;
}

.form-group.checkbox {
  display: flex;
  align-items: center;
}

.form-group.checkbox input {
  width: auto;
  margin-right: 10px;
}

.form-actions {
  margin-top: 20px;
  margin-bottom: 10px;
  display: flex;
  gap: 10px;
}

button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  opacity: 0.9;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Стиль для ссылки на страницу призывника */
.recruit-link {
  color: #007bff;
  text-decoration: none;
  cursor: pointer;
}

.recruit-link:hover {
  text-decoration: underline;
  color: #0056b3;
}

.delete-button {
  background-color: #e74c3c;
  color: white;
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.delete-button:hover {
  background-color: #c0392b;
}

/* Стили для модального окна */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 5px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.modal-header h3 {
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #333;
  padding: 0;
}

.close-button:hover {
  color: #e74c3c;
}

.table-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.add-button {
  background-color: #27ae60;
  color: white;
}

.submit-button {
  background-color: #3498db;
  color: white;
  flex: 1;
}

.reset-button {
  background-color: #95a5a6;
  color: white;
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    padding: 15px;
  }

  .form-actions {
    flex-direction: column;
  }

  .table-container {
    overflow-x: auto;
  }
}
</style>