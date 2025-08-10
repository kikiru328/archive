// src/components/icons/SimpleIcons.tsx
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
} from 'react-icons/fa';

// 타입을 강제로 캐스팅하여 컴포넌트로 사용
const IconWrapper = (IconComponent: any) => (props: any) => {
  const Component = IconComponent as React.ComponentType<any>;
  return React.createElement(Component, props);
};

export const RssIcon = IconWrapper(FaRss);
export const BookmarkIcon = IconWrapper(FaBookmark);
export const BookmarkOutlineIcon = IconWrapper(FaRegBookmark);
export const UsersIcon = IconWrapper(FaUsers);
export const HeartIcon = IconWrapper(FaHeart);
export const HeartOutlineIcon = IconWrapper(FaRegHeart);
export const CommentIcon = IconWrapper(FaComment);
export const CogIcon = IconWrapper(FaCog);
export const TrashIcon = IconWrapper(FaTrash);
export const EyeIcon = IconWrapper(FaEye);
export const SyncIcon = IconWrapper(FaSync);
export const SearchIcon = IconWrapper(FaSearch);
export const FilterIcon = IconWrapper(FaFilter);
export const ShareIcon = IconWrapper(FaShareAlt);
