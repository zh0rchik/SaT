<template>
  <div class="profile-container">
    <h2>Профиль пользователя</h2>
    <!-- Если данные пользователя получены, отображаем их -->
    <div v-if="userInfo" class="profile-info">
      <p><strong>Фамилия: </strong>{{ userInfo.last_name }}</p>
      <p><strong>Имя: </strong> {{ userInfo.first_name }}</p>
      <p><strong>Отчество: </strong>{{ userInfo.father_name }}</p>
      <p><strong>Логин: </strong>{{ userInfo.username }}</p>
      <p><strong>Email: </strong>{{ userInfo.email }}</p>
      <p><strong>Размер страницы: </strong>{{ userInfo.page_size }}</p>
    </div>
    <!-- Если данные еще не получены, отображаем сообщение о загрузке -->
    <div v-else>
      <p>Загрузка...</p>
    </div>
    <div class="actions-container">
      <!-- Кнопка "Назад" -->
      <button @click="goBack" class="back-button">К таблицам</button>
      <!-- Кнопка для выхода из системы -->
      <div class="actions-container">
        <button v-if="user" @click="openEditModal" class="edit-button">
          Редактировать профиль
        </button>
      </div>
    </div>
  </div>

  <!-- Модальное окно для редактирования профиля -->
  <div v-if="showEditModal" class="edit-modal">
    <div class="edit-modal-content">
      <h3>Редактировать профиль</h3>
      <form @submit.prevent="updateUserProfile">
        <label for="first_name">Имя<span class="required">*</span>:</label>
        <input v-model="editUserInfo.first_name" type="text" id="first_name" required />

        <label for="last_name">Фамилия<span class="required">*</span>:</label>
        <input v-model="editUserInfo.last_name" type="text" id="last_name" required />

        <label for="father_name">Отчество<span class="required">*</span>:</label>
        <input v-model="editUserInfo.father_name" type="text" id="father_name" required />

        <label for="email">Email<span class="required">*</span>:</label>
        <input v-model="editUserInfo.email" type="email" id="email" required />

        <label for="password">Пароль:</label>
        <input v-model="editUserInfo.password" type="password" id="password" />

        <label for="confirm_password">Подтверждение пароля:</label>
        <input v-model="confirmPassword" type="password" id="confirm_password" />

        <label for="page_size">Размер страницы<span class="required">*</span>:</label>
        <input v-model="editUserInfo.page_size" type="text" id="page_size" required />

        <div class="form-buttons">
          <button type="submit" class="save-button">Сохранить изменения</button>
          <button type="button" @click="cancelEdit" class="cancel-button">Отмена</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'UserProfile',
  props: ['user'],
  data() {
    return {
      userInfo: null,  // Сюда будет загружена информация о пользователе
      showEditModal: false,  // Флаг для отображения модального окна редактирования
      editUserInfo: {
        first_name: '',
        last_name: '',
        father_name: '',
        email: '',
        password: '',
        username: '',
        page_size: 1,
      },
      confirmPassword: '',  // Поле для подтверждения пароля
    };
  },
  methods: {
    // Метод для загрузки информации о пользователе
    async fetchUserProfile() {
      try {
        const token = this.user.token;  // Получаем токен из props
        const response = await axios.get('http://127.0.0.1:8000/auth/profile', {
          headers: { Authorization: `Bearer ${token}` },  // Отправляем токен в заголовке
        });
        this.userInfo = response.data;  // Сохраняем информацию о пользователе в userInfo
      } catch (error) {
        console.error('Ошибка при загрузке профиля пользователя:', error);
        alert('Ошибка при загрузке профиля');
      }
    },
    // Метод для выхода из системы
    logout() {
      localStorage.removeItem('user');  // Удаляем данные пользователя из localStorage
      this.$emit('logout');  // Отправляем событие на выход
    },
    // Метод для возврата на предыдущую страницу
    goBack() {
      this.$emit('go-home');  // Возвращаем пользователя на предыдущую страницу
    },
    // Метод для открытия модального окна редактирования
    openEditModal() {
      this.editUserInfo = { ...this.userInfo };  // Копируем информацию для редактирования
      this.editUserInfo.password = '';  // Очищаем поле пароля
      this.confirmPassword = '';  // Очищаем поле подтверждения пароля
      this.showEditModal = true;
    },
    // Метод для отмены редактирования
    cancelEdit() {
      this.showEditModal = false;
    },
    // Метод для обновления данных пользователя
    async updateUserProfile() {
      if (this.editUserInfo.password && this.editUserInfo.password !== this.confirmPassword) {
        alert('Пароли не совпадают');
        return;
      }

      try {
        const token = this.user.token;

        // Создаем объект с параметрами для URL
        const params = {
          username: this.editUserInfo.username,
          first_name: this.editUserInfo.first_name,
          last_name: this.editUserInfo.last_name,
          father_name: this.editUserInfo.father_name,
          email: this.editUserInfo.email,
          page_size: this.editUserInfo.page_size
        };

        // Добавляем пароль только если он был введен
        if (this.editUserInfo.password) {
          params.password = this.editUserInfo.password;
        }

        console.log('Отправляемые параметры:', params);

        // Отправляем запрос с параметрами в URL
        const response = await axios.patch('http://127.0.0.1:8000/auth/profile/update', null, {
          headers: { Authorization: `Bearer ${token}` },
          params: params // Передаем параметры в URL
        });

        localStorage.setItem('page_size', Number(response.data.page_size));

        console.log('Ответ сервера:', response.data);

        this.userInfo = response.data;  // Обновляем информацию о пользователе
        this.showEditModal = false;  // Закрываем модальное окно
        alert('Профиль обновлен');
      } catch (error) {
        console.error('Ошибка при обновлении профиля:', error);

        // Расширенная обработка ошибок
        if (error.response && error.response.data) {
          console.log('Детали ошибки:', error.response.data);

          // Если сервер вернул конкретную ошибку, отображаем ее
          if (typeof error.response.data === 'object' && error.response.data.detail) {
            alert('Ошибка: ' + error.response.data.detail);
          } else {
            alert('Ошибка при обновлении профиля. Пожалуйста, проверьте введенные данные.');
          }
        } else {
          alert('Ошибка при обновлении профиля: ' + error.message);
        }
      }
    }
  },
  mounted() {
    if (this.user) {
      this.fetchUserProfile();  // Загружаем профиль при монтировании компонента
    }
  }
};
</script>

