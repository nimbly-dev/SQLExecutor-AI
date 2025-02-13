import React, { useCallback, useMemo, useEffect } from 'react';
import { Box, TextField, MenuItem, FormControlLabel, Checkbox, Button, Portal, Snackbar, Alert } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { Table, VALID_TYPES_ENUM, VALID_CONSTRAINTS_ENUM, Column } from 'types/schema/schemaType';
import PaginatedForm from 'components/common/forms/PaginatedForm';
import EditableCardFormContent from 'components/common/forms/EditableCardFormContent';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import { useFormUpdate } from 'contexts/form/FormUpdateProvider';
import TextListsTagsFormField from 'components/common/forms/field-forms/TextListsTagsFormField';
import SelectTagsFormField from 'components/common/forms/field-forms/SelectTagsFormField';
import { validateColumnDescription } from 'validations/schema-manager/common/description.validations';
import { useValidationFeedback, AlertSeverity } from 'hooks/common/feedback/useValidationFeedback';
import { getAvailableConstraints } from 'validations/schema-manager/tables/columns/constraints.validations';
import { createDebouncedUpdate } from 'utils/forms/formUtils';
import { collectionOperations } from 'utils/forms/collectionUtils'; 

interface SchemaFormTablesColumnsDefinitionProps {
  table: Table;
  pathPrefix: string;
  updateField: (path: string, value: any) => void;
}

type FlattenedColumn = Column & { name: string };

interface ColumnCardProps {
  col: FlattenedColumn;
  pathPrefix: string;
  removeColumn: (key: string) => void;
  onUpdate: (key: string, updatedColumn: Column) => void;
  onRename: (oldKey: string, newKey: string, columnData: Column) => void;
}

