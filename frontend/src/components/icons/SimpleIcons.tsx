// frontend/src/components/icons/SimpleIcons.tsx
import React from 'react';
import { IconType } from 'react-icons';
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

// 간단한 래퍼 컴포넌트
export const RssIcon: React.FC<{ size?: string | number }> = (props) => <FaRss {...props} />;
export const BookmarkIcon: React.FC<{ size?: string | number }> = (props) => <FaBookmark {...props} />;
export const BookmarkOutlineIcon: React.FC<{ size?: string | number }> = (props) => <FaRegBookmark {...props} />;
export const UsersIcon: React.FC<{ size?: string | number }> = (props) => <FaUsers {...props} />;
export const HeartIcon: React.FC<{ size?: string | number }> = (props) => <FaHeart {...props} />;
export const HeartOutlineIcon: React.FC<{ size?: string | number }> = (props) => <FaRegHeart {...props} />;
export const CommentIcon: React.FC<{ size?: string | number }> = (props) => <FaComment {...props} />;
export const CogIcon: React.FC<{ size?: string | number }> = (props) => <FaCog {...props} />;
export const TrashIcon: React.FC<{ size?: string | number }> = (props) => <FaTrash {...props} />;
export const EyeIcon: React.FC<{ size?: string | number }> = (props) => <FaEye {...props} />;
export const SyncIcon: React.FC<{ size?: string | number }> = (props) => <FaSync {...props} />;
export const SearchIcon: React.FC<{ size?: string | number }> = (props) => <FaSearch {...props} />;
export const FilterIcon: React.FC<{ size?: string | number }> = (props) => <FaFilter {...props} />;
export const ShareIcon: React.FC<{ size?: string | number }> = (props) => <FaShareAlt {...props} />;
