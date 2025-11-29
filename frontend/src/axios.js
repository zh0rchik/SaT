import axios from 'axios';

const instance = axios.create({
  baseURL:
    window.location.hostname === 'localhost'
      ? 'http://localhost:8000'  // локальная разработка
      : 'https://sat-sv5g.onrender.com',  // прод
});

export default instance;
