import React, { useState } from 'react';
import { Box, Typography, useTheme, Collapse, IconButton, Stack, useMediaQuery, Theme } from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import ErrorIcon from './ErrorIcon';
import { ErrorType } from '../../../../types/sql-generation/errors/errorTypes';
import { QueryScopeErrorResponse, 
         SchemaDiscoveryErrorResponse, 
         SqlGenerationErrorResponse, 
         ValidationErrorResponse, 
         APIError } from '../../../../types/sql-generation/errors/errorResponses';
import { AccessDeniedError } from './error-types/AccessDeniedError';
import { QueryScopeError } from './error-types/QueryScopeError';
import { SchemaDiscoveryError } from './error-types/SchemaDiscoveryError';
import { ValidationError } from './error-types/ValidationError';
import { GenericError } from './error-types/GenericError';
import '../../../../styles/sqlexecutor-playground/middle-cards/error-display/ErrorCard.scss';  // Using relative path
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

/**
 * Returns a user-friendly string based on the ErrorType enum.
 * @param errorType - The type of error.
 * @returns A formatted string representing the error type.
 */
const getErrorTypeDisplay = (errorType?: ErrorType): string => {
  switch (errorType) {
    case ErrorType.ACCESS_DENIED:
      return 'Access Denied';
    case ErrorType.QUERY_SCOPE_ERROR:
      return 'Query Scope Error';
    case ErrorType.SCHEMA_DISCOVERY_ERROR:
      return 'Schema Discovery Error';
    default:
      return 'Error';
  }
};

interface ErrorCardProps {
  error?: APIError;
  title?: string;
  severity?: 'error' | 'warning' | 'info';
  children?: React.ReactNode;
}

/**
 * ErrorCard component to display detailed error information with collapsible functionality.
 * @param {ErrorCardProps} props - The props for the component.
 * @returns {JSX.Element} The rendered ErrorCard component.
 */
const ErrorCard: React.FC<ErrorCardProps> = ({ error, ...props }) => {
  const theme = useTheme();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const isDarkMode = theme.palette.mode === 'dark';

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsCollapsed(!isCollapsed);
  };

  const renderErrorContent = () => {
    if (!error?.detail) return null;
    if (typeof error.detail === 'string') {
      return <GenericError detail={{
        error_type: ErrorType.RUNTIME_ERROR, 
        message: error.detail, 
        detail: error.detail
      }} />;
    }
    switch (error.detail.error_type) {
      case ErrorType.ACCESS_DENIED:
        return <AccessDeniedError response={{ detail: error.detail }} />;
      case ErrorType.QUERY_SCOPE_ERROR:
        return <QueryScopeError response={{ detail: error.detail }} />;
      case ErrorType.SCHEMA_DISCOVERY_ERROR:
        return <SchemaDiscoveryError response={{ detail: error.detail }} />;
      case ErrorType.VALIDATION_ERROR:
        return <ValidationError response={{ detail: error.detail }} />;
      default:
        return <GenericError detail={error.detail} />;
    }
  };

  return (
    <Box
      className={`error-card__container error-card__container--${isDarkMode ? 'dark' : 'light'}`}
      sx={{
        border: '1px solid #f5c6cb',
        backgroundColor: isDarkMode ? 'rgba(247, 222, 230, 0.1)' : '#fff5f5',
        height: 'fit-content',
        maxHeight: isCollapsed ? '48px' : '300px', // Reduced from auto to 300px
        minHeight: '48px',
        transition: 'all 0.3s ease-in-out',
      }}
    >
      <Box
        className={`error-card__header`}
        onClick={handleToggle}
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: '48px', // Fixed height
          px: 2,
          gap: 1,
        }}
      >
        <Stack 
          direction="row" 
          alignItems="center" 
          spacing={1.5} 
          sx={{ 
            height: '100%',
            flex: 1,
          }}
        >
          <ErrorIcon 
            errorType={typeof error?.detail === 'string' ? undefined : error?.detail?.error_type}
            sx={{ 
              color: '#842029',
              fontSize: 24,
              display: 'flex',
            }}
          />
          <Typography 
            color="#842029"
            sx={{
              fontSize: '1rem',
              fontWeight: 500,
              display: 'flex',
              alignItems: 'center',
            }}
          >
            {getErrorTypeDisplay(typeof error?.detail === 'string' ? undefined : error?.detail?.error_type)}
          </Typography>
        </Stack>
        <IconButton
          size="small"
          sx={{ 
            color: '#842029',
            padding: '6px',
            '& svg': {
              fontSize: 24,
            }
          }}
        >
          {isCollapsed ? <ExpandMoreIcon /> : <ExpandLessIcon />}
        </IconButton>
      </Box>

      <Collapse in={!isCollapsed}>
        <Box 
          className="error-card__content"
          sx={{
            position: 'relative',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'auto',
            maxHeight: '252px', // 300px - 48px (header height)
            padding: '8px',
            '&::-webkit-scrollbar': {
              width: '6px'
            },
            '&::-webkit-scrollbar-thumb': {
              backgroundColor: '#f5c6cb',
              borderRadius: '3px'
            }
          }}
        >
          {error && renderErrorContent()}
        </Box>
      </Collapse>
    </Box>
  );
};

export default ErrorCard;
