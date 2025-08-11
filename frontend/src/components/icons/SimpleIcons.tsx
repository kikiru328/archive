// frontend/src/components/icons/SimpleIcons.tsx
import React from 'react';
import { 
  FaRss, 
  FaBookmark, 
  FaUsers, 
  FaHeart,
  FaRegHeart,
  FaComment,
  FaCog,
  FaTrash,
  FaEye,
  FaSync,
  FaSearch,
  FaFilter,
  FaShareAlt,
  FaRegBookmark,
  FaEdit,
} from 'react-icons/fa';

interface IconProps {
  size?: string | number;
  className?: string;
  style?: React.CSSProperties;
}

// 타입 어서션을 사용한 래퍼 컴포넌트
export const RssIcon: React.FC<IconProps> = (props) => (FaRss as any)(props);
export const BookmarkIcon: React.FC<IconProps> = (props) => (FaBookmark as any)(props);
export const BookmarkOutlineIcon: React.FC<IconProps> = (props) => (FaRegBookmark as any)(props);
export const UsersIcon: React.FC<IconProps> = (props) => (FaUsers as any)(props);
export const HeartIcon: React.FC<IconProps> = (props) => (FaHeart as any)(props);
export const HeartOutlineIcon: React.FC<IconProps> = (props) => (FaRegHeart as any)(props);
export const CommentIcon: React.FC<IconProps> = (props) => (FaComment as any)(props);
export const CogIcon: React.FC<IconProps> = (props) => (FaCog as any)(props);
export const TrashIcon: React.FC<IconProps> = (props) => (FaTrash as any)(props);
export const EyeIcon: React.FC<IconProps> = (props) => (FaEye as any)(props);
export const SyncIcon: React.FC<IconProps> = (props) => (FaSync as any)(props);
export const SearchIcon: React.FC<IconProps> = (props) => (FaSearch as any)(props);
export const FilterIcon: React.FC<IconProps> = (props) => (FaFilter as any)(props);
export const ShareIcon: React.FC<IconProps> = (props) => (FaShareAlt as any)(props);
