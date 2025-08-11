// src/pages/LikedCurriculums.tsx
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
  Badge,
  Avatar,
  Divider,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { likeAPI } from '../services/api';
import { HeartIcon, EyeIcon } from '../components/icons/SimpleIcons';

interface LikedCurriculum {
  id: string;
  curriculum_id: string;
  user_id: string;
  created_at: string;
  // 확장된 커리큘럼 정보 (실제 API 응답에 따라 조정 필요)
  curriculum_title?: string;
  curriculum_owner_name?: string;
  curriculum_weeks?: number;
  curriculum_lessons?: number;
}

const LikedCurriculums: React.FC = () => {
  const navigate = useNavigate();
  const [likedCurriculums, setLikedCurriculums] = useState<LikedCurriculum[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  const textColor = useColorModeValue('gray.900', 'white');
  const secondaryTextColor = useColorModeValue('gray.600', 'gray.300');
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    fetchLikedCurriculums();
  }, []);

  useEffect(() => {
    if (page > 1) {
      fetchLikedCurriculums(false);
    }
  }, [page]);

  const fetchLikedCurriculums = async (reset = true) => {
    try {
      if (reset) {
        setLoading(true);
        setPage(1);
      }

      const response = await likeAPI.getMyLikes({
        page: reset ? 1 : page,
        items_per_page: 20,
      });

      const newLikes = response.data.likes || [];

      if (reset) {
        setLikedCurriculums(newLikes);
      } else {
        setLikedCurriculums(prev => [...prev, ...newLikes]);
      }

      setTotalCount(response.data.total_count);
      setHasMore((reset ? 1 : page) * 20 < response.data.total_count);
      setError('');
    } catch (error: any) {
      console.error('좋아요 목록 조회 실패:', error);
      
      if (error.response?.status === 404) {
        setError('좋아요 기능이 아직 준비되지 않았습니다.');
      } else {
        setError('좋아요한 커리큘럼을 불러오는데 실패했습니다.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLoadMore = () => {
    if (hasMore && !loading) {
      setPage(prev => prev + 1);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading && likedCurriculums.length === 0) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text color={textColor}>좋아요한 커리큘럼을 불러오는 중...</Text>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="6xl" py={8}>
      <VStack spacing={6} align="stretch">
        {/* 헤더 */}
        <HStack justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <Heading size="lg" color={textColor}>좋아요한 커리큘럼</Heading>
            <Text fontSize="sm" color={secondaryTextColor}>
              좋아요한 커리큘럼 {totalCount}개
            </Text>
          </VStack>
          <Button
            colorScheme="blue"
            onClick={() => navigate('/feed')}
            leftIcon={<HeartIcon />}
          >
            피드 보기
          </Button>
        </HStack>

        {/* 에러 메시지 */}
        {error && (
          <Alert status="error">
            <AlertIcon />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* 좋아요 목록 */}
        {likedCurriculums.length === 0 && !loading ? (
          <Box textAlign="center" py={10}>
            <Box mb={4} display="flex" justifyContent="center">
              <HeartIcon size="48px" />
            </Box>
            <Text fontSize="lg" color={secondaryTextColor} mb={4}>
              아직 좋아요한 커리큘럼이 없습니다
            </Text>
            <Text color={secondaryTextColor} mb={6}>
              관심있는 커리큘럼에 좋아요를 눌러보세요!
            </Text>
            <Button colorScheme="blue" onClick={() => navigate('/feed')}>
              커뮤니티 피드 둘러보기
            </Button>
          </Box>
        ) : (
          <Grid templateColumns="repeat(auto-fill, minmax(350px, 1fr))" gap={6}>
            {likedCurriculums.map((like) => (
              <Card
                key={like.id}
                bg={cardBg}
                borderColor={borderColor}
                _hover={{ shadow: 'md', transform: 'translateY(-2px)' }}
                transition="all 0.2s"
              >
                <CardBody>
                  <VStack align="stretch" spacing={4}>
                    {/* 헤더 */}
                    <HStack justify="space-between" align="start">
                      <VStack align="start" spacing={1}>
                        <HStack>
                          <Avatar name={like.curriculum_owner_name} size="sm" />
                          <VStack align="start" spacing={0}>
                            <Text fontSize="sm" fontWeight="semibold" color={textColor}>
                              {like.curriculum_owner_name || '작성자'}
                            </Text>
                            <Text fontSize="xs" color={secondaryTextColor}>
                              {formatDate(like.created_at)}에 좋아요
                            </Text>
                          </VStack>
                        </HStack>
                      </VStack>
                      <Badge colorScheme="red" variant="solid">
                        <HeartIcon size="12px" style={{ marginRight: '4px' }} />
                        좋아요
                      </Badge>
                    </HStack>

                    {/* 커리큘럼 정보 */}
                    <VStack align="start" spacing={2}>
                      <Heading size="md" color={textColor} noOfLines={2}>
                        {like.curriculum_title || `커리큘럼 ${like.curriculum_id.slice(0, 8)}`}
                      </Heading>

                      {(like.curriculum_weeks || like.curriculum_lessons) && (
                        <HStack spacing={4} fontSize="sm" color={secondaryTextColor}>
                          {like.curriculum_weeks && (
                            <Text>{like.curriculum_weeks}주차</Text>
                          )}
                          {like.curriculum_lessons && (
                            <Text>{like.curriculum_lessons}개 레슨</Text>
                          )}
                        </HStack>
                      )}
                    </VStack>

                    <Divider />

                    {/* 액션 버튼 */}
                    <HStack justify="space-between">
                      <Button
                        leftIcon={<EyeIcon />}
                        size="sm"
                        variant="outline"
                        colorScheme="blue"
                        onClick={() => navigate(`/curriculum/${like.curriculum_id}`)}
                        flex={1}
                      >
                        상세보기
                      </Button>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </Grid>
        )}

        {/* 더 보기 버튼 */}
        {hasMore && likedCurriculums.length > 0 && (
          <Button
            onClick={handleLoadMore}
            isLoading={loading}
            loadingText="로딩 중..."
            variant="outline"
            size="lg"
          >
            더 보기
          </Button>
        )}

        {/* 더 이상 항목이 없을 때 */}
        {!hasMore && likedCurriculums.length > 0 && (
          <Text textAlign="center" color={secondaryTextColor} py={4}>
            모든 좋아요한 커리큘럼을 확인했습니다!
          </Text>
        )}
      </VStack>
    </Container>
  );
};

export default LikedCurriculums;
