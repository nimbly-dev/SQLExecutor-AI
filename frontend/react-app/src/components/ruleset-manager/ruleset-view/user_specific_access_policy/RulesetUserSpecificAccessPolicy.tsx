import React, { useState, useMemo, useCallback } from 'react';
import {
  Button, Stack, Box, TextField
} from '@mui/material';
import { DataTable } from 'components/common/tables/DataTable';
import JsonFormView from 'components/common/forms/JsonFormView';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import { UserSpecificAccessPolicy, Ruleset } from 'types/ruleset/rulesetType';
import { SimpleColumnResponse, SimpleTablesResponse } from 'types/schema/schemaType';
import { useFormUpdate } from 'contexts/form/FormUpdateProvider';
import MultiTabModal from 'components/common/modal/MultiTabModal';
import type { TabItem } from 'components/common/modal/MultiTabModal';
import UserPolicyInfo from './user-forms/UserPolicyFormInfo';
import UserPolicyFormTables from './user-forms/UserPolicyFormTables';

interface Props {
  ruleset: Ruleset;
  tables: SimpleTablesResponse;
}

interface Column {
  id: string;
  label: string;
  render: (item: UserSpecificAccessPolicy) => React.ReactNode;
}

interface UserTableRule {
  columns: {
    allow: string | string[];
    deny: string[];
  };
  condition: string;
}

interface LocalPoliciesState {
  items: UserSpecificAccessPolicy[];
}

