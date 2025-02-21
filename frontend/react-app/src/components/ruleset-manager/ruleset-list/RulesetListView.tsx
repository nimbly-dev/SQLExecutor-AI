import React from 'react';
import { DataTable } from 'components/common/tables/DataTable';
import { Column } from 'types/common/tableTypes';
import { RulesetSummary } from 'types/ruleset/rulesetType';
import { Button, Chip } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';

interface RulesetListViewProps {
  rulesets: RulesetSummary[];
  total: number;
  page: number;
  pageSize: number;
  loading: boolean;
  onPageChange: (page: number) => void;
  onPageSizeChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onDelete: (rulesetName: string) => void;
  onView: (ruleset: RulesetSummary) => void;
}

const ROW_COUNT_OPTIONS = [5, 10, 25, 50, 100];

export const RulesetListView: React.FC<RulesetListViewProps> = ({
  rulesets,
  total,
  page,
  pageSize,
  loading,
  onPageChange,
  onPageSizeChange,
  onDelete,
  onView,
}) => {
  const columns: Column<RulesetSummary>[] = [
    { id: 'ruleset_name', label: 'Ruleset Name' },
    { id: 'description', label: 'Description' },
    { id: 'connected_schema_name', label: 'Connected Schema' },
    { 
      id: 'is_ruleset_enabled',
      label: 'Status',
      render: (ruleset) => (
        <Chip 
          label={ruleset.is_ruleset_enabled ? 'Enabled' : 'Disabled'}
          color={ruleset.is_ruleset_enabled ? 'success' : 'default'}
          size="small"
        />
      )
    },
    {
      id: 'has_injectors',
      label: 'Has Injectors',
      render: (ruleset) => (
        <Chip 
          label={ruleset.has_injectors ? 'Yes' : 'No'}
          color={ruleset.has_injectors ? 'info' : 'default'}
          size="small"
        />
      )
    },
  ];

  const getRowCountOptions = () => {
    if (total <= 10) return [5, 10];
    if (total <= 25) return [5, 10, 25];
    if (total <= 50) return [5, 10, 25, 50];
    return ROW_COUNT_OPTIONS;
  };

  const renderActions = (ruleset: RulesetSummary) => (
    <div style={{ display: 'flex', gap: '8px' }}>
      <Button
        startIcon={<VisibilityIcon />}
        variant="outlined"
        size="small"
        onClick={() => onView(ruleset)}
      >
        View
      </Button>
      <Button
        startIcon={<DeleteIcon />}
        variant="outlined"
        color="error"
        size="small"
        onClick={() => onDelete(ruleset.ruleset_name)}
      >
        Delete
      </Button>
    </div>
  );

  return (
    <DataTable
      items={rulesets}
      columns={columns}
      total={total}
      page={page}
      pageSize={pageSize}
      loading={loading}
      onPageChange={onPageChange}
      onPageSizeChange={onPageSizeChange}
      rowActions={renderActions}
      rowsPerPageOptions={getRowCountOptions()}
    />
  );
};
