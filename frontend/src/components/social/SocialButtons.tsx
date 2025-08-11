// src/components/social/SocialButtons.tsx - 댓글 조회 기능 추가
import React, { useState, useEffect } from 'react';
import {
  HStack,
  IconButton,
  Text,
  useToast,
  useColorModeValue,
  Tooltip,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  VStack,
  Box,
  Avatar,
  Divider,
  Button,
  Textarea,
  FormControl,
  FormLabel,
  Spinner,
} from '@chakra-ui/react';
import { likeAPI, bookmarkAPI, socialStatsAPI, commentAPI } from '../../services/api';
import { 
  HeartIcon, 
  HeartOutlineIcon, 
  CommentIcon, 
  BookmarkIcon, 
  BookmarkOutlineIcon,
  ShareIcon,
} from '../icons/SimpleIcons';

interface SocialButtonsProps {
  curriculumId: string;
  onCommentClick?: () => void;
  size?: 'sm' | 'md' | 'lg';
  showCounts?: boolean;
}

interface SocialStats {
  like_count: number;
  comment_count: number;
  is_liked_by_user: boolean;
  is_bookmarked_by_user: boolean;
}

interface Comment {
  id: string;
  curriculum_id: string;
  user_id: string;
  user_name?: string;       // 백엔드에서 제공되지 않음
  username?: string;        // 백엔드에서 제공되지 않음  
  content?: string;         // 전체 내용 (상세 조회시)
  content_snippet?: string; // 요약된 내용 (목록 조회시)
  content_length: number;   // 내용 길이
  created_at: string;
  updated_at?: string;
}

