<template>
  <div class="recruitment-page">
    <h2>Информация о призывнике</h2>

    <div v-if="loading" class="loading">
      Загрузка данных...
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="fetchRecruitment" class="retry-button">Попробовать снова</button>
    </div>
    <div v-else-if="recruit" class="recruit-info">
      <div class="recruit-container">
        <!-- Фото призывника -->
        <div class="recruit-photo">
          <img :src="getPhotoUrl(recruit.photo)" alt="Фото призывника" />
          <!-- Упрощенная загрузка фото -->
          <label v-if="user" class="upload-photo-button">
            Загрузить фото
            <input
                type="file"
                @change="onPhotoSelectedAndUpload"
                accept="image/*"
                style="display: none;"
            />
          </label>
        </div>

        <!-- Текстовая информация -->
        <div class="recruit-details">
          <p><strong>ID призывника:</strong> {{ recruit.id }}</p>
          <p><strong>ФИО:</strong> {{ recruit.name || 'Не указано' }}</p>
          <p><strong>Адрес:</strong> {{ recruit.address || 'Не указано' }}</p>
          <p><strong>Дата рождения:</strong> {{ formatDate(recruit.date_of_birth) }}</p>
          <p><strong>Семейное положение:</strong> {{ recruit.marital_status ? 'Женат' : 'Холост' }}</p>
          <p><strong>Призывной пункт:</strong> {{ recruitmentOffice ? `${recruitmentOffice.address} (Начальник: ${recruitmentOffice.chief_name})` : 'Не указан' }}</p>
          <p><strong>Род войск:</strong> {{ troop ? troop.name : 'Не указан' }}</p>
        </div>
      </div>

      <!-- Кнопка редактирования только для авторизованных пользователей -->
      <div class="actions-container">
        <button @click="goBack" class="back-button">Назад к списку</button>
        <button v-if="user" @click="openEditModal" class="edit-button">Редактировать данные</button>
      </div>
    </div>
    <div v-else>
      <p>Данные не найдены</p>
      <button @click="goBack" class="back-button">Назад к списку</button>
    </div>
  </div>

  <!-- Модальное окно редактирования -->
  <div v-if="showEditModal" class="modal-overlay" @click="closeModalOnOverlay">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>Редактирование данных призывника</h3>
        <button @click="closeEditModal" class="close-button">&times;</button>
      </div>

      <div v-if="updateError" class="error">
        <p>{{ updateError }}</p>
      </div>
      <div v-if="updateSuccess" class="success">
        <p>{{ updateSuccess }}</p>
      </div>

      <form @submit.prevent="submitUpdate" class="edit-form">
        <div class="form-group">
          <label for="name">ФИО:</label>
          <input id="name" v-model="editForm.name" type="text" placeholder="Введите ФИО призывника" />
        </div>

        <div class="form-group">
          <label for="address">Адрес:</label>
          <input id="address" v-model="editForm.address" type="text" placeholder="Введите адрес призывника" />
        </div>

        <div class="form-group">
          <label for="date_of_birth">Дата рождения:</label>
          <input id="date_of_birth" v-model="editForm.date_of_birth" type="date" />
        </div>

        <div class="form-group">
          <label for="marital_status">Семейное положение:</label>
          <select id="marital_status" v-model="editForm.marital_status">
            <option :value="false">Холост</option>
            <option :value="true">Женат</option>
          </select>
        </div>

        <div class="form-group">
          <label for="recruitment_office_id">Призывной пункт:</label>
          <select id="recruitment_office_id" v-model="editForm.recruitment_office_id">
            <option :value="null">Не выбрано</option>
            <option v-for="office in recruitmentOffices" :key="office.id" :value="office.id">
              {{ office.address }} ({{ office.chief_name }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="troop_id">Род войск:</label>
          <select id="troop_id" v-model="editForm.troop_id">
            <option :value="null">Не выбрано</option>
            <option v-for="t in troops" :key="t.id" :value="t.id">
              {{ t.name }}
            </option>
          </select>
          <p class="help-text">Внимание: Для назначение рода войск призывник должен пройти мед. комиссию со статусом: "годен к строевой службе"</p>
        </div>

        <div class="form-actions">
          <button type="submit" :disabled="updating">
            {{ updating ? 'Сохранение...' : 'Сохранить изменения' }}
          </button>
          <button type="button" @click="closeEditModal" :disabled="updating">
            Отмена
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Добавьте после блока с основной информацией -->
  <div class="medexams-section">
    <h3>Медицинские комиссии</h3>
      <table class="medexams-table">
        <thead>
        <tr>
          <th>№</th>
          <th>Дата</th>
          <th>Результат</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="exam in medExams" :key="exam.id">
          <td style="text-align: center;">{{ medExams.indexOf(exam) + 1 }}</td>
          <td>{{ formatDate(exam.date_of_exam) }}</td>
          <td :class="getResultClass(exam.result)">{{ exam.result }}</td>
        </tr>
        </tbody>
      </table>
  </div>

  <!-- Добавьте в конец блока medexams-section -->
  <div class="medexams-actions" v-if="user">
    <button @click="openAddMedExamModal" class="add-button">Добавить медкомиссию</button>
  </div>

  <!-- Добавьте в конец шаблона перед закрывающим тегом template -->
  <!-- Модальное окно добавления медкомиссии -->
  <div v-if="showAddMedExamModal" class="modal-overlay" @click="closeAddMedExamModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>Добавление медкомиссии</h3>
        <button @click="closeAddMedExamModal" class="close-button">&times;</button>
      </div>

      <div v-if="addMedExamError" class="error">
        <p>{{ addMedExamError }}</p>
      </div>
      <div v-if="addMedExamSuccess" class="success">
        <p>{{ addMedExamSuccess }}</p>
      </div>

      <form @submit.prevent="submitAddMedExam" class="edit-form">
        <div class="form-group">
          <label for="date_of_exam">Дата медкомиссии <span class="required">*</span>:</label>
          <input id="date_of_exam" v-model="medExamForm.date_of_exam" type="date" required />
        </div>

        <div class="form-group">
          <label for="recruitment_id">ID призывника:</label>
          <input id="recruitment_id" :value="medExamForm.recruitment_id" type="number" disabled />
          <p class="help-text">ID призывника не может быть изменен</p>
        </div>

        <div class="form-group">
          <label for="result">Результат <span class="required">*</span>:</label>
          <select id="result" v-model="medExamForm.result" required>
            <option v-for="result in examResults" :key="result" :value="result">
              {{ result }}
            </option>
          </select>
        </div>

        <div class="form-actions">
          <button type="submit" :disabled="addingMedExam">
            {{ addingMedExam ? 'Сохранение...' : 'Сохранить' }}
          </button>
          <button type="button" @click="closeAddMedExamModal" :disabled="addingMedExam">
            Отмена
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { ref, reactive, onMounted } from 'vue';

export default {
  name: 'RecruitmentPage',
  props: {
    recruitId: {
      type: [Number, String],
      required: true
    },
    user: Object
  },
  emits: ['back'],
  setup(props, { emit }) {
    const medExams = ref([]);
    const loadingMedExams = ref(false);
    const medExamsError = ref(null);

    const recruit = ref(null);
    const recruitmentOffice = ref(null);
    const troop = ref(null);
    const loading = ref(true);
    const error = ref(null);
    const showEditModal = ref(false);
    const updating = ref(false);
    const updateError = ref(null);
    const updateSuccess = ref(null);
    const recruitmentOffices = ref([]);
    const troops = ref([]);

    const showAddMedExamModal = ref(false);
    const addingMedExam = ref(false);
    const addMedExamError = ref(null);
    const addMedExamSuccess = ref(null);

    // Форма редактирования
    const editForm = reactive({
      name: '',
      address: '',
      date_of_birth: '',
      marital_status: false, // Изначально холост
      recruitment_office_id: null,
      troop_id: null
    });

    // Форма для добавления медкомиссии
    const medExamForm = reactive({
      date_of_exam: new Date().toISOString().substr(0, 10), // Текущая дата по умолчанию
      recruitment_id: props.recruitId,
      result: "годен к строевой службе" // Значение по умолчанию
    });

    // Варианты результатов
    const examResults = [
      "годен к строевой службе",
      "годен к альтернативной службе",
      "ограничено годен",
      "не годен"
    ];

    // Функция открытия модального окна добавления медкомиссии
    const openAddMedExamModal = () => {
      showAddMedExamModal.value = true;
      addMedExamError.value = null;
      addMedExamSuccess.value = null;

      // Сбросить форму к начальным значениям
      medExamForm.date_of_exam = new Date().toISOString().substr(0, 10);
      medExamForm.recruitment_id = props.recruitId;
      medExamForm.result = "годен к строевой службе";
    };

// Функция закрытия модального окна
    const closeAddMedExamModal = () => {
      showAddMedExamModal.value = false;
    };

// Функция для отправки формы
    const submitAddMedExam = async () => {
      if (!props.user || !props.user.token) {
        addMedExamError.value = 'Необходима авторизация для добавления медкомиссии.';
        return;
      }

      addingMedExam.value = true;
      addMedExamError.value = null;
      addMedExamSuccess.value = null;

      try {
        await axios.post(
            'http://127.0.0.1:8000/medexams/',
            {
              date_of_exam: medExamForm.date_of_exam,
              recruitment_id: medExamForm.recruitment_id,
              result: medExamForm.result
            },
            {
              headers: {
                'Authorization': `Bearer ${props.user.token}`,
                'Content-Type': 'application/json'
              }
            }
        );

        addMedExamSuccess.value = 'Данные медкомиссии успешно добавлены!';
        await fetchMedExams(); // Перезагрузка данных медкомиссий

        // Закрыть модальное окно через 1 секунду
        setTimeout(() => {
          closeAddMedExamModal();
        }, 1000);
      } catch (err) {
        console.error('Ошибка при добавлении медкомиссии:', err);
        addMedExamError.value = err.response?.data?.detail || 'Ошибка при добавлении данных медкомиссии.';
      } finally {
        addingMedExam.value = false;
      }
    };

    const fetchMedExams = async () => {
      loadingMedExams.value = true;
      medExamsError.value = null;
      try {
        const response = await axios.get(`http://127.0.0.1:8000/medexams/${props.recruitId}`);
        medExams.value = response.data;
      } catch (err) {
        console.error('Ошибка при загрузке данных медкомиссий:', err);
        medExamsError.value = 'Ошибка при загрузке данных медкомиссий.';
      } finally {
        loadingMedExams.value = false;
      }
    };

    const getResultClass = (result) => {
      switch (result) {
        case 'годен к строевой службе':
          return 'result-fit';
        case 'годен к альтернативной службе':
          return 'result-alternative';
        case 'ограничено годен':
          return 'result-limited';
        case 'не годен':
          return 'result-unfit';
        default:
          return '';
      }
    };

    // Загрузка данных призывника
    const fetchRecruitment = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await axios.get(`http://127.0.0.1:8000/recruitments/${props.recruitId}`);
        recruit.value = response.data;

        // Обновляем форму данными
        editForm.name = response.data.name || '';
        editForm.address = response.data.address || '';
        editForm.date_of_birth = response.data.date_of_birth || '';
        editForm.marital_status = Boolean(response.data.marital_status);
        editForm.recruitment_office_id = response.data.recruitment_office_id || null;
        editForm.troop_id = response.data.troop_id || null;

        // Получаем связанные данные, если они есть
        if (response.data.recruitment_office_id) {
          try {
            const officeResponse = await axios.get(`http://127.0.0.1:8000/recruitment_offices/${response.data.recruitment_office_id}`);
            recruitmentOffice.value = officeResponse.data;
          } catch (officeErr) {
            console.error('Ошибка при загрузке данных призывного пункта:', officeErr);
          }
        }

        if (response.data.troop_id) {
          try {
            const troopResponse = await axios.get(`http://127.0.0.1:8000/troops/${response.data.troop_id}`);
            troop.value = troopResponse.data;
          } catch (troopErr) {
            console.error('Ошибка при загрузке данных о роде войск:', troopErr);
          }
        }
      } catch (err) {
        console.error('Ошибка при загрузке данных призывника:', err);
        error.value = 'Ошибка при загрузке данных призывника.';
      } finally {
        loading.value = false;
      }
    };

    const handleMaritalStatusChange = (event) => {
      editForm.marital_status = event.target.value === 'false'; // точно преобразуем в boolean
    };


    // Загрузка списков для выбора
    const fetchOfficesAndTroops = async () => {
      try {
        const [officesRes, troopsRes] = await Promise.all([
          axios.get('http://127.0.0.1:8000/recruitment_offices/'),
          axios.get('http://127.0.0.1:8000/troops/')
        ]);
        recruitmentOffices.value = officesRes.data;
        troops.value = troopsRes.data;
      } catch (err) {
        console.error('Ошибка при загрузке списков:', err);
        updateError.value = 'Ошибка при загрузке списков офисов и родов войск.';
      }
    };

    // Открыть модальное окно
    const openEditModal = async () => {
      try {
        await fetchOfficesAndTroops();
        showEditModal.value = true;
        updateError.value = null;
        updateSuccess.value = null;
      } catch (err) {
        console.error('Ошибка при открытии модального окна:', err);
      }
    };

    const closeEditModal = () => {
      showEditModal.value = false;
    };

    const closeModalOnOverlay = (e) => {
      if (e.target === e.currentTarget) {
        closeEditModal();
      }
    };

    // Сохранить изменения - исправляем обработку marital_status
    const submitUpdate = async () => {
      updating.value = true;
      updateError.value = null;
      updateSuccess.value = null;

      try {
        // Создаем URL с параметрами запроса вместо тела запроса
        const params = new URLSearchParams();

        // Добавляем все поля, даже если они не изменились
        params.append('name', editForm.name || '');
        params.append('address', editForm.address || '');
        if (editForm.date_of_birth) params.append('date_of_birth', editForm.date_of_birth);

        params.append('marital_status', editForm.marital_status ? 'true' : 'false');

        if (editForm.troop_id) params.append('troop_id', editForm.troop_id);
        if (editForm.recruitment_office_id) params.append('recruitment_office_id', editForm.recruitment_office_id);

        console.log('Sending params:', Object.fromEntries(params.entries()));

        const url = `http://127.0.0.1:8000/recruitments/${props.recruitId}?${params.toString()}`;

        await axios.patch(
            url,
            {}, // Пустое тело запроса, так как все данные в URL
            {
              headers: {
                'Authorization': `Bearer ${props.user.token}`
              }
            }
        );

        updateSuccess.value = 'Данные успешно обновлены!';
        await fetchRecruitment(); // Перезагрузка данных
        setTimeout(() => {
          closeEditModal();
        }, 1000);
      } catch (err) {
        console.error('Ошибка при обновлении данных:', err);
        if (err.response?.data) {
          console.error('Детали ошибки:', err.response.data);
        }
        updateError.value = err.response?.data?.detail || 'Ошибка при обновлении данных. Убедитесь, что все поля заполнены корректно.';
      } finally {
        updating.value = false;
      }
    };

    // Работа с фото
    const getPhotoUrl = (photoPath) => {
      if (!photoPath) return '/default-avatar.png';
      return photoPath.startsWith('http') ? photoPath : `http://127.0.0.1:8000${photoPath}`;
    };

    const onPhotoSelectedAndUpload = async (event) => {
      const file = event.target.files[0];
      if (!file) return;

      if (!props.user || !props.user.token) {
        alert('Необходима авторизация для загрузки фото.');
        return;
      }

      const formData = new FormData();
      formData.append('photo', file); // Используем 'photo' вместо 'file'

      try {
        await axios.post(
            `http://127.0.0.1:8000/recruitments/upload_avatar/${props.recruitId}`,
            formData,
            {
              headers: {
                'Authorization': `Bearer ${props.user.token}`,
                'Content-Type': 'multipart/form-data'
              }
            }
        );
        await fetchRecruitment(); // Обновить данные после загрузки фото
      } catch (err) {
        console.error('Ошибка при загрузке фото:', err);
        alert('Ошибка при загрузке фото: ' + (err.response?.data?.detail || err.message));
      }
    };

    // Навигация назад
    const goBack = () => emit('back');

    const formatDate = (dateStr) => {
      if (!dateStr) return 'Не указано';
      try {
        return new Date(dateStr).toLocaleDateString();
      } catch (e) {
        return dateStr;
      }
    };

    // Загрузка данных при монтировании компонента
    onMounted(() => {
      fetchRecruitment();
      fetchMedExams();
    });

    return {
      recruit,
      recruitmentOffice,
      troop,
      loading,
      error,
      showEditModal,
      updating,
      updateError,
      updateSuccess,
      recruitmentOffices,
      troops,
      editForm,
      openEditModal,
      closeEditModal,
      closeModalOnOverlay,
      submitUpdate,
      getPhotoUrl,
      onPhotoSelectedAndUpload,
      goBack,
      formatDate,
      fetchRecruitment,
      handleMaritalStatusChange,
      medExams,
      loadingMedExams,
      medExamsError,
      getResultClass,

      showAddMedExamModal,
      addingMedExam,
      addMedExamError,
      addMedExamSuccess,
      medExamForm,
      examResults,
      openAddMedExamModal,
      closeAddMedExamModal,
      submitAddMedExam,
    };
  }
};
</script>


