import React from 'react';
import { Box, Typography, SxProps, Theme } from '@mui/material';

/**
 * Props for ErrorSection component
 */
interface ErrorSectionProps {
  title: string;
  children: React.ReactNode;
  sx?: SxProps<Theme>;
  isLastSection?: boolean;
}

/**
 * ErrorSection component for consistent styling of error sections.
 */
export const ErrorSection: React.FC<ErrorSectionProps> = ({ 
  title, 
  children, 
  sx,
  isLastSection = false 
}) => (
  <Box 
    className="error-card-section" 
    sx={{ 
      width: '100%',
      mb: 2,  // Reduced margin bottom for all sections
      '&:last-child': {
        mb: 0,  // Remove margin for last section
        pb: 0   // Remove padding for last section
      },
      ...sx 
    }}
  >
    <Typography 
      variant="subtitle2" 
      sx={{ 
        fontWeight: 600,
        mb: 1.5,
        color: 'error.main'
      }}
    >
      {title}
    </Typography>
    <Box sx={{ width: '100%' }}>
      {children}
    </Box>
  </Box>
);