const SocialButtons: React.FC<SocialButtonsProps> = ({ 
  curriculumId, 
  onCommentClick,
  size = 'md',
  showCounts = true 
}) => {
  const [stats, setStats] = useState<SocialStats | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingComments, setLoadingComments] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);
  const toast = useToast();

  const { isOpen: isCommentsOpen, onOpen: onCommentsOpen, onClose: onCommentsClose } = useDisclosure();

  const iconColor = useColorModeValue('gray.600', 'gray.400');
  const activeColor = useColorModeValue('red.500', 'red.400');
  const bookmarkColor = useColorModeValue('blue.500', 'blue.400');
  const cardBg = useColorModeValue('white', 'gray.700');
  const textColor = useColorModeValue('gray.900', 'white');
  const secondaryTextColor = useColorModeValue('gray.600', 'gray.300');
  const commentBoxBg = useColorModeValue('gray.50', 'gray.600');
  const commentWriteBg = useColorModeValue('blue.50', 'blue.900');
  const commentEmptyBg = useColorModeValue('gray.50', 'gray.800');
  const commentBorderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    fetchSocialStats();
  }, [curriculumId]);

  const fetchSocialStats = async () => {
    try {
      const response = await socialStatsAPI.getCurriculumSocialStats(curriculumId);
      setStats(response.data);
    } catch (error) {
      console.error('소셜 통계 조회 실패:', error);
    }
  };

  const fetchComments = async () => {
    try {
      setLoadingComments(true);
      console.log('댓글 조회 요청:', curriculumId);
      const response = await commentAPI.getCommentsByCurriculum(curriculumId);
      console.log('댓글 API 응답:', response.data);
      
      const commentsData = response.data.comments || response.data || [];
      console.log('댓글 데이터:', commentsData);
      console.log('댓글 개수:', commentsData.length);
      
      // 첫 번째 댓글의 구조 확인
      if (commentsData.length > 0) {
        console.log('첫 번째 댓글 구조:', commentsData[0]);
        console.log('첫 번째 댓글의 모든 키:', Object.keys(commentsData[0]));
      }
      
      setComments(commentsData);
    } catch (error) {
      console.error('댓글 조회 실패:', error);
      // 에러가 발생해도 빈 배열로 설정하여 모달이 정상 작동하도록 함
      setComments([]);
      toast({
        title: '댓글을 불러올 수 없습니다',
        description: '새 댓글은 작성할 수 있습니다',
        status: 'warning',
        duration: 3000,
      });
    } finally {
      setLoadingComments(false);
    }
  };

  const handleLike = async () => {
    if (loading || !stats) return;

    try {
      setLoading(true);
      
      if (stats.is_liked_by_user) {
        await likeAPI.deleteLike(curriculumId);
        setStats(prev => prev ? {
          ...prev,
          is_liked_by_user: false,
          like_count: prev.like_count - 1
        } : null);
        toast({
          title: '좋아요를 취소했습니다',
          status: 'info',
          duration: 2000,
        });
      } else {
        await likeAPI.createLike(curriculumId);
        setStats(prev => prev ? {
          ...prev,
          is_liked_by_user: true,
          like_count: prev.like_count + 1
        } : null);
        toast({
          title: '좋아요를 눌렀습니다',
          status: 'success',
          duration: 2000,
        });
      }
    } catch (error: any) {
      console.error('좋아요 처리 실패:', error);
      toast({
        title: '좋아요 처리에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleBookmark = async () => {
    if (loading || !stats) return;

    try {
      setLoading(true);
      
      if (stats.is_bookmarked_by_user) {
        await bookmarkAPI.deleteBookmark(curriculumId);
        setStats(prev => prev ? {
          ...prev,
          is_bookmarked_by_user: false
        } : null);
        toast({
          title: '북마크를 해제했습니다',
          status: 'info',
          duration: 2000,
        });
      } else {
        await bookmarkAPI.createBookmark(curriculumId);
        setStats(prev => prev ? {
          ...prev,
          is_bookmarked_by_user: true
        } : null);
        toast({
          title: '북마크에 추가했습니다',
          status: 'success',
          duration: 2000,
        });
      }
    } catch (error: any) {
      console.error('북마크 처리 실패:', error);
      toast({
        title: '북마크 처리에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleShare = async () => {
    const url = `${window.location.origin}/curriculum/${curriculumId}`;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: '커리큘럼 공유',
          url: url,
        });
      } catch (error) {
        // 사용자가 공유를 취소한 경우 무시
      }
    } else {
      // Web Share API가 지원되지 않는 경우 클립보드에 복사
      try {
        await navigator.clipboard.writeText(url);
        toast({
          title: '링크가 클립보드에 복사되었습니다',
          status: 'success',
          duration: 2000,
        });
      } catch (error) {
        toast({
          title: '링크 복사에 실패했습니다',
          status: 'error',
          duration: 3000,
        });
      }
    }
  };

  const handleCommentClick = () => {
    if (onCommentClick) {
      onCommentClick();
    } else {
      // 내장 댓글 모달 열기
      onCommentsOpen();
      fetchComments();
    }
  };

  const handleSubmitComment = async () => {
    if (!newComment.trim()) return;

    try {
      setSubmittingComment(true);
      await commentAPI.createComment(curriculumId, {
        content: newComment.trim()
      });
      
      setNewComment('');
      toast({
        title: '댓글이 작성되었습니다',
        status: 'success',
        duration: 2000,
      });
      
      // 댓글 목록과 통계 새로고침
      await fetchComments();
      await fetchSocialStats();
    } catch (error: any) {
      console.error('댓글 작성 실패:', error);
      toast({
        title: '댓글 작성에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setSubmittingComment(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!stats) {
    // stats가 없을 때 기본값으로 렌더링
    return (
      <HStack spacing={4}>
        <HStack spacing={1}>
          <IconButton
            aria-label="좋아요"
            icon={<HeartOutlineIcon />}
            color={iconColor}
            variant="ghost"
            size={size}
            isDisabled
          />
          {showCounts && <Text fontSize="sm" color={iconColor}>0</Text>}
        </HStack>

        <HStack spacing={1}>
          <IconButton
            aria-label="댓글"
            icon={<CommentIcon />}
            color={iconColor}
            variant="ghost"
            size={size}
            onClick={handleCommentClick}
            _hover={{
              color: 'blue.500',
              transform: 'scale(1.1)',
            }}
            transition="all 0.2s"
          />
          {showCounts && <Text fontSize="sm" color={iconColor}>0</Text>}
        </HStack>

        <IconButton
          aria-label="북마크"
          icon={<BookmarkOutlineIcon />}
          color={iconColor}
          variant="ghost"
          size={size}
          isDisabled
        />

        <IconButton
          aria-label="공유"
          icon={<ShareIcon />}
          color={iconColor}
          variant="ghost"
          size={size}
          onClick={handleShare}
        />
      </HStack>
    );
  }

  return (
    <>
      <HStack spacing={4}>
        {/* 좋아요 버튼 */}
        <HStack spacing={1}>
          <Tooltip label={stats.is_liked_by_user ? '좋아요 취소' : '좋아요'}>
            <IconButton
              aria-label="좋아요"
              icon={stats.is_liked_by_user ? <HeartIcon /> : <HeartOutlineIcon />}
              color={stats.is_liked_by_user ? activeColor : iconColor}
              variant="ghost"
              size={size}
              isLoading={loading}
              onClick={handleLike}
              _hover={{
                color: activeColor,
                transform: 'scale(1.1)',
              }}
              transition="all 0.2s"
            />
          </Tooltip>
          {showCounts && (
            <Text fontSize="sm" color={iconColor}>
              {stats.like_count}
            </Text>
          )}
        </HStack>

        {/* 댓글 버튼 */}
        <HStack spacing={1}>
          <Tooltip label="댓글">
            <IconButton
              aria-label="댓글"
              icon={<CommentIcon />}
              color={iconColor}
              variant="ghost"
              size={size}
              onClick={handleCommentClick}
              _hover={{
                color: 'blue.500',
                transform: 'scale(1.1)',
              }}
              transition="all 0.2s"
            />
          </Tooltip>
          {showCounts && (
            <Text fontSize="sm" color={iconColor}>
              {stats.comment_count}
            </Text>
          )}
        </HStack>

        {/* 북마크 버튼 */}
        <Tooltip label={stats.is_bookmarked_by_user ? '북마크 해제' : '북마크'}>
          <IconButton
            aria-label="북마크"
            icon={stats.is_bookmarked_by_user ? <BookmarkIcon /> : <BookmarkOutlineIcon />}
            color={stats.is_bookmarked_by_user ? bookmarkColor : iconColor}
            variant="ghost"
            size={size}
            isLoading={loading}
            onClick={handleBookmark}
            _hover={{
              color: bookmarkColor,
              transform: 'scale(1.1)',
            }}
            transition="all 0.2s"
          />
        </Tooltip>

        {/* 공유 버튼 */}
        <Tooltip label="공유">
          <IconButton
            aria-label="공유"
            icon={<ShareIcon />}
            color={iconColor}
            variant="ghost"
            size={size}
            onClick={handleShare}
            _hover={{
              color: 'green.500',
              transform: 'scale(1.1)',
            }}
            transition="all 0.2s"
          />
        </Tooltip>
      </HStack>

      {/* 댓글 모달 */}
      <Modal isOpen={isCommentsOpen} onClose={onCommentsClose} size="lg">
        <ModalOverlay />
        <ModalContent bg={cardBg} color={textColor}>
          <ModalHeader>댓글 ({stats.comment_count})</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4} align="stretch">
              {/* 새 댓글 작성 - 더 눈에 띄게 개선 */}
              <Box p={4} bg={commentWriteBg} borderRadius="md" borderWidth="1px" borderColor="blue.200">
                <VStack spacing={3} align="stretch">
                  <Text fontWeight="semibold" color="blue.600">
                    💬 새 댓글 작성하기
                  </Text>
                  <FormControl>
                    <Textarea
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      placeholder="이 커리큘럼에 대한 의견을 남겨주세요..."
                      rows={4}
                      resize="vertical"
                      focusBorderColor="blue.400"
                    />
                    <Text fontSize="xs" color={secondaryTextColor} mt={1}>
                      {newComment.length}/1000자
                    </Text>
                  </FormControl>
                  <HStack justify="space-between">
                    <Text fontSize="sm" color={secondaryTextColor}>
                      💡 건설적인 댓글을 남겨주세요
                    </Text>
                    <Button
                      colorScheme="blue"
                      size="sm"
                      onClick={handleSubmitComment}
                      isLoading={submittingComment}
                      isDisabled={!newComment.trim() || newComment.length > 1000}
                      leftIcon={<Text>✍️</Text>}
                    >
                      댓글 작성
                    </Button>
                  </HStack>
                </VStack>
              </Box>

              <Divider />

              {/* 댓글 목록 */}
              <VStack spacing={2} align="stretch">
                <Text fontWeight="semibold" color={textColor}>
                  댓글 목록 ({stats.comment_count})
                </Text>
                {loadingComments ? (
                  <VStack py={6}>
                    <Spinner color="blue.500" />
                    <Text color={secondaryTextColor}>댓글을 불러오는 중...</Text>
                  </VStack>
                ) : comments.length === 0 ? (
                  <Box textAlign="center" py={8} bg={commentEmptyBg} borderRadius="md">
                    <Text color={secondaryTextColor} mb={2}>
                      🤔 아직 댓글이 없습니다
                    </Text>
                    <Text fontSize="sm" color={secondaryTextColor}>
                      첫 번째 댓글을 남겨보세요!
                    </Text>
                  </Box>
                ) : (
                  <VStack spacing={3} align="stretch" maxH="400px" overflowY="auto">
                    {comments.map((comment, index) => {
                      console.log(`댓글 ${index + 1}:`, comment);
                      
                      // 사용자 이름 결정 (현재 백엔드에서 제공하지 않으므로 user_id 사용)
                      const displayName = comment.username || 
                                         comment.user_name || 
                                         `사용자${comment.user_id?.slice(-4) || index}`;
                      
                      return (
                        <Box key={comment.id || index} p={3} borderRadius="md" bg={commentBoxBg} 
                             borderWidth="1px" borderColor={commentBorderColor}>
                          <HStack spacing={3} align="start">
                            <Avatar name={displayName} size="sm" />
                            <VStack align="start" spacing={1} flex={1}>
                              <HStack justify="space-between" w="100%">
                                <Text fontWeight="semibold" fontSize="sm" color={textColor}>
                                  {displayName}
                                </Text>
                                <Text fontSize="xs" color={secondaryTextColor}>
                                  {comment.created_at ? formatDate(comment.created_at) : '방금 전'}
                                </Text>
                              </HStack>
                              <Text fontSize="sm" lineHeight="1.5" color={textColor}>
                                {comment.content || comment.content_snippet || '내용이 없습니다'}
                              </Text>
                            </VStack>
                          </HStack>
                        </Box>
                      );
                    })}
                  </VStack>
                )}
              </VStack>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button onClick={onCommentsClose}>닫기</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default SocialButtons;
