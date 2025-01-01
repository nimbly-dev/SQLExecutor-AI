import React, { useState } from 'react';
import { Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoginForm from '../components/login_authentication/LoginForm';
import { loginApi } from '../services/authService'; 

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth(); 

  const [tenantID, setTenantID] = useState('');
  const [userID, setUserID] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    try {
      const response = await loginApi(tenantID, userID, password);

      if (response && response.JWT_TOKEN) {
        const token = response.JWT_TOKEN;

        localStorage.setItem('token', token);

        login();

        navigate('/getting-started');
      } else {
        setError('Invalid credentials. Please try again.');
      }
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
