import React from 'react';
import { Typography, Box, List, ListItem, Stack, Chip } from '@mui/material';
import { SchemaDiscoveryErrorResponse } from '../../../../../types/sql-generation/errors/errorResponses';

/**
 * Props for SchemaDiscoveryError component
 */
interface SchemaDiscoveryErrorProps {
  response: SchemaDiscoveryErrorResponse;
}

/**
 * Renders SchemaDiscoveryError details.
 */
export const SchemaDiscoveryError: React.FC<SchemaDiscoveryErrorProps> = ({ response }) => {
  const detail = response.detail;

  return (
    <>
      <Typography variant="h6" color="error" gutterBottom>
        Schema Discovery Error
      </Typography>
      <Stack spacing={2}>
        <Box>
          <Typography variant="subtitle2" color="error">
            Error Type:
          </Typography>
          <Typography variant="body2" color="error">
            {detail.discovery_error_type}
          </Typography>
        </Box>

        <Box>
          <Typography variant="subtitle2" color="error">
            Message:
          </Typography>
          <Typography variant="body2" color="error">
            {detail.message}
          </Typography>
        </Box>

        {detail.user_query_scope && (
          <Box>
            <Typography variant="subtitle2" color="error">
              Query Scope:
            </Typography>
            <Typography variant="body2" color="error">
              Intent: {detail.user_query_scope.intent}
            </Typography>
          </Box>
        )}

        {detail.matched_schemas && detail.matched_schemas.length > 0 && (
          <Box>
            <Typography variant="subtitle2" color="error">
              Matched Schemas:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
              {detail.matched_schemas.map((schema, idx) => (
                <span key={idx} className="error-badge">
                  {schema}
                </span>
              ))}
            </Box>
          </Box>
        )}

        {detail.unmatched_tables && detail.unmatched_tables.length > 0 && (
          <Box>
            <Typography variant="subtitle2" color="error">
              Unmatched Tables:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
              {detail.unmatched_tables.map((table, idx) => (
                <span key={idx} className="error-badge">
                  {table}
                </span>
              ))}
            </Box>
          </Box>
        )}

        {detail.unmatched_columns && detail.unmatched_columns.length > 0 && (
          <Box>
            <Typography variant="subtitle2" color="error">
              Unmatched Columns:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
              {detail.unmatched_columns.map((column, idx) => (
                <span key={idx} className="error-badge">
                  {column}
                </span>
              ))}
            </Box>
          </Box>
        )}

        {detail.suggestions && detail.suggestions.length > 0 && (
          <Box>
            <Typography variant="subtitle2" color="info">
              Suggestions:
            </Typography>
            <List sx={{ pl: 2 }}>
              {detail.suggestions.map((suggestion, idx) => (
                <ListItem key={idx}>
                  <Typography variant="body2" color="info">
                    {suggestion}
                  </Typography>
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </Stack>
    </>
  );
};