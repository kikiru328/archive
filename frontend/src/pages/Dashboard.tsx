import {
  Box,
  Grid,
  Button,
  VStack,
  Heading,
  Container,
  Text,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();

  return (
    <Container maxW="6xl" py={8}>
      <VStack gap={8} align="stretch">
        <Heading>학습 대시보드</Heading>
        
        {/* 통계 카드 */}
        <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={6}>
          <Box p={6} bg="white" borderRadius="lg" shadow="md">
            <Text fontSize="sm" color="gray.500">진행 중인 커리큘럼</Text>
            <Text fontSize="2xl" fontWeight="bold">2</Text>
            <Text fontSize="sm">총 3개 중</Text>
          </Box>
          
          <Box p={6} bg="white" borderRadius="lg" shadow="md">
            <Text fontSize="sm" color="gray.500">학습 스트릭</Text>
            <Text fontSize="2xl" fontWeight="bold">15일</Text>
            <Text fontSize="sm">연속 학습 중</Text>
          </Box>
          
          <Box p={6} bg="white" borderRadius="lg" shadow="md">
            <Text fontSize="sm" color="gray.500">완료한 요약</Text>
            <Text fontSize="2xl" fontWeight="bold">12개</Text>
            <Text fontSize="sm">이번 달</Text>
          </Box>
        </Grid>

        {/* 빠른 액션 */}
        <Box>
          <Heading size="md" mb={4}>빠른 시작</Heading>
          <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
            <Button
              colorScheme="blue"
              size="lg"
              onClick={() => navigate('/curriculum')}
            >
              새 커리큘럼 생성
            </Button>
            <Button
              colorScheme="green"
              size="lg"
              onClick={() => navigate('/summary')}
            >
              요약 작성하기
            </Button>
          </Grid>
        </Box>

        {/* 최근 활동 */}
        <Box>
          <Heading size="md" mb={4}>최근 활동</Heading>
          <VStack gap={3} align="stretch">
            <Box p={4} bg="white" borderRadius="lg" shadow="sm">
              <Box>React 기초 - 1주차 요약 제출 완료</Box>
              <Box fontSize="sm" color="gray.500">2시간 전</Box>
            </Box>
            <Box p={4} bg="white" borderRadius="lg" shadow="sm">
              <Box>알고리즘 커리큘럼 생성</Box>
              <Box fontSize="sm" color="gray.500">1일 전</Box>
            </Box>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default Dashboard;
