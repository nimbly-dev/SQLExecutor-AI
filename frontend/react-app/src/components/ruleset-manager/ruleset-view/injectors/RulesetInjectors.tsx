import React, { useState, useMemo, useCallback } from 'react';
import { Box, Button, Grid, Paper, TextField, Typography, InputAdornment, Dialog, DialogTitle, DialogContent, DialogActions, Tabs, Tab } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import { Injector, Ruleset } from 'types/ruleset/rulesetType';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import { collectionOperations } from 'utils/forms/collectionUtils';
import { useFormUpdate } from 'contexts/form/FormUpdateProvider';
import { DataTable } from 'components/common/tables/DataTable';
import MultiTabModal, { TabItem } from 'components/common/modal/MultiTabModal';
import RulesetFormInjectorDetails from './injector-forms/RulesetFormInjectorDetails';
import RulesetFormInjectorTables from './injector-forms/RulesetFormInjectorTables';
import { JsonFormView } from 'components/common/forms/JsonFormView';
import { SimpleTablesResponse } from 'types/schema/schemaType';

interface RulesetInjectorsProps {
  ruleset: Ruleset;
  availableTables: SimpleTablesResponse;  // Update type
}

const DEFAULT_INJECTOR: Injector = {
  enabled: true,
  condition: '',
  tables: {}
};

type TabValue = 'details' | 'tables';