<style scoped>
/* Основной контейнер */
.recruitment-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  color: #333;
}

/* Состояния */
.loading,
.error,
.success {
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 6px;
  text-align: center;
}

.loading {
  color: #666;
  font-style: italic;
}

.error {
  background-color: #ffebee;
  color: #b71c1c;
}

.success {
  background-color: #e8f5e9;
  color: #1b5e20;
}

/* Основной блок данных */
.recruit-container {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.recruit-photo {
  flex: 0 0 165px;
}

.recruit-photo img {
  width: 165px;
  height: 220px;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Стиль для кнопки загрузки фото */
.upload-photo-button {
  display: block;
  width: 100%;
  margin-top: 10px;
  padding: 8px;
  background-color: #1976d2;
  color: white;
  text-align: center;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

/* Детали */
.recruit-details {
  flex: 1;
}

.recruit-details p {
  margin: 8px 0;
  line-height: 1.6;
  font-size: 15px;
}

/* Кнопки действий */
.actions-container {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.actions-container button {
  padding: 10px 18px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
}

.back-button {
  background-color: #e0e0e0;
}

.edit-button {
  background-color: #1976d2;
  color: white;
}

/* Кнопка повторить */
.retry-button {
  background-color: #e0e0e0;
  margin-top: 10px;
}

/* Модалка */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  overflow-y: auto;
  max-height: 90vh;
}

/* Модальный заголовок */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-button {
  background: none;
  border: none;
  font-size: 22px;
  color: #757575;
  cursor: pointer;
}

/* Форма */
.edit-form .form-group {
  margin-bottom: 15px;
}

.edit-form label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.edit-form input,
.edit-form select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

/* Форма чекбокс */
.form-group.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
}

.help-text {
  font-size: 0.9rem;
  color: #777;
  margin-top: 5px;
}

/* Кнопки формы */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.form-actions button {
  padding: 10px 18px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
}

.form-actions button[type="submit"] {
  background-color: #1976d2;
  color: white;
}

.form-actions button[type="button"] {
  background-color: #e0e0e0;
}

.form-actions button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.medexams-section {
  margin-top: 30px;
  border-top: 1px solid #e0e0e0;
  padding-top: 20px;
}

.medexams-section h3 {
  margin-bottom: 15px;
  font-size: 18px;
}

.medexams-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.medexams-table th,
.medexams-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.medexams-table th {
  background-color: #f5f5f5;
  font-weight: 500;
}


add-medexam-btn-container {
  margin-top: 15px;
  text-align: right;
}



.medexam-form .form-group {
  margin-bottom: 15px;
}

.medexam-form input[disabled] {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.help-text {
  font-size: 0.8rem;
  color: #757575;
  margin-top: 4px;
  display: block;
}

/* Стили для кнопки добавления */
.medexams-actions {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}

.add-button {
  background-color: #43a047;
  color: white;
  padding: 10px 18px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
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
</style>
