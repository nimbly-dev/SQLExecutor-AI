import React from 'react';
import { Box, TextField, Button, Typography, Grid, Paper } from '@mui/material';

interface LoginFormProps {
  tenantID: string;
  userID: string;
  password: string;
  setTenantID: (value: string) => void;
  setUserID: (value: string) => void;
  setPassword: (value: string) => void;
  handleLogin: () => void;
  error: string | null;
}

const LoginForm: React.FC<LoginFormProps> = ({
  tenantID,
  userID,
  password,
  setTenantID,
  setUserID,
  setPassword,
  handleLogin,
  error,
}) => {
  return (
    <Paper
      elevation={3}
      sx={{
        display: 'flex',
        width: '800px',
        height: '500px',
        borderRadius: '10px',
        overflow: 'hidden',
      }}
    >
      <Grid container sx={{ height: '100%' }}>
        {/* Left Side Form */}
        <Grid
          item
          xs={6}
          sx={{
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            SQLExecutor
          </Typography>
          <Box component="form" sx={{ width: '100%' }}>
            <TextField
              fullWidth
              margin="normal"
              label="Tenant ID"
              variant="outlined"
              value={tenantID}
              onChange={(e) => setTenantID(e.target.value)}
            />
            <TextField
              fullWidth
              margin="normal"
              label="User ID"
              variant="outlined"
              value={userID}
              onChange={(e) => setUserID(e.target.value)}
            />
            <TextField
              fullWidth
              margin="normal"
              label="Password"
              type="password"
              variant="outlined"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button
              fullWidth
              variant="contained"
              color="primary"
              sx={{ marginTop: '20px' }}
              onClick={handleLogin}
            >
              Login
            </Button>
            {error && (
              <Typography color="error" sx={{ marginTop: '10px' }}>
                {error}
              </Typography>
            )}
          </Box>
        </Grid>

        {/* Right Side Image Placeholder */}
        <Grid
          item
          xs={6}
          sx={{
            height: '100%',
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography color="white">Visual Placeholder</Typography>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default LoginForm;
