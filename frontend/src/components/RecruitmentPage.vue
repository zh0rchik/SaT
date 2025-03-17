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

        <select id="marital_status" :value="editForm.marital_status" @change="handleMaritalStatusChange">
          <option value="false">Холост</option>
          <option value="true">Женат</option>
        </select>

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

    // Форма редактирования
    const editForm = reactive({
      name: '',
      address: '',
      date_of_birth: '',
      marital_status: false, // Изначально холост
      recruitment_office_id: null,
      troop_id: null
    });


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
      editForm.marital_status = event.target.value === 'true'; // точно преобразуем в boolean
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
      if (!props.user || !props.user.token) {
        updateError.value = 'Необходима авторизация для внесения изменений.';
        return;
      }

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
      handleMaritalStatusChange
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
</style>
