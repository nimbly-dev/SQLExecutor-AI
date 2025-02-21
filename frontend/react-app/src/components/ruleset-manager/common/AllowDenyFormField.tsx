import React, { useMemo, useState } from 'react';
import { Box, Chip, Stack, Autocomplete, TextField } from '@mui/material';
import { ColumnRule } from 'types/ruleset/rulesetType';
import { SimpleColumnResponse } from 'types/schema/schemaType';


interface AllowDenyFormFieldProps {
  columnRule: ColumnRule;
  onChange: (updatedRule: ColumnRule) => void;
  availableColumns: SimpleColumnResponse[]; 
}

const ALL_COLUMNS = '*';

export const AllowDenyFormField: React.FC<AllowDenyFormFieldProps> = ({
  columnRule,
  onChange,
  availableColumns
}) => {
  const columns = useMemo(() => availableColumns.map(col => col.column_name), [availableColumns]);

  const allowedColumns = useMemo(() => {
    return Array.isArray(columnRule.allow) ? columnRule.allow : [columnRule.allow];
  }, [columnRule.allow]);

  const deniedColumns = useMemo(() => {
    return columnRule.deny;
  }, [columnRule.deny]);

  const hasAllInAllow = allowedColumns.includes(ALL_COLUMNS);
  const hasAllInDeny = deniedColumns.includes(ALL_COLUMNS);

  const allowOptions = useMemo(() => {
    if (hasAllInDeny) return [];
    return [
      ALL_COLUMNS,
      ...columns.filter(col => 
        !deniedColumns.includes(col) && 
        !allowedColumns.includes(col)
      )
    ];
  }, [columns, deniedColumns, hasAllInDeny, allowedColumns]);

  const denyOptions = useMemo(() => {
    if (hasAllInAllow) return [];
    return [
      ALL_COLUMNS,
      ...columns.filter(col => 
        !allowedColumns.includes(col) && 
        !deniedColumns.includes(col)
      )
    ];
  }, [columns, allowedColumns, hasAllInAllow, deniedColumns]);

  // Add inputValue states
  const [allowInputValue, setAllowInputValue] = useState('');
  const [denyInputValue, setDenyInputValue] = useState('');

  // Change handlers
  const handleAllowChange = (_: any, value: string | null) => {
    if (!value) return;
    
    if (value === ALL_COLUMNS) {
      onChange({ allow: ALL_COLUMNS, deny: [] });
    } else {
      const newAllow = [...allowedColumns];
      if (!newAllow.includes(value)) {
        newAllow.push(value);
      }
      onChange({ ...columnRule, allow: newAllow });
    }
    // Reset input value after selection
    setAllowInputValue('');
  };

  const handleDenyChange = (_: any, value: string | null) => {
    if (!value) return;

    if (value === ALL_COLUMNS) {
      onChange({ allow: [], deny: [ALL_COLUMNS] });
    } else {
      const newDeny = [...deniedColumns];
      if (!newDeny.includes(value)) {
        newDeny.push(value);
      }
      onChange({ ...columnRule, deny: newDeny });
    }
    // Reset input value after selection
    setDenyInputValue('');
  };

  const handleRemoveAllow = (column: string) => {
    const newAllow = allowedColumns.filter(col => col !== column);
    onChange({ ...columnRule, allow: newAllow });
  };

  const handleRemoveDeny = (column: string) => {
    const newDeny = deniedColumns.filter(col => col !== column);
    onChange({ ...columnRule, deny: newDeny });
  };

  return (
    <Stack spacing={2}>
      {/* Allow Section */}
      <Box>
        <Autocomplete
          disabled={hasAllInDeny || hasAllInAllow}  
          options={allowOptions}
          value={null} 
          inputValue={allowInputValue}
          onInputChange={(_, newInputValue) => {
            setAllowInputValue(newInputValue);
          }}
          onChange={handleAllowChange}
          clearOnBlur
          selectOnFocus
          handleHomeEndKeys
          renderInput={(params) => (
            <TextField 
              {...params} 
              label="Allow Columns"
              placeholder={hasAllInAllow ? "All columns are allowed" : "Select columns to allow..."}
              disabled={hasAllInDeny || hasAllInAllow}  
            />
          )}
          renderOption={(props, option) => (
            <li {...props}>
              {option === ALL_COLUMNS ? 'All Columns (*)' : option}
            </li>
          )}
        />
        <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {allowedColumns.map((column) => (
            <Chip
              key={column}
              label={column === ALL_COLUMNS ? 'All Columns (*)' : column}
              onDelete={() => handleRemoveAllow(column)}  
              color={column === ALL_COLUMNS ? 'success' : 'default'}
            />
          ))}
        </Box>
      </Box>

      {/* Deny Section */}
      <Box>
        <Autocomplete
          disabled={hasAllInAllow || hasAllInDeny}  
          options={denyOptions}
          value={null}  
          inputValue={denyInputValue}
          onInputChange={(_, newInputValue) => {
            setDenyInputValue(newInputValue);
          }}
          onChange={handleDenyChange}
          clearOnBlur
          selectOnFocus
          handleHomeEndKeys
          renderInput={(params) => (
            <TextField 
              {...params} 
              label="Deny Columns"
              placeholder={hasAllInDeny ? "All columns are denied" : "Select columns to deny..."}
              disabled={hasAllInAllow || hasAllInDeny}  // Also disable TextField
            />
          )}
          renderOption={(props, option) => (
            <li {...props}>
              {option === ALL_COLUMNS ? 'All Columns (*)' : option}
            </li>
          )}
        />
        <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {deniedColumns.map((column) => (
            <Chip
              key={column}
              label={column === ALL_COLUMNS ? 'All Columns (*)' : column}
              onDelete={() => handleRemoveDeny(column)}  // Remove conditional disable
              color={column === ALL_COLUMNS ? 'error' : 'default'}
            />
          ))}
        </Box>
      </Box>
    </Stack>
  );
};

export default AllowDenyFormField;
