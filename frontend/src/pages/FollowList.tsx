// frontend/src/pages/FollowList.tsx
import React, { useState, useEffect } from 'react';
import {
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Card,
  CardBody,
  Button,
  Grid,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  useColorModeValue,
  Box,
  Avatar,
  Badge,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { followAPI } from '../services/api';
import FollowButton from '../components/social/FollowButton';
import { UsersIcon } from '../components/icons/SimpleIcons';
import { getCurrentUserId } from '../utils/auth';

interface FollowUser {
  user_id: string;
  username: string;
  email: string;
  followers_count: number;
  followees_count: number;
  is_following: boolean;
  is_followed_by: boolean;
}

interface FollowListData {
  total_count: number;
  page: number;
  items_per_page: number;
  followers?: FollowUser[];
  followees?: FollowUser[];
}

const FollowList: React.FC = () => {
  const navigate = useNavigate();
  const { userId } = useParams<{ userId?: string }>();
  const [searchParams] = useSearchParams();
  const tab = searchParams.get('tab') || 'followers';
  
  const [followersData, setFollowersData] = useState<FollowListData | null>(null);
  const [followeesData, setFolloweesData] = useState<FollowListData | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(tab === 'following' ? 1 : 0);

  const currentUserId = getCurrentUserId();
  const targetUserId = userId || currentUserId;
  const isMyProfile = !userId || userId === currentUserId;

  const textColor = useColorModeValue('gray.900', 'white');
  const secondaryTextColor = useColorModeValue('gray.600', 'gray.300');
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    if (targetUserId) {
      fetchFollowData();
    }
  }, [targetUserId, activeTab]);

  const fetchFollowData = async () => {
    if (!targetUserId) return;

    try {
      setLoading(true);
      setError('');

      const [followersResponse, followeesResponse] = await Promise.all([
        isMyProfile ? followAPI.getMyFollowers({ page: 1, items_per_page: 20 }) 
                   : followAPI.getFollowers(targetUserId, { page: 1, items_per_page: 20 }),
        isMyProfile ? followAPI.getMyFollowing({ page: 1, items_per_page: 20 })
                   : followAPI.getFollowing(targetUserId, { page: 1, items_per_page: 20 })
      ]);

      setFollowersData(followersResponse.data);
      setFolloweesData(followeesResponse.data);
    } catch (error: any) {
      console.error('팔로우 데이터 조회 실패:', error);
      setError('팔로우 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const loadMoreFollowers = async () => {
    if (!targetUserId || !followersData || loadingMore) return;

    try {
      setLoadingMore(true);
      const nextPage = Math.floor(followersData.followers!.length / 20) + 1;
      
      const response = isMyProfile 
        ? await followAPI.getMyFollowers({ page: nextPage, items_per_page: 20 })
        : await followAPI.getFollowers(targetUserId, { page: nextPage, items_per_page: 20 });

      setFollowersData(prev => prev ? {
        ...prev,
        followers: [...(prev.followers || []), ...(response.data.followers || [])]
      } : null);
    } catch (error) {
      console.error('팔로워 추가 로드 실패:', error);
    } finally {
      setLoadingMore(false);
    }
  };

  const loadMoreFollowees = async () => {
    if (!targetUserId || !followeesData || loadingMore) return;

    try {
      setLoadingMore(true);
      const nextPage = Math.floor(followeesData.followees!.length / 20) + 1;
      
      const response = isMyProfile
        ? await followAPI.getMyFollowing({ page: nextPage, items_per_page: 20 })
        : await followAPI.getFollowing(targetUserId, { page: nextPage, items_per_page: 20 });

      setFolloweesData(prev => prev ? {
        ...prev,
        followees: [...(prev.followees || []), ...(response.data.followees || [])]
      } : null);
    } catch (error) {
      console.error('팔로잉 추가 로드 실패:', error);
    } finally {
      setLoadingMore(false);
    }
  };

  const handleFollowChange = (userId: string, isFollowing: boolean) => {
    // 팔로우 상태 변경 시 로컬 상태 업데이트
    setFollowersData(prev => prev ? {
      ...prev,
      followers: prev.followers?.map(user => 
        user.user_id === userId 
          ? { ...user, is_following: isFollowing }
          : user
      )
    } : null);

    setFolloweesData(prev => prev ? {
      ...prev,
      followees: prev.followees?.map(user => 
        user.user_id === userId 
          ? { ...user, is_following: isFollowing }
          : user
      )
    } : null);
  };

  const renderUserCard = (user: FollowUser) => (
    <Card key={user.user_id} bg={cardBg} borderColor={borderColor}>
      <CardBody>
        <HStack justify="space-between" align="center">
          <HStack spacing={3}>
            <Avatar name={user.username} size="md" />
            <VStack align="start" spacing={1}>
              <Text fontWeight="semibold" color={textColor}>
                {user.username}
              </Text>
              <Text fontSize="sm" color={secondaryTextColor}>
                {user.email}
              </Text>
              <HStack spacing={4} fontSize="xs" color={secondaryTextColor}>
                <Text>팔로워 {user.followers_count}</Text>
                <Text>팔로잉 {user.followees_count}</Text>
              </HStack>
              {user.is_followed_by && (
                <Badge colorScheme="blue" size="sm">
                  나를 팔로우함
                </Badge>
              )}
            </VStack>
          </HStack>
          
          {user.user_id !== currentUserId && (
            <FollowButton
              userId={user.user_id}
              initialFollowState={user.is_following}
              onFollowChange={(isFollowing) => handleFollowChange(user.user_id, isFollowing)}
            />
          )}
        </HStack>
      </CardBody>
    </Card>
  );

  if (loading) {
    return (
      <Container maxW="4xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text color={textColor}>팔로우 정보를 불러오는 중...</Text>
        </VStack>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxW="4xl" py={8}>
        <Alert status="error">
          <AlertIcon />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxW="4xl" py={8}>
      <VStack spacing={6} align="stretch">
        {/* 헤더 */}
        <HStack justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <Heading size="lg" color={textColor}>
              {isMyProfile ? '내 팔로우' : '팔로우 목록'}
            </Heading>
            <Text fontSize="sm" color={secondaryTextColor}>
              팔로워와 팔로잉 목록을 확인하세요
            </Text>
          </VStack>
          <Button
            leftIcon={<UsersIcon />}
            colorScheme="blue"
            onClick={() => navigate('/feed')}
          >
            피드 보기
          </Button>
        </HStack>

        {/* 탭 */}
        <Tabs 
          index={activeTab} 
          onChange={(index) => {
            setActiveTab(index);
            const newTab = index === 0 ? 'followers' : 'following';
            navigate(`${isMyProfile ? '/social/follow' : `/social/users/${userId}/follow`}?tab=${newTab}`, { replace: true });
          }}
          colorScheme="blue"
        >
          <TabList>
            <Tab>
              팔로워 ({followersData?.total_count || 0})
            </Tab>
            <Tab>
              팔로잉 ({followeesData?.total_count || 0})
            </Tab>
          </TabList>

          <TabPanels>
            {/* 팔로워 탭 */}
            <TabPanel px={0}>
              <VStack spacing={4} align="stretch">
                {followersData?.followers && followersData.followers.length > 0 ? (
                  <>
                    <VStack spacing={3} align="stretch">
                      {followersData.followers.map(renderUserCard)}
                    </VStack>
                    
                    {followersData.followers.length < followersData.total_count && (
                      <Button
                        onClick={loadMoreFollowers}
                        isLoading={loadingMore}
                        loadingText="로딩 중..."
                        variant="outline"
                      >
                        더 보기
                      </Button>
                    )}
                  </>
                ) : (
                  <Box textAlign="center" py={10}>
                    <UsersIcon size="48px" style={{ margin: '0 auto 16px' }} />
                    <Text fontSize="lg" color={secondaryTextColor} mb={4}>
                      {isMyProfile ? '아직 팔로워가 없습니다' : '팔로워가 없습니다'}
                    </Text>
                    <Text color={secondaryTextColor}>
                      {isMyProfile 
                        ? '활발한 활동으로 팔로워를 늘려보세요!'
                        : '이 사용자를 팔로우해보세요!'
                      }
                    </Text>
                  </Box>
                )}
              </VStack>
            </TabPanel>

            {/* 팔로잉 탭 */}
            <TabPanel px={0}>
              <VStack spacing={4} align="stretch">
                {followeesData?.followees && followeesData.followees.length > 0 ? (
                  <>
                    <VStack spacing={3} align="stretch">
                      {followeesData.followees.map(renderUserCard)}
                    </VStack>
                    
                    {followeesData.followees.length < followeesData.total_count && (
                      <Button
                        onClick={loadMoreFollowees}
                        isLoading={loadingMore}
                        loadingText="로딩 중..."
                        variant="outline"
                      >
                        더 보기
                      </Button>
                    )}
                  </>
                ) : (
                  <Box textAlign="center" py={10}>
                    <UsersIcon size="48px" style={{ margin: '0 auto 16px' }} />
                    <Text fontSize="lg" color={secondaryTextColor} mb={4}>
                      {isMyProfile ? '아직 팔로우한 사용자가 없습니다' : '팔로우한 사용자가 없습니다'}
                    </Text>
                    <Text color={secondaryTextColor}>
                      {isMyProfile 
                        ? '관심있는 사용자들을 팔로우해보세요!'
                        : '이 사용자의 관심사를 확인해보세요!'
                      }
                    </Text>
                  </Box>
                )}
              </VStack>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>
    </Container>
  );
};

export default FollowList;
