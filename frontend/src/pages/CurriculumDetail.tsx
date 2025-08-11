import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  VStack,
  HStack,
  Heading,
  Container,
  Text,
  Card,
  CardBody,
  Badge,
  IconButton,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  useColorModeValue,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Progress,
  Divider,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Input,
  Textarea,
  FormControl,
  FormLabel,
} from '@chakra-ui/react';
import { 
  ArrowBackIcon, 
  EditIcon, 
  DeleteIcon, 
  AddIcon,
  CheckIcon,
  TimeIcon 
} from '@chakra-ui/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { curriculumAPI, curriculumTagAPI, tagAPI, summaryAPI, feedbackAPI } from '../services/api';
import { getCurrentUserId } from '../utils/auth';

interface WeekSchedule {
  week_number: number;
  title: string; 
  lessons: string[];
}

interface CurriculumDetail {
  id: string;
  owner_id: string;
  title: string;
  visibility: 'PUBLIC' | 'PRIVATE';
  created_at: string;
  updated_at: string;
  week_schedules: WeekSchedule[];
  category?: Category;
  tags?: Tag[];
}

interface LessonForm {
  lesson: string;
  lesson_index?: number;
}

interface WeekForm {
  week_number: number;
  title: string; 
  lessons: string[];
}

interface Tag {
  id: string;
  name: string;
  usage_count: number;
  is_popular: boolean;
}

interface Category {
  id: string;
  name: string;
  color: string;
  icon?: string;
  is_active: boolean;
  usage_count: number;
}
interface WeekProgress {
  week_number: number;
  has_summary: boolean;
  has_feedback: boolean;
  is_completed: boolean; // 요약과 피드백 모두 완료
}

interface CurriculumProgress {
  total_weeks: number;
  completed_weeks: number;
  completion_percentage: number;
  week_progress: WeekProgress[];
}

const CurriculumDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const currentUserId = getCurrentUserId();
  
  // State 선언
  const [curriculum, setCurriculum] = useState<CurriculumDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingWeek, setEditingWeek] = useState<number | null>(null);
  const [editingLessonWeek, setEditingLessonWeek] = useState<number | null>(null);
  const [editingLessonIndex, setEditingLessonIndex] = useState<number | null>(null);
  const [lessonForm, setLessonForm] = useState<LessonForm>({ lesson: '' });
  const [weekForm, setWeekForm] = useState<WeekForm>({ week_number: 1, title: '', lessons: [''] });
  const [editForm, setEditForm] = useState({ title: '', visibility: 'PRIVATE' as 'PUBLIC' | 'PRIVATE' });
  const [tags, setTags] = useState<Tag[]>([]);
  const [category, setCategory] = useState<Category | null>(null);
  const [newTag, setNewTag] = useState('');
  const [tagSuggestions, setTagSuggestions] = useState<Tag[]>([]);
  const [loadingTags, setLoadingTags] = useState(false);
  const [curriculumProgress, setCurriculumProgress] = useState<CurriculumProgress | null>(null);
  const [loadingProgress, setLoadingProgress] = useState(false);

  // 계산된 값들 (state 선언 후에)
  const isOwner = curriculum && currentUserId && curriculum.owner_id === currentUserId;

  // 모달 상태들
  const { isOpen: isLessonModalOpen, onOpen: onLessonModalOpen, onClose: onLessonModalClose } = useDisclosure();
  const { isOpen: isDeleteModalOpen, onOpen: onDeleteModalOpen, onClose: onDeleteModalClose } = useDisclosure();
  const { isOpen: isEditModalOpen, onOpen: onEditModalOpen, onClose: onEditModalClose } = useDisclosure();
  const { isOpen: isWeekModalOpen, onOpen: onWeekModalOpen, onClose: onWeekModalClose } = useDisclosure();
  const { isOpen: isEditLessonModalOpen, onOpen: onEditLessonModalOpen, onClose: onEditLessonModalClose } = useDisclosure();
  const { isOpen: isDeleteWeekModalOpen, onOpen: onDeleteWeekModalOpen, onClose: onDeleteWeekModalClose } = useDisclosure();
  // const { isOpen: isTagModalOpen, onOpen: onTagModalOpen, onClose: onTagModalClose } = useDisclosure();

  // 다크모드 대응 색상
  const bgColor = useColorModeValue('white', 'gray.800');
  const textColor = useColorModeValue('gray.900', 'white');
  const secondaryTextColor = useColorModeValue('gray.600', 'gray.300');
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const hoverBg = useColorModeValue('gray.50', 'gray.600');
  useEffect(() => {
    if (id) {
      fetchCurriculumDetail();
      fetchCurriculumProgress();
    }
  }, [id]);
  const fetchCurriculumProgress = async () => {
    if (!curriculum) return;

    try {
      setLoadingProgress(true);
      
      // 각 주차별로 요약과 피드백 상태 확인
      const weekProgressPromises = curriculum.week_schedules.map(async (week) => {
        try {
          // 해당 주차의 요약 조회
          const summaryResponse = await summaryAPI.getByWeek(curriculum.id, week.week_number);
          const summaries = summaryResponse.data.summaries || [];
          const hasSummary = summaries.length > 0;
          
          // 요약이 있다면 피드백 확인
          let hasFeedback = false;
          if (hasSummary && summaries[0]) {
            try {
              await feedbackAPI.getBySummary(summaries[0].id);
              hasFeedback = true;
            } catch (error) {
              // 피드백이 없는 경우
              hasFeedback = false;
            }
          }

          return {
            week_number: week.week_number,
            has_summary: hasSummary,
            has_feedback: hasFeedback,
            is_completed: hasSummary && hasFeedback, // 요약과 피드백 모두 완료
          };
        } catch (error) {
          console.error(`주차 ${week.week_number} 진행률 조회 실패:`, error);
          return {
            week_number: week.week_number,
            has_summary: false,
            has_feedback: false,
            is_completed: false,
          };
        }
      });

      const weekProgressResults = await Promise.all(weekProgressPromises);
      const completedWeeks = weekProgressResults.filter(week => week.is_completed).length;
      const totalWeeks = curriculum.week_schedules.length;
      const completionPercentage = totalWeeks > 0 ? Math.round((completedWeeks / totalWeeks) * 100) : 0;

      setCurriculumProgress({
        total_weeks: totalWeeks,
        completed_weeks: completedWeeks,
        completion_percentage: completionPercentage,
        week_progress: weekProgressResults,
      });

    } catch (error) {
      console.error('커리큘럼 진행률 계산 실패:', error);
    } finally {
      setLoadingProgress(false);
    }
  };

  const getWeekProgress = (weekNumber: number): WeekProgress | null => {
    return curriculumProgress?.week_progress.find(wp => wp.week_number === weekNumber) || null;
  };

  const renderWeekProgress = (week: WeekSchedule) => {
    const progress = getWeekProgress(week.week_number);
    
    if (!progress) {
      return (
        <Badge colorScheme="gray" variant="outline" size="sm">
          미시작
        </Badge>
      );
    }

    if (progress.is_completed) {
      return (
        <Badge colorScheme="green" variant="solid" size="sm">
          <CheckIcon mr={1} />
          완료
        </Badge>
      );
    }

    if (progress.has_summary && !progress.has_feedback) {
      return (
        <Badge colorScheme="yellow" variant="solid" size="sm">
          <TimeIcon mr={1} />
          피드백 대기
        </Badge>
      );
    }

    return (
      <Badge colorScheme="blue" variant="outline" size="sm">
        진행 중
      </Badge>
    );
  };

  // 진행률 표시 컴포넌트
  const renderProgressSection = () => {
    console.log('renderProgressSection 호출, curriculumProgress:', curriculumProgress);
    console.log('loadingProgress:', loadingProgress);
    
    if (loadingProgress) {
      return (
        <VStack align="start" flex={1} spacing={1}>
          <Text fontSize="sm" color={secondaryTextColor}>진행률</Text>
          <HStack>
            <Spinner size="sm" color="blue.500" />
            <Text fontSize="sm" color={secondaryTextColor}>계산 중...</Text>
          </HStack>
        </VStack>
      );
    }

    if (!curriculumProgress) {
      console.log('curriculumProgress가 null임');
      return (
        <VStack align="start" flex={1} spacing={1}>
          <Text fontSize="sm" color={secondaryTextColor}>진행률</Text>
          <Text fontSize="sm" color={secondaryTextColor}>0/0주차 완료</Text>
          <Progress 
            value={0} 
            size="md" 
            colorScheme="blue" 
            w="200px"
          />
          <Text fontSize="xs" color={secondaryTextColor}>0% 완료</Text>
        </VStack>
      );
    }

    return (
      <VStack align="start" flex={1} spacing={1}>
        <HStack justify="space-between" w="100%">
          <Text fontSize="sm" color={secondaryTextColor}>진행률</Text>
          <Text fontSize="sm" color={secondaryTextColor}>
            {curriculumProgress.completed_weeks}/{curriculumProgress.total_weeks}주차 완료
          </Text>
        </HStack>
        <Progress 
          value={curriculumProgress.completion_percentage} 
          size="md" 
          colorScheme="blue" 
          w="200px"
        />
        <Text fontSize="xs" color={secondaryTextColor}>
          {curriculumProgress.completion_percentage}% 완료
        </Text>
      </VStack>
    );
  };

  const fetchTagsAndCategory = async (curriculumId: string) => {
    try {
      const response = await curriculumTagAPI.getTagsAndCategory(curriculumId);
      setTags(response.data.tags || []);
      setCategory(response.data.category || null);
    } catch (error) {
      console.log('태그/카테고리 정보 없음:', error);
    }
  };

 const fetchCurriculumDetail = async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      setError('');
      
      const curriculumResponse = await curriculumAPI.getById(id);
      const curriculumData = curriculumResponse.data;
      setCurriculum(curriculumData);
      
      // 태그와 카테고리 정보 가져오기
      await fetchTagsAndCategory(id);
      
      // ✅ 중요: 커리큘럼 데이터를 설정한 후 진행률 계산
      console.log('커리큘럼 데이터 로드 완료, 진행률 계산 시작...');
      await calculateProgress(curriculumData); // 직접 데이터 전달
      
    } catch (error: any) {
      console.error('커리큘럼 상세 조회 실패:', error);
      setError('커리큘럼을 불러오는데 실패했습니다.');
      
      if (error.response?.status === 404) {
        toast({
          title: '커리큘럼을 찾을 수 없습니다',
          status: 'error',
          duration: 3000,
        });
        navigate('/curriculum');
      }
    } finally {
      setLoading(false);
    }
  };

  const calculateProgress = async (curriculumData: CurriculumDetail) => {
    console.log('calculateProgress 시작, 커리큘럼:', curriculumData.title);
    
    if (!curriculumData.week_schedules || curriculumData.week_schedules.length === 0) {
      console.log('주차 스케줄이 없음');
      setCurriculumProgress({
        total_weeks: 0,
        completed_weeks: 0,
        completion_percentage: 0,
        week_progress: [],
      });
      return;
    }

    try {
      setLoadingProgress(true);
      console.log('주차별 진행률 계산 시작...');
      
      // 각 주차별로 요약과 피드백 상태 확인
      const weekProgressPromises = curriculumData.week_schedules.map(async (week) => {
        console.log(`${week.week_number}주차 진행률 확인 중...`);
        
        try {
          // 해당 주차의 요약 조회
          const summaryResponse = await summaryAPI.getByWeek(curriculumData.id, week.week_number);
          const summaries = summaryResponse.data.summaries || [];
          const hasSummary = summaries.length > 0;
          
          console.log(`${week.week_number}주차 - 요약: ${hasSummary ? '있음' : '없음'}`);
          
          // 요약이 있다면 피드백 확인
          let hasFeedback = false;
          if (hasSummary && summaries[0]) {
            try {
              await feedbackAPI.getBySummary(summaries[0].id);
              hasFeedback = true;
              console.log(`${week.week_number}주차 - 피드백: 있음`);
            } catch (error) {
              hasFeedback = false;
              console.log(`${week.week_number}주차 - 피드백: 없음`);
            }
          }

          const isCompleted = hasSummary && hasFeedback;
          console.log(`${week.week_number}주차 - 완료 여부: ${isCompleted}`);

          return {
            week_number: week.week_number,
            has_summary: hasSummary,
            has_feedback: hasFeedback,
            is_completed: isCompleted,
          };
        } catch (error) {
          console.error(`주차 ${week.week_number} 진행률 조회 실패:`, error);
          return {
            week_number: week.week_number,
            has_summary: false,
            has_feedback: false,
            is_completed: false,
          };
        }
      });

      const weekProgressResults = await Promise.all(weekProgressPromises);
      const completedWeeks = weekProgressResults.filter(week => week.is_completed).length;
      const totalWeeks = curriculumData.week_schedules.length;
      const completionPercentage = totalWeeks > 0 ? Math.round((completedWeeks / totalWeeks) * 100) : 0;

      console.log('진행률 계산 완료:', {
        completedWeeks,
        totalWeeks,
        completionPercentage,
        weekProgress: weekProgressResults
      });

      setCurriculumProgress({
        total_weeks: totalWeeks,
        completed_weeks: completedWeeks,
        completion_percentage: completionPercentage,
        week_progress: weekProgressResults,
      });

    } catch (error) {
      console.error('커리큘럼 진행률 계산 실패:', error);
      // 에러가 발생해도 기본값 설정
      setCurriculumProgress({
        total_weeks: curriculumData.week_schedules.length,
        completed_weeks: 0,
        completion_percentage: 0,
        week_progress: curriculumData.week_schedules.map(week => ({
          week_number: week.week_number,
          has_summary: false,
          has_feedback: false,
          is_completed: false,
        })),
      });
    } finally {
      setLoadingProgress(false);
    }
  };




  const handleTagSearch = async (query: string) => {
    if (query.length < 1) {
      setTagSuggestions([]);
      return;
    }

    try {
      const response = await tagAPI.searchTags({ q: query, limit: 5 });
      setTagSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('태그 검색 실패:', error);
    }
  };

  const handleAddTag = async (tagName: string) => {
    if (!curriculum || !tagName.trim()) return;

    try {
      setLoadingTags(true);
      await curriculumTagAPI.addTags(curriculum.id, [tagName.trim()]);
      
      toast({
        title: '태그가 추가되었습니다',
        status: 'success',
        duration: 3000,
      });
      
      setNewTag('');
      setTagSuggestions([]);
      await fetchTagsAndCategory(curriculum.id);
    } catch (error: any) {
      console.error('태그 추가 실패:', error);
      toast({
        title: '태그 추가에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoadingTags(false);
    }
  };

  // 태그 제거
  const handleRemoveTag = async (tagName: string) => {
    if (!curriculum) return;

    try {
      await curriculumTagAPI.removeTag(curriculum.id, tagName);
      
      toast({
        title: '태그가 제거되었습니다',
        status: 'success',
        duration: 3000,
      });
      
      await fetchTagsAndCategory(curriculum.id);
    } catch (error: any) {
      console.error('태그 제거 실패:', error);
      toast({
        title: '태그 제거에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleDeleteCurriculum = async () => {
    if (!curriculum) return;

    try {
      await curriculumAPI.delete(curriculum.id);
      
      toast({
        title: '커리큘럼이 삭제되었습니다',
        status: 'success',
        duration: 3000,
      });
      
      navigate('/curriculum');
    } catch (error: any) {
      console.error('커리큘럼 삭제 실패:', error);
      toast({
        title: '커리큘럼 삭제에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleEditCurriculum = async () => {
    if (!curriculum || !editForm.title.trim()) {
      toast({
        title: '제목을 입력해주세요',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    try {
      await curriculumAPI.update(curriculum.id, {
        title: editForm.title.trim(),
        visibility: editForm.visibility
      });
      
      toast({
        title: '커리큘럼이 수정되었습니다',
        status: 'success',
        duration: 3000,
      });
      
      onEditModalClose();
      fetchCurriculumDetail();
    } catch (error: any) {
      console.error('커리큘럼 수정 실패:', error);
      toast({
        title: '커리큘럼 수정에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const openEditModal = () => {
    if (curriculum) {
      setEditForm({
        title: curriculum.title,
        visibility: curriculum.visibility
      });
      onEditModalOpen();
    }
  };

  const handleAddWeek = () => {
    const nextWeekNumber = curriculum ? Math.max(...curriculum.week_schedules.map(w => w.week_number)) + 1 : 1;
    setWeekForm({ 
      week_number: nextWeekNumber, 
      title: '',  // 추가
      lessons: [''] 
    });
    onWeekModalOpen();
  };

  const handleSaveWeek = async () => {
    if (!curriculum || weekForm.lessons.filter(l => l.trim()).length === 0) {
      toast({
        title: '최소 1개의 레슨을 입력해주세요',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    try {
      const validLessons = weekForm.lessons.filter(lesson => lesson.trim());
      await curriculumAPI.addWeek(curriculum.id, {
        week_number: weekForm.week_number,
        title: weekForm.title,
        lessons: validLessons
      });
      
      toast({
        title: '주차가 추가되었습니다',
        status: 'success',
        duration: 3000,
      });
      
      onWeekModalClose();
      fetchCurriculumDetail();
    } catch (error: any) {
      console.error('주차 추가 실패:', error);
      toast({
        title: '주차 추가에 실패했습니다',
        description: error.response?.data?.detail || '다시 시도해주세요',
        status: 'error',
        duration: 5000,
      });
    }
  };

  const handleDeleteWeek = async (weekNumber: number) => {
    if (!curriculum) return;

    try {
      await curriculumAPI.deleteWeek(curriculum.id, weekNumber);
      
      toast({
        title: '주차가 삭제되었습니다',
        status: 'success',
        duration: 3000,
      });
      
      onDeleteWeekModalClose();
      fetchCurriculumDetail();
    } catch (error: any) {
      console.error('주차 삭제 실패:', error);
      toast({
        title: '주차 삭제에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleAddLesson = (weekNumber: number) => {
    setEditingWeek(weekNumber);
    setLessonForm({ lesson: '' });
    onLessonModalOpen();
  };

  const handleSaveLesson = async () => {
    if (!curriculum || !editingWeek || !lessonForm.lesson.trim()) {
      toast({
        title: '레슨 내용을 입력해주세요',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    try {
      await curriculumAPI.addLesson(curriculum.id, editingWeek, {
        lesson: lessonForm.lesson.trim(),
        lesson_index: lessonForm.lesson_index
      });
      
      toast({
        title: '레슨이 추가되었습니다',
        status: 'success',
        duration: 3000,
      });
      
      onLessonModalClose();
      fetchCurriculumDetail();
    } catch (error: any) {
      console.error('레슨 추가 실패:', error);
      toast({
        title: '레슨 추가에 실패했습니다',
        description: error.response?.data?.detail || '다시 시도해주세요',
        status: 'error',
        duration: 5000,
      });
    }
  };

  const handleEditLesson = (weekNumber: number, lessonIndex: number, currentLesson: string) => {
    setEditingLessonWeek(weekNumber);
    setEditingLessonIndex(lessonIndex);
    setLessonForm({ lesson: currentLesson });
    onEditLessonModalOpen();
  };

  const handleUpdateLesson = async () => {
    if (!curriculum || editingLessonWeek === null || editingLessonIndex === null || !lessonForm.lesson.trim()) {
      toast({
        title: '레슨 내용을 입력해주세요',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    try {
      await curriculumAPI.updateLesson(curriculum.id, editingLessonWeek, editingLessonIndex, {
        lesson: lessonForm.lesson.trim()
      });
      
      toast({
        title: '레슨이 수정되었습니다',
        status: 'success',
        duration: 3000,
      });
      
      onEditLessonModalClose();
      fetchCurriculumDetail();
    } catch (error: any) {
      console.error('레슨 수정 실패:', error);
      toast({
        title: '레슨 수정에 실패했습니다',
        description: error.response?.data?.detail || '다시 시도해주세요',
        status: 'error',
        duration: 5000,
      });
    }
  };

  const handleDeleteLesson = async (weekNumber: number, lessonIndex: number) => {
    if (!curriculum) return;

    try {
      await curriculumAPI.deleteLesson(curriculum.id, weekNumber, lessonIndex);
      
      toast({
        title: '레슨이 삭제되었습니다',
        status: 'success',
        duration: 3000,
      });
      
      fetchCurriculumDetail();
    } catch (error: any) {
      console.error('레슨 삭제 실패:', error);
      toast({
        title: '레슨 삭제에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const addLessonToWeekForm = () => {
    setWeekForm({
      ...weekForm,
      lessons: [...weekForm.lessons, '']
    });
  };

  const removeLessonFromWeekForm = (index: number) => {
    if (weekForm.lessons.length > 1) {
      setWeekForm({
        ...weekForm,
        lessons: weekForm.lessons.filter((_, i) => i !== index)
      });
    }
  };

  const updateLessonInWeekForm = (index: number, value: string) => {
    const newLessons = [...weekForm.lessons];
    newLessons[index] = value;
    setWeekForm({
      ...weekForm,
      lessons: newLessons
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getVisibilityColor = (visibility: string) => {
    return visibility === 'PUBLIC' ? 'green' : 'gray';
  };

  const getVisibilityText = (visibility: string) => {
    return visibility === 'PUBLIC' ? '공개' : '비공개';
  };

  const getTotalLessons = () => {
    if (!curriculum) return 0;
    return curriculum.week_schedules.reduce((total: number, week: WeekSchedule) => total + week.lessons.length, 0);
  };

  const getCompletedLessons = () => {
    if (!curriculumProgress) return 0;
    return curriculumProgress.completed_weeks;
  };

  const { isOpen: isTagModalOpen, onOpen: onTagModalOpen, onClose: onTagModalClose } = useDisclosure();

  if (loading) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text color={textColor}>커리큘럼을 불러오는 중...</Text>
        </VStack>
      </Container>
    );
  }

  if (error || !curriculum) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={4}>
          <Alert status="error">
            <AlertIcon />
            <AlertDescription>{error || '커리큘럼을 찾을 수 없습니다.'}</AlertDescription>
          </Alert>
          <Button leftIcon={<ArrowBackIcon />} onClick={() => navigate('/curriculum')}>
            커리큘럼 목록으로 돌아가기
          </Button>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="6xl" py={8}>
      <VStack spacing={6} align="stretch">
        {/* 브레드크럼 */}
        <Breadcrumb color={secondaryTextColor}>
          <BreadcrumbItem>
            <BreadcrumbLink onClick={() => navigate('/curriculum')}>
              커리큘럼
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbItem isCurrentPage>
            <BreadcrumbLink color={textColor}>{curriculum.title}</BreadcrumbLink>
          </BreadcrumbItem>
        </Breadcrumb>

        {/* 헤더 */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack align="stretch" spacing={4}>
              <HStack justify="space-between" align="start">
                <VStack align="start" spacing={2}>
                  <HStack>
                    <Heading size="lg" color={textColor}>{curriculum.title}</Heading>
                    <Badge
                      colorScheme={getVisibilityColor(curriculum.visibility)}
                      variant="solid"
                    >
                      {getVisibilityText(curriculum.visibility)}
                    </Badge>
                  </HStack>
                  <Text color={secondaryTextColor}>
                    생성일: {formatDate(curriculum.created_at)}
                  </Text>
                </VStack>
                
                <HStack>
                  <Button
                    leftIcon={<ArrowBackIcon />}
                    variant="ghost"
                    onClick={() => navigate('/curriculum')}
                    color={textColor}
                  >
                    목록으로
                  </Button>
                  <Button
                    leftIcon={<EditIcon />}
                    colorScheme="blue"
                    variant="outline"
                    onClick={openEditModal}
                  >
                    수정
                  </Button>
                  <Button
                    leftIcon={<DeleteIcon />}
                    colorScheme="red"
                    variant="outline"
                    onClick={onDeleteModalOpen}
                  >
                    삭제
                  </Button>
                </HStack>
              </HStack>

              <Divider />

              {/* 통계 */}
              <HStack spacing={8}>
                <VStack align="start" spacing={1}>
                  <Text fontSize="sm" color={secondaryTextColor}>전체 주차</Text>
                  <Text fontSize="2xl" fontWeight="bold" color={textColor}>
                    {curriculum?.week_schedules.length || 0}주
                  </Text>
                </VStack>
                <VStack align="start" spacing={1}>
                  <Text fontSize="sm" color={secondaryTextColor}>전체 레슨</Text>
                  <Text fontSize="2xl" fontWeight="bold" color={textColor}>
                    {getTotalLessons()}개
                  </Text>
                </VStack>
                {/* 수정된 진행률 섹션 */}
                {renderProgressSection()}
                <VStack align="start" flex={1} spacing={1}>
                  <HStack justify="space-between" w="100%">
                    <Text fontSize="sm" color={secondaryTextColor}>진행률</Text>
                    <Text fontSize="sm" color={secondaryTextColor}>
                      {curriculumProgress ? 
                        `${curriculumProgress.completed_weeks}/${curriculumProgress.total_weeks}주차 완료` : 
                        '계산 중...'
                      }
                    </Text>
                  </HStack>
                  <Progress 
                    value={curriculumProgress?.completion_percentage || 0} 
                    size="md" 
                    colorScheme="blue" 
                    w="200px"
                  />
                  <Text fontSize="xs" color={secondaryTextColor}>
                    {curriculumProgress?.completion_percentage || 0}% 완료
                  </Text>
                </VStack>
              </HStack>

              {/* 카테고리와 태그 */}

              <Divider />

              <VStack align="stretch" spacing={3}>
                {/* 카테고리 */}
                {category && (
                  <VStack align="start" spacing={1}>
                    <Text fontSize="sm" color={secondaryTextColor}>카테고리</Text>
                    <Badge
                      style={{ backgroundColor: category.color }}
                      color="white"
                      variant="solid"
                    >
                      {category.icon && `${category.icon} `}
                      {category.name}
                    </Badge>
                  </VStack>
                )}

                {/* 태그 */}
                <VStack align="start" spacing={2}>
                  <HStack justify="space-between" w="100%">
                    <Text fontSize="sm" color={secondaryTextColor}>태그</Text>
                    <Button
                      size="xs"
                      leftIcon={<AddIcon />}
                      colorScheme="green"
                      variant="outline"
                      onClick={onTagModalOpen}
                    >
                      태그 추가
                    </Button>
                  </HStack>
                  
                  {tags.length > 0 ? (
                    <HStack flexWrap="wrap" spacing={2}>
                      {tags.map((tag) => (
                        <Badge
                          key={tag.id}
                          colorScheme="blue"
                          variant="outline"
                          cursor="pointer"
                          onClick={() => handleRemoveTag(tag.name)}
                          title="클릭하여 제거"
                        >
                          #{tag.name} ×
                        </Badge>
                      ))}
                    </HStack>
                  ) : (
                    <Text fontSize="sm" color={secondaryTextColor} fontStyle="italic">
                      아직 태그가 없습니다
                    </Text>
                  )}
                </VStack>
              </VStack>
            </VStack>
          </CardBody>
        </Card>

        {/* 주차별 내용 */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack align="stretch" spacing={4}>
              <HStack justify="space-between">
                <Heading size="md" color={textColor}>주차별 커리큘럼</Heading>
                <Button
                  leftIcon={<AddIcon />}
                  colorScheme="green"
                  size="sm"
                  onClick={handleAddWeek}
                >
                  주차 추가
                </Button>
              </HStack>
              
              <Accordion allowMultiple>
                {curriculum.week_schedules.map((week) => (
                  <AccordionItem key={week.week_number} border="none">
                    <AccordionButton
                      bg={hoverBg}
                      borderRadius="md"
                      mb={2}
                      _hover={{ bg: hoverBg }}
                      _expanded={{ bg: hoverBg }}
                    >
                      <Box flex="1" textAlign="left">
                        <HStack justify="space-between">
                          <HStack>
                            <VStack align="start" spacing={1}>
                              <Text fontWeight="semibold" color={textColor}>
                                {week.week_number}주차
                              </Text>
                              <Text fontSize="sm" color={secondaryTextColor} fontWeight="normal">
                                {week.title}
                              </Text>
                            </VStack>
                            <Badge colorScheme="blue" variant="subtle">
                              {week.lessons?.length}개 레슨
                            </Badge>
                            {renderWeekProgress(week)}
                          </HStack>
                          <HStack spacing={2}>
                            <IconButton
                              aria-label="레슨 추가"
                              icon={<AddIcon />}
                              size="sm"
                              variant="ghost"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleAddLesson(week.week_number);
                              }}
                            />
                            <IconButton
                              aria-label="주차 삭제"
                              icon={<DeleteIcon />}
                              size="sm"
                              variant="ghost"
                              colorScheme="red"
                              onClick={(e) => {
                                e.stopPropagation();
                                setEditingWeek(week.week_number);
                                onDeleteWeekModalOpen();
                              }}
                            />
                            <AccordionIcon />
                          </HStack>
                        </HStack>
                      </Box>
                    </AccordionButton>
                    <AccordionPanel pb={4}>
                      <VStack align="stretch" spacing={3}>
                        {week.lessons.map((lesson, index) => (
                          <Card key={index} variant="outline" size="sm">
                            <CardBody py={3}>
                              <HStack justify="space-between">
                                <HStack>
                                  <Box
                                    w={6}
                                    h={6}
                                    borderRadius="full"
                                    bg="gray.200"
                                    display="flex"
                                    alignItems="center"
                                    justifyContent="center"
                                  >
                                    <Text fontSize="xs" fontWeight="bold">
                                      {index + 1}
                                    </Text>
                                  </Box>
                                  <Text 
                                    color={textColor} 
                                    cursor="pointer"
                                    _hover={{ color: "blue.500", textDecoration: "underline" }}
                                    onClick={() => {
                                      const params = new URLSearchParams({
                                        curriculum_id: curriculum.id,
                                        week_number: week.week_number.toString(),
                                        lesson_index: index.toString()
                                      });
                                      navigate(`/summary?${params.toString()}`);
                                    }}
                                  >
                                    {lesson}
                                  </Text>
                                </HStack>
                                <HStack spacing={1}>
                                  <IconButton
                                    aria-label="요약 보기"
                                    icon={<CheckIcon />}
                                    size="sm"
                                    variant="ghost"
                                    colorScheme="green"
                                    title="요약 보기"
                                    onClick={() => {
                                      const params = new URLSearchParams({
                                        curriculum_id: curriculum.id,
                                        week_number: week.week_number.toString(),
                                        lesson_index: index.toString(),
                                        view: 'list'
                                      });
                                      navigate(`/summary?${params.toString()}`);
                                    }}
                                  />
                                  {isOwner && (
                                    <>
                                      <IconButton
                                        aria-label="수정"
                                        icon={<EditIcon />}
                                        size="sm"
                                        variant="ghost"
                                        colorScheme="blue"
                                        onClick={() => handleEditLesson(week.week_number, index, lesson)}
                                      />
                                      <IconButton
                                        aria-label="삭제"
                                        icon={<DeleteIcon />}
                                        size="sm"
                                        variant="ghost"
                                        colorScheme="red"
                                        onClick={() => handleDeleteLesson(week.week_number, index)}
                                      />
                                    </>
                                  )}
                                </HStack>
                              </HStack>
                            </CardBody>
                          </Card>
                        ))}
                        
                        {week.lessons.length === 0 && (
                          <Text color={secondaryTextColor} textAlign="center" py={4}>
                            아직 레슨이 없습니다. 레슨을 추가해보세요.
                          </Text>
                        )}
                      </VStack>
                    </AccordionPanel>
                  </AccordionItem>
                ))}
              </Accordion>
            </VStack>
          </CardBody>
        </Card>

        {/* 레슨 추가 모달 */}
        <Modal isOpen={isLessonModalOpen} onClose={onLessonModalClose}>
          <ModalOverlay />
          <ModalContent bg={cardBg} color={textColor}>
            <ModalHeader>{editingWeek}주차 레슨 추가</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel color={textColor}>레슨 내용</FormLabel>
                  <Textarea
                    placeholder="새로운 레슨 내용을 입력하세요"
                    value={lessonForm.lesson}
                    onChange={(e) => setLessonForm({ ...lessonForm, lesson: e.target.value })}
                    color={textColor}
                    borderColor={borderColor}
                  />
                </FormControl>
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onLessonModalClose}>
                취소
              </Button>
              <Button colorScheme="blue" onClick={handleSaveLesson}>
                추가하기
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* 주차 추가 모달 */}
        <Modal isOpen={isWeekModalOpen} onClose={onWeekModalClose} size="lg">
          <ModalOverlay />
          <ModalContent bg={cardBg} color={textColor}>
            <ModalHeader>새 주차 추가</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel color={textColor}>주차 제목</FormLabel>
                  <Input
                    placeholder="주차 제목을 입력하세요"
                    value={weekForm.title}
                    onChange={(e) => setWeekForm({ ...weekForm, title: e.target.value })}
                    color={textColor}
                    borderColor={borderColor}
                  />
                </FormControl>
                <FormControl isRequired>
                  <FormLabel color={textColor}>주차 번호</FormLabel>
                  <Input
                    type="number"
                    value={weekForm.week_number}
                    onChange={(e) => setWeekForm({ ...weekForm, week_number: parseInt(e.target.value) || 1 })}
                    color={textColor}
                    borderColor={borderColor}
                    min={1}
                    max={24}
                  />
                </FormControl>
                <FormControl isRequired>
                  <FormLabel color={textColor}>레슨 목록</FormLabel>
                  <VStack spacing={2} align="stretch">
                    {weekForm.lessons.map((lesson, index) => (
                      <HStack key={index}>
                        <Input
                          placeholder={`레슨 ${index + 1}`}
                          value={lesson}
                          onChange={(e) => updateLessonInWeekForm(index, e.target.value)}
                          color={textColor}
                          borderColor={borderColor}
                        />
                        {weekForm.lessons.length > 1 && (
                          <IconButton
                            aria-label="레슨 제거"
                            icon={<DeleteIcon />}
                            size="sm"
                            colorScheme="red"
                            variant="ghost"
                            onClick={() => removeLessonFromWeekForm(index)}
                          />
                        )}
                      </HStack>
                    ))}
                    <Button
                      leftIcon={<AddIcon />}
                      variant="ghost"
                      size="sm"
                      onClick={addLessonToWeekForm}
                      color={textColor}
                    >
                      레슨 추가
                    </Button>
                  </VStack>
                </FormControl>
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onWeekModalClose}>
                취소
              </Button>
              <Button colorScheme="green" onClick={handleSaveWeek}>
                주차 추가
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* 레슨 수정 모달 */}
        <Modal isOpen={isEditLessonModalOpen} onClose={onEditLessonModalClose}>
          <ModalOverlay />
          <ModalContent bg={cardBg} color={textColor}>
            <ModalHeader>{editingLessonWeek}주차 레슨 수정</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel color={textColor}>레슨 내용</FormLabel>
                  <Textarea
                    value={lessonForm.lesson}
                    onChange={(e) => setLessonForm({ ...lessonForm, lesson: e.target.value })}
                    color={textColor}
                    borderColor={borderColor}
                  />
                </FormControl>
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onEditLessonModalClose}>
                취소
              </Button>
              <Button colorScheme="blue" onClick={handleUpdateLesson}>
                수정하기
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* 커리큘럼 수정 모달 */}
        <Modal isOpen={isEditModalOpen} onClose={onEditModalClose}>
          <ModalOverlay />
          <ModalContent bg={cardBg} color={textColor}>
            <ModalHeader>커리큘럼 수정</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel color={textColor}>제목</FormLabel>
                  <Input
                    value={editForm.title}
                    onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                    color={textColor}
                    borderColor={borderColor}
                  />
                </FormControl>
                <FormControl>
                  <FormLabel color={textColor}>공개 설정</FormLabel>
                  <HStack spacing={4}>
                    <Button
                      variant={editForm.visibility === 'PRIVATE' ? 'solid' : 'outline'}
                      colorScheme="gray"
                      onClick={() => setEditForm({ ...editForm, visibility: 'PRIVATE' })}
                      size="sm"
                    >
                      비공개
                    </Button>
                    <Button
                      variant={editForm.visibility === 'PUBLIC' ? 'solid' : 'outline'}
                      colorScheme="green"
                      onClick={() => setEditForm({ ...editForm, visibility: 'PUBLIC' })}
                      size="sm"
                    >
                      공개
                    </Button>
                  </HStack>
                </FormControl>
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onEditModalClose}>
                취소
              </Button>
              <Button colorScheme="blue" onClick={handleEditCurriculum}>
                수정하기
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* 커리큘럼 삭제 확인 모달 */}
        <Modal isOpen={isDeleteModalOpen} onClose={onDeleteModalClose}>
          <ModalOverlay />
          <ModalContent bg={cardBg} color={textColor}>
            <ModalHeader>커리큘럼 삭제</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4}>
                <Text color={textColor}>
                  정말로 이 커리큘럼을 삭제하시겠습니까?
                </Text>
                <Text fontSize="sm" color="red.500">
                  이 작업은 되돌릴 수 없습니다.
                </Text>
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onDeleteModalClose}>
                취소
              </Button>
              <Button colorScheme="red" onClick={handleDeleteCurriculum}>
                삭제하기
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* 주차 삭제 확인 모달 */}
        <Modal isOpen={isDeleteWeekModalOpen} onClose={onDeleteWeekModalClose}>
          <ModalOverlay />
          <ModalContent bg={cardBg} color={textColor}>
            <ModalHeader>주차 삭제</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4}>
                <Text color={textColor}>
                  {editingWeek}주차를 삭제하시겠습니까?
                </Text>
                <Text fontSize="sm" color="red.500">
                  이 작업은 되돌릴 수 없습니다.
                </Text>
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onDeleteWeekModalClose}>
                취소
              </Button>
              <Button 
                colorScheme="red" 
                onClick={() => editingWeek && handleDeleteWeek(editingWeek)}
              >
                삭제하기
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* 태그 추가 모달 */}
        <Modal isOpen={isTagModalOpen} onClose={onTagModalClose}>
          <ModalOverlay />
          <ModalContent bg={cardBg} color={textColor}>
            <ModalHeader>태그 추가</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4}>
                <FormControl>
                  <FormLabel>태그 이름</FormLabel>
                  <Input
                    placeholder="태그를 입력하세요 (예: react, javascript)"
                    value={newTag}
                    onChange={(e) => {
                      setNewTag(e.target.value);
                      handleTagSearch(e.target.value);
                    }}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleAddTag(newTag);
                      }
                    }}
                  />
                </FormControl>
                
                {/* 태그 제안 */}
                {tagSuggestions.length > 0 && (
                  <VStack align="stretch" w="100%">
                    <Text fontSize="sm" color={secondaryTextColor}>추천 태그:</Text>
                    <HStack flexWrap="wrap">
                      {tagSuggestions.map((suggestion) => (
                        <Badge
                          key={suggestion.id}
                          colorScheme="blue"
                          variant="outline"
                          cursor="pointer"
                          onClick={() => {
                            setNewTag(suggestion.name);
                            setTagSuggestions([]);
                          }}
                        >
                          {suggestion.name} ({suggestion.usage_count})
                        </Badge>
                      ))}
                    </HStack>
                  </VStack>
                )}
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onTagModalClose}>
                취소
              </Button>
              <Button
                colorScheme="green"
                onClick={() => handleAddTag(newTag)}
                isLoading={loadingTags}
                loadingText="추가 중..."
                isDisabled={!newTag.trim()}
              >
                추가하기
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Container>
  );
};

export default CurriculumDetail;
