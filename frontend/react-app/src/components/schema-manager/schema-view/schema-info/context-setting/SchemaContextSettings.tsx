import React, { useCallback } from 'react';
import { Box, TextField, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { Schema, APIContext, SQLContext, ContextSetting } from 'types/schema/schemaType';
import { useFormUpdate } from 'contexts/form/FormUpdateProvider';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import TextListsTagsFormField from 'components/common/forms/field-forms/TextListsTagsFormField';

interface SchemaContextSettingsProps {
  schema: Schema;
}

const defaultSQLContext: SQLContext = {
  table: '',
  user_identifier: '',
  custom_fields: [],
  custom_get_context_query: '',
};

const defaultAPIContext: APIContext = {
  get_user_endpoint: '',
  user_identifier: '',
  custom_fields: [],
  auth_method: '',
};

export const SchemaContextSettings: React.FC<SchemaContextSettingsProps> = ({ schema }) => {
  const { updateField } = useFormUpdate();
  const [localState, setField] = useLocalFormState<ContextSetting>({
    sql_context: schema.context_setting?.sql_context ?? defaultSQLContext,
    api_context: schema.context_setting?.api_context ?? defaultAPIContext,
  });

  const handleContextTypeChange = useCallback((value: string) => {
    updateField('context_type', value);
    if (value === 'sql') {
      updateField('context_setting.api_context', undefined);
    } else if (value === 'api') {
      updateField('context_setting.sql_context', undefined);
    }
  }, [updateField]);

  const handleSQLContextChange = useCallback((field: keyof SQLContext, value: any) => {
    const newContext = { 
      ...localState.sql_context, 
      [field]: value 
    };
    setField('sql_context', newContext);
    updateField('context_setting.sql_context', newContext);
  }, [localState.sql_context, setField, updateField]);

  const handleAPIContextChange = useCallback((field: keyof APIContext, value: any) => {
    const newContext = { 
      ...localState.api_context, 
      [field]: value 
    };
    setField('api_context', newContext);
    updateField('context_setting.api_context', newContext);
  }, [localState.api_context, setField, updateField]);

  return (
    <Box sx={{ p: 2 }}>
      <FormControl required fullWidth margin="dense" size="small">
        <InputLabel id="context-type-label">Context Type</InputLabel>
        <Select
          labelId="context-type-label"
          value={schema.context_type}
          label="Context Type"
          onChange={(e) => handleContextTypeChange(e.target.value)}
        >
          <MenuItem value="sql">SQL</MenuItem>
          <MenuItem value="api">API</MenuItem>
        </Select>
      </FormControl>

      {schema.context_type === 'sql' && (
        <>
          <TextField
            required
            label="Table Name"
            size="small"
            fullWidth
            margin="dense"
            value={localState.sql_context?.table ?? ''}
            onChange={(e) => handleSQLContextChange('table', e.target.value)}
          />
          <TextField
            required
            label="User Identifier"
            size="small"
            fullWidth
            margin="dense"
            value={localState.sql_context?.user_identifier ?? ''}
            onChange={(e) => handleSQLContextChange('user_identifier', e.target.value)}
          />
          <TextListsTagsFormField
            label="Custom Fields"
            tags={localState.sql_context?.custom_fields ?? []}
            onChange={(newTags) => handleSQLContextChange('custom_fields', newTags)}
          />
          <TextField
            label="Custom Get Context Query"
            size="small"
            fullWidth
            margin="dense"
            multiline
            rows={4}
            value={localState.sql_context?.custom_get_context_query ?? ''}
            onChange={(e) => handleSQLContextChange('custom_get_context_query', e.target.value)}
          />
        </>
      )}

      {schema.context_type === 'api' && (
        <>
          <TextField
            required
            label="Get User Endpoint"
            size="small"
            fullWidth
            margin="dense"
            value={localState.api_context?.get_user_endpoint ?? ''}
            onChange={(e) => handleAPIContextChange('get_user_endpoint', e.target.value)}
          />
          <TextField
            required
            label="User Identifier"
            size="small"
            fullWidth
            margin="dense"
            value={localState.api_context?.user_identifier ?? ''}
            onChange={(e) => handleAPIContextChange('user_identifier', e.target.value)}
          />
          <TextListsTagsFormField
            label="Custom Fields"
            tags={localState.api_context?.custom_fields ?? []}
            onChange={(newTags) => handleAPIContextChange('custom_fields', newTags)}
          />
          <TextField
            required
            label="Auth Method"
            size="small"
            fullWidth
            margin="dense"
            value={localState.api_context?.auth_method ?? ''}
            onChange={(e) => handleAPIContextChange('auth_method', e.target.value)}
          />
        </>
      )}
    </Box>
  );
};

export default SchemaContextSettings;
