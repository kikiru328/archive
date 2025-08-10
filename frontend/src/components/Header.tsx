import {
  Box,
  Flex,
  Heading,
  Spacer,
  Button,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem('token');

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <Box bg="blue.500" color="white" px={4} py={3}>
      <Flex align="center">
        <Heading 
          size="lg" 
          cursor="pointer"
          onClick={() => navigate('/')}
        >
          LLearn
        </Heading>
        
        <Spacer />
        
        {isLoggedIn ? (
          <Flex gap={4} align="center">
            <Button onClick={() => navigate('/dashboard')} variant="ghost">
              대시보드
            </Button>
            <Button onClick={handleLogout} variant="ghost">
              로그아웃
            </Button>
            <Box w="8" h="8" bg="gray.300" borderRadius="full" />
          </Flex>
        ) : (
          <Flex gap={2}>
            <Button onClick={() => navigate('/login')} variant="ghost">
              로그인
            </Button>
            <Button onClick={() => navigate('/signup')} variant="outline">
              회원가입
            </Button>
          </Flex>
        )}
      </Flex>
    </Box>
  );
};

export default Header;
