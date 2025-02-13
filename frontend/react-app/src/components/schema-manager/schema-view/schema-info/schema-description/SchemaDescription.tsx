import React, { useCallback } from 'react';
import {
  Box,
  TextField,
  Typography,
  FormControlLabel,
  Checkbox,
  Portal,
  Snackbar,
  Alert,
} from '@mui/material';
import { Schema } from 'types/schema/schemaType';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import { useFormUpdate } from 'contexts/form/FormUpdateProvider';
import { useValidationFeedback, AlertSeverity } from 'hooks/common/feedback/useValidationFeedback';
import DescriptionTextFormField from 'components/common/forms/field-forms/DescriptionTextFormField';
import { validateColumnDescription } from 'validations/schema-manager/common/description.validations';
import TextListsTagsFormField from 'components/common/forms/field-forms/TextListsTagsFormField';
import { convertToStringArray } from 'utils/stringArrayUtils';

interface SchemaDescriptionViewProps {
  schema: Schema;
}

type LocalState = Pick<Schema, 'schema_name' | 'description' | 'exclude_description_on_generate_sql' | 'synonyms'> & {
  filter_rules: string;
};

export const SchemaDescription: React.FC<SchemaDescriptionViewProps> = ({ schema }) => {
  const { updateField } = useFormUpdate();
  const [localState, setField] = useLocalFormState<LocalState>({
    schema_name: schema.schema_name,
    description: schema.description,
    exclude_description_on_generate_sql: schema.exclude_description_on_generate_sql,
    filter_rules: Array.isArray(schema.filter_rules) ? schema.filter_rules.join(', ') : '',
    synonyms: schema.synonyms || [],
  });
  
  const { feedback, showFeedback, clearFeedback } = useValidationFeedback();

  const handleDescriptionChange = useCallback((value: string) => {
    setField('description', value);
    if (validateColumnDescription(value)) {
      updateField('description', value);
    }
  }, [setField, updateField]);

  const handleFieldChange = useCallback((field: keyof LocalState, value: any) => {
    setField(field, value);
  }, [setField]);

  const handleFieldBlur = useCallback((field: keyof LocalState) => {
    const value = field === 'filter_rules' 
      ? convertToStringArray(localState[field])
      : localState[field];
    updateField(field, value);
  }, [localState, updateField]);

  return (
    <Box sx={{ p: 2 }}>
      <TextField
        required
        label="Schema Name"
        size="small"
        fullWidth
        margin="dense"
        value={localState.schema_name}
        onChange={(e) => handleFieldChange('schema_name', e.target.value)}
        onBlur={() => handleFieldBlur('schema_name')}
      />
      <Typography variant="caption" color="textSecondary" sx={{ mb: 2, display: 'block' }}>
        Enter a unique schema name.
      </Typography>
      
      <DescriptionTextFormField
        required
        description={localState.description}
        onChange={handleDescriptionChange}
        onValidationError={(message) => showFeedback(message, 'error')}
        validate={validateColumnDescription}
        placeholder="Enter schema description..."
      />
      
      <FormControlLabel
        control={
          <Checkbox
            size="small"
            checked={localState.exclude_description_on_generate_sql}
            onChange={(e) => {
              handleFieldChange('exclude_description_on_generate_sql', e.target.checked);
              handleFieldBlur('exclude_description_on_generate_sql');
            }}
          />
        }
        label="Exclude Description on Generate SQL"
      />
      
      <TextField
        label="Filter Rules (comma separated)"
        size="small"
        fullWidth
        margin="dense"
        value={localState.filter_rules}
        onChange={(e) => handleFieldChange('filter_rules', e.target.value)}
        onBlur={() => handleFieldBlur('filter_rules')}
      />
      
      <TextListsTagsFormField
        label="Synonyms"
        tags={localState.synonyms}
        onChange={(newTags: string[]) => {
          handleFieldChange('synonyms', newTags);
          updateField('synonyms', newTags);
        }}
      />
      
      <Portal>
        <Snackbar
          open={!!feedback}
          autoHideDuration={4000}
          onClose={clearFeedback}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        >
          <Alert 
            onClose={clearFeedback} 
            severity={(feedback?.type || 'error') as AlertSeverity}
            variant="filled"
          >
            {feedback?.message || ''}
          </Alert>
        </Snackbar>
      </Portal>
    </Box>
  );
};

export default SchemaDescription;
