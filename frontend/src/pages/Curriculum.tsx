// src/pages/Curriculum.tsx
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
  Grid,
  Badge,
  IconButton,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Input,
  Textarea,
  Select,
  FormControl,
  FormLabel,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  useColorModeValue,
} from '@chakra-ui/react';
import { AddIcon } from '@chakra-ui/icons';
import { useNavigate } from 'react-router-dom';
import { curriculumAPI, categoryAPI, curriculumTagAPI } from '../services/api';

interface WeekSchedule {
  week_number: number;
  title: string; 
  lessons: string[];
}

interface Curriculum {
  id: string;
  owner_id: string;
  title: string;
  visibility: 'PUBLIC' | 'PRIVATE';
  total_weeks: number;
  total_lessons: number;
  created_at: string;
  updated_at: string;
  week_schedules?: WeekSchedule[];
  category?: Category;
  tags?: Array<{ id: string; name: string; usage_count: number }>;
}
interface Category {
  id: string;
  name: string;
  color: string;
  icon?: string;
  is_active: boolean;
  usage_count: number;
}
interface CreateCurriculumForm {
  goal: string;
  period: number;
  difficulty: 'beginner' | 'intermediate' | 'expert';
  details: string;
  category_id: string;
}

const Curriculum: React.FC = () => {
  const navigate = useNavigate();
  const [curriculums, setCurriculums] = useState<Curriculum[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState<CreateCurriculumForm>({
    goal: '',
    period: 4,
    difficulty: 'beginner',
    details: '',
    category_id: ''
  });
  const [categories, setCategories] = useState<Category[]>([]);
  const [loadingCategories, setLoadingCategories] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  // 다크모드 대응 색상
  const bgColor = useColorModeValue('white', 'gray.800');
  const textColor = useColorModeValue('gray.900', 'white');
  const secondaryTextColor = useColorModeValue('gray.600', 'gray.300');
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    fetchMyCurriculums();
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      setLoadingCategories(true);
      const response = await categoryAPI.getActive();
      setCategories(response.data || []);
    } catch (error) {
      console.error('카테고리 조회 실패:', error);
    } finally {
      setLoadingCategories(false);
    }
  };

  const fetchMyCurriculums = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await curriculumAPI.getAll();
      console.log('커리큘럼 목록 응답:', response.data);
      
      let curriculumData = [];
      if (response.data && response.data.curriculums) {
        curriculumData = response.data.curriculums;
      } else if (Array.isArray(response.data)) {
        curriculumData = response.data;
      } else {
        console.warn('예상하지 못한 응답 구조:', response.data);
        curriculumData = [];
      }

      // 각 커리큘럼의 카테고리/태그 정보 로드
      const curriculumsWithCategories = await loadCurriculumCategories(curriculumData);
      setCurriculums(curriculumsWithCategories);
    } catch (error: any) {
      console.error('커리큘럼 조회 실패:', error);
      setError('커리큘럼을 불러오는데 실패했습니다.');
      setCurriculums([]);
    } finally {
      setLoading(false);
    }
  };

  const loadCurriculumCategories = async (curriculums: Curriculum[]) => {
    const updatedCurriculums = await Promise.all(
      curriculums.map(async (curriculum) => {
        try {
          const response = await curriculumTagAPI.getTagsAndCategory(curriculum.id);
          return {
            ...curriculum,
            category: response.data.category,
            tags: response.data.tags
          };
        } catch (error) {
          console.log(`커리큘럼 ${curriculum.id}의 태그/카테고리 정보 없음`);
          return curriculum;
        }
      })
    );
    return updatedCurriculums;
  };

  const handleCreateCurriculum = async () => {
    if (!form.goal.trim()) {
      toast({
        title: '목표를 입력해주세요',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    try {
      setCreating(true);
      const response = await curriculumAPI.create({
        goal: form.goal,
        duration: form.period,
        difficulty: form.difficulty,
        details: form.details
      });
      
      console.log('커리큘럼 생성 성공:', response.data);

      if (form.category_id) {
        try {
          await curriculumTagAPI.assignCategory(response.data.id, form.category_id);
          console.log('카테고리 할당 성공');
        } catch (error) {
          console.warn('카테고리 할당 실패:', error);
          // 카테고리 할당 실패해도 커리큘럼 생성은 성공으로 처리
        }
      }
      
      toast({
        title: '커리큘럼이 생성되었습니다!',
        status: 'success',
        duration: 3000,
      });
      
      setForm({
        goal: '',
        period: 4,
        difficulty: 'beginner',
        details: '',
        category_id: ''
      });
      onClose();
      fetchMyCurriculums();
    } catch (error: any) {
      console.error('커리큘럼 생성 실패:', error);
      
      let errorMessage = '커리큘럼 생성에 실패했습니다';
      
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          // 배열인 경우 각 에러의 msg 속성만 추출
          errorMessage = error.response.data.detail
            .map((err: any) => {
              if (typeof err === 'object' && err.msg) {
                return err.msg;
              }
              return String(err);
            })
            .join(', ');
        } else {
          errorMessage = String(error.response.data.detail);
        }
      } else if (error.response?.data?.message) {
        errorMessage = String(error.response.data.message);
      } else if (error.message) {
        errorMessage = String(error.message);
      }
      
      toast({
        title: '커리큘럼 생성 실패',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setCreating(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getVisibilityColor = (visibility: string) => {
    return visibility === 'PUBLIC' ? 'green' : 'gray';
  };

  const getVisibilityText = (visibility: string) => {
    return visibility === 'PUBLIC' ? '공개' : '비공개';
  };

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

  return (
    <Container maxW="6xl" py={8}>
      <VStack spacing={6} align="stretch">
        {/* 헤더 */}
        <HStack justify="space-between" align="center">
          <Heading size="lg" color={textColor}>내 커리큘럼</Heading>
          <Button
            leftIcon={<AddIcon />}
            colorScheme="blue"
            onClick={onOpen}
          >
            새 커리큘럼 생성
          </Button>
        </HStack>

        {/* 에러 메시지 */}
        {error && (
          <Alert status="error">
            <AlertIcon />
            <AlertDescription color={textColor}>{error}</AlertDescription>
          </Alert>
        )}

        {/* 커리큘럼 목록 */}
        {curriculums.length === 0 ? (
          <Box textAlign="center" py={10} bg={cardBg} borderRadius="lg" borderWidth="1px" borderColor={borderColor}>
            <Text fontSize="lg" color={secondaryTextColor} mb={4}>
              아직 생성된 커리큘럼이 없습니다
            </Text>
            <Button
              colorScheme="blue"
              leftIcon={<AddIcon />}
              onClick={onOpen}
            >
              첫 번째 커리큘럼 만들기
            </Button>
          </Box>
        ) : (
          <Grid templateColumns="repeat(auto-fill, minmax(300px, 1fr))" gap={6}>
            {curriculums.map((curriculum) => (
              <Card 
                key={curriculum.id} 
                variant="outline" 
                bg={cardBg} 
                borderColor={borderColor}
                cursor="pointer"
                transition="all 0.2s"
                _hover={{ 
                  transform: "translateY(-2px)", 
                  shadow: "lg",
                  borderColor: "blue.300"
                }}
                onClick={() => navigate(`/curriculum/${curriculum.id}`)}
              >
                <CardBody>
                  <VStack align="stretch" spacing={3}>
                    {/* 헤더와 카테고리 */}
                    <VStack align="stretch" spacing={2}>
                      <HStack justify="space-between" align="start">
                        <Heading size="md" noOfLines={2} color={textColor}>
                          {curriculum.title}
                        </Heading>
                        <Badge
                          colorScheme={getVisibilityColor(curriculum.visibility)}
                          variant="solid"
                        >
                          {getVisibilityText(curriculum.visibility)}
                        </Badge>
                      </HStack>

                      {/* 카테고리 표시 */}
                      {curriculum.category && (
                        <HStack>
                          <Badge
                            style={{ backgroundColor: curriculum.category.color }}
                            color="white"
                            variant="solid"
                            size="sm"
                          >
                            {curriculum.category.icon && `${curriculum.category.icon} `}
                            {curriculum.category.name}
                          </Badge>
                        </HStack>
                      )}

                      {/* 태그 표시 */}
                      {curriculum.tags && curriculum.tags.length > 0 && (
                        <HStack flexWrap="wrap" spacing={1}>
                          {curriculum.tags.slice(0, 3).map((tag) => (
                            <Badge
                              key={tag.id}
                              colorScheme="gray"
                              variant="outline"
                              size="sm"
                            >
                              #{tag.name}
                            </Badge>
                          ))}
                          {curriculum.tags.length > 3 && (
                            <Badge
                              colorScheme="gray"
                              variant="outline"
                              size="sm"
                            >
                              +{curriculum.tags.length - 3}
                            </Badge>
                          )}
                        </HStack>
                      )}
                    </VStack>

                    {/* 통계 */}
                    <HStack spacing={4} fontSize="sm" color={secondaryTextColor}>
                      <Text>{curriculum.total_weeks}주차</Text>
                      <Text>{curriculum.total_lessons}개 레슨</Text>
                    </HStack>

                    {/* 날짜 */}
                    <Text fontSize="xs" color={secondaryTextColor}>
                      생성일: {formatDate(curriculum.created_at)}
                    </Text>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </Grid>
        )}

        {/* 커리큘럼 생성 모달 */}
        <Modal isOpen={isOpen} onClose={onClose} size="lg">
          <ModalOverlay />
          <ModalContent bg={cardBg} color={textColor}>
            <ModalHeader color={textColor}>새 커리큘럼 생성</ModalHeader>
            <ModalCloseButton color={textColor} />
            <ModalBody>
              <VStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel color={textColor}>학습 목표</FormLabel>
                  <Input
                    placeholder="예: React 웹 개발 마스터하기"
                    value={form.goal}
                    onChange={(e) => setForm({ ...form, goal: e.target.value })}
                    color={textColor}
                    borderColor={borderColor}
                    _placeholder={{ color: secondaryTextColor }}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel color={textColor}>학습 기간 (주)</FormLabel>
                  <Select
                    value={form.period}
                    onChange={(e) => setForm({ ...form, period: parseInt(e.target.value) })}
                    color={textColor}
                    borderColor={borderColor}
                  >
                    {Array.from({ length: 24 }, (_, i) => i + 1).map((week) => (
                      <option key={week} value={week} style={{ backgroundColor: cardBg, color: textColor }}>
                        {week}주
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel color={textColor}>난이도</FormLabel>
                  <Select
                    value={form.difficulty}
                    onChange={(e) => setForm({ ...form, difficulty: e.target.value as any })}
                    color={textColor}
                    borderColor={borderColor}
                  >
                    <option value="beginner" style={{ backgroundColor: cardBg, color: textColor }}>초급</option>
                    <option value="intermediate" style={{ backgroundColor: cardBg, color: textColor }}>중급</option>
                    <option value="expert" style={{ backgroundColor: cardBg, color: textColor }}>고급</option>
                  </Select>
                </FormControl>
                <FormControl>
                  <FormLabel color={textColor}>카테고리 (선택사항)</FormLabel>
                  <Select
                    value={form.category_id}
                    onChange={(e) => setForm({ ...form, category_id: e.target.value })}
                    color={textColor}
                    borderColor={borderColor}
                    placeholder="카테고리를 선택하세요"
                  >
                    {categories.map((category) => (
                      <option key={category.id} value={category.id} style={{ backgroundColor: cardBg, color: textColor }}>
                        {category.icon && `${category.icon} `}{category.name}
                      </option>
                    ))}
                  </Select>
                  {loadingCategories && (
                    <Text fontSize="xs" color={secondaryTextColor} mt={1}>
                      카테고리 로딩 중...
                    </Text>
                  )}
                  {categories.length === 0 && !loadingCategories && (
                    <Text fontSize="xs" color={secondaryTextColor} mt={1}>
                      사용 가능한 카테고리가 없습니다
                    </Text>
                  )}
                </FormControl>
                <FormControl>
                  <FormLabel color={textColor}>추가 세부사항</FormLabel>
                  <Textarea
                    placeholder="특별한 요구사항이나 학습 방향을 입력해주세요"
                    value={form.details}
                    onChange={(e) => setForm({ ...form, details: e.target.value })}
                    rows={3}
                    color={textColor}
                    borderColor={borderColor}
                    _placeholder={{ color: secondaryTextColor }}
                  />
                </FormControl>
              </VStack>
            </ModalBody>

            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onClose} color={textColor}>
                취소
              </Button>
              <Button
                colorScheme="blue"
                onClick={handleCreateCurriculum}
                isLoading={creating}
                loadingText="생성 중..."
              >
                생성하기
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Container>
  );
};

export default Curriculum;
