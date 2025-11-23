import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding the auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401 Unauthorized
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // Handle other errors
    // const errorMessage = error.response?.data?.message || error.response?.data?.error || 'An unexpected error occurred';
    
    // Don't show toast for 401 as we redirect
    if (error.response?.status !== 401) {
        // Optional: You might want to suppress toasts for specific endpoints or handle them in the component
        // For now, we'll let the component handle the UI feedback or add a global toast here if desired.
        // toast.error(errorMessage); 
    }

    return Promise.reject(error);
  }
);


export default api;
