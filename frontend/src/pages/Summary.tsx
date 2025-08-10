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
  week_number: number;
  content: string;
  content_length: number;
  snippet: string;
  created_at: string;
  updated_at: string;
}

interface WeekSchedule {
  week_number: number;
  title: string; 
  lessons: string[];
}

interface Curriculum {
  id: string;
  title: string;
  total_weeks: number;
  week_schedules?: WeekSchedule[];
}

interface SummaryForm {
  curriculum_id: string;
  week_number: number;
  content: string;
}

const Summary: React.FC = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [searchParams] = useSearchParams();
  
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [curriculums, setCurriculums] = useState<Curriculum[]>([]);
  const [selectedCurriculum, setSelectedCurriculum] = useState<Curriculum | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [editingSummary, setEditingSummary] = useState<Summary | null>(null);
  const [summaryForm, setSummaryForm] = useState<SummaryForm>({
    curriculum_id: '',
    week_number: 1,
    content: ''
  });
  const [currentView, setCurrentView] = useState<'create' | 'list'>('list');
  
  const { isOpen: isCreateModalOpen, onOpen: onCreateModalOpen, onClose: onCreateModalClose } = useDisclosure();
  const { isOpen: isEditModalOpen, onOpen: onEditModalOpen, onClose: onEditModalClose } = useDisclosure();
  
  // 다크모드 대응 색상
  const textColor = useColorModeValue('gray.900', 'white');
  const secondaryTextColor = useColorModeValue('gray.600', 'gray.300');
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    initializePage();
  }, [searchParams]);

  const initializePage = async () => {
    // URL 파라미터에서 정보 가져오기
    const curriculumId = searchParams.get('curriculum_id');
    const weekNumber = searchParams.get('week_number');
    const lessonIndex = searchParams.get('lesson_index');
    const view = searchParams.get('view');

    await fetchData();

    if (curriculumId && weekNumber) {
      setSummaryForm(prev => ({
        ...prev,
        curriculum_id: curriculumId,
        week_number: parseInt(weekNumber),
      }));

      if (view === 'list') {
        // 요약 목록 보기 모드
        setCurrentView('list');
        await fetchSummariesByCurriculumAndWeek(curriculumId, parseInt(weekNumber));
      } else {
        // 요약 작성 모드
        setCurrentView('create');
        onCreateModalOpen();
      }
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // 내 커리큘럼 목록과 요약 목록을 병렬로 가져오기
      const [curriculumResponse, summaryResponse] = await Promise.all([
        curriculumAPI.getAll(),
        summaryAPI.getAll()
      ]);
      
      console.log('커리큘럼 응답:', curriculumResponse.data);
      console.log('요약 응답:', summaryResponse.data);
      
      const curriculumData = curriculumResponse.data.curriculums || [];
      setCurriculums(curriculumData);

      const summaryData = summaryResponse.data.summaries || [];
      setSummaries(summaryData);
    } catch (error: any) {
      console.error('데이터 조회 실패:', error);
      setError('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const fetchSummariesByCurriculumAndWeek = async (curriculumId: string, weekNumber: number) => {
    try {
      const response = await summaryAPI.getByWeek(curriculumId, weekNumber);
      setSummaries(response.data.summaries || []);
      
      // 선택된 커리큘럼 정보 설정
      const curriculum = curriculums.find(c => c.id === curriculumId);
      setSelectedCurriculum(curriculum || null);
    } catch (error: any) {
      console.error('주차별 요약 조회 실패:', error);
      toast({
        title: '요약을 불러오는데 실패했습니다',
        status: 'error',
        duration: 3000,
      });
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // 선택된 커리큘럼의 주차 목록 생성 (week_schedules가 없어도 total_weeks 기반으로 생성)
  const getSelectedCurriculumWeeks = () => {
    if (!summaryForm.curriculum_id) return [];
    
    const curriculum = curriculums.find(c => c.id === summaryForm.curriculum_id);
    if (!curriculum) return [];

    // 디버깅 로그 추가
    console.log('선택된 커리큘럼:', curriculum);
    console.log('week_schedules 존재 여부:', !!curriculum.week_schedules);
    console.log('week_schedules 길이:', curriculum.week_schedules?.length);

    if (curriculum.week_schedules && curriculum.week_schedules.length > 0) {
      console.log('실제 week_schedules 사용:', curriculum.week_schedules);
      return curriculum.week_schedules;
    } else if (curriculum.total_weeks) {
      console.log('임시 데이터 생성 - total_weeks:', curriculum.total_weeks);
      return Array.from({ length: curriculum.total_weeks }, (_, index) => ({
        week_number: index + 1,
        title: `${index + 1}주차 학습`,
        lessons: [`${index + 1}주차 학습 내용`]
      }));
    }
    
    return [];
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
          <Heading size="lg" color={textColor}>
            {selectedCurriculum ? `${selectedCurriculum.title} - 요약` : '학습 요약'}
          </Heading>
          <HStack>
            {selectedCurriculum && (
              <Button
                variant="outline"
                onClick={() => {
                  setCurrentView('list');
                  setSelectedCurriculum(null);
                  fetchData();
                }}
              >
                전체 보기
              </Button>
            )}
            <Button
              leftIcon={<AddIcon />}
              colorScheme="blue"
              onClick={onCreateModalOpen}
            >
              새 요약 작성
            </Button>
          </HStack>
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
                  {selectedCurriculum ? '이 커리큘럼에는 아직 작성된 요약이 없습니다' : '아직 작성된 요약이 없습니다'}
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
                        {summary.week_number}주차
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
                      {summary.snippet}
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
                          {week.week_number}주차: {week.title} ({week.lessons.length}개 레슨)
                        </option>
                      ))}
                    </Select>
                  </FormControl>
                )}

                {/* 선택된 주차의 레슨 정보 표시 */}
                {summaryForm.curriculum_id && summaryForm.week_number && (
                  <Box w="100%" p={3} bg="blue.50" borderRadius="md" borderColor={borderColor}>
                    <Text fontSize="sm" fontWeight="semibold" color="blue.700" mb={2}>
                      {summaryForm.week_number}주차 학습 내용:
                    </Text>
                    <VStack align="start" spacing={1}>
                      {getSelectedWeekLessons().map((lesson, index) => (
                        <Text key={index} fontSize="sm" color="blue.600">
                          • {lesson}
                        </Text>
                      ))}
                    </VStack>
                  </Box>
                )}

                <FormControl isRequired>
                  <FormLabel color={textColor}>요약 내용</FormLabel>
                  <Textarea
                    placeholder="학습한 내용을 요약해주세요... (최소 100자)"
                    value={summaryForm.content}
                    onChange={(e) => setSummaryForm({ ...summaryForm, content: e.target.value })}
                    color={textColor}
                    borderColor={borderColor}
                    rows={8}
                    minLength={100}
                  />
                  <Text fontSize="xs" color={secondaryTextColor} mt={1}>
                    {summaryForm.content.length}/5000자 (최소 100자 필요)
                  </Text>
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
                isDisabled={summaryForm.content.length < 100}
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
                    minLength={100}
                  />
                  <Text fontSize="xs" color={secondaryTextColor} mt={1}>
                    {summaryForm.content.length}/5000자 (최소 100자 필요)
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
                onClick={handleUpdateSummary}
                isLoading={submitting}
                loadingText="수정 중..."
                isDisabled={summaryForm.content.length < 100}
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
