import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  withCredentials: true, // Required — sends/receives httpOnly auth cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// No request interceptor needed — cookies are sent automatically by the browser.

// Response interceptor: on 401, clear local auth state and redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      sessionStorage.removeItem('isAuthenticated');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
