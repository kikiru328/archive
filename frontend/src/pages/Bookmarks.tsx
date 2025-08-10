// src/pages/Bookmarks.tsx - 완전히 수정된 버전
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
  IconButton,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { bookmarkAPI } from '../services/api';
import { BookmarkIcon, EyeIcon, TrashIcon } from '../components/icons/SimpleIcons';

interface Bookmark {
  id: string;
  curriculum_id: string;
  user_id: string;
  created_at: string;
}

interface BookmarkWithDetails extends Bookmark {
  curriculum_title?: string;
  curriculum_weeks?: number;
  curriculum_lessons?: number;
}

const Bookmarks: React.FC = () => {
  const navigate = useNavigate();
  const [bookmarks, setBookmarks] = useState<BookmarkWithDetails[]>([]);
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
    fetchBookmarks();
  }, []);

  useEffect(() => {
    if (page > 1) {
      fetchBookmarks(false);
    }
  }, [page]);

  const fetchBookmarks = async (reset = true) => {
    try {
      if (reset) {
        setLoading(true);
        setPage(1);
      }

      const response = await bookmarkAPI.getMyBookmarks({
        page: reset ? 1 : page,
        items_per_page: 20,
      });

      const newBookmarks = response.data.bookmarks || [];

      if (reset) {
        setBookmarks(newBookmarks);
      } else {
        setBookmarks(prev => [...prev, ...newBookmarks]);
      }

      setTotalCount(response.data.total_count);
      setHasMore((reset ? 1 : page) * 20 < response.data.total_count);
      setError('');
    } catch (error: any) {
      console.error('북마크 조회 실패:', error);
      setError('북마크를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveBookmark = async (curriculumId: string) => {
    try {
      await bookmarkAPI.deleteBookmark(curriculumId);
      setBookmarks(prev => prev.filter(b => b.curriculum_id !== curriculumId));
      setTotalCount(prev => prev - 1);
    } catch (error: any) {
      console.error('북마크 삭제 실패:', error);
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

  if (loading && bookmarks.length === 0) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text color={textColor}>북마크를 불러오는 중...</Text>
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
            <Heading size="lg" color={textColor}>내 북마크</Heading>
            <Text fontSize="sm" color={secondaryTextColor}>
              저장한 커리큘럼 {totalCount}개
            </Text>
          </VStack>
          <Button
            colorScheme="blue"
            onClick={() => navigate('/feed')}
            leftIcon={<BookmarkIcon />}
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

        {/* 북마크 목록 */}
        {bookmarks.length === 0 && !loading ? (
          <Box textAlign="center" py={10}>
            <Box mb={4} display="flex" justifyContent="center">
              <BookmarkIcon size="48px" />
            </Box>
            <Text fontSize="lg" color={secondaryTextColor} mb={4}>
              아직 북마크한 커리큘럼이 없습니다
            </Text>
            <Text color={secondaryTextColor} mb={6}>
              관심있는 커리큘럼을 북마크하여 나중에 쉽게 찾아보세요!
            </Text>
            <Button colorScheme="blue" onClick={() => navigate('/feed')}>
              커뮤니티 피드 둘러보기
            </Button>
          </Box>
        ) : (
          <Grid templateColumns="repeat(auto-fill, minmax(300px, 1fr))" gap={6}>
            {bookmarks.map((bookmark) => (
              <Card
                key={bookmark.id}
                bg={cardBg}
                borderColor={borderColor}
                _hover={{ shadow: 'md', transform: 'translateY(-2px)' }}
                transition="all 0.2s"
              >
                <CardBody>
                  <VStack align="stretch" spacing={4}>
                    {/* 커리큘럼 정보 */}
                    <VStack align="start" spacing={2}>
                      <HStack justify="space-between" w="100%">
                        <Badge colorScheme="blue" variant="solid">
                          <Box as="span" mr={1}>
                            <BookmarkIcon />
                          </Box>
                          북마크됨
                        </Badge>
                        <IconButton
                          aria-label="북마크 제거"
                          icon={<TrashIcon />}
                          size="sm"
                          variant="ghost"
                          colorScheme="red"
                          onClick={() => handleRemoveBookmark(bookmark.curriculum_id)}
                        />
                      </HStack>

                      <Heading size="md" color={textColor} noOfLines={2}>
                        {bookmark.curriculum_title || `커리큘럼 ${bookmark.curriculum_id.slice(0, 8)}`}
                      </Heading>

                      {(bookmark.curriculum_weeks || bookmark.curriculum_lessons) && (
                        <HStack spacing={4} fontSize="sm" color={secondaryTextColor}>
                          {bookmark.curriculum_weeks && (
                            <Text>{bookmark.curriculum_weeks}주차</Text>
                          )}
                          {bookmark.curriculum_lessons && (
                            <Text>{bookmark.curriculum_lessons}개 레슨</Text>
                          )}
                        </HStack>
                      )}
                    </VStack>

                    {/* 북마크 날짜 */}
                    <Text fontSize="xs" color={secondaryTextColor}>
                      {formatDate(bookmark.created_at)}에 북마크함
                    </Text>

                    {/* 액션 버튼 */}
                    <HStack justify="space-between">
                      <Button
                        leftIcon={<EyeIcon />}
                        size="sm"
                        variant="outline"
                        colorScheme="blue"
                        onClick={() => navigate(`/curriculum/${bookmark.curriculum_id}`)}
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
        {hasMore && bookmarks.length > 0 && (
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
        {!hasMore && bookmarks.length > 0 && (
          <Text textAlign="center" color={secondaryTextColor} py={4}>
            모든 북마크를 확인했습니다!
          </Text>
        )}
      </VStack>
    </Container>
  );
};

export default Bookmarks;
