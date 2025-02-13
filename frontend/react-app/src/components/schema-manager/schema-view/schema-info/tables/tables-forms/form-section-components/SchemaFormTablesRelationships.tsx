import React, { useCallback, useMemo } from 'react';
import {
  Box,
  Button,
  Checkbox,
  FormControlLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Snackbar,
  Alert,
} from '@mui/material';
import PaginatedForm from 'components/common/forms/PaginatedForm';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import { Table, Joins, VALID_JOINS_ENUM } from 'types/schema/schemaType';
import { useValidationFeedback, AlertSeverity } from 'hooks/common/feedback/useValidationFeedback';
import EditableCardFormContent from 'components/common/forms/EditableCardFormContent';
import { collectionOperations } from 'utils/forms/collectionUtils';
import DescriptionTextFormField from 'components/common/forms/field-forms/DescriptionTextFormField';
import { validateColumnDescription } from 'validations/schema-manager/common/description.validations';
import DynamicSelectFormField from 'components/common/forms/field-forms/DynamicSelectFormField';
import DynamicAutocompleteFormField from 'components/common/forms/field-forms/DynamicAutocompleteFormField';

interface SchemaFormTablesRelationshipsProps {
  table: Table;
  allTables: Array<{ key: string } & Table>;
  pathPrefix: string;
  updateField: (path: string, value: any) => void;
}

interface RelationshipCardProps {
  relationshipKey: string;
  relationship: Joins;
  availableTableNames: string[];
  currentTableKey: string; // Changed from currentTableName
  allTables: Array<{ key: string } & Table>;
  onUpdate: (key: string, updated: Joins) => void;
  onRemove: (key: string) => void;
}

