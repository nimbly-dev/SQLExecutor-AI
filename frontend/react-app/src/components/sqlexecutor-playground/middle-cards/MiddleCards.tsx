import React, { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import ChatInterface from './ChatInterface';
import SQLResults from './sql-results/SQLResults';
import ChatInterfaceErrorDisplay from './chat-interface/ChatInterfaceErrorDisplay';
import { ExternalSessionData } from '../../../types/authentication/externalUserSessionData';
import { useSqlGeneration } from '../../../hooks/sqlexecutor-playground/middle-cards/useSqlGeneration';
import { useSchemaManagement } from '../../../hooks/sqlexecutor-playground/middle-cards/useSchemaManagement';

interface MiddleCardsProps {
  sessionData: ExternalSessionData | null;
  setSessionData: React.Dispatch<React.SetStateAction<ExternalSessionData | null>>;
}

/**
 * MiddleCards component to manage the middle section of the SQL execution playground.
 * @param {MiddleCardsProps} props - The props for the component.
 * @returns {JSX.Element} The rendered component.
 */
function MiddleCards({ sessionData, setSessionData }: MiddleCardsProps) {
  const {
    queryHistory,
    generatedSQL,
    setGeneratedSQL,
    isLoading,
    error,
    handleGenerateSQL,
    setError
  } = useSqlGeneration();

  const { schemas, loading: schemasLoading } = useSchemaManagement();
  const handleChatSubmit = async (prompt: string, schema: string | null, runSql: boolean) => {
    setError(null);
    setGeneratedSQL(null);
    await handleGenerateSQL(prompt, schema, runSql);
  };

  return (
    <Box
      sx={{
        padding: '20px',
        backgroundColor: 'transparent',
        order: { xs: 2, md: 'unset' },
        marginBottom: { xs: 2, md: 0 },
        display: 'flex',
        flexDirection: 'column',
        gap: 3,
      }}
    >
      <ChatInterface
        onGenerateSQL={handleChatSubmit}
        queryHistory={queryHistory}
        schemas={schemas}
        isLoading={isLoading}
        onError={setError}
      />
      {error && (
        <ChatInterfaceErrorDisplay 
          error={error}
        />
      )}
      <SQLResults results={generatedSQL} isLoading={isLoading} />
    </Box>
  );
};

export default MiddleCards;
