import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

function NotFoundPage(){
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
        404 - Page Not Found
      </Typography>
      <Typography variant="h6" color="text.secondary" textAlign="center" gutterBottom>
        Sorry, the page you are looking for does not exist.
      </Typography>
      <Button
        variant="contained"
        color="primary"
        sx={{ marginTop: '20px' }}
        onClick={() => navigate('/')}
      >
        Go Home
      </Button>
    </Box>
  );
}

export default NotFoundPage;
