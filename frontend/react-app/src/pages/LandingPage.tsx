import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

function LandingPage () {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        padding: '20px',
      }}
    >
      <Typography variant="h2" fontWeight="bold" gutterBottom>
        Welcome to SQLExecutor
      </Typography>
      <Typography variant="h6" color="text.secondary" textAlign="center" gutterBottom>
        Test SQL Queries, Manage Schemas, Explore APIs, and Configure Access Rules—all in one place.
      </Typography>
      <Box sx={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
        <Button variant="contained" color="primary" onClick={() => navigate('/sqlexecutor-playground')}>Get Started</Button>
        <Button variant="outlined" onClick={() => navigate('/login')}>Login</Button>
      </Box>
    </Box>
  );
};

export default LandingPage;
