// src/pages/Signup.tsx
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

const Signup = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
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
      'String should have at least 2 characters': '최소 2자 이상 입력해주세요',
      'String should have at most 32 characters': '최대 32자까지 입력할 수 있습니다',
      'field required': '필수 입력 항목입니다',
      'Input should be a valid email': '올바른 이메일 형식을 입력해주세요',
    };

    // 부분 단어 번역
    const partialTranslations: { [key: string]: string } = {
      'Email Not found': '등록되지 않은 이메일입니다',
      'Password incorrect': '비밀번호가 올바르지 않습니다',
      'Email already exists': '이미 존재하는 이메일입니다',
      'Username already exist': '이미 존재하는 사용자명입니다',
      'ExistEmailError': '이미 존재하는 이메일입니다',
      'ExistNameError': '이미 존재하는 사용자명입니다',
      'Invalid email format': '이메일 형식이 올바르지 않습니다',
      'Email cannot be empty': '이메일을 입력해주세요',
      'Name cannot be empty': '이름을 입력해주세요',
      'Password must be': '비밀번호는 8-64자로 대소문자, 숫자, 특수문자를 포함해야 합니다',
      'Name length must be': '이름은 2-32자로 입력해주세요',
      'Name can only contain': '이름은 한글, 영문, 숫자만 사용할 수 있습니다',
      'characters': '자',
      'at least': '최소',
      'at most': '최대',
      'should have': '',
      'String': '',
      'value is not a valid email address': '올바른 이메일 형식을 입력해주세요',
      'The part after the @-sign is not valid': '',
      'It should have a period': '',
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

    // 3. 특수 패턴 처리
    if (translatedMessage.includes('비밀번호는') && translatedMessage.includes('자')) {
      return '비밀번호는 8-64자로 대소문자, 숫자, 특수문자를 포함해야 합니다';
    }
    
    if (translatedMessage.includes('이름은') && translatedMessage.includes('자')) {
      return '이름은 2-32자로 입력해주세요';
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

  const handleSignup = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      console.log('회원가입 시도:', { name, email, password });
      const response = await authAPI.register({ 
        username: name, 
        email, 
        password 
      });
      console.log('회원가입 성공:', response.data);
      setSuccess('회원가입 성공! 로그인 페이지로 이동합니다.');
      
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error: any) {
      console.error('회원가입 에러 전체:', error);
      console.error('에러 응답:', error.response?.data);
      console.error('에러 상태:', error.response?.status);
      
      let errorMessage = '회원가입에 실패했습니다.';
      
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
          <Heading color={textColor}>LLearn 회원가입</Heading>
          
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
            <Text mb={2} color={textColor}>이름</Text>
            <Input
              placeholder="2-32자 한글/영문/숫자"
              value={name}
              onChange={(e) => setName(e.target.value)}
              isInvalid={!!error && error.includes('name')}
              color={textColor}
              borderColor={borderColor}
            />
          </Box>

          <Box w="100%">
            <Text mb={2} color={textColor}>이메일</Text>
            <Input
              type="email"
              placeholder="example@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              isInvalid={!!error && error.includes('email')}
              color={textColor}
              borderColor={borderColor}
            />
          </Box>

          <Box w="100%">
            <Text mb={2} color={textColor}>비밀번호</Text>
            <Input
              type="password"
              placeholder="8-64자, 대소문자/숫자/특수문자 포함"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              isInvalid={!!error && error.includes('password')}
              color={textColor}
              borderColor={borderColor}
            />
          </Box>

          <Button
            colorScheme="blue"
            width="100%"
            isLoading={loading}
            onClick={handleSignup}
            isDisabled={!name || !email || !password}
          >
            회원가입
          </Button>

          <Text fontSize="sm" color={textColor}>
            이미 계정이 있으신가요?{' '}
            <Link color="blue.500" onClick={() => navigate('/login')}>
              로그인하기
            </Link>
          </Text>
        </VStack>
      </Box>
    </Container>
  );
};

export default Signup;
