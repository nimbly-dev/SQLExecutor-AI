// SchemaFormTablesGeneralInfo.tsx
import React, { useCallback, useState } from 'react';
import { Box, TextField, Checkbox, FormControlLabel } from '@mui/material';
import { Table } from 'types/schema/schemaType';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import { useFormUpdate } from 'contexts/form/FormUpdateProvider';
import DescriptionTextFormField from 'components/common/forms/field-forms/DescriptionTextFormField';
import { validateColumnDescription } from 'validations/schema-manager/common/description.validations';
import { useValidationFeedback, AlertSeverity } from 'hooks/common/feedback/useValidationFeedback';
import { Portal, Snackbar, Alert } from '@mui/material';
import TextListsTagsFormField from 'components/common/forms/field-forms/TextListsTagsFormField';

interface SchemaFormTablesGeneralInfoProps {
  table: Table;
  tableName: string; // The key from the Record
  pathPrefix: string;
  updateField: (path: string, value: any) => void;
  onNameChange: (oldKey: string, newKey: string, tableData: Table) => void;
}

const SchemaFormTablesGeneralInfo: React.FC<SchemaFormTablesGeneralInfoProps> = ({ 
  table, 
  tableName,
  pathPrefix, 
  updateField, 
  onNameChange 
}) => {
  const [localName, setLocalName] = useState(tableName);
  const { feedback, showFeedback, clearFeedback } = useValidationFeedback();

  const handleNameChange = useCallback(() => {
    if (localName && localName !== tableName) {
      onNameChange(tableName, localName, table);
    }
  }, [localName, tableName, onNameChange, table]);

  return (
    <>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField
          label="Name"
          value={localName}
          onChange={(e) => setLocalName(e.target.value)}
          onBlur={handleNameChange}
          fullWidth
        />
        <DescriptionTextFormField
          description={table.description ?? ''}
          onChange={(value) => updateField(`${pathPrefix}.description`, value)}
          validate={validateColumnDescription}
          onValidationError={(message) => showFeedback(message, 'error')}
          placeholder="Enter table description..."
        />
        <TextListsTagsFormField
          label="Synonyms"
          tags={table.synonyms || []}
          onChange={(newTags: string[]) => updateField(`${pathPrefix}.synonyms`, newTags)}
        />
        <FormControlLabel
          control={
            <Checkbox
              checked={table.exclude_description_on_generate_sql}
              onChange={(e) =>
                updateField(`${pathPrefix}.exclude_description_on_generate_sql`, e.target.checked)
              }
            />
          }
          label="Exclude Description on Generate SQL"
        />
      </Box>
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
    </>
  );
};

export default SchemaFormTablesGeneralInfo;