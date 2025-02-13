import React from 'react';
import { DataTable } from 'components/common/tables/DataTable';
import { Column } from 'types/common/tableTypes';
import { SchemaSummary } from 'types/schema/schemaType';
import { Button } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';

interface SchemaListViewProps {
  schemas: SchemaSummary[];
  total: number;
  page: number;
  pageSize: number;
  loading: boolean;
  onPageChange: (page: number) => void;
  onPageSizeChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onDelete: (schemaName: string) => void;
  onView: (schema: SchemaSummary) => void;
}

const ROW_COUNT_OPTIONS = [5, 10, 25, 50, 100];

export const SchemaListView: React.FC<SchemaListViewProps> = ({
  schemas,
  total,
  page,
  pageSize,
  loading,
  onPageChange,
  onPageSizeChange,
  onDelete,
  onView,
}) => {
  const columns: Column<SchemaSummary>[] = [
    { id: 'schema_name', label: 'Schema Name' },
    { id: 'description', label: 'Description' },
    { id: 'context_type', label: 'Context Type' },
    { id: 'user_identifier', label: 'User Identifier' },
  ];

  const getRowCountOptions = () => {
    if (total <= 10) return [5, 10];
    if (total <= 25) return [5, 10, 25];
    if (total <= 50) return [5, 10, 25, 50];
    return ROW_COUNT_OPTIONS;
  };

  const renderActions = (schema: SchemaSummary) => (
    <div style={{ display: 'flex', gap: '8px' }}>
      <Button
        startIcon={<VisibilityIcon />}
        variant="outlined"
        size="small"
        onClick={() => onView(schema)}
      >
        View
      </Button>
      <Button
        startIcon={<DeleteIcon />}
        variant="outlined"
        color="error"
        size="small"
        onClick={() => onDelete(schema.schema_name)}
      >
        Delete
      </Button>
    </div>
  );

  return (
    <DataTable
      items={schemas}
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
