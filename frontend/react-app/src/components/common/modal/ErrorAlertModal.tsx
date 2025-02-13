import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Alert,
  useTheme,
} from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

type ErrorType = 'error' | 'warning' | 'info' | 'success';

interface ErrorData {
  error?: string;
  detail?: Array<{ field: string; msg: string; type: string }> | string;
}

interface ErrorAlertModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  error: unknown;
  errorType?: ErrorType;
}

const ErrorAlertModal: React.FC<ErrorAlertModalProps> = ({
  open,
  onClose,
  title,
  error,
  errorType = 'error'
}) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === 'dark';

  const getErrorIcon = (type: ErrorType) => {
    switch (type) {
      case 'warning':
        return <WarningIcon />;
      case 'info':
        return <InfoIcon />;
      case 'success':
        return <CheckCircleIcon />;
      default:
        return <ErrorOutlineIcon />;
    }
  };

  const parseErrorData = (errorContent: unknown): ErrorData => {
    if (errorContent && typeof errorContent === 'object') {
      const errorObj = errorContent as Record<string, any>;
      
      // Handle axios error response
      if ('response' in errorObj && errorObj.response?.data) {
        return parseErrorData(errorObj.response.data);
      }

      // Return structured error data
      return {
        error: errorObj.error || title,
        detail: errorObj.detail || []
      };
    }
    
    return {
      error: title,
      detail: String(errorContent)
    };
  };

  const renderDetailItem = (item: { field: string; msg: string; type: string }) => (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        bgcolor: isDarkMode ? 'rgba(0, 0, 0, 0.2)' : 'rgba(255, 255, 255, 0.1)',
        borderLeft: 3,
        borderColor: `${errorType}.main`,
        p: 1.5,
        borderRadius: 1,
        mb: 1,
        '& > *': {
          color: isDarkMode ? 'grey.300' : 'grey.800'
        }
      }}
    >
      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
        {item.field}
      </Typography>
      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
        {item.msg}
      </Typography>
      <Typography variant="caption" sx={{ color: `${errorType}.main`, mt: 0.5 }}>
        {item.type}
      </Typography>
    </Box>
  );

  const errorData = parseErrorData(error);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          bgcolor: isDarkMode ? 'grey.900' : 'background.paper',
          boxShadow: theme.shadows[10]
        },
      }}
    >
      <DialogTitle
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          bgcolor: `${errorType}.main`,
          color: `${errorType}.contrastText`,
          p: 2,
        }}
      >
        {getErrorIcon(errorType)}
        <Typography variant="h6" component="span">
          {errorData.error || title}
        </Typography>
      </DialogTitle>
      
      <DialogContent sx={{ mt: 2, pb: 1 }}>
        {Array.isArray(errorData.detail) ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {errorData.detail.map((item, index) => (
              <React.Fragment key={index}>
                {renderDetailItem(item)}
              </React.Fragment>
            ))}
          </Box>
        ) : (
          <Alert 
            severity={errorType}
            sx={{
              mb: 2,
              '& .MuiAlert-message': {
                fontFamily: 'monospace'
              }
            }}
          >
            {errorData.detail || 'An unknown error occurred'}
          </Alert>
        )}
      </DialogContent>

      <DialogActions 
        sx={{ 
          p: 2, 
          pt: 0,
          borderTop: 1,
          borderColor: isDarkMode ? 'grey.800' : 'grey.200'
        }}
      >
        <Button
          onClick={onClose}
          variant="contained"
          color={errorType}
          size="medium"
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ErrorAlertModal;
