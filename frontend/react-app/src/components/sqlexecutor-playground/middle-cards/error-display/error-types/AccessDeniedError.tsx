import React from 'react';
import { Typography, Box, Stack, Chip } from '@mui/material';
import { SqlGenerationErrorResponse, QueryScopeErrorResponse } from 'types/sql-generation/errors/errorResponses';
import { ErrorSection } from 'components/sqlexecutor-playground/middle-cards/error-display/error-types/shared/ErrorSection';

/**
 * Props for AccessDeniedError component
 */
interface AccessDeniedErrorProps {
  response: SqlGenerationErrorResponse;
}

/**
 * Renders AccessDeniedError details.
 */
export const AccessDeniedError: React.FC<AccessDeniedErrorProps> = ({ response }) => {
  const detail = response.detail;

  return (
    <Stack spacing={2}>
      {detail.denied_tables.length > 0 && (
        <ErrorSection title="Denied Tables">
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {detail.denied_tables.map((table, idx) => (
              <span key={idx} className="error-badge">
                {table}
              </span>
            ))}
          </Box>
        </ErrorSection>
      )}

      {detail.access_violations.length > 0 && (
        <ErrorSection title="Access Violations">
          {detail.access_violations.map((violation, idx) => (
            <Box 
              key={idx} 
              sx={{ 
                mb: 1.5,
                p: 1.5,
                border: '1px solid',
                borderColor: 'error.light',
                borderRadius: 1,
                '&:last-child': { mb: 0 }
              }}
            >
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                <span className="error-badge">
                  {violation.entity}
                </span>
                <span className="error-badge">
                  {violation.violation_type}
                </span>
              </Box>
              <Typography variant="body2" color="error.main">
                {violation.reason}
              </Typography>
              {violation.policy_name && (
                <Typography variant="body2" color="error.main" sx={{ mt: 0.5 }}>
                  Policy: {violation.policy_type} ({violation.policy_name})
                </Typography>
              )}
              {violation.failed_condition && (
                <Typography 
                  variant="body2" 
                  sx={{ 
                    mt: 0.5,
                    color: 'error.light',
                    fontStyle: 'italic'
                  }}
                >
                  Failed condition: {violation.failed_condition}
                </Typography>
              )}
            </Box>
          ))}
        </ErrorSection>
      )}
    </Stack>
  );
};