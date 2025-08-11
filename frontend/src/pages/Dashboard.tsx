// src/pages/Dashboard.tsx - 소개 페이지로 변경
import {
  Box,
  Button,
  VStack,
  HStack,
  Heading,
  Container,
  Text,
  useColorModeValue,
  Card,
  CardBody,
  Grid,
  Icon,
  Image,
  Flex,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { StarIcon } from '@chakra-ui/icons';
import { RssIcon, HeartIcon, BookmarkIcon, UsersIcon } from '../components/icons/SimpleIcons';

const Dashboard = () => {
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem('token');
  
  // 다크모드 대응 색상
  const textColor = useColorModeValue('gray.900', 'white');
  const secondaryTextColor = useColorModeValue('gray.600', 'gray.300');
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const gradientBg = useColorModeValue(
    'linear(to-r, blue.400, purple.500)',
    'linear(to-r, blue.600, purple.700)'
  );
  const featureBg = useColorModeValue('blue.50', 'blue.900');

  const handleGetStarted = () => {
    if (isLoggedIn) {
      navigate('/curriculum');
    } else {
      navigate('/signup');
    }
  };

  const features = [
    {
      icon: ({ boxSize }: { boxSize: number }) => <Text fontSize={`${boxSize * 4}px`}>📚</Text>,
      title: 'AI 커리큘럼 생성',
      description: '목표와 기간을 입력하면 AI가 맞춤형 학습 커리큘럼을 자동으로 생성해드립니다.',
      color: 'blue',
    },
    {
      icon: StarIcon,
      title: '학습 요약 & 피드백',
      description: '학습한 내용을 요약하고 AI로부터 개인화된 피드백을 받아보세요.',
      color: 'green',
    },
    {
      icon: UsersIcon,
      title: '소셜 학습',
      description: '다른 학습자들과 커리큘럼을 공유하고 서로의 학습 여정을 응원해보세요.',
      color: 'purple',
    },
  ];

  const socialFeatures = [
    {
      icon: RssIcon,
      title: '커뮤니티 피드',
      description: '다른 사용자들의 학습 커리큘럼을 둘러보고 영감을 얻어보세요.',
    },
    {
      icon: HeartIcon,
      title: '좋아요 & 댓글',
      description: '마음에 드는 커리큘럼에 좋아요를 누르고 댓글로 소통하세요.',
    },
    {
      icon: BookmarkIcon,
      title: '북마크',
      description: '관심있는 커리큘럼을 북마크하여 나중에 쉽게 찾아보세요.',
    },
  ];

  return (
    <Container maxW="6xl" py={8}>
      <VStack spacing={16} align="stretch">
        {/* 히어로 섹션 */}
        <Box textAlign="center" py={12}>
          <VStack spacing={6}>
            <Heading 
              size="2xl" 
              bgGradient={gradientBg}
              bgClip="text"
              fontWeight="bold"
            >
              LLearn
            </Heading>
            <Heading size="lg" color={textColor} fontWeight="normal">
              AI가 만들어주는 맞춤형 학습 여정
            </Heading>
            <Text 
              fontSize="xl" 
              color={secondaryTextColor} 
              maxW="2xl" 
              lineHeight="tall"
            >
              당신의 학습 목표와 수준에 맞는 커리큘럼을 AI가 자동으로 생성해드립니다. 
              학습 과정을 기록하고, 피드백을 받으며, 다른 학습자들과 함께 성장해보세요.
            </Text>
            <HStack spacing={4} pt={4}>
              <Button
                size="lg"
                colorScheme="blue"
                onClick={handleGetStarted}
                px={8}
                py={6}
                fontSize="lg"
                rightIcon={<Text fontSize="lg">📚</Text>}
              >
                {isLoggedIn ? '내 커리큘럼 보기' : '사용해보기'}
              </Button>
              {!isLoggedIn && (
                <Button
                  size="lg"
                  variant="outline"
                  colorScheme="blue"
                  onClick={() => navigate('/feed')}
                  px={8}
                  py={6}
                  fontSize="lg"
                  rightIcon={<RssIcon />}
                >
                  둘러보기
                </Button>
              )}
            </HStack>
          </VStack>
        </Box>

        {/* 주요 기능 섹션 */}
        <Box>
          <VStack spacing={8}>
            <Heading size="lg" color={textColor} textAlign="center">
              주요 기능
            </Heading>
            <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={8}>
              {features.map((feature, index) => (
                <Card 
                  key={index} 
                  bg={cardBg} 
                  borderColor={borderColor}
                  _hover={{ transform: 'translateY(-4px)', shadow: 'lg' }}
                  transition="all 0.3s"
                >
                  <CardBody textAlign="center" py={8}>
                    <VStack spacing={4}>
                      <Box
                        p={4}
                        bg={featureBg}
                        borderRadius="full"
                        color={`${feature.color}.500`}
                      >
                        {typeof feature.icon === 'function' ? (
                          <feature.icon boxSize={8} />
                        ) : (
                          <Icon as={feature.icon} boxSize={8} />
                        )}
                      </Box>
                      <Heading size="md" color={textColor}>
                        {feature.title}
                      </Heading>
                      <Text color={secondaryTextColor} lineHeight="tall">
                        {feature.description}
                      </Text>
                    </VStack>
                  </CardBody>
                </Card>
              ))}
            </Grid>
          </VStack>
        </Box>

        {/* 소셜 기능 섹션 */}
        <Box bg={featureBg} py={12} borderRadius="lg">
          <Container maxW="4xl">
            <VStack spacing={8}>
              <VStack spacing={4} textAlign="center">
                <Heading size="lg" color={textColor}>
                  함께 배우는 즐거움
                </Heading>
                <Text fontSize="lg" color={secondaryTextColor} maxW="2xl">
                  혼자서는 어려운 학습도 커뮤니티와 함께라면 더욱 재미있고 지속가능해집니다.
                </Text>
              </VStack>
              <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={6}>
                {socialFeatures.map((feature, index) => (
                  <VStack key={index} spacing={3} textAlign="center">
                    <Box color="blue.500">
                      <feature.icon size="32px" />
                    </Box>
                    <Heading size="sm" color={textColor}>
                      {feature.title}
                    </Heading>
                    <Text fontSize="sm" color={secondaryTextColor}>
                      {feature.description}
                    </Text>
                  </VStack>
                ))}
              </Grid>
            </VStack>
          </Container>
        </Box>

        {/* 시작하기 CTA */}
        <Box textAlign="center" py={8}>
          <VStack spacing={6}>
            <Heading size="lg" color={textColor}>
              지금 바로 시작해보세요
            </Heading>
            <Text fontSize="lg" color={secondaryTextColor}>
              {isLoggedIn 
                ? '나만의 학습 커리큘럼을 만들어보세요!'
                : '무료로 회원가입하고 첫 번째 커리큘럼을 만들어보세요!'
              }
            </Text>
            <Button
              size="lg"
              colorScheme="blue"
              onClick={handleGetStarted}
              px={8}
              py={6}
              fontSize="lg"
            >
              {isLoggedIn ? '커리큘럼 만들기' : '무료로 시작하기'}
            </Button>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default Dashboard;
