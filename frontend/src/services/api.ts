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
export const userAPI = {
  // 현재 사용자 프로필 조회
  getProfile: () => api.get('/users/me'),
  
  // 프로필 수정
  updateProfile: (data: { name?: string; password?: string }) =>
    api.put('/users/me', data),
  
  // 계정 삭제
  deleteAccount: () => api.delete('/users/me'),
  
  // 사용자 검색 (소셜 기능용)
  searchUsers: (params: { q: string; page?: number; items_per_page?: number }) =>
    api.get('/users', { params }),
  
  // 특정 사용자 프로필 조회 (공개 정보만)
  getUserProfile: (userId: string) => api.get(`/users/${userId}/profile`),
};

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

export const tagAPI = {
  // 태그 관련
  getPopularTags: (params?: { limit?: number; min_usage?: number }) =>
    api.get('/tags/popular', { params }),
  
  searchTags: (params: { q: string; limit?: number }) =>
    api.get('/tags/search', { params }),
  
  getAll: (params?: { page?: number; items_per_page?: number; search?: string; min_usage?: number }) =>
    api.get('/tags', { params }),
  
  create: (data: { name: string }) =>
    api.post('/tags', data),
  
  update: (id: string, data: { name?: string }) =>
    api.patch(`/tags/${id}`, data),
  
  delete: (id: string) =>
    api.delete(`/tags/${id}`),
  
  getStatistics: () =>
    api.get('/tags/statistics'),
};

export const categoryAPI = {
  // 카테고리 관련
  getActive: () =>
    api.get('/categories/active'),
  
  getAll: (params?: { page?: number; items_per_page?: number; include_inactive?: boolean }) =>
    api.get('/categories', { params }),
  
  getById: (id: string) =>
    api.get(`/categories/${id}`),
  
  create: (data: { name: string; description?: string; color: string; icon?: string; sort_order?: number }) =>
    api.post('/categories', data),
  
  update: (id: string, data: { name?: string; description?: string; color?: string; icon?: string; sort_order?: number; is_active?: boolean }) =>
    api.patch(`/categories/${id}`, data),
  
  delete: (id: string) =>
    api.delete(`/categories/${id}`),
  
  activate: (id: string) =>
    api.post(`/categories/${id}/activate`),
  
  deactivate: (id: string) =>
    api.post(`/categories/${id}/deactivate`),
  
  reorder: (categories: Array<{ id: string; sort_order: number }>) =>
    api.post('/categories/reorder', { categories }),
  
  getStatistics: () =>
    api.get('/categories/statistics'),
};

export const curriculumTagAPI = {
  // 커리큘럼-태그 관련
  addTags: (curriculumId: string, tagNames: string[]) =>
    api.post(`/curriculums/${curriculumId}/tags`, { tag_names: tagNames }),
  
  removeTag: (curriculumId: string, tagName: string) =>
    api.delete(`/curriculums/${curriculumId}/tags`, { data: { tag_name: tagName } }),
  
  assignCategory: (curriculumId: string, categoryId: string) =>
    api.post(`/curriculums/${curriculumId}/category`, { category_id: categoryId }),
  
  removeCategory: (curriculumId: string) =>
    api.delete(`/curriculums/${curriculumId}/category`),
  
  getTagsAndCategory: (curriculumId: string) =>
    api.get(`/curriculums/${curriculumId}/tags-and-category`),
  
  // 검색
  findByTags: (tagNames: string[], params?: { page?: number; items_per_page?: number }) =>
    api.get('/curriculums/search/by-tags', { params: { tag_names: tagNames, ...params } }),
  
  findByCategory: (categoryId: string, params?: { page?: number; items_per_page?: number }) =>
    api.get(`/curriculums/search/by-category/${categoryId}`, { params }),
  
  // 사용자 활동
  getMyTaggedCurriculums: (params?: { page?: number; items_per_page?: number }) =>
    api.get('/curriculums/tags/my-tagged-curriculums', { params }),
  
  getMyCategorizedCurriculums: (params?: { page?: number; items_per_page?: number }) =>
    api.get('/curriculums/categories/my-categorized-curriculums', { params }),
};
export const likeAPI = {
  // 좋아요 생성/삭제
  createLike: (curriculumId: string) =>
    api.post(`/curriculums/${curriculumId}/like`, {}),
  
  deleteLike: (curriculumId: string) =>
    api.delete(`/curriculums/${curriculumId}/like`),
  
  // 좋아요 상태 조회
  getLikeStatus: (curriculumId: string) =>
    api.get(`/curriculums/${curriculumId}/like/status`),
  
  // 커리큘럼의 좋아요 목록
  getLikesByCurriculum: (curriculumId: string, params?: { page?: number; items_per_page?: number }) =>
    api.get(`/curriculums/${curriculumId}/likes`, { params }),
  
  // 내가 한 좋아요 목록
  getMyLikes: (params?: { page?: number; items_per_page?: number }) =>
    api.get('/users/me/likes', { params }),
};

