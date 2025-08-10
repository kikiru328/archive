// src/pages/SummaryDetail.tsx
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
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  useColorModeValue,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  Divider,
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
  ArrowBackIcon, 
  EditIcon, 
  DeleteIcon,
  StarIcon,
  CheckIcon
} from '@chakra-ui/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { summaryAPI, curriculumAPI, feedbackAPI } from '../services/api';
import { getCurrentUserId } from '../utils/auth';
interface SummaryDetail {
  id: string;
  curriculum_id: string;
  week_number: number;
  lesson_index?: number;
  content: string;
  created_at: string;
  updated_at: string;
}

interface Feedback {
  id: string;
  summary_id: string;
  comment: string;
  score: number;
  grade: string;
  created_at: string;
}

interface Curriculum {
  id: string;
  owner_id: string;
  title: string;
  week_schedules: Array<{
    week_number: number;
    title: string;
    lessons: string[];
  }>;
}

const SummaryDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const currentUserId = getCurrentUserId();
  const [summary, setSummary] = useState<SummaryDetail | null>(null);
  const [curriculum, setCurriculum] = useState<Curriculum | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState('');
  const [editContent, setEditContent] = useState('');
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [loadingFeedback, setLoadingFeedback] = useState(false);
  
  const { isOpen: isEditModalOpen, onOpen: onEditModalOpen, onClose: onEditModalClose } = useDisclosure();
  
  // 다크모드 대응 색상
  const textColor = useColorModeValue('gray.900', 'white');
  const secondaryTextColor = useColorModeValue('gray.600', 'gray.300');
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const highlightBg = useColorModeValue('blue.50', 'blue.900');
  const isOwner = curriculum && currentUserId && curriculum.owner_id === currentUserId;
  useEffect(() => {
    if (id) {
      fetchSummaryDetail();
    }
  }, [id]);

  const fetchSummaryDetail = async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      setError('');
      
      const summaryResponse = await summaryAPI.getById(id);
      const summaryData = summaryResponse.data;
      setSummary(summaryData);
      
      // 커리큘럼 정보도 가져오기
      const curriculumResponse = await curriculumAPI.getById(summaryData.curriculum_id);
      setCurriculum(curriculumResponse.data);
      
      await fetchFeedback(summaryData.id);

    } catch (error: any) {
      console.error('요약 상세 조회 실패:', error);
      setError('요약을 불러오는데 실패했습니다.');
      
      if (error.response?.status === 404) {
        toast({
          title: '요약을 찾을 수 없습니다',
          status: 'error',
          duration: 3000,
        });
        navigate('/summary');
      }
    } finally {
      setLoading(false);
    }
  };
  
  const handleEditSummary = () => {
    if (summary) {
      setEditContent(summary.content);
      onEditModalOpen();
    }
  };

  const handleUpdateSummary = async () => {
    if (!summary || !editContent.trim()) {
      toast({
        title: '내용을 입력해주세요',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    try {
      setUpdating(true);
      await summaryAPI.update(summary.id, {
        content: editContent.trim()
      });
      
      toast({
        title: '요약이 수정되었습니다!',
        status: 'success',
        duration: 3000,
      });
      
      onEditModalClose();
      fetchSummaryDetail();
    } catch (error: any) {
      console.error('요약 수정 실패:', error);
      toast({
        title: '요약 수정에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setUpdating(false);
    }
  };
  
  const handleDeleteSummary = async () => {
    if (!summary) return;
    
    if (!window.confirm('정말로 이 요약을 삭제하시겠습니까?')) {
      return;
    }

    try {
      await summaryAPI.delete(summary.id);
      
      toast({
        title: '요약이 삭제되었습니다',
        status: 'success',
        duration: 3000,
      });
      
      navigate('/summary');
    } catch (error: any) {
      console.error('요약 삭제 실패:', error);
      toast({
        title: '요약 삭제에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleRequestFeedback = async () => {
    if (!summary) return;

    try {
      setLoadingFeedback(true);
      
      await feedbackAPI.generateFeedback(summary.id);
      
      toast({
        title: '피드백 생성을 요청했습니다',
        description: '잠시 후 피드백이 생성됩니다',
        status: 'success',
        duration: 3000,
      });
      
      // 3초 후 피드백 다시 로드
      setTimeout(async () => {
        await fetchFeedback(summary.id);
        setLoadingFeedback(false);
      }, 3000);
      
    } catch (error: any) {
      console.error('피드백 요청 실패:', error);
      toast({
        title: '피드백 요청에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
      setLoadingFeedback(false);
    }
  };

  const fetchFeedback = async (summaryId: string) => {
    try {
      const response = await feedbackAPI.getBySummary(summaryId);
      setFeedback(response.data);
    } catch (error: any) {
      // 피드백이 없는 경우는 정상적인 상황
      console.log('피드백 없음:', error);
      setFeedback(null);
    }
  };

  const getLessonTitle = () => {
    if (!curriculum || !summary) return '';
    
    const week = curriculum.week_schedules.find(w => w.week_number === summary.week_number);
    
    if (summary.lesson_index !== undefined && week && week.lessons[summary.lesson_index]) {
      return `${week.title} - ${week.lessons[summary.lesson_index]}`;
    }
    
    return week?.title || `${summary.week_number}주차`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <StarIcon
        key={i}
        color={i < rating ? 'yellow.400' : 'gray.300'}
        boxSize={4}
      />
    ));
  };

  if (loading) {
    return (
      <Container maxW="4xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text color={textColor}>요약을 불러오는 중...</Text>
        </VStack>
      </Container>
    );
  }

  if (error || !summary) {
    return (
      <Container maxW="4xl" py={8}>
        <VStack spacing={4}>
          <Alert status="error">
            <AlertIcon />
            <AlertDescription>{error || '요약을 찾을 수 없습니다.'}</AlertDescription>
          </Alert>
          <Button leftIcon={<ArrowBackIcon />} onClick={() => navigate('/summary')}>
            요약 목록으로 돌아가기
          </Button>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="4xl" py={8}>
      <VStack spacing={6} align="stretch">
        {/* 브레드크럼 */}
        <Breadcrumb color={secondaryTextColor}>
          <BreadcrumbItem>
            <BreadcrumbLink onClick={() => navigate('/summary')}>
              학습 요약
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbItem isCurrentPage>
            <BreadcrumbLink color={textColor}>
              {curriculum?.title} - {summary.week_number}주차
            </BreadcrumbLink>
          </BreadcrumbItem>
        </Breadcrumb>

        {/* 헤더 */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack align="stretch" spacing={4}>
              <HStack justify="space-between" align="start">
                <VStack align="start" spacing={2}>
                  <Text fontSize="sm" color="blue.500" fontWeight="semibold">
                    {curriculum?.title}
                  </Text>
                  <Heading size="lg" color={textColor}>
                    {getLessonTitle()}
                  </Heading>
                  <HStack>
                    <Badge colorScheme="blue" variant="solid">
                      {summary.week_number}주차
                    </Badge>
                    {summary.lesson_index !== undefined && (
                      <Badge colorScheme="green" variant="subtle">
                        레슨 {summary.lesson_index + 1}
                      </Badge>
                    )}
                  </HStack>
                </VStack>
                
                <HStack>
                  <Button
                    leftIcon={<ArrowBackIcon />}
                    variant="ghost"
                    onClick={() => navigate('/summary')}
                    color={textColor}
                  >
                    목록으로
                  </Button>
                  <Button
                    leftIcon={<EditIcon />}
                    colorScheme="blue"
                    variant="outline"
                    onClick={handleEditSummary}
                  >
                    수정
                  </Button>
                  <Button
                    leftIcon={<DeleteIcon />}
                    colorScheme="red"
                    variant="outline"
                    onClick={handleDeleteSummary}
                  >
                    삭제
                  </Button>
                </HStack>
              </HStack>

              <Divider />

              {/* 메타 정보 */}
              <HStack spacing={6} fontSize="sm" color={secondaryTextColor}>
                <Text>작성일: {formatDate(summary.created_at)}</Text>
                {summary.updated_at !== summary.created_at && (
                  <Text>수정일: {formatDate(summary.updated_at)}</Text>
                )}
              </HStack>
            </VStack>
          </CardBody>
        </Card>

        {/* 요약 내용 */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack align="stretch" spacing={4}>
              <Heading size="md" color={textColor}>학습 요약</Heading>
              <Box
                p={4}
                bg={highlightBg}
                borderRadius="md"
                borderLeft="4px solid"
                borderLeftColor="blue.500"
              >
                <Text 
                  color={textColor}
                  whiteSpace="pre-wrap"
                  lineHeight="1.6"
                >
                  {summary.content}
                </Text>
              </Box>
            </VStack>
          </CardBody>
        </Card>

        {/* AI 피드백 섹션 */}
        {feedback ? (
          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <VStack align="stretch" spacing={4}>
                <HStack justify="space-between">
                  <Heading size="md" color={textColor}>AI 피드백</Heading>
                  <HStack>
                    {Array.from({ length: 5 }, (_, i) => (
                      <StarIcon
                        key={i}
                        color={i < Math.floor(feedback.score) ? 'yellow.400' : 'gray.300'}
                        boxSize={4}
                      />
                    ))}
                    <Text fontSize="sm" color={secondaryTextColor}>
                      ({feedback.score}/10)
                    </Text>
                  </HStack>
                </HStack>
                
                <Text color={textColor} lineHeight="1.6">
                  {feedback.comment}
                </Text>
                
                <Text fontSize="xs" color={secondaryTextColor}>
                  피드백 생성일: {formatDate(feedback.created_at)}
                </Text>
              </VStack>
            </CardBody>
          </Card>
        ) : (
          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <VStack spacing={4}>
                <StarIcon boxSize={8} color="gray.400" />
                <Text color={secondaryTextColor} textAlign="center">
                  아직 AI 피드백이 생성되지 않았습니다.<br />
                  곧 피드백을 받아볼 수 있습니다!
                </Text>
                <Button
                  colorScheme="blue"
                  variant="outline"
                  onClick={handleRequestFeedback}
                  isLoading={loadingFeedback}
                  loadingText="요청 중..."
                >
                  피드백 요청하기
                </Button>
              </VStack>
            </CardBody>
          </Card>
        )}

        {/* 요약 수정 모달 */}
        <Modal isOpen={isEditModalOpen} onClose={onEditModalClose} size="xl">
          <ModalOverlay />
          <ModalContent bg={cardBg} color={textColor}>
            <ModalHeader>요약 수정</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4}>
                <Box w="100%">
                  <Text fontWeight="semibold" color={textColor} mb={2}>
                    {curriculum?.title} - {getLessonTitle()}
                  </Text>
                </Box>
                
                <FormControl isRequired>
                  <FormLabel color={textColor}>요약 내용</FormLabel>
                  <Textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    color={textColor}
                    borderColor={borderColor}
                    rows={12}
                    placeholder="학습한 내용을 요약해주세요..."
                  />
                </FormControl>
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onEditModalClose}>
                취소
              </Button>
              <Button 
                colorScheme="blue" 
                onClick={handleUpdateSummary}
                isLoading={updating}
                loadingText="수정 중..."
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

export default SummaryDetail;
