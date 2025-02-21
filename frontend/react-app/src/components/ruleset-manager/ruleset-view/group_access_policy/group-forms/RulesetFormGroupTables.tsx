import React, { useState } from 'react';
import { Box, TextField, Button, Paper, Autocomplete } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { GroupAccessPolicy } from 'types/ruleset/rulesetType';
import PaginatedForm from 'components/common/forms/PaginatedForm';
import AllowDenyFormField from 'components/ruleset-manager/common/AllowDenyFormField';
import { SimpleTablesResponse } from 'types/schema/schemaType';
import { separateColumnsByAccess } from 'utils/schema/tableUtils';

interface GroupTablesTabProps {
  group: GroupAccessPolicy;
  groupKey: string;
  onUpdate: (key: string, value: GroupAccessPolicy) => void;
  availableTables: SimpleTablesResponse;
}

const GroupTablesTab: React.FC<GroupTablesTabProps> = ({
  group,
  groupKey,
  onUpdate,
  availableTables
}) => {
  const handleAddTable = (tableName: string | null) => {
    if (!tableName) return;

    const tableColumns = availableTables.find(
      table => table.table_name === tableName
    )?.columns || [];
    
    const { allow, deny } = separateColumnsByAccess(tableColumns);

    const updatedTables = {
      ...group.tables,
      [tableName]: {
        columns: { allow, deny }
      }
    };

    onUpdate(groupKey, {
      ...group,
      tables: updatedTables
    });
  };

  const handleRemoveTable = (tableName: string) => {
    const updatedTables = { ...group.tables };
    delete updatedTables[tableName];

    onUpdate(groupKey, {
      ...group,
      tables: updatedTables
    });
  };

  const filterTableEntry = ([tableName]: [string, any], term: string) =>
    tableName.toLowerCase().includes(term.toLowerCase());

  return (
    <Box sx={{ p: 3 }}>
      <PaginatedForm
        items={Object.entries(group.tables)}
        searchPlaceholder="Search tables..."
        filterFunc={filterTableEntry}
        renderHeader={(searchTerm, setSearchTerm) => (
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
              options={availableTables.map(table => table.table_name)} // Convert to string array
              renderInput={(params) => (
                <TextField 
                  {...params} 
                  size="small" 
                  placeholder="Add table..." 
                />
              )}
              onChange={(_, value) => handleAddTable(value)}
              value={null}
            />
          </Box>
        )}
        renderItem={([tableName, tableRule]) => (
          <Paper sx={{ p: 2, mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ fontWeight: 'bold' }}>{tableName}</Box>
              <Button
                startIcon={<DeleteIcon />}
                onClick={() => handleRemoveTable(tableName)}
                color="error"
                size="small"
              >
                Remove
              </Button>
            </Box>
            <AllowDenyFormField
              columnRule={tableRule.columns}
              onChange={(newColumns) => {
                // Ensure allow is always string[]
                const allow = Array.isArray(newColumns.allow) 
                  ? newColumns.allow 
                  : [newColumns.allow];

                const updatedTables = {
                  ...group.tables,
                  [tableName]: {
                    columns: {
                      allow,
                      deny: newColumns.deny
                    }
                  }
                };
                onUpdate(groupKey, {
                  ...group,
                  tables: updatedTables
                });
              }}
              availableColumns={availableTables.find(t => t.table_name === tableName)?.columns || []}
            />
          </Paper>
        )}
      />
    </Box>
  );
};

export default GroupTablesTab;