<style scoped>
.profile-container {
  max-width: 400px;
  margin: auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.profile-info {
  margin-bottom: 20px;
  text-align: left;
}

.profile-info p {
  margin: 8px 0;
}

.buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

button {
  padding: 10px 20px;
  border: none;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.back-button {
  background-color: #007bff;
}

.back-button:hover {
  background-color: #0056b3;
}

.logout-button {
  background-color: #dc3545;
}

.logout-button:hover {
  background-color: #c82333;
}

.actions-container {
  max-width: 400px;
  margin: 15px auto;
  text-align: center;
}

.edit-button {
  background-color: #28a745;
  padding: 8px 16px;
}

.edit-button:hover {
  background-color: #218838;
}

.edit-modal {
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

.edit-modal-content {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  width: 350px;
  max-width: 90%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.edit-modal-content h3 {
  margin-top: 0;
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

form label {
  display: block;
  margin: 10px 0 5px;
  font-weight: 500;
  color: #555;
}

form input {
  width: 100%;
  padding: 10px;
  margin-bottom: 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 14px;
}

form input:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.form-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.save-button {
  background-color: #007bff;
  width: 48%;
}

.save-button:hover {
  background-color: #0056b3;
}

.cancel-button {
  background-color: #6c757d;
  width: 48%;
}

.cancel-button:hover {
  background-color: #5a6268;
}
</style>