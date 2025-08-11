// src/pages/MyComments.tsx
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
  useToast,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { commentAPI } from '../services/api';
import { CommentIcon, EyeIcon } from '../components/icons/SimpleIcons';
import { EditIcon, DeleteIcon } from '@chakra-ui/icons';

interface MyComment {
  id: string;
  curriculum_id: string;
  user_id: string;
  content?: string;
  content_snippet?: string;
  content_length: number;
  created_at: string;
  updated_at?: string;
  // 확장된 커리큘럼 정보 (실제 API 응답에 따라 조정 필요)
  curriculum_title?: string;
  curriculum_owner_name?: string;
}

const MyComments: React.FC = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [comments, setComments] = useState<MyComment[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  
  // 수정 모달 관련
  const [editingComment, setEditingComment] = useState<MyComment | null>(null);
  const [editContent, setEditContent] = useState('');
  const { isOpen: isEditModalOpen, onOpen: onEditModalOpen, onClose: onEditModalClose } = useDisclosure();

  const textColor = useColorModeValue('gray.900', 'white');
  const secondaryTextColor = useColorModeValue('gray.600', 'gray.300');
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const commentBg = useColorModeValue('gray.50', 'gray.600');

  useEffect(() => {
    fetchMyComments();
  }, []);

  useEffect(() => {
    if (page > 1) {
      fetchMyComments(false);
    }
  }, [page]);

  const fetchMyComments = async (reset = true) => {
      try {
        if (reset) {
          setLoading(true);
          setPage(1);
        }

        const response = await commentAPI.getMyComments({
          page: reset ? 1 : page,
          items_per_page: 20,
        });

        const newComments = response.data.comments || [];

        if (reset) {
          setComments(newComments);
        } else {
          setComments(prev => [...prev, ...newComments]);
        }

        setTotalCount(response.data.total_count);
        setHasMore((reset ? 1 : page) * 20 < response.data.total_count);
        setError('');
      } catch (error: any) {
        console.error('내 댓글 조회 실패:', error);
        
        if (error.response?.status === 404) {
          // 404인 경우 백엔드에서 아직 구현되지 않은 상태
          setError('댓글 기능이 아직 준비되지 않았습니다.');
          setComments([]); // 빈 배열로 설정
          setTotalCount(0);
          setHasMore(false);
        } else {
          setError('댓글을 불러오는데 실패했습니다.');
        }
      } finally {
        setLoading(false);
      }
    };

  const handleEditComment = (comment: MyComment) => {
    setEditingComment(comment);
    setEditContent(comment.content || comment.content_snippet || '');
    onEditModalOpen();
  };

  const handleUpdateComment = async () => {
    if (!editingComment || !editContent.trim()) {
      toast({
        title: '댓글 내용을 입력해주세요',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    try {
      setUpdating(true);
      await commentAPI.updateComment(editingComment.id, {
        content: editContent.trim()
      });
      
      toast({
        title: '댓글이 수정되었습니다',
        status: 'success',
        duration: 3000,
      });
      
      onEditModalClose();
      fetchMyComments();
    } catch (error: any) {
      console.error('댓글 수정 실패:', error);
      toast({
        title: '댓글 수정에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setUpdating(false);
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    if (!window.confirm('정말로 이 댓글을 삭제하시겠습니까?')) {
      return;
    }

    try {
      await commentAPI.deleteComment(commentId);
      
      toast({
        title: '댓글이 삭제되었습니다',
        status: 'success',
        duration: 3000,
      });
      
      setComments(prev => prev.filter(c => c.id !== commentId));
      setTotalCount(prev => prev - 1);
    } catch (error: any) {
      console.error('댓글 삭제 실패:', error);
      toast({
        title: '댓글 삭제에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
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
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading && comments.length === 0) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text color={textColor}>댓글을 불러오는 중...</Text>
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
            <Heading size="lg" color={textColor}>내가 작성한 댓글</Heading>
            <Text fontSize="sm" color={secondaryTextColor}>
              작성한 댓글 {totalCount}개
            </Text>
          </VStack>
          <Button
            colorScheme="blue"
            onClick={() => navigate('/feed')}
            leftIcon={<CommentIcon />}
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

        {/* 댓글 목록 */}
        {comments.length === 0 && !loading ? (
          <Box textAlign="center" py={10}>
            <Box mb={4} display="flex" justifyContent="center">
              <CommentIcon size="48px" />
            </Box>
            <Text fontSize="lg" color={secondaryTextColor} mb={4}>
              아직 작성한 댓글이 없습니다
            </Text>
            <Text color={secondaryTextColor} mb={6}>
              커리큘럼에 댓글을 남겨보세요!
            </Text>
            <Button colorScheme="blue" onClick={() => navigate('/feed')}>
              커뮤니티 피드 둘러보기
            </Button>
          </Box>
        ) : (
          <VStack spacing={4} align="stretch">
            {comments.map((comment) => (
              <Card
                key={comment.id}
                bg={cardBg}
                borderColor={borderColor}
                _hover={{ shadow: 'md', transform: 'translateY(-1px)' }}
                transition="all 0.2s"
              >
                <CardBody>
                  <VStack align="stretch" spacing={4}>
                    {/* 헤더 - 커리큘럼 정보 */}
                    <HStack justify="space-between" align="start">
                      <VStack align="start" spacing={1}>
                        <Text fontSize="sm" color="blue.500" fontWeight="semibold">
                          {comment.curriculum_title || `커리큘럼 ${comment.curriculum_id.slice(0, 8)}`}
                        </Text>
                        <Text fontSize="xs" color={secondaryTextColor}>
                          {comment.curriculum_owner_name && `작성자: ${comment.curriculum_owner_name}`}
                        </Text>
                      </VStack>
                      <Badge colorScheme="blue" variant="outline">
                        댓글
                      </Badge>
                    </HStack>

                    {/* 댓글 내용 */}
                    <Box p={3} bg={commentBg} borderRadius="md" borderLeft="3px solid" borderLeftColor="blue.500">
                      <Text color={textColor} lineHeight="1.6">
                        {comment.content || comment.content_snippet}
                      </Text>
                      {comment.content_length && (
                        <Text fontSize="xs" color={secondaryTextColor} mt={2}>
                          {comment.content_length}자
                        </Text>
                      )}
                    </Box>

                    {/* 메타 정보와 액션 */}
                    <HStack justify="space-between" align="center">
                      <VStack align="start" spacing={1}>
                        <Text fontSize="xs" color={secondaryTextColor}>
                          작성일: {formatDate(comment.created_at)}
                        </Text>
                        {comment.updated_at && comment.updated_at !== comment.created_at && (
                          <Text fontSize="xs" color={secondaryTextColor}>
                            수정일: {formatDate(comment.updated_at)}
                          </Text>
                        )}
                      </VStack>

                      <HStack spacing={2}>
                        <Button
                          leftIcon={<EyeIcon />}
                          size="sm"
                          variant="ghost"
                          colorScheme="blue"
                          onClick={() => navigate(`/curriculum/${comment.curriculum_id}`)}
                        >
                          커리큘럼 보기
                        </Button>
                        <IconButton
                          aria-label="댓글 수정"
                          icon={<EditIcon />}
                          size="sm"
                          variant="ghost"
                          colorScheme="green"
                          onClick={() => handleEditComment(comment)}
                        />
                        <IconButton
                          aria-label="댓글 삭제"
                          icon={<DeleteIcon />}
                          size="sm"
                          variant="ghost"
                          colorScheme="red"
                          onClick={() => handleDeleteComment(comment.id)}
                        />
                      </HStack>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </VStack>
        )}

        {/* 더 보기 버튼 */}
        {hasMore && comments.length > 0 && (
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
        {!hasMore && comments.length > 0 && (
          <Text textAlign="center" color={secondaryTextColor} py={4}>
            모든 댓글을 확인했습니다!
          </Text>
        )}

        {/* 댓글 수정 모달 */}
        <Modal isOpen={isEditModalOpen} onClose={onEditModalClose} size="lg">
          <ModalOverlay />
          <ModalContent bg={cardBg} color={textColor}>
            <ModalHeader>댓글 수정</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4}>
                {editingComment && (
                  <Box w="100%">
                    <Text fontSize="sm" color="blue.500" fontWeight="semibold" mb={2}>
                      {editingComment.curriculum_title || `커리큘럼 ${editingComment.curriculum_id.slice(0, 8)}`}
                    </Text>
                  </Box>
                )}
                
                <FormControl isRequired>
                  <FormLabel color={textColor}>댓글 내용</FormLabel>
                  <Textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    color={textColor}
                    borderColor={borderColor}
                    rows={6}
                    placeholder="댓글 내용을 입력하세요..."
                  />
                  <Text fontSize="xs" color={secondaryTextColor} mt={1}>
                    {editContent.length}/1000자
                  </Text>
                </FormControl>
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onEditModalClose}>
                취소
              </Button>
              <Button 
                colorScheme="blue" 
                onClick={handleUpdateComment}
                isLoading={updating}
                loadingText="수정 중..."
                isDisabled={!editContent.trim() || editContent.length > 1000}
              >
                수정하기
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Container>
  );
};

export default MyComments;