export const RulesetInjectors: React.FC<RulesetInjectorsProps> = ({ 
  ruleset,
  availableTables
}) => {
  const { updateField } = useFormUpdate();
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(5);
  const [selectedInjector, setSelectedInjector] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabValue>('details');
  const [viewMode, setViewMode] = useState<'form' | 'json'>('form');
  // Use simple state here for selected injector
  const [selectedInjectorData, setSelectedInjectorData] = useState<Injector>(DEFAULT_INJECTOR);
  const [injectorToDelete, setInjectorToDelete] = useState<string | null>(null);
  
  const [localInjectors, , , , updateState] = useLocalFormState<Record<string, Injector>>(
    ruleset.injectors || {}
  );

  const { handleAdd, handleUpdate, handleRemove, handleRename } = collectionOperations(
    localInjectors,
    updateState,
    (path: string, value: any) => {
      const updatedInjectors = value === undefined ? {} : value;
      
      if (typeof updatedInjectors !== 'object') {
        console.error('Invalid injectors update:', updatedInjectors);
        return;
      }

      updateField('injectors', updatedInjectors);

      // Clean up modal state if needed
      if (selectedInjector && (value === undefined || !updatedInjectors[selectedInjector])) {
        setSelectedInjector(null);
        setSelectedInjectorData(DEFAULT_INJECTOR);
      }
    },
    '',
    'injectors'
  );

  const filteredInjectors = useMemo(() => {
    const injectorEntries = Object.entries(localInjectors);
    return injectorEntries.filter(([key]) =>
      key.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [localInjectors, searchTerm]);

  const paginatedData = useMemo(() => {
    const start = page * pageSize;
    const end = start + pageSize; 
    return filteredInjectors.slice(start, end);
  }, [filteredInjectors, page, pageSize]);

  const handleAddInjector = () => {
    const newKey = `injector_${Object.keys(localInjectors).length + 1}`;
    handleAdd(newKey, DEFAULT_INJECTOR);
  };

  const handleEdit = (key: string) => {
    setSelectedInjector(key);
    setSelectedInjectorData({
      ...DEFAULT_INJECTOR,  
      ...localInjectors[key], 
      tables: { ...(localInjectors[key]?.tables || {}) } 
    });
  };

  const updateSelectedInjectorField = <K extends keyof Injector>(field: K, value: Injector[K]) => {
    if (!selectedInjector) return;

    const updatedInjector = {
      ...selectedInjectorData,
      [field]: value
    };

    setSelectedInjectorData(updatedInjector);
    handleUpdate(selectedInjector, updatedInjector);
  };

  const handleInjectorDelete = useCallback((key: string) => {
    if (selectedInjector === key) {
      setSelectedInjector(null);
      setSelectedInjectorData(DEFAULT_INJECTOR);
    }
    handleRemove(key);
  }, [selectedInjector, handleRemove]);

  const handleDeleteClick = (key: string) => {
    setInjectorToDelete(key);
  };

  const handleDeleteConfirm = () => {
    if (injectorToDelete) {
      handleInjectorDelete(injectorToDelete);
      setInjectorToDelete(null);
    }
  };

  const handleDeleteCancel = () => {
    setInjectorToDelete(null);
  };

  const handleJsonChange = (newData: Record<string, Injector>) => {
    if (typeof newData !== 'object') return;
    
    // Update both local and parent state
    updateState(newData);
    updateField('injectors', newData);
  };

  const columns = [
    { 
      id: 'name', 
      label: 'Name', 
      render: (item: [string, Injector]) => item[0]  // Use key as name
    },
    {
      id: 'enabled',
      label: 'Status',
      render: (item: [string, Injector]) => (item[1].enabled ? 'Enabled' : 'Disabled')
    },
    {
      id: 'condition',
      label: 'Condition',
      render: (item: [string, Injector]) => item[1].condition || 'No condition'
    }
  ];

  // Convert availableTables to string[] for table names
  const tableNames = useMemo(() => 
    availableTables.map(table => table.table_name),
    [availableTables]
  );

  const tabs: TabItem<TabValue>[] = [
    {
      value: 'details',
      label: 'Injector Info',
      content: (
        <RulesetFormInjectorDetails
          injector={selectedInjectorData}
          injectorKey={selectedInjector || ''}
          onChange={updateSelectedInjectorField}
          onKeyChange={(newKey: string) => {
            if (selectedInjector) {
              handleRename(selectedInjector, newKey, selectedInjectorData);
              setSelectedInjector(newKey);
            }
          }}
        />
      )
    },
    {
      value: 'tables',
      label: 'Tables',
      content: (
        <RulesetFormInjectorTables
          tables={selectedInjectorData.tables}
          onChange={(tables) => updateSelectedInjectorField('tables', tables)}
          connectedSchemaName={ruleset.connected_schema_name}
          availableTables={tableNames} 
        />
      )
    }
  ];

  const modalFooter = (
    <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
      <Button variant="outlined" onClick={() => setSelectedInjector(null)}>
        Close
      </Button>
    </Box>
  );

  return (
    <>
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 2,
        mb: 3  // Add margin bottom for spacing
      }}>
        <Tabs
          value={viewMode}
          onChange={(_, newValue) => setViewMode(newValue)}
          sx={{ ml: 2 }}
        >
          <Tab value="form" label="Form View" />
          <Tab value="json" label="JSON View" />
        </Tabs>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'flex-end', 
              alignItems: 'center', 
              mb: 2 
            }}>
              {viewMode === 'form' && (
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <TextField
                    size="small"
                    placeholder="Search injectors..."
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
                  <Button startIcon={<AddIcon />} onClick={handleAddInjector} variant="contained">
                    Add Injector
                  </Button>
                </Box>
              )}
            </Box>

            {viewMode === 'form' ? (
              <DataTable
                items={paginatedData}
                columns={columns}
                total={filteredInjectors.length}
                page={page}
                pageSize={pageSize}
                onPageChange={setPage}
                onPageSizeChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setPageSize(Number(e.target.value))
                }
                rowActions={(item: [string, Injector]) => (
                  <Box 
                    sx={{ 
                      display: 'flex', 
                      gap: 1,
                      minWidth: 'fit-content',
                      '& .MuiButton-root': {
                        minWidth: '60px'  
                      }
                    }}
                  >
                    <Button 
                      variant="outlined" 
                      size="small" 
                      onClick={() => handleEdit(item[0])}
                    >
                      Edit
                    </Button>
                    <Button 
                      variant="outlined" 
                      color="error"
                      size="small" 
                      onClick={() => handleDeleteClick(item[0])}
                    >
                      Delete
                    </Button>
                  </Box>
                )}
              />
            ) : (
              <JsonFormView
                data={localInjectors}  
                onChange={handleJsonChange}
              />
            )}
          </Paper>
        </Grid>
        <Dialog
          open={!!injectorToDelete}
          onClose={handleDeleteCancel}
        >
          <DialogTitle>Confirm Delete</DialogTitle>
          <DialogContent>
            Are you sure you want to delete this injector? This action cannot be undone.
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDeleteCancel}>Cancel</Button>
            <Button onClick={handleDeleteConfirm} color="error" variant="contained">
              Delete
            </Button>
          </DialogActions>
        </Dialog>
        <MultiTabModal
          open={!!selectedInjector}
          onClose={() => setSelectedInjector(null)}
          value={activeTab}
          onTabChange={setActiveTab}
          tabs={tabs}
          footer={modalFooter}
        />
      </Grid>
    </>
  );
};

export default RulesetInjectors;
