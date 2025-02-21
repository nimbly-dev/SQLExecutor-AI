import React, { useState, useCallback, useMemo } from 'react';
import { Box, TextField, Button, Paper, Autocomplete } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import PaginatedForm from 'components/common/forms/PaginatedForm';
import { AllowDenyFormField } from 'components/ruleset-manager/common/AllowDenyFormField';
import { collectionOperations } from 'utils/forms/collectionUtils';
import { separateColumnsByAccess } from 'utils/schema/tableUtils';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import { UserSpecificAccessPolicy } from 'types/ruleset/rulesetType';
import { SimpleColumnResponse } from 'types/schema/schemaType';
import { createDebouncedUpdate } from 'utils/forms/formUtils';

interface UserTableRule {
  columns: {
    allow: string | string[];
    deny: string[];
  };
  condition: string;
}

interface UserSpecificTableRule {
  allow?: string | string[];
  deny?: string[];
  condition?: string;
}

interface UserPolicyFormTablesProps {
  selectedUser: string;
  policy: UserSpecificAccessPolicy;
  availableTables: string[];
  availableColumns: Record<string, SimpleColumnResponse[]>;
  onUpdate: (userId: string, updatedPolicy: UserSpecificAccessPolicy) => void;
}

const UserPolicyFormTables: React.FC<UserPolicyFormTablesProps> = ({
  selectedUser,
  policy,
  availableTables,
  availableColumns,
  onUpdate,
}) => {
  const initialTables = useMemo(() => {
    const tables = policy.tables as Record<string, UserSpecificTableRule>;
    return Object.entries(tables || {}).reduce((acc, [key, value]) => ({
      ...acc,
      [key]: {
        columns: {
          allow: value.allow || [],
          deny: value.deny || []
        },
        condition: value.condition || ''
      }
    }), {} as Record<string, UserTableRule>);
  }, [policy.tables]);

  const [localTables, setField, commit, reset, updateState] = useLocalFormState<Record<string, UserTableRule>>(initialTables);
  const [localConditions, setCondition, commitConditions] = useLocalFormState<Record<string, string>>(
    Object.entries(localTables).reduce((acc, [key, value]) => ({
      ...acc,
      [key]: value.condition
    }), {})
  );

  const debouncedSyncConditions = useMemo(() => createDebouncedUpdate(300), []);

  const { handleAdd, handleUpdate, handleRemove } = useMemo(() => 
    collectionOperations<UserTableRule>(
      localTables,
      updateState,
      (_path, value) => onUpdate(selectedUser, { ...policy, tables: value }),
      '',
      'tables'
    ), [localTables, selectedUser, policy, onUpdate]);

  const usedTables = useMemo(() => Object.keys(localTables), [localTables]);
  const availableTableOptions = useMemo(() =>
    availableTables.filter(table => !usedTables.includes(table))
  , [availableTables, usedTables]);

  // Add state to control Autocomplete input
  const [addTableInput, setAddTableInput] = useState('');

  const renderHeader = useCallback((searchTerm: string, setSearchTerm: (term: string) => void) => (
    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
      <TextField
        size="small"
        placeholder="Search tables..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        sx={{ flex: '60%' }}
      />
      <Autocomplete
        sx={{ flex: '40%' }}
        size="small"
        options={availableTableOptions}
        renderInput={(params) => (
          <TextField 
            {...params} 
            size="small" 
            placeholder="Add table..." 
          />
        )}
        onChange={(_, value) => {
          if (value) {
            const defaultRule = separateColumnsByAccess(availableColumns[value]);
            handleAdd(value, {
              columns: {
                allow: defaultRule.allow,
                deny: defaultRule.deny
              },
              condition: ''
            });
            setAddTableInput('');
          }
        }}
        value={null}
        inputValue={addTableInput}
        onInputChange={(_, newValue) => {
          setAddTableInput(newValue);
        }}
        clearOnBlur
        clearOnEscape
      />
    </Box>
  ), [availableTableOptions, availableColumns, handleAdd, addTableInput]);

  const renderTableRule = useCallback((tableName: string, rule: UserTableRule) => (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ fontWeight: 'bold' }}>{tableName}</Box>
        <Button
          startIcon={<DeleteIcon />}
          onClick={() => handleRemove(tableName)}
          color="error"
          size="small"
        >
          Remove
        </Button>
      </Box>
      <AllowDenyFormField
        columnRule={rule.columns}
        onChange={(updatedRule) => {
          const allow = Array.isArray(updatedRule.allow) 
            ? updatedRule.allow 
            : [updatedRule.allow];

          handleUpdate(tableName, {
            ...rule,
            columns: {
              allow,
              deny: updatedRule.deny
            }
          });
        }}
        availableColumns={availableColumns[tableName] || []}
      />
      <TextField
        fullWidth
        size="small"
        label="Condition"
        value={localConditions[tableName] || ''}
        onChange={(e) => {
          // Update local state immediately for responsive UI
          setCondition(tableName, e.target.value);
          
          // Debounce the sync with parent state
          debouncedSyncConditions(
            () => {
              const updatedRule = {
                ...rule,
                condition: e.target.value
              };
              handleUpdate(tableName, updatedRule);
              onUpdate(selectedUser, {
                ...policy,
                tables: {
                  ...localTables,
                  [tableName]: updatedRule
                }
              });
            },
            'condition',
            e.target.value
          );
        }}
        sx={{ mt: 2 }}
      />
    </Paper>
  ), [availableColumns, handleRemove, handleUpdate, localConditions, setCondition, debouncedSyncConditions, selectedUser, policy, localTables, onUpdate]);

  return (
    <Box sx={{ p: 3 }}>
      <PaginatedForm
        items={Object.entries(localTables)}
        filterFunc={(item, term) => item[0].toLowerCase().includes(term.toLowerCase())}
        renderHeader={renderHeader}
        renderItem={([tableName, rule]: [string, UserTableRule]) =>
          renderTableRule(tableName, rule)
        }
        pageSizeOptions={[3, 6, 8, 10]} // Add custom page size options
      />
    </Box>
  );
};

export default UserPolicyFormTables;
