import { ChakraProvider, Box, extendTheme, ColorModeScript } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Curriculum from './pages/Curriculum';
import CurriculumDetail from './pages/CurriculumDetail';

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
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/curriculum" element={<Curriculum />} />
              <Route path="/curriculum/:id" element={<CurriculumDetail />} />
              <Route path="/" element={<Dashboard />} />
            </Routes>
          </Box>
        </Router>
      </ChakraProvider>
    </>
  );
}

export default App;
