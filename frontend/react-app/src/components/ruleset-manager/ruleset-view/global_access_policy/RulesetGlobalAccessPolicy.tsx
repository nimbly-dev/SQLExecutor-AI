import React, { useState, useEffect, useMemo } from 'react';
import { 
  Box, Button, Grid, Paper, TextField, Typography, InputAdornment,
  Dialog, DialogContent, DialogTitle, DialogActions, Autocomplete
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import { TableRule, Ruleset } from 'types/ruleset/rulesetType';
import { useFormUpdate } from 'contexts/form/FormUpdateProvider';
import { DataTable } from 'components/common/tables/DataTable';
import { JsonFormView } from 'components/common/forms/JsonFormView';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import { collectionOperations } from 'utils/forms/collectionUtils';
import { SimpleTablesResponse } from 'types/schema/schemaType';
import AllowDenyFormField from 'components/ruleset-manager/common/AllowDenyFormField';
import { separateColumnsByAccess } from 'utils/schema/tableUtils';

interface RulesetGlobalAccessPolicyProps {
  ruleset: Ruleset;
  availableTables: SimpleTablesResponse;
}

export const RulesetGlobalAccessPolicy: React.FC<RulesetGlobalAccessPolicyProps> = ({ 
  ruleset,
  availableTables 
}) => {
  const { updateField } = useFormUpdate();
  const [viewMode, setViewMode] = useState<'form' | 'json'>('form');
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(5);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [isAddingTable, setIsAddingTable] = useState(false);

  // Local state for tables
  const [localTables, , , , updateState] = useLocalFormState<Record<string, TableRule>>(
    ruleset.global_access_policy.tables || {}
  );

  const { handleAdd, handleUpdate, handleRemove } = collectionOperations(
    localTables,
    updateState,
    (path: string, value: any) => {
      updateField('global_access_policy.tables', value);
    },
    '',
    'tables'
  );

  // Filter and paginate tables
  const filteredAndPaginatedTables = useMemo(() => {
    const tableEntries = Object.entries(localTables);
    const filtered = tableEntries.filter(([key]) => 
      key.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const start = page * pageSize;
    const end = start + pageSize;

    return {
      items: filtered.slice(start, end),
      total: filtered.length
    };
  }, [localTables, searchTerm, page, pageSize]);

  const handleJsonChange = (newData: Record<string, TableRule>) => {
    updateField('global_access_policy.tables', newData);
  };

  const columns = [
    { 
      id: 'table', 
      label: 'Table', 
      render: (item: [string, TableRule]) => item[0]
    }
  ];

  const availableTableOptions = useMemo(() => 
    availableTables
      .map(table => table.table_name)
      .filter(tableName => !localTables[tableName]),
    [availableTables, localTables]
  );

  return (
    <>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant={viewMode === 'form' ? 'contained' : 'outlined'}
            onClick={() => setViewMode('form')}
          >
            Form View
          </Button>
          <Button
            variant={viewMode === 'json' ? 'contained' : 'outlined'}
            onClick={() => setViewMode('json')}
          >
            JSON View
          </Button>
        </Box>
      </Box>

      {viewMode === 'form' ? (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <TextField
                    size="small"
                    placeholder="Search tables..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <SearchIcon />
                        </InputAdornment>
                      )
                    }}
                  />
                  <Button
                    startIcon={<AddIcon />}
                    onClick={() => setIsAddingTable(true)}
                    variant="contained"
                  >
                    Add Table
                  </Button>
                </Box>
              </Box>

              <DataTable
                items={filteredAndPaginatedTables.items}
                columns={columns}
                total={filteredAndPaginatedTables.total}
                page={page}
                pageSize={pageSize}
                onPageChange={setPage}
                onPageSizeChange={(e) => setPageSize(Number(e.target.value))}
                rowActions={(item: [string, TableRule]) => (
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => setSelectedTable(item[0])}
                    >
                      View
                    </Button>
                    <Button
                      variant="outlined"
                      color="error"
                      size="small"
                      onClick={() => handleRemove(item[0])}
                    >
                      Delete
                    </Button>
                  </Box>
                )}
              />
            </Paper>
          </Grid>
        </Grid>
      ) : (
        <JsonFormView
          data={localTables}
          onChange={handleJsonChange}
        />
      )}

      {/* Add Table Dialog */}
      <Dialog 
        open={isAddingTable} 
        onClose={() => setIsAddingTable(false)}
        maxWidth="sm"  
        fullWidth      
      >
        <DialogTitle>Add Table</DialogTitle>
        <DialogContent sx={{ minHeight: '150px', pt: 2 }}>
          <Autocomplete
            options={availableTableOptions}  // Use filtered options
            renderInput={(params) => (
              <TextField 
                {...params} 
                label="Select Table" 
                fullWidth 
              />
            )}
            onChange={(_, value) => {
              if (value) {
                // Get columns for selected table
                const tableColumns = availableTables.find(
                  table => table.table_name === value
                )?.columns || [];
                
                const { allow, deny } = separateColumnsByAccess(tableColumns);

                handleAdd(value, {
                  columns: { allow, deny },
                  condition: ''
                });
                setIsAddingTable(false);
              }
            }}
            noOptionsText="No available tables to add"  // Add helpful message when no options
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsAddingTable(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>

      {/* View/Edit Table Dialog */}
      <Dialog 
        open={!!selectedTable} 
        onClose={() => setSelectedTable(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Edit Table: {selectedTable}</DialogTitle>
        <DialogContent>
          {selectedTable && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 2 }}>
              <AllowDenyFormField
                columnRule={localTables[selectedTable].columns}
                onChange={(newColumnRule) => {
                  handleUpdate(selectedTable, {
                    ...localTables[selectedTable],
                    columns: newColumnRule
                  });
                }}
                availableColumns={availableTables.find(t => t.table_name === selectedTable)?.columns || []}
              />
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Condition"
                value={localTables[selectedTable].condition}
                onChange={(e) => {
                  handleUpdate(selectedTable, {
                    ...localTables[selectedTable],
                    condition: e.target.value
                  });
                }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedTable(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default RulesetGlobalAccessPolicy;
