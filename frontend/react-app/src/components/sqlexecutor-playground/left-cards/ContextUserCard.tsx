import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Stack,
} from '@mui/material';
import { ExternalSessionData } from '../../../types/authentication/externalUserSessionData';

interface ContextUserCardProps {
  sessionData: ExternalSessionData | null;
  onImpersonateClick: () => void;
  onStopImpersonation: () => void;
}

const ContextUserCard: React.FC<ContextUserCardProps> = ({
  sessionData,
  onImpersonateClick,
  onStopImpersonation,
}) => {
  const handleStopImpersonation = () => {
    onStopImpersonation();
    sessionStorage.removeItem('contextUserSessionId');
  };

  if (!sessionData) {
    return (
      <Card>
        <CardContent sx={{ padding: '10px' }}>
          <Typography
            variant="h6"
            sx={{
              fontSize: '18px',
              fontWeight: 'bold',
              borderBottom: (theme) =>
                `1px solid ${
                  theme.palette.mode === 'dark' ? '#444444' : '#e0e0e0'
                }`,
              paddingBottom: '10px',
              marginBottom: '10px',
            }}
          >
            Context User Impersonation
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={onImpersonateClick}
            fullWidth
            sx={{ mt: 2 }}
          >
            Impersonate User
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent sx={{ padding: '10px' }}>
        <Typography
          variant="h6"
          sx={{
            fontSize: '18px',
            fontWeight: 'bold',
            borderBottom: (theme) =>
              `1px solid ${
                theme.palette.mode === 'dark' ? '#444444' : '#e0e0e0'
              }`,
            paddingBottom: '10px',
            marginBottom: '10px',
          }}
        >
          Context User Impersonation
        </Typography>
        <Typography variant="subtitle1">
          Context User Impersonated: {sessionData.user_id}
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Custom Fields:
          </Typography>
          <Box component="ul" sx={{ 
            listStyle: 'disc',
            pl: 4, // Add left padding for the bullets
            '& li': {
              mb: 0.5, // Add some space between list items
            }
          }}>
            {Object.entries(sessionData.custom_fields).map(([key, value]) => (
              <li key={key}>
                {`${key}: ${value.toString()}`}
              </li>
            ))}
          </Box>
        </Box>
        <Stack spacing={1} sx={{ mt: 2 }}>
          <Button
            variant="outlined"
            color="primary"
            onClick={onImpersonateClick}
            fullWidth
          >
            Change User
          </Button>
          <Button
            variant="outlined"
            color="error"       
            onClick={handleStopImpersonation}
            fullWidth
          >
            Stop Impersonation
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default ContextUserCard;
