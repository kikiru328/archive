// src/components/social/SocialButtons.tsx - 완전히 수정된 버전
import React, { useState, useEffect } from 'react';
import {
  HStack,
  IconButton,
  Text,
  useToast,
  useColorModeValue,
  Tooltip,
  Badge,
} from '@chakra-ui/react';
import { likeAPI, bookmarkAPI, socialStatsAPI } from '../../services/api';
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

const SocialButtons: React.FC<SocialButtonsProps> = ({ 
  curriculumId, 
  onCommentClick,
  size = 'md',
  showCounts = true 
}) => {
  const [stats, setStats] = useState<SocialStats | null>(null);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const iconColor = useColorModeValue('gray.600', 'gray.400');
  const activeColor = useColorModeValue('red.500', 'red.400');
  const bookmarkColor = useColorModeValue('blue.500', 'blue.400');

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

  if (!stats) return null;

  return (
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
            onClick={onCommentClick}
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
  );
};

export default SocialButtons;
