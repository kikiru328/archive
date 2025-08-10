// src/services/api.ts
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
  console.log('API 요청:', config.method?.toUpperCase(), config.url);
  console.log('토큰 사용:', token ? '있음' : '없음');
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답 인터셉터 추가 (에러 처리용)
api.interceptors.response.use(
  (response) => {
    console.log('API 응답 성공:', response.config.url, response.status);
    return response;
  },
  (error) => {
    console.error('API 에러:', error.response?.data);
    console.error('에러 상태:', error.response?.status);
    console.error('에러 URL:', error.config?.url);
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
  
  // 내 커리큘럼 목록 조회 - 백엔드에서 확인된 정상 작동 엔드포인트
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
  addWeek: (curriculumId: string, data: { week_number: number; title: string; lessons: string[] }) =>
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
  // 요약 생성 - 백엔드 라우팅에 맞게 수정
  create: (data: { 
    curriculum_id: string; 
    week_number: number; 
    content: string;
  }) => api.post(`/curriculums/${data.curriculum_id}/weeks/${data.week_number}/summaries`, {
    content: data.content
  }),
  
  // 내 요약 목록 조회
  getAll: (params?: { page?: number; items_per_page?: number }) => 
    api.get('/users/me/summaries', { params }),
  
  // 특정 요약 조회
  getById: (id: string) => api.get(`/curriculums/summaries/${id}`),
  
  // 커리큘럼별 요약 조회
  getByCurriculum: (curriculumId: string, params?: { page?: number; items_per_page?: number }) =>
    api.get(`/curriculums/${curriculumId}/summaries`, { params }),
  
  // 특정 커리큘럼의 특정 주차 요약 조회
  getByWeek: (curriculumId: string, weekNumber: number, params?: { page?: number; items_per_page?: number }) =>
    api.get(`/curriculums/${curriculumId}/weeks/${weekNumber}/summaries`, { params }),
  
  // 요약 수정
  update: (id: string, data: { content: string }) =>
    api.put(`/curriculums/summaries/${id}`, data),
  
  // 요약 삭제
  delete: (id: string) => api.delete(`/curriculums/summaries/${id}`),
};

export const feedbackAPI = {
  // AI 피드백 생성
  generateFeedback: (summaryId: string) =>
    api.post(`/summaries/${summaryId}/feedbacks/generate`, {}),
  
  // 요약의 피드백 조회
  getBySummary: (summaryId: string) =>
    api.get(`/summaries/${summaryId}/feedbacks`),
  
  // 특정 피드백 조회
  getById: (feedbackId: string) =>
    api.get(`/summaries/feedbacks/${feedbackId}`),
  
  // 피드백 삭제
  delete: (feedbackId: string) =>
    api.delete(`/summaries/feedbacks/${feedbackId}`),
  
  // 커리큘럼별 피드백 조회
  getByCurriculum: (curriculumId: string, params?: { page?: number; items_per_page?: number }) =>
    api.get(`/curriculums/${curriculumId}/feedbacks`, { params }),
  
  // 내 피드백 목록 조회
  getAll: (params?: { 
    page?: number; 
    items_per_page?: number; 
    min_score?: number; 
    max_score?: number; 
  }) => api.get('/users/me/feedbacks', { params }),
};

export const learningStatsAPI = {
  // 내 학습 통계 조회
  getMyStats: (params?: { days?: number }) =>
    api.get('/users/me/learning/stats', { params }),
  
  // 학습 현황 간단 요약 (대시보드용)
  getOverview: () =>
    api.get('/users/me/learning/overview'),
  
  // 커리큘럼별 진도 현황
  getProgress: () =>
    api.get('/users/me/learning/progress'),
  
  // 학습 연속성 정보
  getStreak: () =>
    api.get('/users/me/learning/streak'),
};

export default api;
