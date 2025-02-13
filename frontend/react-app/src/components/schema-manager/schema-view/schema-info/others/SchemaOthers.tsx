import React from 'react';
import { Box, Switch, TextField, FormControlLabel } from '@mui/material';
import { Schema, SchemaChatInterfaceIntegrationSetting } from 'types/schema/schemaType';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import { useFormUpdate } from 'contexts/form/FormUpdateProvider';

interface SchemaOthersViewProps {
  schema: Schema;
}

interface LocalState {
  integration: SchemaChatInterfaceIntegrationSetting;
}

export const SchemaOthers: React.FC<SchemaOthersViewProps> = ({ schema }) => {
  const { updateField } = useFormUpdate();
  
  const [localState, setLocalField] = useLocalFormState<LocalState>({
    integration: {
      enabled: schema.schema_chat_interface_integration?.enabled ?? false,
      get_contexts_query: schema.schema_chat_interface_integration?.get_contexts_query ?? '',
      get_contexts_count_query: schema.schema_chat_interface_integration?.get_contexts_count_query ?? ''
    }
  });

  const handleIntegrationChange = (field: keyof SchemaChatInterfaceIntegrationSetting, value: any) => {
    const newIntegration = {
      enabled: schema.schema_chat_interface_integration?.enabled ?? false,
      get_contexts_query: schema.schema_chat_interface_integration?.get_contexts_query ?? '',
      get_contexts_count_query: schema.schema_chat_interface_integration?.get_contexts_count_query ?? '',
      [field]: value,
    };
    
    setLocalField('integration', newIntegration);
    updateField('schema_chat_interface_integration', newIntegration);
  };

  return (
    <Box sx={{ p: 2 }}>
      <FormControlLabel
        control={
          <Switch
            checked={localState.integration.enabled}
            onChange={(e) => handleIntegrationChange('enabled', e.target.checked)}
          />
        }
        label="Enable Chat Interface Integration"
      />
      
      {localState.integration.enabled && (
        <>
          <TextField
            required
            label="Get Contexts Query"
            size="small"
            fullWidth
            margin="dense"
            multiline
            rows={4}
            value={localState.integration.get_contexts_query}
            onChange={(e) => setLocalField('integration', {
              ...localState.integration,
              get_contexts_query: e.target.value
            })}
            onBlur={() => handleIntegrationChange('get_contexts_query', localState.integration.get_contexts_query)}
          />
          
          <TextField
            required
            label="Get Contexts Count Query"
            size="small"
            fullWidth
            margin="dense"
            multiline
            rows={4}
            value={localState.integration.get_contexts_count_query}
            onChange={(e) => setLocalField('integration', {
              ...localState.integration,
              get_contexts_count_query: e.target.value
            })}
            onBlur={() => handleIntegrationChange('get_contexts_count_query', localState.integration.get_contexts_count_query)}
          />
        </>
      )}
    </Box>
  );
};

export default SchemaOthers;
