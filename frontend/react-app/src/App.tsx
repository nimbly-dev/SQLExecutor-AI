import React, { useState } from 'react';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import { lightTheme } from './themes/lightTheme';
import { darkTheme } from './themes/darkTheme';
import MyAccount from './components/account/MyAccount';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import LandingPage from './pages/LandingPage';
import { AuthProvider } from './contexts/AuthContext'; 

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false);
  const toggleTheme = () => setDarkMode(!darkMode);

  return (
    <AuthProvider> {/* Wrap the entire app in AuthProvider */}
      <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
        <CssBaseline />
        <Router>
          <Box
            sx={{
              height: '100vh',
              width: '100vw',
              bgcolor: 'background.default',
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            {/* My Account Component */}
            <Box sx={{ position: 'absolute', top: 10, right: 10 }}>
              <MyAccount darkMode={darkMode} toggleTheme={toggleTheme} />
            </Box>

            {/* Routes */}
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/getting-started" element={<LandingPage />} />
            </Routes>
          </Box>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
};

export default App;
