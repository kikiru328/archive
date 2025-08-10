// src/pages/Summary.tsx
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
  Grid,
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
  Select,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
} from '@chakra-ui/react';
import { 
  AddIcon, 
  EditIcon, 
  DeleteIcon,
  ViewIcon,
  StarIcon
} from '@chakra-ui/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { summaryAPI, curriculumAPI } from '../services/api';

interface Summary {
  id: string;
  curriculum_id: string;
  curriculum_title?: string;
  week_number: number;
  lesson_title?: string;
  content: string;
  created_at: string;
  updated_at: string;
}

interface Curriculum {
  id: string;
  title: string;
  week_schedules: Array<{
    week_number: number;
    lessons: string[];
  }>;
}

interface SummaryForm {
  curriculum_id: string;
  week_number: number;
  lesson_index?: number;
  content: string;
}

const Summary: React.FC = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [searchParams] = useSearchParams();
  
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [curriculums, setCurriculums] = useState<Curriculum[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [editingSummary, setEditingSummary] = useState<Summary | null>(null);
  const [summaryForm, setSummaryForm] = useState<SummaryForm>({
    curriculum_id: '',
    week_number: 1,
    content: ''
  });
  
  const { isOpen: isCreateModalOpen, onOpen: onCreateModalOpen, onClose: onCreateModalClose } = useDisclosure();
  const { isOpen: isEditModalOpen, onOpen: onEditModalOpen, onClose: onEditModalClose } = useDisclosure();
  
  // 다크모드 대응 색상
  const textColor = useColorModeValue('gray.900', 'white');
  const secondaryTextColor = useColorModeValue('gray.600', 'gray.300');
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    fetchData();
    
    // URL 파라미터에서 커리큘럼 정보 가져오기
    const curriculumId = searchParams.get('curriculum_id');
    const weekNumber = searchParams.get('week_number');
    const lessonIndex = searchParams.get('lesson_index');
    
    if (curriculumId && weekNumber) {
      setSummaryForm(prev => ({
        ...prev,
        curriculum_id: curriculumId,
        week_number: parseInt(weekNumber),
        lesson_index: lessonIndex ? parseInt(lessonIndex) : undefined
      }));
      onCreateModalOpen();
    }
  }, [searchParams, onCreateModalOpen]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // 내 커리큘럼 목록과 요약 목록을 병렬로 가져오기
      const [curriculumResponse, summaryResponse] = await Promise.all([
        curriculumAPI.getAll(),
        summaryAPI.getAll()
      ]);
      
      setCurriculums(curriculumResponse.data.curriculums || []);
      setSummaries(summaryResponse.data || []);
    } catch (error: any) {
      console.error('데이터 조회 실패:', error);
      setError('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSummary = async () => {
    if (!summaryForm.curriculum_id || !summaryForm.content.trim()) {
      toast({
        title: '필수 정보를 입력해주세요',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    try {
      setSubmitting(true);
      await summaryAPI.create({
        curriculum_id: summaryForm.curriculum_id,
        week_number: summaryForm.week_number,
        lesson_index: summaryForm.lesson_index,
        content: summaryForm.content.trim()
      });
      
      toast({
        title: '요약이 저장되었습니다!',
        status: 'success',
        duration: 3000,
      });
      
      setSummaryForm({
        curriculum_id: '',
        week_number: 1,
        content: ''
      });
      onCreateModalClose();
      fetchData();
    } catch (error: any) {
      console.error('요약 생성 실패:', error);
      toast({
        title: '요약 저장에 실패했습니다',
        description: error.response?.data?.detail || '다시 시도해주세요',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditSummary = (summary: Summary) => {
    setEditingSummary(summary);
    setSummaryForm({
      curriculum_id: summary.curriculum_id,
      week_number: summary.week_number,
      content: summary.content
    });
    onEditModalOpen();
  };

  const handleUpdateSummary = async () => {
    if (!editingSummary || !summaryForm.content.trim()) {
      toast({
        title: '내용을 입력해주세요',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    try {
      setSubmitting(true);
      await summaryAPI.update(editingSummary.id, {
        content: summaryForm.content.trim()
      });
      
      toast({
        title: '요약이 수정되었습니다!',
        status: 'success',
        duration: 3000,
      });
      
      onEditModalClose();
      fetchData();
    } catch (error: any) {
      console.error('요약 수정 실패:', error);
      toast({
        title: '요약 수정에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteSummary = async (summaryId: string) => {
    if (!window.confirm('정말로 이 요약을 삭제하시겠습니까?')) {
      return;
    }

    try {
      await summaryAPI.delete(summaryId);
      
      toast({
        title: '요약이 삭제되었습니다',
        status: 'success',
        duration: 3000,
      });
      
      fetchData();
    } catch (error: any) {
      console.error('요약 삭제 실패:', error);
      toast({
        title: '요약 삭제에 실패했습니다',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const getCurriculumTitle = (curriculumId: string) => {
    const curriculum = curriculums.find(c => c.id === curriculumId);
    return curriculum?.title || '알 수 없는 커리큘럼';
  };

  const getLessonTitle = (curriculumId: string, weekNumber: number, lessonIndex?: number) => {
    const curriculum = curriculums.find(c => c.id === curriculumId);
    const week = curriculum?.week_schedules.find(w => w.week_number === weekNumber);
    
    if (lessonIndex !== undefined && week && week.lessons[lessonIndex]) {
      return week.lessons[lessonIndex];
    }
    
    return `${weekNumber}주차 전체`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getSelectedCurriculumWeeks = () => {
    if (!summaryForm.curriculum_id) return [];
    const curriculum = curriculums.find(c => c.id === summaryForm.curriculum_id);
    return curriculum?.week_schedules || [];
  };

  const getSelectedWeekLessons = () => {
    const weeks = getSelectedCurriculumWeeks();
    const week = weeks.find(w => w.week_number === summaryForm.week_number);
    return week?.lessons || [];
  };

  if (loading) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text color={textColor}>요약을 불러오는 중...</Text>
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
            <BreadcrumbLink onClick={() => navigate('/')}>
              홈
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbItem isCurrentPage>
            <BreadcrumbLink color={textColor}>학습 요약</BreadcrumbLink>
          </BreadcrumbItem>
        </Breadcrumb>

        {/* 헤더 */}
        <HStack justify="space-between" align="center">
          <Heading size="lg" color={textColor}>학습 요약</Heading>
          <Button
            leftIcon={<AddIcon />}
            colorScheme="blue"
            onClick={onCreateModalOpen}
          >
            새 요약 작성
          </Button>
        </HStack>

        {/* 에러 메시지 */}
        {error && (
          <Alert status="error">
            <AlertIcon />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* 요약 목록 */}
        {summaries.length === 0 ? (
          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <VStack spacing={4} py={8}>
                <StarIcon boxSize={12} color="gray.400" />
                <Heading size="md" color={secondaryTextColor}>
                  아직 작성된 요약이 없습니다
                </Heading>
                <Text color={secondaryTextColor} textAlign="center">
                  학습한 내용을 요약해보세요!<br />
                  요약을 통해 학습 내용을 더 잘 기억할 수 있습니다.
                </Text>
                <Button
                  leftIcon={<AddIcon />}
                  colorScheme="blue"
                  onClick={onCreateModalOpen}
                >
                  첫 번째 요약 작성하기
                </Button>
              </VStack>
            </CardBody>
          </Card>
        ) : (
          <Grid templateColumns="repeat(auto-fill, minmax(350px, 1fr))" gap={6}>
            {summaries.map((summary) => (
              <Card 
                key={summary.id} 
                variant="outline" 
                bg={cardBg} 
                borderColor={borderColor}
                transition="all 0.2s"
                _hover={{ 
                  transform: "translateY(-2px)", 
                  shadow: "lg",
                  borderColor: "blue.300"
                }}
              >
                <CardBody>
                  <VStack align="stretch" spacing={3}>
                    {/* 헤더 */}
                    <VStack align="start" spacing={1}>
                      <Text fontSize="sm" color="blue.500" fontWeight="semibold">
                        {getCurriculumTitle(summary.curriculum_id)}
                      </Text>
                      <Heading size="sm" color={textColor} noOfLines={1}>
                        {getLessonTitle(summary.curriculum_id, summary.week_number, summary.lesson_title ? 0 : undefined)}
                      </Heading>
                      <Badge colorScheme="blue" variant="subtle" size="sm">
                        {summary.week_number}주차
                      </Badge>
                    </VStack>

                    {/* 요약 내용 미리보기 */}
                    <Text 
                      color={secondaryTextColor} 
                      fontSize="sm" 
                      noOfLines={3}
                      minH="60px"
                    >
                      {summary.content}
                    </Text>

                    {/* 메타 정보 */}
                    <Text fontSize="xs" color={secondaryTextColor}>
                      {formatDate(summary.created_at)}
                      {summary.updated_at !== summary.created_at && ' (수정됨)'}
                    </Text>

                    {/* 액션 버튼 */}
                    <HStack spacing={2} justify="flex-end">
                      <Button
                        leftIcon={<ViewIcon />}
                        size="sm"
                        variant="ghost"
                        onClick={() => navigate(`/summary/${summary.id}`)}
                      >
                        보기
                      </Button>
                      <Button
                        leftIcon={<EditIcon />}
                        size="sm"
                        variant="ghost"
                        colorScheme="blue"
                        onClick={() => handleEditSummary(summary)}
                      >
                        수정
                      </Button>
                      <Button
                        leftIcon={<DeleteIcon />}
                        size="sm"
                        variant="ghost"
                        colorScheme="red"
                        onClick={() => handleDeleteSummary(summary.id)}
                      >
                        삭제
                      </Button>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </Grid>
        )}

        {/* 요약 작성 모달 */}
        <Modal isOpen={isCreateModalOpen} onClose={onCreateModalClose} size="xl">
          <ModalOverlay />
          <ModalContent bg={cardBg} color={textColor}>
            <ModalHeader>새 요약 작성</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel color={textColor}>커리큘럼 선택</FormLabel>
                  <Select
                    placeholder="커리큘럼을 선택하세요"
                    value={summaryForm.curriculum_id}
                    onChange={(e) => setSummaryForm({ 
                      ...summaryForm, 
                      curriculum_id: e.target.value,
                      week_number: 1 
                    })}
                    color={textColor}
                    borderColor={borderColor}
                  >
                    {curriculums.map((curriculum) => (
                      <option key={curriculum.id} value={curriculum.id}>
                        {curriculum.title}
                      </option>
                    ))}
                  </Select>
                </FormControl>

                {summaryForm.curriculum_id && (
                  <FormControl isRequired>
                    <FormLabel color={textColor}>주차 선택</FormLabel>
                    <Select
                      value={summaryForm.week_number}
                      onChange={(e) => setSummaryForm({ 
                        ...summaryForm, 
                        week_number: parseInt(e.target.value) 
                      })}
                      color={textColor}
                      borderColor={borderColor}
                    >
                      {getSelectedCurriculumWeeks().map((week) => (
                        <option key={week.week_number} value={week.week_number}>
                          {week.week_number}주차 ({week.lessons.length}개 레슨)
                        </option>
                      ))}
                    </Select>
                  </FormControl>
                )}

                {summaryForm.curriculum_id && getSelectedWeekLessons().length > 0 && (
                  <FormControl>
                    <FormLabel color={textColor}>레슨 선택 (선택사항)</FormLabel>
                    <Select
                      placeholder="전체 주차 요약"
                      value={summaryForm.lesson_index ?? ''}
                      onChange={(e) => setSummaryForm({ 
                        ...summaryForm, 
                        lesson_index: e.target.value ? parseInt(e.target.value) : undefined 
                      })}
                      color={textColor}
                      borderColor={borderColor}
                    >
                      {getSelectedWeekLessons().map((lesson, index) => (
                        <option key={index} value={index}>
                          {index + 1}. {lesson}
                        </option>
                      ))}
                    </Select>
                  </FormControl>
                )}

                <FormControl isRequired>
                  <FormLabel color={textColor}>요약 내용</FormLabel>
                  <Textarea
                    placeholder="학습한 내용을 요약해주세요..."
                    value={summaryForm.content}
                    onChange={(e) => setSummaryForm({ ...summaryForm, content: e.target.value })}
                    color={textColor}
                    borderColor={borderColor}
                    rows={8}
                  />
                </FormControl>
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onCreateModalClose}>
                취소
              </Button>
              <Button 
                colorScheme="blue" 
                onClick={handleCreateSummary}
                isLoading={submitting}
                loadingText="저장 중..."
              >
                저장하기
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

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
                    {editingSummary && getCurriculumTitle(editingSummary.curriculum_id)} - {editingSummary?.week_number}주차
                  </Text>
                </Box>
                
                <FormControl isRequired>
                  <FormLabel color={textColor}>요약 내용</FormLabel>
                  <Textarea
                    value={summaryForm.content}
                    onChange={(e) => setSummaryForm({ ...summaryForm, content: e.target.value })}
                    color={textColor}
                    borderColor={borderColor}
                    rows={8}
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
                isLoading={submitting}
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

export default Summary;
