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
      <p><strong>ID призывника:</strong> {{ recruitId }}</p>
      <!-- Здесь будет отображаться остальная информация о призывнике -->
    </div>

    <button @click="goBack" class="back-button">Назад к списку</button>
  </div>
</template>

<script>
import axios from 'axios';
import { ref, onMounted } from 'vue';

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
    const loading = ref(true);
    const error = ref(null);

    const fetchRecruitment = async () => {
      loading.value = true;
      error.value = null;

      try {
        const response = await axios.get(`http://127.0.0.1:8000/recruitments/${props.recruitId}`, {
          timeout: 5000
        });

        recruit.value = response.data;
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

    const goBack = () => {
      emit('back');
    };

    onMounted(() => {
      fetchRecruitment();
    });

    return {
      recruit,
      loading,
      error,
      fetchRecruitment,
      goBack
    };
  }
};
</script>

<style scoped>
.recruitment-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
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

.recruit-info {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background-color: #f9f9f9;
}

.back-button {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 20px;
}

.back-button:hover {
  background-color: #0056b3;
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
</style>