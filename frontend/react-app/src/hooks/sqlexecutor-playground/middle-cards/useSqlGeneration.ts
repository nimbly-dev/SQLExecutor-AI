import { useState } from 'react';
import { generateSql } from 'services/sqlGenerationService';
import { SqlGenerationResponse } from 'types/sql-generation/sqlGeneration';
import { APIError } from 'types/sql-generation/errors/errorResponses';
import { ErrorType } from 'types/sql-generation/errors/errorTypes';

export interface QueryHistoryItem {
  prompt: string;
  sql: string;
}

export const useSqlGeneration = () => {
  const [queryHistory, setQueryHistory] = useState<QueryHistoryItem[]>([]);
  const [generatedSQL, setGeneratedSQL] = useState<SqlGenerationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<APIError | null>(null);

  const handleGenerateSQL = async (prompt: string, schema: string | null, runSql: boolean) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await generateSql(runSql, prompt, schema);
      setGeneratedSQL(response);
      setQueryHistory(prev => [...prev, { prompt, sql: response.sql_query }]);
    } catch (err) {
      if (err && typeof err === 'object' && 'detail' in err) {
        setError(err as APIError);
      } else {
        setError({
          detail: {
            error_type: ErrorType.RUNTIME_ERROR,
            message: 'An unexpected error occurred',
            detail: 'An unexpected runtime error occurred'
          }
        } as APIError);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return {
    queryHistory,
    generatedSQL,
    setGeneratedSQL,
    isLoading,
    error,
    handleGenerateSQL,
    setError
  };
};
