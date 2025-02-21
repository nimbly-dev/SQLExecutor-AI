import React, { useState, useMemo } from 'react';
import { 
  Box, TextField, Button, IconButton, 
  Paper, Typography 
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { GroupAccessPolicy } from 'types/ruleset/rulesetType';
import AddIcon from '@mui/icons-material/Add';
import { createDebouncedUpdate } from 'utils/forms/formUtils';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import PaginatedForm from 'components/common/forms/PaginatedForm';

interface RulesetFormMatchingCriteriaProps {
  group: GroupAccessPolicy;
  groupKey: string;
  onUpdate: (key: string, value: GroupAccessPolicy) => void;
}

interface EditingState {
  key: string;
  value: string;
}

const RulesetFormMatchingCriteria: React.FC<RulesetFormMatchingCriteriaProps> = ({
  group,
  groupKey,
  onUpdate
}) => {
  const [newFieldKey, setNewFieldKey] = useState('');
  const [editingFields, setEditingFields] = useState<Record<string, EditingState>>({});
  const [localCriteria, setField] = useLocalFormState(group.criteria);
  
  const debouncedUpdate = useMemo(() => createDebouncedUpdate(300), []);

  // Guard against undefined group
  if (!group || !group.criteria) {
    return null;
  }

  const handleAddField = () => {
    if (!newFieldKey) return;

    const updatedCriteria = {
      ...group.criteria,
      matching_criteria: {
        ...group.criteria.matching_criteria,
        [newFieldKey]: ''
      }
    };

    onUpdate(groupKey, {
      ...group,
      criteria: updatedCriteria
    });

    setNewFieldKey('');
  };

  const handleRemoveField = (field: string) => {
    const updatedCriteria = { ...group.criteria.matching_criteria };
    delete updatedCriteria[field];

    onUpdate(groupKey, {
      ...group,
      criteria: {
        ...group.criteria,
        matching_criteria: updatedCriteria
      }
    });
  };

  const handleFieldKeyChange = (oldKey: string, newValue: string) => {
    // Update local state immediately
    setEditingFields(prev => ({
      ...prev,
      [oldKey]: {
        key: newValue,
        value: prev[oldKey]?.value ?? group.criteria.matching_criteria[oldKey]
      }
    }));

    // Debounce the actual update
    debouncedUpdate(
      () => {
        if (!newValue || oldKey === newValue) return;

        const updatedCriteria = Object.entries(group.criteria.matching_criteria)
          .reduce((acc, [key, value]) => {
            if (key === oldKey) {
              acc[newValue] = value;
            } else {
              acc[key] = value;
            }
            return acc;
          }, {} as Record<string, any>);

        onUpdate(groupKey, {
          ...group,
          criteria: {
            ...group.criteria,
            matching_criteria: updatedCriteria
          }
        });

        // Clear local editing state after update
        setEditingFields(prev => {
          const next = { ...prev };
          delete next[oldKey];
          return next;
        });
      },
      'matching_criteria',
      newValue
    );
  };

  const handleFieldValueChange = (field: string, newValue: string) => {
    setEditingFields(prev => ({
      ...prev,
      [field]: {
        key: field,
        value: newValue
      }
    }));

    debouncedUpdate(
      () => {
        const updatedCriteria = {
          ...group.criteria.matching_criteria,
          [field]: newValue
        };

        onUpdate(groupKey, {
          ...group,
          criteria: {
            ...group.criteria,
            matching_criteria: updatedCriteria
          }
        });
      },
      'criteria',
      newValue
    );
  };

  return (
    <Box sx={{ p: 3, display: 'flex', flexDirection: 'column', gap: 3 }}>
      <TextField
        fullWidth
        multiline
        size="small"
        rows={3}
        label="Condition"
        value={localCriteria.condition || ''}
        onChange={(e) => {
          const newCondition = e.target.value;
          setField('condition', newCondition);
          debouncedUpdate(
            () => {
              onUpdate(groupKey, {
                ...group,
                criteria: {
                  ...group.criteria,
                  condition: newCondition
                }
              });
            },
            'condition',
            newCondition
          );
        }}
      />

      <PaginatedForm
        items={Object.entries(group.criteria.matching_criteria)}
        searchPlaceholder="Search fields..."
        filterFunc={(item, searchTerm) => {
          const [fieldKey] = item;
          return fieldKey.toLowerCase().includes(searchTerm.toLowerCase());
        }}
        renderHeader={(searchTerm, setSearchTerm) => (
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
            <TextField
              size="small"
              placeholder="Search fields..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              sx={{ flex: '60%' }}
            />
            <TextField
              label="New Field Key"
              value={newFieldKey}
              onChange={(e) => setNewFieldKey(e.target.value)}
              size="small"
              sx={{ flex: '40%' }}
              InputProps={{
                endAdornment: (
                  <Button
                    size="small"
                    onClick={handleAddField}
                    disabled={!newFieldKey}
                    startIcon={<AddIcon />}
                    sx={{ 
                      ml: 1,
                      whiteSpace: 'nowrap',
                      minWidth: 'auto'
                    }}
                  >
                    Add Field
                  </Button>
                ),
              }}
            />
          </Box>
        )}
        renderItem={([field, value]) => (
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
              <TextField
                fullWidth
                label="Field Key"
                value={editingFields[field]?.key ?? field}
                size="small"
                onChange={(e) => handleFieldKeyChange(field, e.target.value)}
              />
              <TextField
                fullWidth
                label="Field Value"
                value={editingFields[field]?.value ?? value}
                onChange={(e) => handleFieldValueChange(field, e.target.value)}
                size="small"
              />
              <IconButton
                onClick={() => handleRemoveField(field)}
                color="error"
                size="small"
              >
                <DeleteIcon />
              </IconButton>
            </Box>
          </Paper>
        )}
      />
    </Box>
  );
};

export default RulesetFormMatchingCriteria;
