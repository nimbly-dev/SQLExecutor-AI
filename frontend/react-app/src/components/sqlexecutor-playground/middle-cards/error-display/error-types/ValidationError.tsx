import React from 'react';
import { Typography, Box, List, ListItem } from '@mui/material';
import { ValidationErrorResponse } from 'types/sql-generation/errors/errorResponses';

/**
 * Props for ValidationError component
 */
interface ValidationErrorProps {
  response: ValidationErrorResponse;
}

/**
 * Renders ValidationError details.
 */
export const ValidationError: React.FC<ValidationErrorProps> = ({ response }) => {
  const detail = response.detail;
  return (
    <>
      <Box>
        <Typography variant="body2" color="error">
          There were validation errors with your request.
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" color="error" sx={{ mb: 1 }}>
            Details:
          </Typography>
          <List sx={{ pl: 2, mt: 0 }}>
            {detail.detail.map((validationError, index) => (
              <ListItem key={index} sx={{ py: 0.5 }}>
                <Typography variant="body2" color="error">
                  {validationError.field}: {validationError.msg}
                </Typography>
              </ListItem>
            ))}
          </List>
        </Box>
      </Box>
    </>
  );
};