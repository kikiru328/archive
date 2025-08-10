import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1'; // v1_router 경로

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// JWT 토큰 인터셉터
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// v1 API 엔드포인트
export const authAPI = {
  login: (data: { username: string; password: string }) => {
    // FastAPI OAuth2PasswordRequestForm 형식으로 변환
    const formData = new FormData();
    formData.append('username', data.username); // email을 username으로 전송
    formData.append('password', data.password);
    
    return api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  register: (data: { username: string; email: string; password: string }) =>
    api.post('/auth/signup', {
      name: data.username,
      email: data.email, 
      password: data.password
    }),
  getProfile: () => api.get('/users/me'),
};

export const curriculumAPI = {
  create: (data: { goal: string; duration: number }) =>
    api.post('/curriculums', data),
  getAll: () => api.get('/curriculums'),
  getById: (id: string) => api.get(`/curriculums/${id}`),
};

export const summaryAPI = {
  submit: (data: { week: number; content: string; curriculum_id: string }) =>
    api.post('/summaries', data),
  getByWeek: (curriculumId: string, week: number) =>
    api.get(`/summaries/${curriculumId}/${week}`),
};

export const feedbackAPI = {
  getByWeek: (curriculumId: string, week: number) =>
    api.get(`/feedback/${curriculumId}/${week}`),
};

export default api;
