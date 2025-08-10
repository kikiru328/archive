import { jwtDecode } from 'jwt-decode';

interface JWTPayload {
  sub: string; // user_id
  exp: number;
  iat: number;
}

export const getCurrentUserId = (): string | null => {
  try {
    const token = localStorage.getItem('token');
    if (!token) return null;
    
    const decoded = jwtDecode<JWTPayload>(token);
    return decoded.sub;
  } catch (error) {
    console.error('토큰 디코딩 실패:', error);
    return null;
  }
};

export const isTokenValid = (): boolean => {
  try {
    const token = localStorage.getItem('token');
    if (!token) return false;
    
    const decoded = jwtDecode<JWTPayload>(token);
    return decoded.exp > Date.now() / 1000;
  } catch (error) {
    return false;
  }
};
