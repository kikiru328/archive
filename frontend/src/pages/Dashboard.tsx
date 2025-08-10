import {
  Box,
  Grid,
  Button,
  VStack,
  Heading,
  Container,
  Text,
  useColorModeValue,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();
  
  // 다크모드 대응 색상
  const textColor = useColorModeValue('gray.900', 'white');
  const secondaryTextColor = useColorModeValue('gray.500', 'gray.400');
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  return (
    <Container maxW="6xl" py={8}>
      <VStack gap={8} align="stretch">
        <Heading color={textColor}>학습 대시보드</Heading>
        
        {/* 통계 카드 */}
        <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={6}>
          <Box p={6} bg={cardBg} borderRadius="lg" shadow="md" borderWidth="1px" borderColor={borderColor}>
            <Text fontSize="sm" color={secondaryTextColor}>진행 중인 커리큘럼</Text>
            <Text fontSize="2xl" fontWeight="bold" color={textColor}>2</Text>
            <Text fontSize="sm" color={secondaryTextColor}>총 3개 중</Text>
          </Box>
          
          <Box p={6} bg={cardBg} borderRadius="lg" shadow="md" borderWidth="1px" borderColor={borderColor}>
            <Text fontSize="sm" color={secondaryTextColor}>학습 스트릭</Text>
            <Text fontSize="2xl" fontWeight="bold" color={textColor}>15일</Text>
            <Text fontSize="sm" color={secondaryTextColor}>연속 학습 중</Text>
          </Box>
          
          <Box p={6} bg={cardBg} borderRadius="lg" shadow="md" borderWidth="1px" borderColor={borderColor}>
            <Text fontSize="sm" color={secondaryTextColor}>완료한 요약</Text>
            <Text fontSize="2xl" fontWeight="bold" color={textColor}>12개</Text>
            <Text fontSize="sm" color={secondaryTextColor}>이번 달</Text>
          </Box>
        </Grid>

        {/* 빠른 액션 */}
        <Box>
          <Heading size="md" mb={4} color={textColor}>빠른 시작</Heading>
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
          <Heading size="md" mb={4} color={textColor}>최근 활동</Heading>
          <VStack gap={3} align="stretch">
            <Box p={4} bg={cardBg} borderRadius="lg" shadow="sm" borderWidth="1px" borderColor={borderColor}>
              <Box color={textColor}>React 기초 - 1주차 요약 제출 완료</Box>
              <Box fontSize="sm" color={secondaryTextColor}>2시간 전</Box>
            </Box>
            <Box p={4} bg={cardBg} borderRadius="lg" shadow="sm" borderWidth="1px" borderColor={borderColor}>
              <Box color={textColor}>알고리즘 커리큘럼 생성</Box>
              <Box fontSize="sm" color={secondaryTextColor}>1일 전</Box>
            </Box>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default Dashboard;
