// frontend/src/pages/UserExplore.tsx
import React, { useState, useEffect } from 'react';
import {
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Card,
  CardBody,
  Input,
  Button,
  Grid,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  useColorModeValue,
  Box,
  Avatar,
  InputGroup,
  InputLeftElement,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { userAPI, followAPI } from '../services/api';
import FollowButton from '../components/social/FollowButton';
import { SearchIcon, UsersIcon } from '../components/icons/SimpleIcons';
import { getCurrentUserId } from '../utils/auth';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  created_at: string;
}

interface FollowSuggestion {
  user_id: string;
  username: string;
  email: string;
  followers_count: number;
  followees_count: number;
  is_following: boolean;
  is_followed_by: boolean;
}

const UserExplore: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<User[]>([]);
  const [suggestions, setSuggestions] = useState<FollowSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [suggestionsLoading, setSuggestionsLoading] = useState(true);
  const [error, setError] = useState('');

  const currentUserId = getCurrentUserId();

  const textColor = useColorModeValue('gray.900', 'white');
  const secondaryTextColor = useColorModeValue('gray.600', 'gray.300');
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    fetchSuggestions();
  }, []);

  const fetchSuggestions = async () => {
    try {
      setSuggestionsLoading(true);
      const response = await followAPI.getFollowSuggestions({ limit: 10 });
      setSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('추천 사용자 조회 실패:', error);
    } finally {
      setSuggestionsLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      setLoading(true);
      setError('');
      
      const response = await userAPI.searchUsers({
        q: searchQuery.trim(),
        page: 1,
        items_per_page: 20
      });
      
      setSearchResults(response.data.users || []);
    } catch (error: any) {
      console.error('사용자 검색 실패:', error);
      setError('사용자 검색에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleFollowChange = (userId: string, isFollowing: boolean) => {
    // 검색 결과에서 상태 업데이트는 필요없음 (User 타입에 팔로우 정보 없음)
    // 추천 목록에서 상태 업데이트
    setSuggestions(prev => 
      prev.map(user => 
        user.user_id === userId 
          ? { ...user, is_following: isFollowing }
          : user
      )
    );
  };

  const renderUserCard = (user: User | FollowSuggestion) => {
    const isUser = 'name' in user;
    const userId = isUser ? user.id : user.user_id;
    const userName = isUser ? user.name : user.username;
    const userEmail = isUser ? user.email : user.email;
    
    return (
      <Card key={userId} bg={cardBg} borderColor={borderColor}>
        <CardBody>
          <HStack justify="space-between" align="center">
            <HStack spacing={3}>
              <Avatar name={userName} size="md" />
              <VStack align="start" spacing={1}>
                <Text fontWeight="semibold" color={textColor}>
                  {userName}
                </Text>
                <Text fontSize="sm" color={secondaryTextColor}>
                  {userEmail}
                </Text>
                {!isUser && (
                  <HStack spacing={4} fontSize="xs" color={secondaryTextColor}>
                    <Text>팔로워 {(user as FollowSuggestion).followers_count}</Text>
                    <Text>팔로잉 {(user as FollowSuggestion).followees_count}</Text>
                  </HStack>
                )}
              </VStack>
            </HStack>
            
            {userId !== currentUserId && (
              <FollowButton
                userId={userId}
                initialFollowState={!isUser ? (user as FollowSuggestion).is_following : false}
                onFollowChange={(isFollowing) => handleFollowChange(userId, isFollowing)}
              />
            )}
          </HStack>
        </CardBody>
      </Card>
    );
  };

  return (
    <Container maxW="4xl" py={8}>
      <VStack spacing={6} align="stretch">
        {/* 헤더 */}
        <VStack align="start" spacing={1}>
          <Heading size="lg" color={textColor}>사용자 탐색</Heading>
          <Text fontSize="sm" color={secondaryTextColor}>
            새로운 사용자를 찾아 팔로우해보세요
          </Text>
        </VStack>

        {/* 검색 */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Text fontWeight="semibold" color={textColor}>사용자 검색</Text>
              <HStack>
                <InputGroup>
                  <InputLeftElement pointerEvents="none">
                    <SearchIcon />
                  </InputLeftElement>
                  <Input
                    placeholder="사용자 이름이나 이메일로 검색..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                  />
                </InputGroup>
                <Button
                  leftIcon={<SearchIcon />}
                  colorScheme="blue"
                  onClick={handleSearch}
                  isLoading={loading}
                  loadingText="검색 중..."
                >
                  검색
                </Button>
              </HStack>

              {/* 검색 결과 */}
              {searchResults.length > 0 && (
                <VStack spacing={3} align="stretch">
                  <Text fontWeight="semibold" color={textColor}>
                    검색 결과 ({searchResults.length}명)
                  </Text>
                  {searchResults.map(renderUserCard)}
                </VStack>
              )}

              {/* 검색 에러 */}
              {error && (
                <Alert status="error">
                  <AlertIcon />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </VStack>
          </CardBody>
        </Card>

        {/* 추천 사용자 */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between">
                <Text fontWeight="semibold" color={textColor}>추천 사용자</Text>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={fetchSuggestions}
                  isLoading={suggestionsLoading}
                >
                  새로고침
                </Button>
              </HStack>

              {suggestionsLoading ? (
                <VStack py={6}>
                  <Spinner color="blue.500" />
                  <Text color={secondaryTextColor}>추천 사용자를 불러오는 중...</Text>
                </VStack>
              ) : suggestions.length > 0 ? (
                <VStack spacing={3} align="stretch">
                  {suggestions.map(renderUserCard)}
                </VStack>
              ) : (
                <Box textAlign="center" py={6}>
                  <UsersIcon size="40px" style={{ margin: '0 auto 12px' }} />
                  <Text color={secondaryTextColor}>
                    추천할 사용자가 없습니다
                  </Text>
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </Container>
  );
};

export default UserExplore;
