import {
  Box,
  Flex,
  Heading,
  Spacer,
  Button,
  IconButton,
  useColorMode,
  useColorModeValue,
} from '@chakra-ui/react';
import { MoonIcon, SunIcon } from '@chakra-ui/icons';
import { useNavigate, useLocation } from 'react-router-dom';

const Header = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { colorMode, toggleColorMode } = useColorMode();
  
  // 테마에 따른 배경색 결정
  const headerBg = useColorModeValue('blue.500', 'blue.600');
  const isLoggedIn = !!localStorage.getItem('token');

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const isActivePage = (path: string) => {
    if (path === '/' || path === '/dashboard') {
      return location.pathname === '/' || location.pathname === '/dashboard';
    }
    return location.pathname === path;
  };

  return (
    <Box bg={headerBg} color="white" px={4} py={3}>
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
            {/* 테마 토글 버튼 */}
            <IconButton
              aria-label="테마 변경"
              icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
              onClick={toggleColorMode}
              variant="ghost"
              size="sm"
              color="white"
              _hover={{ bg: 'whiteAlpha.200' }}
            />
            
            <Button 
              onClick={() => navigate('/dashboard')} 
              variant="ghost"
              bg={isActivePage('/dashboard') ? 'whiteAlpha.300' : 'transparent'}
              _hover={{ bg: 'whiteAlpha.200' }}
            >
              대시보드
            </Button>
            <Button 
              onClick={() => navigate('/curriculum')} 
              variant="ghost"
              bg={isActivePage('/curriculum') ? 'whiteAlpha.300' : 'transparent'}
              _hover={{ bg: 'whiteAlpha.200' }}
            >
              커리큘럼
            </Button>
            <Button 
              onClick={handleLogout} 
              variant="ghost"
              _hover={{ bg: 'whiteAlpha.200' }}
            >
              로그아웃
            </Button>
            <Box w="8" h="8" bg="gray.300" borderRadius="full" />
          </Flex>
        ) : (
          <Flex gap={2} align="center">
            {/* 테마 토글 버튼 */}
            <IconButton
              aria-label="테마 변경"
              icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
              onClick={toggleColorMode}
              variant="ghost"
              size="sm"
              color="white"
              _hover={{ bg: 'whiteAlpha.200' }}
              mr={2}
            />
            
            <Button 
              onClick={() => navigate('/login')} 
              variant="ghost"
              _hover={{ bg: 'whiteAlpha.200' }}
            >
              로그인
            </Button>
            <Button 
              onClick={() => navigate('/signup')} 
              variant="outline"
              _hover={{ bg: 'whiteAlpha.200' }}
            >
              회원가입
            </Button>
          </Flex>
        )}
      </Flex>
    </Box>
  );
};

export default Header;
