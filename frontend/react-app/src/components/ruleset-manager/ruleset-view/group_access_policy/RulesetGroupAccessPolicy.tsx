import React, { useState, useMemo, useCallback } from 'react';
import {
  Box, Button, Grid, Paper, TextField, InputAdornment,
  Dialog, DialogContent, DialogTitle, DialogActions, 
  Tabs, Tab, Autocomplete
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import { GroupAccessPolicy, Ruleset } from 'types/ruleset/rulesetType';
import { useFormUpdate } from 'contexts/form/FormUpdateProvider';
import { DataTable } from 'components/common/tables/DataTable';
import { JsonFormView } from 'components/common/forms/JsonFormView';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import { collectionOperations } from 'utils/forms/collectionUtils';
import MultiTabModal from 'components/common/modal/MultiTabModal';
import RulesetFormGroupInfo from './group-forms/RulesetFormGroupInfo';
import RulesetFormMatchingCriteria from './group-forms/RulesetFormMatchingCriteria';
import GroupTablesTab from './group-forms/RulesetFormGroupTables';
import { SimpleTablesResponse } from 'types/schema/schemaType';

interface RulesetGroupAccessPolicyProps {
  ruleset: Ruleset;
  availableTables: SimpleTablesResponse;  // Update type here
}

const DEFAULT_GROUP_POLICY: GroupAccessPolicy = {
  description: '',
  criteria: {
    matching_criteria: {},
    condition: ''
  },
  tables: {}
};

type TabValue = 'info' | 'criteria' | 'tables';

export const RulesetGroupAccessPolicy: React.FC<RulesetGroupAccessPolicyProps> = ({
  ruleset,
  availableTables,
}) => {
  const { updateField } = useFormUpdate();
  const [viewMode, setViewMode] = useState<'form' | 'json'>('form');
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(5);
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabValue>('info');

  const [localGroups, , , , updateState] = useLocalFormState<Record<string, GroupAccessPolicy>>(
    ruleset.group_access_policy || {}
  );

  const { handleAdd, handleUpdate, handleRemove, handleRename } = collectionOperations(
    localGroups,
    updateState,
    (path: string, value: any) => {
      updateField('group_access_policy', value);
    },
    '',
    'groups'
  );

  // Filter and paginate groups
  const filteredAndPaginatedGroups = useMemo(() => {
    const groupEntries = Object.entries(localGroups);
    const filtered = groupEntries.filter(([key]) => 
      key.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const start = page * pageSize;
    const end = start + pageSize;

    return {
      items: filtered.slice(start, end),
      total: filtered.length
    };
  }, [localGroups, searchTerm, page, pageSize]);

  const handleJsonChange = (newData: Record<string, GroupAccessPolicy>) => {
    updateState(newData);
    updateField('group_access_policy', newData);
  };

  const handleAddGroup = () => {
    const newKey = `group_${Object.keys(localGroups).length + 1}`;
    handleAdd(newKey, DEFAULT_GROUP_POLICY);
    setSelectedGroup(newKey);
    setActiveTab('info');
  };

  const handleGroupRename = useCallback((oldKey: string, newKey: string, value: GroupAccessPolicy) => {
    const updatedGroups = { ...localGroups };
    delete updatedGroups[oldKey];
    updatedGroups[newKey] = value;
    
    // Batch our updates
    updateState(updatedGroups);
    updateField('group_access_policy', updatedGroups);
    setSelectedGroup(newKey);
  }, [localGroups, updateState, updateField]);

  const columns = [
    { 
      id: 'name', 
      label: 'Name', 
      render: (item: [string, GroupAccessPolicy]) => item[0]
    },
    {
      id: 'description',
      label: 'Description',
      render: (item: [string, GroupAccessPolicy]) => item[1].description || 'No description'
    }
  ];

  const tabs = selectedGroup && localGroups[selectedGroup] ? [
    {
      value: 'info' as TabValue,
      label: 'Group Info',
      content: (
        <RulesetFormGroupInfo
          group={localGroups[selectedGroup]}
          groupKey={selectedGroup}
          onUpdate={handleUpdate}
          onRename={handleGroupRename}  // Use new handler
        />
      )
    },
    {
      value: 'criteria' as TabValue,
      label: 'Matching Criteria',
      content: (
        <RulesetFormMatchingCriteria
          group={localGroups[selectedGroup]}
          onUpdate={handleUpdate}
          groupKey={selectedGroup}
        />
      )
    },
    {
      value: 'tables' as TabValue,
      label: 'Tables',
      content: (
        <GroupTablesTab
          group={localGroups[selectedGroup]}
          onUpdate={handleUpdate}
          groupKey={selectedGroup}
          availableTables={availableTables}
        />
      )
    }
  ] : [];

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
                    placeholder="Search groups..."
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
                    onClick={handleAddGroup}
                    variant="contained"
                  >
                    Add Group
                  </Button>
                </Box>
              </Box>

              <DataTable
                items={filteredAndPaginatedGroups.items}
                columns={columns}
                total={filteredAndPaginatedGroups.total}
                page={page}
                pageSize={pageSize}
                onPageChange={setPage}
                onPageSizeChange={(e) => setPageSize(Number(e.target.value))}
                rowActions={(item: [string, GroupAccessPolicy]) => (
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => {
                        setSelectedGroup(item[0]);
                        setActiveTab('info');
                      }}
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
          data={localGroups}
          onChange={handleJsonChange}
        />
      )}

      <MultiTabModal
        open={!!selectedGroup}
        onClose={() => setSelectedGroup(null)}
        value={activeTab}
        onTabChange={setActiveTab}
        tabs={tabs}
        footer={
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button onClick={() => setSelectedGroup(null)}>
              Close
            </Button>
          </Box>
        }
      />
    </>
  );
};

export default RulesetGroupAccessPolicy;
