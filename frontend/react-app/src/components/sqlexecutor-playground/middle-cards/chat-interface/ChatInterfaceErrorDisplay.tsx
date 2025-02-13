import React from 'react';
import { Box } from '@mui/material';
import ErrorCard from 'components/sqlexecutor-playground/middle-cards/error-display/ErrorCard';
import { APIError } from 'types/sql-generation/errors/errorResponses';

interface ChatInterfaceErrorDisplayProps {
  error: APIError | null;
}

/**
 * ChatInterfaceErrorDisplay component displays errors in the chat interface.
 * @param {ChatInterfaceErrorDisplayProps} props - The component props
 * @returns {JSX.Element | null} The rendered error display or null if no error
 */
const ChatInterfaceErrorDisplay: React.FC<ChatInterfaceErrorDisplayProps> = ({ error }) => {
  if (!error) return null;

  return (
    <Box
      sx={{
        width: '100%',
        mt: 2,
        mb: 2,
      }}
    >
      <ErrorCard error={error} />
    </Box>
  );
};

export default ChatInterfaceErrorDisplay;