const RelationshipCard: React.FC<RelationshipCardProps> = ({
  relationshipKey,
  relationship,
  availableTableNames,
  currentTableKey, // Changed from currentTableName
  allTables,
  onUpdate,
  onRemove,
}) => {
  const [localState, setField] = useLocalFormState<Joins>(relationship);
  const { feedback, showFeedback, clearFeedback } = useValidationFeedback();

  const handleChange = useCallback((field: keyof Joins, value: any) => {
    const updatedRelationship: Joins = {
      ...localState,
      [field]: value,
      description: field === 'description' ? value : localState.description,
      exclude_description_on_generate_sql: field === 'exclude_description_on_generate_sql' ? value : localState.exclude_description_on_generate_sql,
      table: field === 'table' ? value : localState.table,
      on: field === 'on' ? value : localState.on,
      type: field === 'type' ? value as Joins['type'] : localState.type,
    };
    setField(field, value);
    onUpdate(relationshipKey, updatedRelationship);
  }, [relationshipKey, localState, onUpdate, setField]);

  const getOnConditionOptions = useCallback(() => {
    if (!localState.table) return { options: [] };

    const relatedTable = allTables.find(t => t.key === localState.table);
    const currentTableEntry = allTables.find(t => t.key === currentTableKey);

    if (!relatedTable?.columns || !currentTableEntry?.columns) return { options: [] };

    const optionsSet: { [key: string]: boolean } = {};

    // Check for all FOREIGN KEY constraints in current table
    Object.entries(currentTableEntry.columns || {}).forEach(([columnName, column]) => {
      if (column?.constraints?.includes('FOREIGN KEY')) {
        const joinCondition = `${currentTableKey}.${columnName} = ${localState.table}.${columnName}`;
        optionsSet[joinCondition] = true;
      }
    });

    // Check for all FOREIGN KEY constraints in related table
    Object.entries(relatedTable.columns || {}).forEach(([columnName, column]) => {
      if (column?.constraints?.includes('FOREIGN KEY')) {
        const joinCondition = `${currentTableKey}.${columnName} = ${localState.table}.${columnName}`;
        optionsSet[joinCondition] = true;
      }
    });

    console.log('Generated join options:', {
      currentTable: currentTableKey,
      relatedTable: localState.table,
      options: Object.keys(optionsSet)
    });

    return {
      options: Object.keys(optionsSet),
      getOptionLabel: (option: string) => option,
      isOptionEqualToValue: (option: string, value: string) => String(option) === String(value)
    };
  }, [currentTableKey, localState.table, allTables]);

  return (
    <EditableCardFormContent
      fieldKey={relationshipKey}
      fieldValue={localState}
      titleLabel="Relationship"
      onChange={(newKey) => onUpdate(newKey, {...relationship, ...localState} as Joins)}
      onDelete={() => onRemove(relationshipKey)}
      defaultExpanded={true}
    >
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <DynamicSelectFormField
          label="Related Table"
          value={localState.table}
          onChange={(value) => handleChange('table', value)}
          options={availableTableNames.map(tableName => ({
            value: tableName,
            label: tableName
          }))}
          placeholder="Select a table to relate to..."
        />

        <DynamicAutocompleteFormField<string>
          label="On Condition"
          value={localState.on || ''} 
          onChange={(value) => handleChange('on', value || '')}
          optionsHandler={getOnConditionOptions}
          placeholder="Define join condition"
          helperText="Define how tables are related"
          clearOnBlur={false}
          selectOnFocus
          handleHomeEndKeys
          freeSolo
          open={true}
          disableCloseOnSelect
        />

        <FormControl fullWidth size="small">
          <InputLabel id={`join-type-label-${relationshipKey}`}>Join Type</InputLabel>
          <Select
            labelId={`join-type-label-${relationshipKey}`}
            id={`join-type-select-${relationshipKey}`}
            value={localState.type}
            onChange={(e) => handleChange('type', e.target.value)}
            label="Join Type"
            MenuProps={{
              anchorOrigin: {
                vertical: 'bottom',
                horizontal: 'left',
              },
              transformOrigin: {
                vertical: 'top',
                horizontal: 'left',
              },
            }}
          >
            {Object.values(VALID_JOINS_ENUM).map((joinType) => (
              <MenuItem key={joinType} value={joinType}>
                {joinType}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <DescriptionTextFormField
          description={localState.description ?? ''}
          onChange={(value) => handleChange('description', value)}
          validate={validateColumnDescription}
          onValidationError={(message) => showFeedback(message, 'error')}
          placeholder="Enter relationship description..."
        />

        <FormControlLabel
          control={
            <Checkbox
              checked={localState.exclude_description_on_generate_sql}
              onChange={(e) => handleChange('exclude_description_on_generate_sql', e.target.checked)}
            />
          }
          label="Exclude Description when Resolving Schema"
        />
      </Box>

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
    </EditableCardFormContent>
  );
};

const SchemaFormTablesRelationships: React.FC<SchemaFormTablesRelationshipsProps> = ({
  table,
  allTables,
  pathPrefix,
  updateField,
}) => {
  const initialRelationships = table.relationships || {};
  const [localRelationships, _, __, ___, updateState] = 
    useLocalFormState<Record<string, Joins>>(initialRelationships);

  const { feedback, showFeedback, clearFeedback } = useValidationFeedback();

  const { handleAdd, handleUpdate, handleRemove, handleRename } = collectionOperations(
    localRelationships,
    updateState,
    updateField,
    pathPrefix,
    'relationships',
    {
      onError: (message) => showFeedback(message, 'error'),
      onSuccess: (message) => showFeedback(message, 'success'),
      errorMessages: {
        addFailed: 'Failed to add relationship',
        removeFailed: 'Failed to remove relationship',
        renameFailed: 'Failed to rename relationship',
        itemNotFound: 'Relationship not found',
      },
      successMessages: {
        addSuccess: 'Relationship added successfully',
        removeSuccess: 'Relationship removed successfully',
        renameSuccess: 'Relationship renamed successfully',
      }
    }
  );

  const defaultRelationship: Joins = {
    description: '',
    exclude_description_on_generate_sql: false,
    table: '',
    on: '',
    type: VALID_JOINS_ENUM.INNER,
  };

  const handleAddRelationship = useCallback(() => {
    const relationshipKey = `rel_${Date.now()}`;
    handleAdd(relationshipKey, defaultRelationship);
  }, [handleAdd]);

  const handleUpdateRelationship = useCallback((key: string, updatedRelationship: Joins) => {
    if (key !== updatedRelationship.table) {
      // If key is different from table name, it's a rename operation
      handleRename(key, updatedRelationship.table, updatedRelationship);
    } else {
      // Otherwise it's just an update
      handleUpdate(key, updatedRelationship);
    }
  }, [handleUpdate, handleRename]);

  const availableTableNames = useMemo(() => 
    allTables.map((t) => t.key), 
  [allTables]);

  return (
    <Box>
      <PaginatedForm
        items={Object.entries(localRelationships).map(([key, rel]) => ({
          key,
          ...rel,
        }))}
        searchPlaceholder="Search Relationships"
        paginationLabel="Relationships per page"
        pageSizeOptions={[5, 10, 15, 20]}
        filterFunc={(rel, searchTerm) => {
          const search = searchTerm.toLowerCase();
          return (
            rel.key.toLowerCase().includes(search) ||
            (rel.table || '').toLowerCase().includes(search) ||
            (rel.description || '').toLowerCase().includes(search) ||
            (rel.type || '').toLowerCase().includes(search)
          );
        }}
        renderItem={(rel) => (
          <RelationshipCard
            key={rel.key}
            relationshipKey={rel.key}
            relationship={rel}
            availableTableNames={availableTableNames}
            currentTableKey={pathPrefix.split('.')[1]} // Get table key from path
            allTables={allTables}
            onUpdate={handleUpdateRelationship}
            onRemove={handleRemove}
          />
        )}
      />
      <Button 
        variant="contained" 
        onClick={handleAddRelationship} 
        size="small"
      >
        Add Relationship
      </Button>
    </Box>
  );
};

export default SchemaFormTablesRelationships;
