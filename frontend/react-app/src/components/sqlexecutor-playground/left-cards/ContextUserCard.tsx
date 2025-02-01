import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Stack,
  Tooltip,
} from '@mui/material';
import { ExternalSessionData } from '../../../types/authentication/externalUserSessionData';
import { useSQLExecutorContext } from '../../../pages/SQLExecutorPlayground';

const ContextUserCard: React.FC = () => {
  const { sessionData, setIsModalOpen, stopImpersonation, selectedSchema } = useSQLExecutorContext();

  const handleImpersonateClick = () => {
    if (!sessionData && !selectedSchema) {
      return;
    }
    setIsModalOpen(true);
  };

  const handleStopImpersonation = () => {
    stopImpersonation();
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
          <Tooltip title={!selectedSchema ? 'Please select a schema first' : ''} disableHoverListener={!!selectedSchema}>
            <span style={{ display: 'block' }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleImpersonateClick}
                fullWidth
                disabled={!selectedSchema}
                sx={{ mt: 2 }}
              >
                Impersonate User
              </Button>
            </span>
          </Tooltip>
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
            onClick={handleImpersonateClick}
            fullWidth
            // Removed disabled check so the button remains enabled even if selectedSchema is null
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
