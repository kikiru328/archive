// src/App.tsx - 소셜 기능 라우트 추가
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
