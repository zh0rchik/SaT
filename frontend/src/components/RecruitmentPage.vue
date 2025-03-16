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

        <div class="form-group checkbox">
          <input id="marital_status" v-model="editForm.marital_status" type="checkbox" />
          <label for="marital_status">Женат</label>
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

    // Переменные для загрузки фото (упрощенный вариант)
    const selectedPhoto = ref(null);

    // Форма редактирования
    const editForm = reactive({
      name: '',
      address: '',
      date_of_birth: '',
      marital_status: false,
      recruitment_office_id: null,
      troop_id: null
    });

    const fetchRecruitment = async () => {
      loading.value = true;
      error.value = null;

      try {
        const response = await axios.get(`http://127.0.0.1:8000/recruitments/${props.recruitId}`, {
          timeout: 5000
        });
        recruit.value = response.data;

        // Загружаем данные о призывном пункте и роде войск, если у призывника есть эти ID
        if (recruit.value.recruitment_office_id) {
          fetchRecruitmentOffice(recruit.value.recruitment_office_id);
        }

        if (recruit.value.troop_id) {
          fetchTroop(recruit.value.troop_id);
        }
      } catch (err) {
        console.error('Ошибка при загрузке данных призывника:', err);
        if (err.code === 'ECONNABORTED') {
          error.value = 'Превышено время ожидания ответа от сервера';
        } else if (err.response) {
          error.value = `Ошибка сервера: ${err.response.status} - ${err.response.data?.detail || 'Неизвестная ошибка'}`;
        } else if (err.request) {
          error.value = 'Не удалось соединиться с сервером. Проверьте, что сервер запущен и доступен.';
        } else {
          error.value = `Ошибка: ${err.message}`;
        }
      } finally {
        loading.value = false;
      }
    };

    const fetchRecruitmentOffice = async (id) => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/recruitment_offices/${id}`, {
          timeout: 3000
        });
        recruitmentOffice.value = response.data;
      } catch (err) {
        console.error('Ошибка при загрузке данных о призывном пункте:', err);
        recruitmentOffice.value = { address: 'Ошибка загрузки', chief_name: 'Недоступно' };
      }
    };

    const fetchTroop = async (id) => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/troops/${id}`, {
          timeout: 3000
        });
        troop.value = response.data;
      } catch (err) {
        console.error('Ошибка при загрузке данных о роде войск:', err);
        troop.value = { name: 'Не определён' };
      }
    };

    const fetchAllRecruitmentOffices = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/recruitment_offices/', {
          timeout: 5000
        });
        recruitmentOffices.value = response.data;
      } catch (err) {
        console.error('Ошибка при загрузке списка призывных пунктов:', err);
        updateError.value = 'Не удалось загрузить список призывных пунктов';
      }
    };

    const fetchAllTroops = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/troops/', {
          timeout: 5000
        });
        troops.value = response.data;
      } catch (err) {
        console.error('Ошибка при загрузке списка родов войск:', err);
        updateError.value = 'Не удалось загрузить список родов войск';
      }
    };

    const formatDate = (dateString) => {
      if (!dateString) return 'Не указано';
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU');
    };

    const getPhotoUrl = (photoPath) => {
      if (!photoPath) return 'http://127.0.0.1:8000/static/uploads/avatar.jpg';
      // Если фото сохранено с относительным путем, подставляем домен
      return `http://127.0.0.1:8000${photoPath}`;
    };

    const goBack = () => {
      emit('back');
    };

    const openEditModal = async () => {
      // Сбрасываем ошибки и сообщения об успехе
      updateError.value = null;
      updateSuccess.value = null;

      // Загружаем данные для выпадающих списков
      await Promise.all([
        fetchAllRecruitmentOffices(),
        fetchAllTroops()
      ]);

      // Заполняем форму текущими данными
      editForm.name = recruit.value.name || '';
      editForm.address = recruit.value.address || '';
      editForm.date_of_birth = recruit.value.date_of_birth || '';
      editForm.marital_status = recruit.value.marital_status || false;
      editForm.recruitment_office_id = recruit.value.recruitment_office_id || null;
      editForm.troop_id = recruit.value.troop_id || null;

      // Открываем модальное окно
      showEditModal.value = true;
    };

    const closeEditModal = () => {
      showEditModal.value = false;
    };

    const closeModalOnOverlay = (event) => {
      if (event.target.classList.contains('modal-overlay')) {
        if (showEditModal.value) closeEditModal();
      }
    };

    const getToken = () => {
      if (props.user && props.user.token) {
        return props.user.token;
      }
      return null;
    };

    const submitUpdate = async () => {
      updateError.value = null;
      updateSuccess.value = null;
      updating.value = true;

      const token = getToken();
      if (!token) {
        updateError.value = 'Необходима авторизация для внесения изменений';
        updating.value = false;
        return;
      }

      try {
        // Формируем данные для отправки как URL-параметры
        const params = new URLSearchParams();
        if (editForm.name !== recruit.value.name) params.append('name', editForm.name);
        if (editForm.address !== recruit.value.address) params.append('address', editForm.address);
        if (editForm.date_of_birth !== recruit.value.date_of_birth) params.append('date_of_birth', editForm.date_of_birth);
        if (editForm.marital_status !== recruit.value.marital_status) params.append('marital_status', editForm.marital_status);
        if (editForm.recruitment_office_id !== recruit.value.recruitment_office_id) params.append('recruitment_office_id', editForm.recruitment_office_id);
        if (editForm.troop_id !== recruit.value.troop_id) params.append('troop_id', editForm.troop_id);

        // Отправляем запрос на обновление с параметрами в URL
        const response = await axios.patch(
            `http://127.0.0.1:8000/recruitments/${props.recruitId}?${params.toString()}`,
            {}, // Пустой объект, так как данные уже в URL
            {
              timeout: 5000,
              headers: {
                'Authorization': `Bearer ${token}`
              }
            }
        );

        // Обновляем данные в компоненте
        recruit.value = response.data;

        // Обновляем связанные данные при необходимости
        if (response.data.recruitment_office_id !== recruitmentOffice.value?.id) {
          fetchRecruitmentOffice(response.data.recruitment_office_id);
        }

        if (response.data.troop_id !== troop.value?.id) {
          fetchTroop(response.data.troop_id);
        }

        updateSuccess.value = 'Данные успешно обновлены';

        // Закрываем модальное окно через 1.5 секунды
        setTimeout(() => {
          closeEditModal();
        }, 1500);

      } catch (err) {
        console.error('Ошибка при обновлении данных:', err);

        if (err.response && err.response.status === 400) {
          updateError.value = 'Призывнику необходимо пройти мед. комиссию';
        } else if (err.response && err.response.status === 401) {
          updateError.value = 'Ошибка авторизации. Возможно, срок действия токена истек';
        } else if (err.response && err.response.status === 422) {
          updateError.value = 'Ошибка валидации данных. Проверьте правильность заполнения формы';
        } else if (err.code === 'ECONNABORTED') {
          updateError.value = 'Превышено время ожидания ответа от сервера';
        } else if (err.request) {
          updateError.value = 'Не удалось соединиться с сервером. Проверьте подключение к интернету';
        } else {
          updateError.value = `Произошла ошибка: ${err.message || 'Неизвестная ошибка'}`;
        }
      } finally {
        updating.value = false;
      }
    };

    // Функция для автоматической загрузки фото
    const onPhotoSelectedAndUpload = async (event) => {
      const file = event.target.files[0];
      if (!file) return;

      selectedPhoto.value = file;

      const token = getToken();
      if (!token) {
        return;
      }

      try {
        // Создаем FormData для отправки файла
        const formData = new FormData();
        formData.append('photo', file);

        // Отправляем запрос на загрузку фото
        const response = await axios.post(
            `http://127.0.0.1:8000/recruitments/upload_avatar/${props.recruitId}`,
            formData,
            {
              timeout: 10000,
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'multipart/form-data'
              }
            }
        );

        // Обновляем данные в компоненте
        recruit.value.photo = response.data.photo_url;

      } catch (err) {
        console.error('Ошибка при загрузке фото:', err);

      } finally {
        event.target.value = '';
      }
    };

    onMounted(() => {
      fetchRecruitment();
    });

    return {
      recruit,
      recruitmentOffice,
      troop,
      loading,
      error,
      formatDate,
      getPhotoUrl,
      goBack,
      showEditModal,
      openEditModal,
      closeEditModal,
      closeModalOnOverlay,
      editForm,
      updating,
      updateError,
      updateSuccess,
      submitUpdate,
      recruitmentOffices,
      troops,
      // Переменные для загрузки фото
      selectedPhoto,
      onPhotoSelectedAndUpload,
      fetchRecruitment
    };
  }
}
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
