import React from 'react';
import { Typography, Box } from '@mui/material';
import { GenericErrorDetail } from '../../../../../types/sql-generation/errors/errorResponses';
import { ErrorType } from '../../../../../types/sql-generation/errors/errorTypes';

/**
 * Props for GenericError component
 */
interface GenericErrorProps {
  detail: GenericErrorDetail;
}

/**
 * Renders a simple generic error screen.
 */
export const GenericError: React.FC<GenericErrorProps> = ({ detail }) => {
  return (
    <Box>
      <Typography variant="body2" color="error">
        {detail.message || detail.detail || 'An unexpected error occurred'}
      </Typography>
    </Box>
  );
};

// No changes needed as the generic error maintains consistent styling.
// Ensure that any new badges or interactive elements are styled using the existing .error-badge classes.