import React from 'react';
import { CardContent, Typography, Box, useTheme, useMediaQuery, CircularProgress } from '@mui/material';
import { SqlGenerationResponse } from '../../../../types/sql-generation/sqlGeneration';
import ErrorCard from '../error-display/ErrorCard';
import { APIError } from '../../../../types/sql-generation/errors/errorResponses';
import '../../../../styles/sqlexecutor-playground/middle-cards/SQLResults.scss';

interface SQLResultsProps {
  results: SqlGenerationResponse | APIError | null;
  isLoading?: boolean;
}

/**
 * SQLResults component to display the generated SQL and its response.
 * @param {SQLResultsProps} props - The props for the component.
 * @returns {JSX.Element} The rendered component.
 */
const SQLResults: React.FC<SQLResultsProps> = ({ results, isLoading = false }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isDarkMode = theme.palette.mode === 'dark';

  // Don't render anything if there are no results and not loading
  if (!results && !isLoading) {
    return null;
  }

  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          p: 2,
          backgroundColor: theme.palette.mode === 'dark' ? 'transparent' : '#ffffff',
          borderRadius: '5px',
          boxShadow: theme.palette.mode === 'dark'
            ? 'none'
            : '0px 4px 6px rgba(0, 0, 0, 0.1)',
          border: `1px solid ${theme.palette.mode === 'dark' ? '#444444' : '#e0e0e0'}`,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // If it's an error response type, show the detailed error using ErrorCard
  if (results && 'detail' in results) {
    // Check if detail is an object with error_type
    if (typeof results.detail === 'object' && 'error_type' in results.detail) {
      return (
        <Box sx={{ p: 2 }}>
          <ErrorCard error={results as APIError} />
        </Box>
      );
    }
  }

  // Handle QueryScopeResolutionErrorResponse or SchemaDiscoveryErrorResponse
  if (results && 'message' in results && 'user_query_scope' in results) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body2" color="error">
          {String(results.message)}
        </Typography>
        {/* Render additional details based on the error type */}
      </Box>
    );
  }

  // Handle SqlGenerationResponse
  if (results && 'sql_query' in results) {
    return (
      <Box className={`sql-results__container sql-results__container--${theme.palette.mode}`}>
        <CardContent>
          <Typography className="sql-results__title">
            SQL Results
          </Typography>

          <Box className="sql-results__scrollbar">
            {/* Scrollable Content */}
            <Box className="sql-results__content">
              {!results ? (
                <Box
                  sx={{
                    p: 2,
                    borderRadius: 1,
                    border: 1,
                    borderColor: theme.palette.mode === 'dark' ? '#666666' : 'divider',
                    backgroundColor: theme.palette.mode === 'dark' ? '#444444' : 'background.paper',
                  }}
                >
                  <Typography
                    variant="body2"
                    sx={{ color: theme.palette.mode === 'dark' ? '#ffffff' : 'inherit' }}
                  >
                    No results yet.
                  </Typography>
                </Box>
              ) : (
                <>
                  {/* SQL Query Section */}
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 1,
                      border: 1,
                      borderColor: theme.palette.mode === 'dark' ? '#666666' : 'divider',
                      backgroundColor: theme.palette.mode === 'dark' ? '#444444' : 'background.paper',
                      marginBottom: '20px',
                    }}
                  >
                    <Typography
                      variant="subtitle2"
                      sx={{
                        color: theme.palette.primary.main,
                        mb: 1,
                        fontWeight: 600,
                      }}
                    >
                      Generated SQL Query:
                    </Typography>
                    <Typography
                      variant="body2"
                      component="pre"
                      tabIndex={0}
                      sx={{
                        p: 1.5,
                        borderRadius: 1,
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        backgroundColor: theme.palette.mode === 'dark' ? '#333333' : 'background.default',
                        border: 1,
                        borderColor: theme.palette.mode === 'dark' ? '#555555' : 'divider',
                        color: theme.palette.mode === 'dark' ? '#ffffff' : 'inherit',
                        '&:focus': {
                          outline: `2px solid ${theme.palette.primary.main}`,
                          outlineOffset: '2px',
                        },
                      }}
                    >
                      {('sql_query' in results) ? results.sql_query : ''}
                    </Typography>
                  </Box>

                  {/* Query Response Section */}
                  {('sql_response' in results) && results.sql_response && (
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: 1,
                        border: 1,
                        borderColor: theme.palette.mode === 'dark' ? '#666666' : 'divider',
                        backgroundColor: theme.palette.mode === 'dark' ? '#444444' : 'background.paper',
                      }}
                    >
                      <Typography
                        variant="subtitle2"
                        sx={{
                          color: theme.palette.primary.main,
                          mb: 1,
                          fontWeight: 600,
                        }}
                      >
                        Query Response:
                      </Typography>
                      <Typography
                        variant="body2"
                        component="pre"
                        tabIndex={0}
                        sx={{
                          p: 1.5,
                          borderRadius: 1,
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          backgroundColor: theme.palette.mode === 'dark' ? '#333333' : 'background.default',
                          border: 1,
                          borderColor: theme.palette.mode === 'dark' ? '#555555' : 'divider',
                          color: theme.palette.mode === 'dark' ? '#ffffff' : 'inherit',
                          '&:focus': {
                            outline: `2px solid ${theme.palette.primary.main}`,
                            outlineOffset: '2px',
                          },
                        }}
                      >
                        {results.sql_response ? JSON.stringify(results.sql_response, null, 2) : ''}
                      </Typography>
                    </Box>
                  )}
                </>
              )}
            </Box>
          </Box>
        </CardContent>
      </Box>
    );
  }

  return null;
};

export default SQLResults;
