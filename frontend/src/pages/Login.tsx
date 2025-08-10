// src/pages/Login.tsx
import {
  Box,
  Button,
  Input,
  VStack,
  Heading,
  Container,
  Text,
  Link,
  Alert,
  AlertIcon,
  AlertDescription,
  useColorModeValue,
} from '@chakra-ui/react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  // 다크모드 대응 색상
  const bgColor = useColorModeValue('white', 'gray.700');
  const textColor = useColorModeValue('gray.900', 'white');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const translateErrorMessage = (errorMessage: string): string => {
    // 완전한 메시지 매칭
    const fullMessageTranslations: { [key: string]: string } = {
      'value is not a valid email address: The part after the @-sign is not valid. It should have a period.': '올바른 이메일 형식을 입력해주세요 (예: user@example.com)',
      'String should have at least 8 characters': '최소 8자 이상 입력해주세요',
      'String should have at most 64 characters': '최대 64자까지 입력할 수 있습니다',
      'field required': '필수 입력 항목입니다',
      'Input should be a valid email': '올바른 이메일 형식을 입력해주세요',
    };

    // 부분 단어 번역
    const partialTranslations: { [key: string]: string } = {
      'Email Not found': '등록되지 않은 이메일입니다',
      'Password incorrect': '비밀번호가 올바르지 않습니다', 
      'Invalid email format': '이메일 형식이 올바르지 않습니다',
      'Email cannot be empty': '이메일을 입력해주세요',
      'Password must be': '비밀번호를 확인해주세요',
      'Request failed with status code': '서버 오류가 발생했습니다',
      'Network Error': '네트워크 연결을 확인해주세요',
      'value is not a valid email address': '올바른 이메일 형식을 입력해주세요',
      'The part after the @-sign is not valid': '',
      'It should have a period': '',
      'characters': '자',
      'at least': '최소',
      'at most': '최대',
      'should have': '',
      'String': '',
    };

    let translatedMessage = errorMessage;

    // 1. 완전한 메시지 먼저 확인
    for (const [english, korean] of Object.entries(fullMessageTranslations)) {
      if (translatedMessage.includes(english)) {
        return korean;
      }
    }

    // 2. 부분 번역 적용
    Object.entries(partialTranslations).forEach(([english, korean]) => {
      translatedMessage = translatedMessage.replace(new RegExp(english, 'gi'), korean);
    });

    // 3. 상태 코드별 처리
    if (translatedMessage.includes('400') || translatedMessage.includes('Bad Request')) {
      return '이메일 또는 비밀번호를 확인해주세요';
    }
    
    if (translatedMessage.includes('401') || translatedMessage.includes('Unauthorized')) {
      return '이메일 또는 비밀번호가 올바르지 않습니다';
    }

    if (translatedMessage.includes('500') || translatedMessage.includes('Internal Server Error')) {
      return '서버에 문제가 발생했습니다. 잠시 후 다시 시도해주세요';
    }

    // 4. 정리 작업
    translatedMessage = translatedMessage
      .replace(/,\s*,/g, ', ')  // 연속된 쉼표 제거
      .replace(/\s+/g, ' ')     // 연속된 공백 제거
      .replace(/^\s*,\s*/, '')  // 시작 쉼표 제거
      .replace(/\s*,\s*$/, '')  // 끝 쉼표 제거
      .trim();

    return translatedMessage || '입력값을 확인해주세요';
  };

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      console.log('로그인 시도:', { username, password });
      const response = await authAPI.login({ username, password });
      console.log('로그인 응답:', response.data);
      localStorage.setItem('token', response.data.access_token);
      setSuccess('로그인 성공! 대시보드로 이동합니다.');
      
      setTimeout(() => {
        navigate('/dashboard');
      }, 1000);
    } catch (error: any) {
      console.error('로그인 에러 전체:', error);
      console.error('에러 응답:', error.response?.data);
      console.error('에러 상태:', error.response?.status);
      
      let errorMessage = '로그인에 실패했습니다.';
      
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail
            .map((err: any) => {
              const msg = err.msg || JSON.stringify(err);
              return translateErrorMessage(msg);
            })
            .join(', ');
        } else {
          errorMessage = translateErrorMessage(error.response.data.detail);
        }
      } else if (error.response?.data?.message) {
        errorMessage = translateErrorMessage(error.response.data.message);
      } else if (error.message) {
        errorMessage = translateErrorMessage(error.message);
      }
      
      setError(errorMessage);
    }
    setLoading(false);
  };

  return (
    <Container maxW="md" centerContent>
      <Box mt={20} p={8} borderWidth={1} borderRadius="lg" w="100%" bg={bgColor} borderColor={borderColor}>
        <VStack gap={4}>
          <Heading color={textColor}>LLearn 로그인</Heading>
          
          {/* 에러 메시지 */}
          {error && (
            <Alert status="error" borderRadius="md">
              <AlertIcon />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* 성공 메시지 */}
          {success && (
            <Alert status="success" borderRadius="md">
              <AlertIcon />
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}
          
          <Box w="100%">
            <Text mb={2} color={textColor}>이메일</Text>
            <Input
              type="email"
              placeholder="example@email.com"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              isInvalid={!!error}
              color={textColor}
              borderColor={borderColor}
            />
          </Box>
          
          <Box w="100%">
            <Text mb={2} color={textColor}>비밀번호</Text>
            <Input
              type="password"
              placeholder="8자 이상, 대소문자/숫자/특수문자 포함"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              isInvalid={!!error}
              color={textColor}
              borderColor={borderColor}
            />
          </Box>
          
          <Button
            colorScheme="blue"
            width="100%"
            isLoading={loading}
            onClick={handleLogin}
            isDisabled={!username || !password}
          >
            로그인
          </Button>

          <Text fontSize="sm" color={textColor}>
            계정이 없으신가요?{' '}
            <Link color="blue.500" onClick={() => navigate('/signup')}>
              회원가입하기
            </Link>
          </Text>
        </VStack>
      </Box>
    </Container>
  );
};

export default Login;
