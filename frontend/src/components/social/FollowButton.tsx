// frontend/src/components/social/FollowButton.tsx
import React, { useState, useEffect } from 'react';
import {
  Button,
  useToast,
  useColorModeValue,
} from '@chakra-ui/react';
import { followAPI } from '../../services/api';
import { UsersIcon } from '../icons/SimpleIcons';

interface FollowButtonProps {
  userId: string;
  initialFollowState?: boolean;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  variant?: 'solid' | 'outline' | 'ghost';
  onFollowChange?: (isFollowing: boolean) => void;
}

const FollowButton: React.FC<FollowButtonProps> = ({ 
  userId, 
  initialFollowState = false,
  size = 'sm',
  variant = 'outline',
  onFollowChange 
}) => {
  const [isFollowing, setIsFollowing] = useState(initialFollowState);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const buttonColor = useColorModeValue('blue.500', 'blue.400');
  const followingColor = useColorModeValue('green.500', 'green.400');

  useEffect(() => {
    checkFollowStatus();
  }, [userId]);

  const checkFollowStatus = async () => {
    try {
      const response = await followAPI.getFollowStatus(userId);
      setIsFollowing(response.data.is_following);
    } catch (error) {
      console.error('팔로우 상태 확인 실패:', error);
    }
  };

  const handleFollowToggle = async () => {
    if (loading) return;

    try {
      setLoading(true);
      
      if (isFollowing) {
        await followAPI.unfollowUser(userId);
        setIsFollowing(false);
        toast({
          title: '언팔로우 완료',
          status: 'info',
          duration: 2000,
        });
      } else {
        await followAPI.followUser(userId);
        setIsFollowing(true);
        toast({
          title: '팔로우 완료',
          status: 'success',
          duration: 2000,
        });
      }
      
      onFollowChange?.(isFollowing);
    } catch (error: any) {
      console.error('팔로우 토글 실패:', error);
      
      let errorMessage = '팔로우 처리에 실패했습니다';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      toast({
        title: errorMessage,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      leftIcon={<UsersIcon />}
      size={size}
      variant={variant}
      colorScheme={isFollowing ? 'green' : 'blue'}
      color={isFollowing ? followingColor : buttonColor}
      onClick={handleFollowToggle}
      isLoading={loading}
      loadingText={isFollowing ? '언팔로우 중...' : '팔로우 중...'}
      _hover={{
        transform: 'scale(1.05)',
      }}
      transition="all 0.2s"
    >
      {isFollowing ? '팔로잉' : '팔로우'}
    </Button>
  );
};

export default FollowButton;
