import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

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

// 응답 인터셉터 추가 (에러 처리용)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API 에러:', error.response?.data);
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (data: { username: string; password: string }) => {
    const formData = new FormData();
    formData.append('username', data.username);
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
  // AI 커리큘럼 생성
  create: (data: { 
    goal: string; 
    duration: number;
    difficulty?: 'beginner' | 'intermediate' | 'expert';
    details?: string;
  }) => api.post('/curriculums/generate', {
    goal: data.goal,
    period: data.duration,
    difficulty: data.difficulty || 'beginner',
    details: data.details || ''
  }),
  
  // 내 커리큘럼 목록 조회
  getAll: (params?: { page?: number; items_per_page?: number }) => 
    api.get('/curriculums/me', { params }),
  
  // 공개 커리큘럼 목록 조회
  getPublic: (params?: { page?: number; items_per_page?: number }) => 
    api.get('/curriculums/public', { params }),
  
  // 팔로우한 사용자들의 커리큘럼 조회
  getFollowing: (params?: { page?: number; items_per_page?: number }) => 
    api.get('/curriculums/following', { params }),
  
  // 특정 커리큘럼 조회
  getById: (id: string) => api.get(`/curriculums/${id}`),
  
  // 커리큘럼 수정
  update: (id: string, data: { title?: string; visibility?: 'PUBLIC' | 'PRIVATE' }) =>
    api.patch(`/curriculums/${id}`, data),
  
  // 커리큘럼 삭제
  delete: (id: string) => api.delete(`/curriculums/${id}`),
  
  // 주차 추가
  addWeek: (curriculumId: string, data: { week_number: number; lessons: string[] }) =>
    api.post(`/curriculums/${curriculumId}/weeks`, data),
  
  // 주차 삭제
  deleteWeek: (curriculumId: string, weekNumber: number) =>
    api.delete(`/curriculums/${curriculumId}/weeks/${weekNumber}`),
  
  // 레슨 추가
  addLesson: (curriculumId: string, weekNumber: number, data: { lesson: string; lesson_index?: number }) =>
    api.post(`/curriculums/${curriculumId}/weeks/${weekNumber}/lessons`, data),
  
  // 레슨 수정
  updateLesson: (curriculumId: string, weekNumber: number, lessonIndex: number, data: { lesson: string }) =>
    api.put(`/curriculums/${curriculumId}/weeks/${weekNumber}/lessons/${lessonIndex}`, data),
  
  // 레슨 삭제
  deleteLesson: (curriculumId: string, weekNumber: number, lessonIndex: number) =>
    api.delete(`/curriculums/${curriculumId}/weeks/${weekNumber}/lessons/${lessonIndex}`),
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
