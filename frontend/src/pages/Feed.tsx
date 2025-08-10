// src/pages/Feed.tsx
import React, { useState, useEffect } from 'react';
import {
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Card,
  CardBody,
  Badge,
  Button,
  Input,
  Select,
  Grid,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  useColorModeValue,
  Box,
  Divider,
  Avatar,
  IconButton,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Textarea,
  FormControl,
  FormLabel,
} from '@chakra-ui/react';
import { 
  FaSearch, 
  FaFilter, 
  FaSync,
  FaEye,
  FaHeart,
  FaComment,
  FaBookmark,
} from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import { feedAPI, categoryAPI, commentAPI } from '../services/api';
import SocialButtons from '../components/social/SocialButtons';

interface FeedItem {
  curriculum_id: string;
  title: string;
  owner_id: string;
  owner_name: string;
  total_weeks: number;
  total_lessons: number;
  created_at: string;
  updated_at: string;
  time_ago: string;
  category_name?: string;
  category_color?: string;
  tags: string[];
}

interface Category {
  id: string;
  name: string;
  color: string;
  icon?: string;
}

const Feed: React.FC = () => {
  const navigate = useNavigate();
  const [feedItems, setFeedItems] = useState<FeedItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  
  // 필터 상태
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedTags, setSelectedTags] = useState('');
  
  // 페이지네이션
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [totalCount, setTotalCount] = useState(0);

  // 댓글 모달
  const { isOpen: isCommentOpen, onOpen: onCommentOpen, onClose: onCommentClose } = useDisclosure();
  const [selectedCurriculumId, setSelectedCurriculumId] = useState('');
  const [commentContent, setCommentContent] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);

  const textColor = useColorModeValue('gray.900', 'white');
  const secondaryTextColor = useColorModeValue('gray.600', 'gray.300');
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const filterBg = useColorModeValue('gray.50', 'gray.800');

  useEffect(() => {
    fetchCategories();
    fetchFeed();
  }, []);

  useEffect(() => {
    fetchFeed();
  }, [page, selectedCategory, searchQuery, selectedTags]);

  const fetchCategories = async () => {
    try {
      const response = await categoryAPI.getActive();
      setCategories(response.data || []);
    } catch (error) {
      console.error('카테고리 조회 실패:', error);
    }
  };

  const fetchFeed = async (reset = false) => {
    try {
      if (reset) {
        setLoading(true);
        setPage(1);
      }

      const params = {
        page: reset ? 1 : page,
        items_per_page: 20,
        ...(selectedCategory && { category_id: selectedCategory }),
        ...(searchQuery && { search: searchQuery }),
        ...(selectedTags && { tags: selectedTags }),
      };

      const response = await feedAPI.getPublicFeed(params);
      const newItems = response.data.items || [];

      if (reset) {
        setFeedItems(newItems);
      } else {
        setFeedItems(prev => [...prev, ...newItems]);
      }

      setTotalCount(response.data.total_count);
      setHasMore(response.data.has_next);
      setError('');
    } catch (error: any) {
      console.error('피드 조회 실패:', error);
      setError('피드를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await feedAPI.refreshFeed();
      await fetchFeed(true);
    } catch (error) {
      console.error('피드 새로고침 실패:', error);
      await fetchFeed(true); // 실패해도 일반 조회는 시도
    }
  };

  const handleLoadMore = () => {
    if (hasMore && !loading) {
      setPage(prev => prev + 1);
    }
  };

  const handleSearch = () => {
    fetchFeed(true);
  };

  const handleFilterChange = () => {
    fetchFeed(true);
  };

  const handleCommentSubmit = async () => {
    if (!commentContent.trim() || !selectedCurriculumId) return;

    try {
      setSubmittingComment(true);
      await commentAPI.createComment(selectedCurriculumId, {
        content: commentContent.trim()
      });
      
      setCommentContent('');
      onCommentClose();
      // 피드 새로고침 (댓글 수 업데이트를 위해)
      await fetchFeed(true);
    } catch (error: any) {
      console.error('댓글 작성 실패:', error);
    } finally {
      setSubmittingComment(false);
    }
  };

  const openCommentModal = (curriculumId: string) => {
    setSelectedCurriculumId(curriculumId);
    onCommentOpen();
  };

  if (loading && feedItems.length === 0) {
    return (
      <Container maxW="4xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text color={textColor}>피드를 불러오는 중...</Text>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="4xl" py={8}>
      <VStack spacing={6} align="stretch">
        {/* 헤더 */}
        <HStack justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <Heading size="lg" color={textColor}>커뮤니티 피드</Heading>
            <Text fontSize="sm" color={secondaryTextColor}>
              {totalCount}개의 공개 커리큘럼
            </Text>
          </VStack>
          <IconButton
            aria-label="새로고침"
            icon={<FaSync />}
            colorScheme="blue"
            variant="outline"
            isLoading={refreshing}
            onClick={handleRefresh}
          />
        </HStack>

        {/* 필터 영역 */}
        <Card bg={filterBg} borderColor={borderColor}>
          <CardBody>
            <VStack spacing={4}>
              <Grid templateColumns={{ base: '1fr', md: '1fr 200px' }} gap={4} w="100%">
                <HStack>
                  <Input
                    placeholder="커리큘럼 제목이나 작성자로 검색..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                  <IconButton
                    aria-label="검색"
                    icon={<FaSearch />}
                    colorScheme="blue"
                    onClick={handleSearch}
                  />
                </HStack>
                <Button
                  leftIcon={<FaFilter />}
                  variant="outline"
                  onClick={handleFilterChange}
                >
                  필터 적용
                </Button>
              </Grid>

              <Grid templateColumns={{ base: '1fr', md: '1fr 1fr' }} gap={4} w="100%">
                <Select
                  placeholder="모든 카테고리"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                >
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.icon && `${category.icon} `}{category.name}
                    </option>
                  ))}
                </Select>
                <Input
                  placeholder="태그 (쉼표로 구분)"
                  value={selectedTags}
                  onChange={(e) => setSelectedTags(e.target.value)}
                />
              </Grid>
            </VStack>
          </CardBody>
        </Card>

        {/* 에러 메시지 */}
        {error && (
          <Alert status="error">
            <AlertIcon />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* 피드 아이템들 */}
        <VStack spacing={4} align="stretch">
          {feedItems.map((item) => (
            <Card key={item.curriculum_id} bg={cardBg} borderColor={borderColor}
                  _hover={{ shadow: 'md', transform: 'translateY(-1px)' }}
                  transition="all 0.2s"
            >
              <CardBody>
                <VStack align="stretch" spacing={4}>
                  {/* 헤더 */}
                  <HStack justify="space-between" align="start">
                    <HStack spacing={3}>
                      <Avatar name={item.owner_name} size="sm" />
                      <VStack align="start" spacing={0}>
                        <Text fontWeight="semibold" color={textColor}>
                          {item.owner_name}
                        </Text>
                        <Text fontSize="xs" color={secondaryTextColor}>
                          {item.time_ago}
                        </Text>
                      </VStack>
                    </HStack>
                    {item.category_name && (
                      <Badge
                        style={{ backgroundColor: item.category_color }}
                        color="white"
                        variant="solid"
                      >
                        {item.category_name}
                      </Badge>
                    )}
                  </HStack>

                  {/* 커리큘럼 제목 */}
                  <Heading
                    size="md"
                    color={textColor}
                    cursor="pointer"
                    onClick={() => navigate(`/curriculum/${item.curriculum_id}`)}
                    _hover={{ color: 'blue.500', textDecoration: 'underline' }}
                  >
                    {item.title}
                  </Heading>

                  {/* 메타 정보 */}
                  <HStack spacing={4} fontSize="sm" color={secondaryTextColor}>
                    <Text>{item.total_weeks}주차</Text>
                    <Text>{item.total_lessons}개 레슨</Text>
                    <Button
                      leftIcon={<FaEye />}
                      size="xs"
                      variant="ghost"
                      onClick={() => navigate(`/curriculum/${item.curriculum_id}`)}
                    >
                      상세보기
                    </Button>
                  </HStack>

                  {/* 태그 */}
                  {item.tags && item.tags.length > 0 && (
                    <HStack flexWrap="wrap" spacing={1}>
                      {item.tags.slice(0, 5).map((tag, index) => (
                        <Badge key={index} colorScheme="gray" variant="outline" size="sm">
                          #{tag}
                        </Badge>
                      ))}
                      {item.tags.length > 5 && (
                        <Badge colorScheme="gray" variant="outline" size="sm">
                          +{item.tags.length - 5}
                        </Badge>
                      )}
                    </HStack>
                  )}

                  <Divider />

                  {/* 소셜 버튼 */}
                  <SocialButtons
                    curriculumId={item.curriculum_id}
                    onCommentClick={() => openCommentModal(item.curriculum_id)}
                    size="sm"
                  />
                </VStack>
              </CardBody>
            </Card>
          ))}
        </VStack>

        {/* 더 보기 버튼 */}
        {hasMore && (
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
        {!hasMore && feedItems.length > 0 && (
          <Text textAlign="center" color={secondaryTextColor} py={4}>
            모든 커리큘럼을 확인했습니다!
          </Text>
        )}

        {/* 빈 상태 */}
        {feedItems.length === 0 && !loading && (
          <Box textAlign="center" py={10}>
            <Text fontSize="lg" color={secondaryTextColor} mb={4}>
              표시할 커리큘럼이 없습니다
            </Text>
            <Button colorScheme="blue" onClick={() => navigate('/curriculum')}>
              첫 번째 커리큘럼 만들기
            </Button>
          </Box>
        )}

        {/* 댓글 작성 모달 */}
        <Modal isOpen={isCommentOpen} onClose={onCommentClose}>
          <ModalOverlay />
          <ModalContent bg={cardBg} color={textColor}>
            <ModalHeader>댓글 작성</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <FormControl>
                <FormLabel>댓글 내용</FormLabel>
                <Textarea
                  value={commentContent}
                  onChange={(e) => setCommentContent(e.target.value)}
                  placeholder="이 커리큘럼에 대한 의견을 남겨주세요..."
                  rows={4}
                />
              </FormControl>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onCommentClose}>
                취소
              </Button>
              <Button
                colorScheme="blue"
                onClick={handleCommentSubmit}
                isLoading={submittingComment}
                isDisabled={!commentContent.trim()}
              >
                댓글 작성
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Container>
  );
};

export default Feed;
