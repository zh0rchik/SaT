import axios from 'axios';

const instance = axios.create({
    baseURL: 'http://localhost:8000', // Правильный порт для FastAPI
});

export default instance;