const ColumnCard: React.FC<ColumnCardProps> = React.memo(
  ({ col, pathPrefix, removeColumn, onUpdate, onRename }) => {
    const theme = useTheme();
    const [localState, setField] = useLocalFormState({
      type: col.type,
      description: col.description,
      synonyms: col.synonyms.join(', '),
    });
    const { updateField } = useFormUpdate();
    const { feedback, showFeedback, clearFeedback } = useValidationFeedback();

    // Compute column path based on columns type.
    const columnPath = `${pathPrefix}.columns.${col.name}`;

    const debouncedUpdate = useMemo(() => createDebouncedUpdate<typeof localState>(300), [
      columnPath,
      updateField,
      showFeedback,
    ]);
    useEffect(() => {
      return () => {
        if ((debouncedUpdate as any).cancel instanceof Function) {
          (debouncedUpdate as any).cancel();
        }
      };
    }, [debouncedUpdate]);

    const handleDescriptionChange = useCallback(
      (value: string) => {
        try {
          const validationResult = validateColumnDescription(value);
          if (validationResult?.type === 'error') {
            showFeedback(validationResult.message, validationResult.type);
            return;
          }
          debouncedUpdate(
            (action) => {
              try {
                updateField(`${columnPath}.description`, action.value);
              } catch (updateError) {
                console.warn('Update field failed:', updateError);
              }
            },
            'description',
            value,
            { strict: true }
          );
        } catch (error) {
          console.error('Validation error:', error);
          showFeedback('Invalid description format', 'error');
        }
      },
      [debouncedUpdate, columnPath, updateField, showFeedback]
    );

    return (
      <>
        <EditableCardFormContent
          fieldKey={col.name}
          fieldValue={col}
          titleLabel="Column"
          onChange={(newKey) => onRename(col.name, newKey, col)}
          onDelete={() => removeColumn(col.name)}
          defaultExpanded={true}
        >
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              select
              label="Column Type"
              value={localState.type}
              onChange={(e) => {
                setField('type', e.target.value);
                onUpdate(col.name, { ...col, type: e.target.value });
              }}
              fullWidth
              variant="outlined"
              size="small"
              SelectProps={{ MenuProps: { disablePortal: true } }}
            >
              {Object.values(VALID_TYPES_ENUM).map((type) => (
                <MenuItem key={type} value={type}>
                  {type}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Description"
              value={localState.description}
              onChange={(e) => {
                const newValue = e.target.value;
                if (newValue.length > 64) {
                  showFeedback('Description too long', 'error'); // Block further input and show alert
                  return;
                }
                setField('description', newValue);
                handleDescriptionChange(newValue);
              }}
              fullWidth
              multiline
              minRows={2}
              maxRows={4}
              variant="outlined"
              size="small"
              error={localState.description.length > 64}
              helperText={
                localState.description.length > 64 ? 'Description too long' : ''
              }
            />
            <TextListsTagsFormField
              label="Synonyms"
              placeholder="Type synonym and press Enter"
              tags={col.synonyms}
              onChange={(newTags) =>
                onUpdate(col.name, { ...col, synonyms: newTags })
              }
            />
            <SelectTagsFormField
              options={getAvailableConstraints(col.constraints)}
              selected={col.constraints}
              onChange={(newConstraints, action, changedConstraint) => {
                let updatedConstraints = [...newConstraints];
                if (
                  action === 'add' &&
                  changedConstraint === VALID_CONSTRAINTS_ENUM.PRIMARY_KEY
                ) {
                  if (!updatedConstraints.includes(VALID_CONSTRAINTS_ENUM.NOT_NULL)) {
                    updatedConstraints.push(VALID_CONSTRAINTS_ENUM.NOT_NULL);
                  }
                  if (!updatedConstraints.includes(VALID_CONSTRAINTS_ENUM.UNIQUE)) {
                    updatedConstraints.push(VALID_CONSTRAINTS_ENUM.UNIQUE);
                  }
                  showFeedback(
                    'Automatically added NOT NULL and UNIQUE for PRIMARY KEY',
                    'success'
                  );
                }
                onUpdate(col.name, { ...col, constraints: updatedConstraints });
              }}
              label="Constraints"
              placeholder="Select constraints"
              showSelectedInField={false}
              customTextValue="Select constraints..."
              getTooltip={(constraint: string) => {
                const tooltips: Record<string, string> = {
                  [VALID_CONSTRAINTS_ENUM.PRIMARY_KEY]:
                    'Unique identifier for the row. Automatically applies NOT NULL and UNIQUE.',
                  [VALID_CONSTRAINTS_ENUM.FOREIGN_KEY]:
                    'References a PRIMARY KEY in another table.',
                  [VALID_CONSTRAINTS_ENUM.NOT_NULL]:
                    'Ensures the field cannot be empty.',
                  [VALID_CONSTRAINTS_ENUM.UNIQUE]:
                    'Ensures all values in this column are unique.',
                };
                return tooltips[constraint] || '';
              }}
            />
            <Box sx={{ mt: 1, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={col.exclude_description_on_generate_sql}
                    onChange={(e) =>
                      onUpdate(col.name, {
                        ...col,
                        exclude_description_on_generate_sql: e.target.checked,
                      })
                    }
                    size="small"
                  />
                }
                label="Exclude Description when Resolving Schema"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={col.is_sensitive_column}
                    onChange={(e) =>
                      onUpdate(col.name, { ...col, is_sensitive_column: e.target.checked })
                    }
                    size="small"
                  />
                }
                label="Sensitive Column"
              />
            </Box>
          </Box>
        </EditableCardFormContent>
        <Portal>
          <Snackbar
            open={!!feedback}
            autoHideDuration={4000}
            onClose={clearFeedback}
            anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
            sx={{
              position: 'fixed',
              zIndex: theme.zIndex.snackbar,
              '& .MuiSnackbar-root': { position: 'fixed', top: '24px' },
            }}
          >
            <Alert
              onClose={clearFeedback}
              severity={(feedback?.type || 'error') as AlertSeverity}
              variant="filled"
              sx={{
                width: '100%',
                display: feedback ? 'flex' : 'none',
                boxShadow: theme.shadows[4],
                position: 'relative',
              }}
            >
              {feedback?.message || ''}
            </Alert>
          </Snackbar>
        </Portal>
      </>
    );
  }
);

const SchemaFormTablesColumnsDefinition: React.FC<SchemaFormTablesColumnsDefinitionProps> = ({
  table,
  pathPrefix,
  updateField,
}) => {
  const initialColumns = useMemo(() => {
    return table.columns || {};
  }, [table.columns]);

  const [localColumns, , , , updateState] = useLocalFormState<Record<string, Column>>(
    initialColumns
  );
  const { feedback, showFeedback, clearFeedback } = useValidationFeedback();

  const { handleAdd, handleUpdate: baseHandleUpdate, handleRemove, handleRename } =
    collectionOperations(
      localColumns,
      updateState,
      updateField,
      pathPrefix,
      'columns',
      {
        onError: (message: string) => showFeedback(message, 'error'),
        onSuccess: (message: string) => showFeedback(message, 'success'),
        errorMessages: {
          addFailed: 'Failed to add column',
          removeFailed: 'Failed to remove column',
          renameFailed: 'Failed to rename column',
          itemNotFound: 'Column not found',
        },
        successMessages: {
          addSuccess: 'Column added successfully',
          removeSuccess: 'Column removed successfully',
          renameSuccess: 'Column renamed successfully',
        },
      }
    );

  // Wrap handleUpdate to strip out the name property
  const handleUpdate = useCallback(
    (key: string, updatedColumn: Column & { name?: string }) => {
      const { name, ...columnData } = updatedColumn;
      baseHandleUpdate(key, columnData);
    },
    [baseHandleUpdate]
  );

  const defaultColumn: Column = {
    type: VALID_TYPES_ENUM.TEXT,
    description: '',
    constraints: [],
    synonyms: [],
    is_sensitive_column: false,
    exclude_description_on_generate_sql: false,
  };

  const displayColumns = useMemo(() => {
    return Object.entries(localColumns || {})
      .map(([name, data]) => {
        if (!data) return null;
        const safeData: Column = {
          type: data.type || VALID_TYPES_ENUM.TEXT,
          description: data.description || '',
          constraints: data.constraints || [],
          synonyms: data.synonyms || [],
          is_sensitive_column: data.is_sensitive_column || false,
          exclude_description_on_generate_sql:
            data.exclude_description_on_generate_sql || false,
        };
        return {
          ...safeData,
          name,
        };
      })
      .filter(Boolean) as FlattenedColumn[];
  }, [localColumns]);

  return (
    <Box>
      <PaginatedForm<FlattenedColumn>
        items={displayColumns}
        searchPlaceholder="Search Columns"
        paginationLabel="Columns per page"
        pageSizeOptions={[5, 10, 15, 20]}
        filterFunc={(col, searchTerm) => {
          if (!col || !col.name) return false;
          const search = searchTerm.toLowerCase();
          return (
            col.name.toLowerCase().includes(search) ||
            (col.description || '').toLowerCase().includes(search) ||
            (col.synonyms || []).some((syn: string) =>
              syn.toLowerCase().includes(search)
            ) ||
            (col.constraints || []).some((constraint: string) =>
              constraint.toLowerCase().includes(search)
            )
          );
        }}
        renderItem={(col) => (
          <Box key={col.name}>
            <ColumnCard
              col={col}
              pathPrefix={pathPrefix}
              removeColumn={() => handleRemove(col.name)}
              onUpdate={handleUpdate}
              onRename={handleRename}
            />
          </Box>
        )}
      />
      <Button
        variant="contained"
        onClick={() => handleAdd(`column_${Date.now()}`, defaultColumn)}
        size="small"
      >
        Add Column
      </Button>
    </Box>
  );
};

export default SchemaFormTablesColumnsDefinition;