import React, { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoginForm from '../components/login_authentication/LoginForm';
import { loginAdmin } from '../services/authService';
import Cookies from 'js-cookie';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth(); // Auth Context

  // States
  const [tenantID, setTenantID] = useState('');
  const [userID, setUserID] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Automatically log in if token exists
  useEffect(() => {
    const token = Cookies.get('token');
    if (token) {
      login(); // Update Auth Context
      navigate('/getting-started'); // Redirect to protected route
    }
  }, [login, navigate]); // Only runs once on component mount

  // Login Handler
  const handleLogin = async () => {
    try {
      await loginAdmin(tenantID, userID, password); // Login via API

      // Update Auth Context
      login();
      navigate('/getting-started'); // Redirect to protected route
    } catch (err) {
      console.error('Login error:', err);
      setError('Failed to login. Please check your credentials and try again.');
    }
  };

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
      }}
    >
      <LoginForm
        tenantID={tenantID}
        userID={userID}
        password={password}
        setTenantID={setTenantID}
        setUserID={setUserID}
        setPassword={setPassword}
        handleLogin={handleLogin}
        error={error}
      />
    </Box>
  );
};

export default LoginPage;
