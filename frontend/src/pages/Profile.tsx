// src/pages/Profile.tsx
import React, { useState, useEffect } from 'react';
import {
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Card,
  CardBody,
  Button,
  Grid,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  useColorModeValue,
  Box,
  Badge,
  Avatar,
  Divider,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Input,
  FormControl,
  FormLabel,
  useToast,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  IconButton,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { authAPI, followAPI, curriculumAPI, summaryAPI, feedbackAPI, userAPI } from '../services/api';
import { UsersIcon, HeartIcon, CommentIcon, BookmarkIcon } from '../components/icons/SimpleIcons';
import { EditIcon } from '@chakra-ui/icons';
import { getCurrentUserId } from '../utils/auth';

interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: string;
  created_at: string;
  updated_at: string;
}

interface FollowStats {
  followers_count: number;
  followees_count: number;
}

interface ActivityStats {
  curriculum_count: number;
  summary_count: number;
  feedback_count: number;
  avg_score?: number;
}

interface UpdateProfileForm {
  name: string;
  password: string;
}

const Profile: React.FC = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [followStats, setFollowStats] = useState<FollowStats | null>(null);
  const [activityStats, setActivityStats] = useState<ActivityStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState('');
  
  const [updateForm, setUpdateForm] = useState<UpdateProfileForm>({
    name: '',
    password: ''
  });
  
  const { isOpen: isEditModalOpen, onOpen: onEditModalOpen, onClose: onEditModalClose } = useDisclosure();

  const textColor = useColorModeValue('gray.900', 'white');
  const secondaryTextColor = useColorModeValue('gray.600', 'gray.300');
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const statBg = useColorModeValue('blue.50', 'blue.900');
  const highlightBg = useColorModeValue('gray.50', 'gray.800');

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // 프로필 정보 가져오기
      const profileResponse = await userAPI.getProfile(); // ✅ userAPI 사용
      setProfile(profileResponse.data);
      
      // 팔로우 통계 가져오기
      const currentUserId = getCurrentUserId();
      if (currentUserId) {
        try {
          const followResponse = await followAPI.getFollowStats(currentUserId);
          setFollowStats(followResponse.data);
        } catch (error) {
          console.log('팔로우 통계 조회 실패 - 서비스가 준비되지 않음');
        }
        
        // 활동 통계 계산
        await calculateActivityStats();
      }
      
    } catch (error: any) {
      console.error('프로필 조회 실패:', error);
      setError('프로필 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const calculateActivityStats = async () => {
    try {
      const [curriculumResponse, summaryResponse, feedbackResponse] = await Promise.all([
        curriculumAPI.getAll({ page: 1, items_per_page: 1 }),
        summaryAPI.getAll({ page: 1, items_per_page: 1 }),
        feedbackAPI.getAll({ page: 1, items_per_page: 100 }) // 평균 점수 계산을 위해 더 많이 가져오기
      ]);

      const curriculumCount = curriculumResponse.data?.total_count || 0;
      const summaryCount = summaryResponse.data?.total_count || 0;
      const feedbacks = feedbackResponse.data?.feedbacks || [];
      const feedbackCount = feedbacks.length;
      
      // 평균 점수 계산
      let avgScore = undefined;
      if (feedbacks.length > 0) {
        const totalScore = feedbacks.reduce((sum: number, feedback: any) => sum + (feedback.score || 0), 0);
        avgScore = totalScore / feedbacks.length;
      }

      setActivityStats({
        curriculum_count: curriculumCount,
        summary_count: summaryCount,
        feedback_count: feedbackCount,
        avg_score: avgScore
      });
    } catch (error) {
      console.error('활동 통계 계산 실패:', error);
    }
  };

  const handleEditProfile = () => {
    if (profile) {
      setUpdateForm({
        name: profile.name,
        password: ''
      });
      onEditModalOpen();
    }
  };

  const handleUpdateProfile = async () => {
    if (!updateForm.name.trim()) {
      toast({
        title: '이름을 입력해주세요',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    try {
      setUpdating(true);
      
      // 실제 API 호출
      await userAPI.updateProfile({
        name: updateForm.name.trim(),
        ...(updateForm.password.trim() && { password: updateForm.password.trim() })
      });
      
      toast({
        title: '프로필이 수정되었습니다',
        status: 'success',
        duration: 3000,
      });
      
      onEditModalClose();
      await fetchProfileData(); // 프로필 정보 새로고침
    } catch (error: any) {
      console.error('프로필 수정 실패:', error);
      
      let errorMessage = '프로필 수정에 실패했습니다';
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail
            .map((err: any) => err.msg || JSON.stringify(err))
            .join(', ');
        } else {
          errorMessage = error.response.data.detail;
        }
      }
      
      toast({
        title: errorMessage,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setUpdating(false);
    }
  };


  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getRoleText = (role: string) => {
    return role === 'ADMIN' ? '관리자' : '사용자';
  };

  const getRoleColor = (role: string) => {
    return role === 'ADMIN' ? 'purple' : 'blue';
  };

  if (loading) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text color={textColor}>프로필을 불러오는 중...</Text>
        </VStack>
      </Container>
    );
  }

  if (error || !profile) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={4}>
          <Alert status="error">
            <AlertIcon />
            <AlertDescription>{error || '프로필 정보를 찾을 수 없습니다.'}</AlertDescription>
          </Alert>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="6xl" py={8}>
      <VStack spacing={6} align="stretch">
        {/* 프로필 헤더 */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack spacing={6}>
              {/* 기본 정보 */}
              <HStack spacing={6} align="start" w="100%">
                <Avatar name={profile.name} size="2xl" />
                <VStack align="start" flex={1} spacing={3}>
                  <HStack justify="space-between" w="100%">
                    <VStack align="start" spacing={1}>
                      <HStack>
                        <Heading size="lg" color={textColor}>{profile.name}</Heading>
                        <Badge 
                          colorScheme={getRoleColor(profile.role)} 
                          variant="solid"
                        >
                          {getRoleText(profile.role)}
                        </Badge>
                      </HStack>
                      <Text color={secondaryTextColor}>{profile.email}</Text>
                      <Text fontSize="sm" color={secondaryTextColor}>
                        가입일: {formatDate(profile.created_at)}
                      </Text>
                    </VStack>
                    
                    <IconButton
                      aria-label="프로필 수정"
                      icon={<EditIcon />}
                      colorScheme="blue"
                      variant="outline"
                      onClick={handleEditProfile}
                    />
                  </HStack>
                </VStack>
              </HStack>

              <Divider />

              {/* 통계 정보 */}
              <Grid templateColumns="repeat(auto-fit, minmax(150px, 1fr))" gap={6} w="100%">
                {/* 팔로우 통계 */}
                {followStats && (
                  <>
                    <Stat 
                      textAlign="center" 
                      bg={statBg} 
                      p={4} 
                      borderRadius="md"
                      cursor="pointer" // ✅ 추가
                      _hover={{ transform: 'scale(1.02)', shadow: 'md' }} // ✅ 추가
                      transition="all 0.2s" // ✅ 추가
                      onClick={() => navigate('/social/follow?tab=followers')} // ✅ 추가
                    >
                      <StatLabel color={secondaryTextColor}>팔로워</StatLabel>
                      <StatNumber color={textColor}>{followStats.followers_count}</StatNumber>
                      <StatHelpText color={secondaryTextColor}>
                        <UsersIcon style={{ display: 'inline', marginRight: '4px' }} />
                        명이 팔로우
                      </StatHelpText>
                    </Stat>
                    
                    <Stat 
                      textAlign="center" 
                      bg={statBg} 
                      p={4} 
                      borderRadius="md"
                      cursor="pointer" // ✅ 추가
                      _hover={{ transform: 'scale(1.02)', shadow: 'md' }} // ✅ 추가
                      transition="all 0.2s" // ✅ 추가
                      onClick={() => navigate('/social/follow?tab=following')} // ✅ 추가
                    >
                      <StatLabel color={secondaryTextColor}>팔로잉</StatLabel>
                      <StatNumber color={textColor}>{followStats.followees_count}</StatNumber>
                      <StatHelpText color={secondaryTextColor}>
                        <UsersIcon style={{ display: 'inline', marginRight: '4px' }} />
                        명을 팔로우
                      </StatHelpText>
                    </Stat>
                  </>
                )}

                {/* 활동 통계 */}
                {activityStats && (
                  <>
                    <Stat textAlign="center" bg={highlightBg} p={4} borderRadius="md">
                      <StatLabel color={secondaryTextColor}>커리큘럼</StatLabel>
                      <StatNumber color={textColor}>{activityStats.curriculum_count}</StatNumber>
                      <StatHelpText color={secondaryTextColor}>개 생성</StatHelpText>
                    </Stat>
                    
                    <Stat textAlign="center" bg={highlightBg} p={4} borderRadius="md">
                      <StatLabel color={secondaryTextColor}>학습 요약</StatLabel>
                      <StatNumber color={textColor}>{activityStats.summary_count}</StatNumber>
                      <StatHelpText color={secondaryTextColor}>개 작성</StatHelpText>
                    </Stat>
                    
                    <Stat textAlign="center" bg={highlightBg} p={4} borderRadius="md">
                      <StatLabel color={secondaryTextColor}>AI 피드백</StatLabel>
                      <StatNumber color={textColor}>{activityStats.feedback_count}</StatNumber>
                      <StatHelpText color={secondaryTextColor}>
                        {activityStats.avg_score && (
                          <>평균 {activityStats.avg_score.toFixed(1)}점</>
                        )}
                      </StatHelpText>
                    </Stat>
                  </>
                )}
              </Grid>
            </VStack>
          </CardBody>
        </Card>

        {/* 탭 섹션 */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <Tabs colorScheme="blue">
              <TabList>
                <Tab>내 활동</Tab>
                <Tab>소셜</Tab>
                <Tab>설정</Tab>
              </TabList>

              <TabPanels>
                {/* 내 활동 탭 */}
                <TabPanel>
                  <VStack spacing={4} align="stretch">
                    <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
                      <VStack>
                        <Button
                          variant="outline"
                          height="80px"
                          onClick={() => navigate('/curriculum')}
                          w="100%"
                        >
                          <VStack spacing={2}>
                            <Text fontWeight="bold">내 커리큘럼</Text>
                            <Text fontSize="sm" color={secondaryTextColor}>
                              {activityStats?.curriculum_count || 0}개
                            </Text>
                          </VStack>
                        </Button>
                      </VStack>
                      
                      <VStack>
                        <Button
                          variant="outline"
                          height="80px"
                          onClick={() => navigate('/summary')}
                          w="100%"
                        >
                          <VStack spacing={2}>
                            <Text fontWeight="bold">학습 요약</Text>
                            <Text fontSize="sm" color={secondaryTextColor}>
                              {activityStats?.summary_count || 0}개
                            </Text>
                          </VStack>
                        </Button>
                      </VStack>
                      
                      <VStack>
                        <Button
                          variant="outline"
                          height="80px"
                          onClick={() => navigate('/bookmarks')}
                          w="100%"
                        >
                          <VStack spacing={2}>
                            <BookmarkIcon style={{ fontSize: '20px' }} />
                            <Text fontWeight="bold">북마크</Text>
                          </VStack>
                        </Button>
                      </VStack>
                      
                      <VStack>
                        <Button
                          variant="outline"
                          height="80px"
                          onClick={() => navigate('/social/comments')}
                          w="100%"
                        >
                          <VStack spacing={2}>
                            <CommentIcon style={{ fontSize: '20px' }} />
                            <Text fontWeight="bold">내 댓글</Text>
                          </VStack>
                        </Button>
                      </VStack>
                    </Grid>
                  </VStack>
                </TabPanel>

                {/* 소셜 탭 */}
                <TabPanel>
                  <VStack spacing={4} align="stretch">
                    <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
                      <VStack>
                        <Button
                          variant="outline"
                          height="80px"
                          onClick={() => navigate('/social/liked')}
                          w="100%"
                        >
                          <VStack spacing={2}>
                            <HeartIcon style={{ fontSize: '20px' }} />
                            <Text fontWeight="bold">좋아요한 글</Text>
                          </VStack>
                        </Button>
                      </VStack>
                      
                      <VStack>
                        <Button
                          variant="outline"
                          height="80px"
                          onClick={() => navigate('/feed')}
                          w="100%"
                        >
                          <VStack spacing={2}>
                            <Text fontWeight="bold">커뮤니티 피드</Text>
                            <Text fontSize="sm" color={secondaryTextColor}>
                              둘러보기
                            </Text>
                          </VStack>
                        </Button>
                      </VStack>
                      
                      {followStats && (
                        <>
                          <VStack>
                            <Button
                              variant="outline"
                              height="80px"
                              w="100%"
                              onClick={() => navigate('/social/follow?tab=followers')} // ✅ 이 부분 수정
                            >
                              <VStack spacing={2}>
                                <Text fontWeight="bold">팔로워</Text>
                                <Text fontSize="sm" color={secondaryTextColor}>
                                  {followStats.followers_count}명
                                </Text>
                              </VStack>
                            </Button>
                          </VStack>
                          
                          <VStack>
                            <Button
                              variant="outline"
                              height="80px"
                              w="100%"
                              onClick={() => navigate('/social/follow?tab=following')} // ✅ 이 부분 수정
                            >
                              <VStack spacing={2}>
                                <Text fontWeight="bold">팔로잉</Text>
                                <Text fontSize="sm" color={secondaryTextColor}>
                                  {followStats.followees_count}명
                                </Text>
                              </VStack>
                            </Button>
                          </VStack>
                        </>
                      )}
                    </Grid>
                  </VStack>
                </TabPanel>

                {/* 설정 탭 */}
                <TabPanel>
                  <VStack spacing={4} align="stretch">
                    <Button
                      colorScheme="blue"
                      variant="outline"
                      onClick={handleEditProfile}
                      size="lg"
                    >
                      프로필 정보 수정
                    </Button>
                    
                    <Button
                      colorScheme="red"
                      variant="outline"
                      onClick={() => {
                        localStorage.removeItem('token');
                        navigate('/login');
                        toast({
                          title: '로그아웃되었습니다',
                          status: 'success',
                          duration: 3000,
                        });
                      }}
                      size="lg"
                    >
                      로그아웃
                    </Button>
                  </VStack>
                </TabPanel>
              </TabPanels>
            </Tabs>
          </CardBody>
        </Card>

        {/* 프로필 수정 모달 */}
        <Modal isOpen={isEditModalOpen} onClose={onEditModalClose}>
          <ModalOverlay />
          <ModalContent bg={cardBg} color={textColor}>
            <ModalHeader>프로필 수정</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel color={textColor}>이름</FormLabel>
                  <Input
                    value={updateForm.name}
                    onChange={(e) => setUpdateForm({ ...updateForm, name: e.target.value })}
                    color={textColor}
                    borderColor={borderColor}
                    placeholder="2-32자 한글/영문/숫자"
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel color={textColor}>새 비밀번호</FormLabel>
                  <Input
                    type="password"
                    value={updateForm.password}
                    onChange={(e) => setUpdateForm({ ...updateForm, password: e.target.value })}
                    color={textColor}
                    borderColor={borderColor}
                    placeholder="변경하지 않으려면 비워두세요"
                  />
                  <Text fontSize="xs" color={secondaryTextColor} mt={1}>
                    8-64자, 대소문자/숫자/특수문자 포함
                  </Text>
                </FormControl>
                
                <Box w="100%" p={3} bg={highlightBg} borderRadius="md">
                  <Text fontSize="sm" color={secondaryTextColor}>
                    <strong>참고:</strong> 이메일은 보안상의 이유로 변경할 수 없습니다.
                  </Text>
                </Box>
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onEditModalClose}>
                취소
              </Button>
              <Button 
                colorScheme="blue" 
                onClick={handleUpdateProfile}
                isLoading={updating}
                loadingText="수정 중..."
                isDisabled={!updateForm.name.trim()}
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

export default Profile;
