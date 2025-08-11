// src/App.tsx - 프로필 라우트 추가
import { ChakraProvider, Box, extendTheme, ColorModeScript } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Curriculum from './pages/Curriculum';
import CurriculumDetail from './pages/CurriculumDetail';
import Summary from './pages/Summary';
import SummaryDetail from './pages/SummaryDetail';
import Feed from './pages/Feed';
import Bookmarks from './pages/Bookmarks';
import LikedCurriculums from './pages/LikedCurriculums';
import MyComments from './pages/MyComments';
import Profile from './pages/Profile';
import FollowList from './pages/FollowList';
import UserExplore from './pages/UserExplore';
// Chakra UI 테마 확장
const theme = extendTheme({
  config: {
    initialColorMode: 'light',
    useSystemColorMode: false,
  },
  styles: {
    global: (props: any) => ({
      body: {
        bg: props.colorMode === 'dark' ? 'gray.900' : 'gray.50',
      },
    }),
  },
  components: {
    Button: {
      defaultProps: {
        size: 'md',
      },
    },
  },
});

function App() {
  return (
    <>
      <ColorModeScript initialColorMode={theme.config.initialColorMode} />
      <ChakraProvider theme={theme}>
        <Router>
          <Box minH="100vh">
            <Header />
            <Routes>
              {/* 인증 관련 */}
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              
              {/* 메인 기능 */}
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/curriculum" element={<Curriculum />} />
              <Route path="/curriculum/:id" element={<CurriculumDetail />} />
              <Route path="/summary" element={<Summary />} />
              <Route path="/summary/:id" element={<SummaryDetail />} />
              
              {/* 소셜 기능 */}
              <Route path="/feed" element={<Feed />} />
              <Route path="/bookmarks" element={<Bookmarks />} />
              <Route path="/liked" element={<LikedCurriculums />} />
              <Route path="/social/liked" element={<LikedCurriculums />} />
              <Route path="/comments" element={<MyComments />} />
              <Route path="/social/comments" element={<MyComments />} />
              
              {/* 프로필 */}
              <Route path="/profile" element={<Profile />} />
              <Route path="/social/profile" element={<Profile />} />
              
              {/* ✅ 팔로우 관련 라우트 추가 */}
              <Route path="/social/follow" element={<FollowList />} />
              <Route path="/social/users/:userId/follow" element={<FollowList />} />
              <Route path="/social/explore" element={<UserExplore />} />
              
              {/* 기본 라우트 */}
              <Route path="/" element={<Dashboard />} />
            </Routes>
          </Box>
        </Router>
      </ChakraProvider>
    </>
  );
}

export default App;
