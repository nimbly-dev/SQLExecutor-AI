import React from 'react';
import { Typography, Box, Stack, Chip } from '@mui/material';
import { QueryScopeErrorResponse } from '../../../../../types/sql-generation/errors/errorResponses';
import { ErrorSection } from './shared/ErrorSection';

/**
 * Props for QueryScopeError component
 */
interface QueryScopeErrorProps {
  response: QueryScopeErrorResponse;
}

/**
 * Renders QueryScopeError details.
 */
export const QueryScopeError: React.FC<QueryScopeErrorProps> = ({ response }) => {
  const detail = response.detail;

  return (
    <Stack 
      spacing={2}  // Reduced from 3 to 2
      sx={{
        width: '100%',
        overflow: 'visible',
        pb: 0, // Removed bottom padding
        '& .MuiBox-root': { // Target all Box components
          width: '100%',
          wordBreak: 'break-word' // Handle long text
        }
      }}
    >
      <ErrorSection title="Message">
        <Box>
          <Typography variant="body2" color="error">
            {detail.message}
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              mt: 1,
              color: 'warning.main',
              fontWeight: 500
            }}
          >
            Error Type: {detail.scope_error_type}
          </Typography>
        </Box>
      </ErrorSection>

      {detail.user_query_scope && (
        <ErrorSection title="Query Scope">
          <Stack spacing={1}>
            <Box>
              <Typography component="dt" variant="body2" sx={{ fontWeight: 600 }}>
                Intent:
              </Typography>
              <Typography component="dd" variant="body2" sx={{ m: 0 }}>
                {detail.user_query_scope.intent}
              </Typography>
            </Box>
            <Box>
              <Typography component="dt" variant="body2" sx={{ fontWeight: 600 }}>
                Tables:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 0.5 }}>
                {detail.user_query_scope.entities.tables.map((table, idx) => (
                  <span key={idx} className="error-badge">
                    {table}
                  </span>
                ))}
              </Box>
            </Box>
            <Box>
              <Typography component="dt" variant="body2" sx={{ fontWeight: 600 }}>
                Columns:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 0.5 }}>
                {detail.user_query_scope.entities.columns.map((column, idx) => (
                  <span key={idx} className="error-badge">
                    {column}
                  </span>
                ))}
              </Box>
            </Box>
          </Stack>
        </ErrorSection>
      )}

      {detail.sensitive_columns_removed && detail.sensitive_columns_removed.length > 0 && (
        <ErrorSection title="Sensitive Columns Removed">
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {detail.sensitive_columns_removed.map((column, idx) => (
              <span key={idx} className="error-badge warning">
                {column}
              </span>
            ))}
          </Box>
          <Typography 
            variant="body2" 
            sx={{ 
              mt: 1,
              color: 'warning.main',
              fontStyle: 'italic'
            }}
          >
            These columns were removed due to sensitivity concerns
          </Typography>
        </ErrorSection>
      )}

      {detail.issues && detail.issues.length > 0 && (
        <ErrorSection 
          title="Issues"
          sx={{ mb: 2 }} // Reduced margin
        >
          <Stack 
            spacing={2}
            sx={{
              width: '100%',
              mb: 2, // Add margin bottom
              '& > *:last-child': {
                mb: 2 // Ensure last item has spacing
              }
            }}
          >
            {detail.issues.map((issue, idx) => (
              <Box 
                key={idx} 
                sx={{ 
                  p: 1.5, 
                  border: '1px solid',
                  borderColor: 'error.light',
                  borderRadius: 1,
                  mb: 2 // Add margin bottom to each issue
                }}
              >
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                  <span className="error-badge">
                    {`Invalid ${issue.type}`}
                  </span>
                  <span className="error-badge">
                    {issue.input}
                  </span>
                </Box>
                {issue.suggestions && issue.suggestions.length > 0 && (
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                    <Typography variant="body2" color="info.main">
                      Did you mean:
                    </Typography>
                    {issue.suggestions.map((suggestion, sIdx) => (
                      <span key={sIdx} className="suggestion-badge">
                        {suggestion}
                      </span>
                    ))}
                  </Box>
                )}
              </Box>
            ))}
          </Stack>
        </ErrorSection>
      )}

      {detail.suggestions && detail.suggestions.length > 0 && (
        <ErrorSection 
          title="Suggestions"
          isLastSection={true}
          sx={{ 
            mb: 0,
            pb: 0  // Remove padding bottom
          }}
        >
          <Box 
            component="ul" 
            sx={{ 
              m: 0, 
              pl: 3,
              listStyle: 'disc',
              '& li': {
                mb: 1, // Add margin bottom to list items
                '&:last-child': {
                  mb: 0  // Remove margin from last item
                }
              }
            }}
          >
            {detail.suggestions.map((suggestion, idx) => (
              <Typography 
                key={idx} 
                component="li" 
                variant="body2" 
                color="info.main"
              >
                {suggestion}
              </Typography>
            ))}
          </Box>
        </ErrorSection>
      )}
    </Stack>
  );
};