export const RulesetUserSpecificAccessPolicy: React.FC<Props> = ({
  ruleset,
  tables,
}) => {
  const { updateField } = useFormUpdate();  
  
  // View state
  const [viewMode, setViewMode] = useState<'form' | 'json'>('form');
  const [filterTerm, setFilterTerm] = useState('');
  
  // Modal states – selectedUser now holds the array index as string
  const [selectedUser, setSelectedUser] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'info' | 'tables'>('info');

  // Initialize state with wrapper object
  const initialState: LocalPoliciesState = {
    items: Array.isArray(ruleset.user_specific_access_policy)
      ? ruleset.user_specific_access_policy
      : []
  };

  const [localState, , , , updateState] = useLocalFormState<LocalPoliciesState>(initialState);
  const localPolicies = localState.items;

  // Define our own add/update/remove
  const handleAddPolicy = useCallback((): void => {
    const newPolicy: UserSpecificAccessPolicy = {
      user_identifier: '',
      tables: {}
    };
    const updatedPolicies = [...localPolicies, newPolicy];
    updateState({ items: updatedPolicies });
    updateField('user_specific_access_policy', updatedPolicies);
  }, [localPolicies, updateState, updateField]);

  const handleUpdatePolicy = useCallback((index: number, updatedPolicy: UserSpecificAccessPolicy): void => {
    const newPolicies = [...localPolicies];
    newPolicies[index] = updatedPolicy;
    updateState({ items: newPolicies });
    updateField('user_specific_access_policy', newPolicies);
  }, [localPolicies, updateState, updateField]);

  const handleRemovePolicy = useCallback((index: number): void => {
    const newPolicies = localPolicies.filter((_policy: UserSpecificAccessPolicy, i: number) => i !== index);
    updateState({ items: newPolicies });
    updateField('user_specific_access_policy', newPolicies);
  }, [localPolicies, updateState, updateField]);

  // Transform tables data for component use
  const availableTables = useMemo(() => 
    tables.map(table => table.table_name),
    [tables]
  );

  const availableColumns = useMemo(() => 
    tables.reduce((acc, table) => ({
      ...acc,
      [table.table_name]: table.columns
    }), {} as Record<string, SimpleColumnResponse[]>),
    [tables]
  );

  // Simplify columns to only show user identifier
  const columns: Column[] = [
    {
      id: 'user_identifier',
      label: 'User Identifier',
      render: (policy: UserSpecificAccessPolicy) => policy.user_identifier || 'Unnamed User'
    }
  ];

  // Filter policies based on user identifier
  const filteredPolicies = useMemo(() => {
    if (!filterTerm) return localPolicies;
    
    return localPolicies.filter((policy: UserSpecificAccessPolicy) => {
      const userIdentifier = policy.user_identifier || '';
      return userIdentifier.toLowerCase().includes(filterTerm.toLowerCase());
    });
  }, [localPolicies, filterTerm]);

  // Define row actions; derive index from array
  const renderActions = useCallback((item: UserSpecificAccessPolicy): React.ReactNode => {
    const index = localPolicies.findIndex((p: UserSpecificAccessPolicy) => 
      p.user_identifier === item.user_identifier
    );
    return (
      <Box sx={{ display: 'flex', gap: 1 }}>
        <Button
          variant="outlined"
          size="small"
          onClick={() => {
            setSelectedUser(String(index));
            setIsModalOpen(true);
          }}
        >
          View
        </Button>
        <Button
          variant="outlined"
          color="error"
          size="small"
          onClick={() => handleRemovePolicy(index)}
        >
          Delete
        </Button>
      </Box>
    );
  }, [handleRemovePolicy, localPolicies]);

  // Pagination state
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  // Tabs for modal content
  const tabs: TabItem<'info' | 'tables'>[] = useMemo((): TabItem<'info' | 'tables'>[] => {
    if (selectedUser === null) return [];
    
    const index = Number(selectedUser);
    const policy = localPolicies[index];
    if (!policy) return [];
    const transformedPolicy = {
      ...policy,
      tables: Object.entries(policy.tables).reduce<Record<string, UserTableRule>>(
        (acc, [key, value]) => {
          const rule = value as Partial<UserTableRule>;
          return {
            ...acc,
            [key]: {
              columns: rule.columns || { allow: [], deny: [] },
              condition: rule.condition ? rule.condition : '',
            },
          };
        },
        {}
      ),
    };
    
    return [
      {
        value: 'info',
        label: 'User Info',
        content: (
          <UserPolicyInfo
            selectedUser={selectedUser}
            policy={transformedPolicy}
            onUpdate={(userId: string, updatedPolicy: UserSpecificAccessPolicy) =>
              handleUpdatePolicy(Number(userId), updatedPolicy)
            }
          />
        ),
      },
      {
        value: 'tables',
        label: 'Tables',
        content: (
          <UserPolicyFormTables
            selectedUser={selectedUser}
            policy={transformedPolicy}
            availableTables={availableTables}
            availableColumns={availableColumns}
            onUpdate={(userId: string, updatedPolicy: UserSpecificAccessPolicy) =>
              handleUpdatePolicy(Number(userId), updatedPolicy)
            }
          />
        ),
      },
    ];
  }, [selectedUser, localPolicies, availableTables, availableColumns, handleUpdatePolicy]);

  return (
    <Stack spacing={2}>
      <Box sx={{ display: 'flex', gap: 1 }}>
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
  
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Box sx={{ flex: 1, display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            size="small"
            placeholder="Filter by User Identifier..."
            value={filterTerm}
            onChange={(e) => setFilterTerm(e.target.value)}
            sx={{ flex: 1 }}
          />
          <Button 
            variant="contained" 
            onClick={handleAddPolicy}
            size="small"
            sx={{ 
              height: '40px',  // Match TextField height
              minWidth: '120px' // Give button a consistent width
            }}
          >
            Add User
          </Button>
        </Box>
      </Box>

      {viewMode === 'json' ? (
        <JsonFormView<UserSpecificAccessPolicy[]>
          data={localPolicies}
          onChange={(newValue: UserSpecificAccessPolicy[]) => {
            updateState({ items: newValue });
            updateField('user_specific_access_policy', newValue);
          }}
        />
      ) : (
        <DataTable<UserSpecificAccessPolicy>
          items={filteredPolicies}
          columns={columns}
          total={filteredPolicies.length}
          page={page}
          pageSize={pageSize}
          onPageChange={setPage}
          onPageSizeChange={(event) => setPageSize(parseInt(event.target.value, 10))}
          rowActions={renderActions}
        />
      )}

      <MultiTabModal
        open={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedUser(null);
        }}
        value={activeTab}
        onTabChange={setActiveTab}
        tabs={tabs}
        footer={
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button onClick={() => {
              setIsModalOpen(false);
              setSelectedUser(null);
            }}>
              Close
            </Button>
          </Box>
        }
      />
    </Stack>
  );
};

export default RulesetUserSpecificAccessPolicy;