// Comment API
export const commentAPI = {
  // 댓글 생성
  createComment: (curriculumId: string, data: { content: string }) =>
    api.post(`/curriculums/${curriculumId}/comments`, data),
  
  // 댓글 수정
  updateComment: (commentId: string, data: { content: string }) =>
    api.put(`/curriculums/comments/${commentId}`, data),
  
  // 댓글 삭제
  deleteComment: (commentId: string) =>
    api.delete(`/curriculums/comments/${commentId}`),
  
  // 커리큘럼의 댓글 목록
  getCommentsByCurriculum: (curriculumId: string, params?: { page?: number; items_per_page?: number }) =>
    api.get(`/curriculums/${curriculumId}/comments`, { params }),
  
  // 내가 작성한 댓글 목록
  getMyComments: (params?: { page?: number; items_per_page?: number }) =>
    api.get('/users/me/comments', { params }),
};

// Bookmark API
export const bookmarkAPI = {
  // 북마크 생성/삭제
  createBookmark: (curriculumId: string) =>
    api.post(`/curriculums/${curriculumId}/bookmark`, {}),
  
  deleteBookmark: (curriculumId: string) =>
    api.delete(`/curriculums/${curriculumId}/bookmark`),
  
  // 북마크 상태 조회
  getBookmarkStatus: (curriculumId: string) =>
    api.get(`/curriculums/${curriculumId}/bookmark/status`),
  
  // 내 북마크 목록
  getMyBookmarks: (params?: { page?: number; items_per_page?: number }) =>
    api.get('/users/me/bookmarks', { params }),
};

// Follow API
export const followAPI = {
  // 팔로우/언팔로우
  followUser: (followeeId: string) =>
    api.post('/social/follow', { followee_id: followeeId }),
  
  unfollowUser: (followeeId: string) =>
    api.delete('/social/unfollow', { data: { followee_id: followeeId } }),
  
  // 팔로우 상태 확인
  getFollowStatus: (userId: string) =>
    api.get(`/social/users/${userId}/status`),
  
  // 팔로워/팔로잉 목록
  getFollowers: (userId: string, params?: { page?: number; items_per_page?: number }) =>
    api.get(`/social/users/${userId}/followers`, { params }),
  
  getFollowing: (userId: string, params?: { page?: number; items_per_page?: number }) =>
    api.get(`/social/users/${userId}/following`, { params }),
  
  // 내 팔로워/팔로잉
  getMyFollowers: (params?: { page?: number; items_per_page?: number }) =>
    api.get('/social/me/followers', { params }),
  
  getMyFollowing: (params?: { page?: number; items_per_page?: number }) =>
    api.get('/social/me/following', { params }),
  
  // 팔로우 통계
  getFollowStats: (userId: string) =>
    api.get(`/social/users/${userId}/stats`),
  
  // 팔로우 추천
  getFollowSuggestions: (params?: { limit?: number }) =>
    api.get('/social/suggestions', { params }),
};

// Feed API
export const feedAPI = {
  // 공개 피드 조회
  getPublicFeed: (params?: { 
    page?: number; 
    items_per_page?: number; 
    category_id?: string; 
    tags?: string; 
    search?: string; 
  }) => api.get('/feed/public', { params }),
  
  // 피드 새로고침
  refreshFeed: () =>
    api.post('/feed/refresh'),
  
  refreshCurriculumFeed: (curriculumId: string) =>
    api.post(`/feed/refresh/${curriculumId}`),
};

// Social Stats API
export const socialStatsAPI = {
  // 커리큘럼 소셜 통계
  getCurriculumSocialStats: (curriculumId: string) =>
    api.get(`/curriculums/${curriculumId}/social-stats`),
};

