// src/components/Header.tsx - 완전히 수정된 버전
import {
  Box,
  Flex,
  Heading,
  Spacer,
  Button,
  IconButton,
  useColorMode,
  useColorModeValue,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  Avatar,
  HStack,
  Badge,
  Text,
} from '@chakra-ui/react';
import { 
  MoonIcon, 
  SunIcon, 
  ChevronDownIcon,
  BellIcon,
} from '@chakra-ui/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { followAPI, userAPI } from '../services/api';
import { 
  RssIcon, 
  BookmarkIcon, 
  UsersIcon, 
  HeartIcon,
  CommentIcon,
  CogIcon,
  SearchIcon
} from '../components/icons/SimpleIcons';
import { getCurrentUserId } from '../utils/auth';

const Header = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { colorMode, toggleColorMode } = useColorMode();
  
  // 테마에 따른 배경색 결정
  const headerBg = useColorModeValue('blue.500', 'blue.600');
  const textColor = useColorModeValue('white', 'white');
  const isLoggedIn = !!localStorage.getItem('token');
  // ✅ 사용자 정보 상태 추가
  const [userProfile, setUserProfile] = useState<{
    name: string;
    email: string;
  } | null>(null);
  // 소셜 통계 상태
  const [followStats, setFollowStats] = useState<{
    followers_count: number;
    followees_count: number;
  } | null>(null);

  useEffect(() => {
    if (isLoggedIn) {
      fetchUserProfile();
      fetchFollowStats();
    }
  }, [isLoggedIn]);

  const fetchUserProfile = async () => {
    try {
      const response = await userAPI.getProfile();
      setUserProfile({
        name: response.data.name,
        email: response.data.email
      });
    } catch (error) {
      console.error('사용자 프로필 조회 실패:', error);
    }
  };

  const fetchFollowStats = async () => {
    try {
      // 현재 사용자 ID를 가져와야 하는데, 여기서는 임시로 처리
      // 실제로는 auth context나 user store에서 가져와야 함
      const currentUserId = getCurrentUserId(); // auth utils에서 현재 사용자 ID 가져오기
      if (!currentUserId) {
        console.log('현재 사용자 ID를 찾을 수 없음');
        return;
      }
      const response = await followAPI.getFollowStats(currentUserId);
      setFollowStats(response.data);
    } catch (error) {
      console.error('팔로우 통계 조회 실패:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const isActivePage = (path: string) => {
    if (path === '/' || path === '/dashboard') {
      return location.pathname === '/' || location.pathname === '/dashboard';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <Box bg={headerBg} color={textColor} px={4} py={3}>
      <Flex align="center">
        <Heading 
          size="lg" 
          cursor="pointer"
          onClick={() => navigate('/')}
          _hover={{ opacity: 0.8 }}
        >
          LLearn
        </Heading>
        
        <Spacer />
        
        {isLoggedIn ? (
          <HStack spacing={4} align="center">
            {/* 테마 토글 버튼 */}
            <IconButton
              aria-label="테마 변경"
              icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
              onClick={toggleColorMode}
              variant="ghost"
              size="sm"
              color={textColor}
              _hover={{ bg: 'whiteAlpha.200' }}
            />

            {/* 알림 버튼 */}
            <IconButton
              aria-label="알림"
              icon={<BellIcon />}
              variant="ghost"
              size="sm"
              color={textColor}
              _hover={{ bg: 'whiteAlpha.200' }}
              onClick={() => {
                // TODO: 알림 페이지 또는 모달 구현
                console.log('알림 클릭');
              }}
            />
            
            {/* 네비게이션 버튼들 */}
            <Button 
              onClick={() => navigate('/dashboard')} 
              variant="ghost"
              bg={isActivePage('/dashboard') ? 'whiteAlpha.300' : 'transparent'}
              _hover={{ bg: 'whiteAlpha.200' }}
              color={textColor}
            >
              대시보드
            </Button>

            <Button 
              onClick={() => navigate('/feed')} 
              variant="ghost"
              bg={isActivePage('/feed') ? 'whiteAlpha.300' : 'transparent'}
              _hover={{ bg: 'whiteAlpha.200' }}
              leftIcon={<RssIcon />}
              color={textColor}
            >
              피드
            </Button>
            
            <Button 
              onClick={() => navigate('/curriculum')} 
              variant="ghost"
              bg={isActivePage('/curriculum') ? 'whiteAlpha.300' : 'transparent'}
              _hover={{ bg: 'whiteAlpha.200' }}
              color={textColor}
            >
              커리큘럼
            </Button>
            
            <Button 
              onClick={() => navigate('/summary')} 
              variant="ghost"
              bg={isActivePage('/summary') ? 'whiteAlpha.300' : 'transparent'}
              _hover={{ bg: 'whiteAlpha.200' }}
              color={textColor}
            >
              요약
            </Button>

            {/* 사용자 메뉴 */}
            <Menu>
              <MenuButton
                as={Button}
                variant="ghost"
                rightIcon={<ChevronDownIcon />}
                _hover={{ bg: 'whiteAlpha.200' }}
                color={textColor}
              >
                <HStack spacing={2}>
                  <Avatar 
                    name={userProfile?.name || '사용자'} // ✅ 실제 이름 사용
                    size="sm" 
                  />
                  <Box textAlign="left" display={{ base: 'none', md: 'block' }}>
                    <Text fontSize="sm" fontWeight="semibold">
                      {userProfile?.name || '사용자'} {/* ✅ 실제 이름 사용 */}
                    </Text>
                    {followStats && (
                      <Text 
                        fontSize="xs" 
                        opacity={0.8}
                        cursor="pointer"
                        _hover={{ opacity: 1, textDecoration: 'underline' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate('/social/follow');
                        }}
                      >
                        팔로워 {followStats.followers_count} · 팔로잉 {followStats.followees_count}
                      </Text>
                    )}
                  </Box>
                </HStack>
              </MenuButton>
              <MenuList color="black">
                <MenuItem 
                  icon={<UsersIcon />}
                  onClick={() => navigate('/social/profile')}
                >
                  내 프로필
                </MenuItem>

                <MenuItem 
                  icon={<SearchIcon />} // ✅ 추가
                  onClick={() => navigate('/social/explore')} // ✅ 추가
                >
                  사용자 탐색
                </MenuItem>

                <MenuItem 
                  icon={<BookmarkIcon />}
                  onClick={() => navigate('/bookmarks')}
                >
                  북마크
                  {/* TODO: 북마크 수 표시 */}
                </MenuItem>

                <MenuItem 
                  icon={<HeartIcon />}
                  onClick={() => navigate('/social/liked')}
                >
                  좋아요한 글
                </MenuItem>
                <MenuItem 
                  icon={<CommentIcon />}
                  onClick={() => navigate('/social/comments')}
                >
                  내 댓글
                </MenuItem>
                <MenuDivider />
                <MenuItem 
                  icon={<CogIcon />}
                  onClick={() => navigate('/settings')}
                >
                  설정
                </MenuItem>
                <MenuItem onClick={handleLogout}>
                  로그아웃
                </MenuItem>
              </MenuList>
            </Menu>
          </HStack>
        ) : (
          <HStack spacing={2} align="center">
            {/* 테마 토글 버튼 */}
            <IconButton
              aria-label="테마 변경"
              icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
              onClick={toggleColorMode}
              variant="ghost"
              size="sm"
              color={textColor}
              _hover={{ bg: 'whiteAlpha.200' }}
              mr={2}
            />
            
            <Button 
              onClick={() => navigate('/feed')} 
              variant="ghost"
              _hover={{ bg: 'whiteAlpha.200' }}
              leftIcon={<RssIcon />}
              color={textColor}
            >
              피드 구경하기
            </Button>
            
            <Button 
              onClick={() => navigate('/login')} 
              variant="ghost"
              _hover={{ bg: 'whiteAlpha.200' }}
              color={textColor}
            >
              로그인
            </Button>
            <Button 
              onClick={() => navigate('/signup')} 
              variant="outline"
              _hover={{ bg: 'whiteAlpha.200' }}
              color={textColor}
              borderColor={textColor}
            >
              회원가입
            </Button>
          </HStack>
        )}
      </Flex>
    </Box>
  );
};

export default Header;
