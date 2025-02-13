import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Box, Button, IconButton, TextField } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete'; // Fix import path
import { DataTable } from 'components/common/tables/DataTable';
import MultiTabModal, { TabItem } from 'components/common/modal/MultiTabModal';
import SchemaFormTablesGeneralInfo from 'components/schema-manager/schema-view/schema-info/tables/tables-forms/form-section-components/SchemaFormTablesGeneralInfo';
import SchemaFormTablesColumnsDefinition from 'components/schema-manager/schema-view/schema-info/tables/tables-forms/form-section-components/SchemaFormTablesColumnsDefinition';
import SchemaFormTablesRelationships from 'components/schema-manager/schema-view/schema-info/tables/tables-forms/form-section-components/SchemaFormTablesRelationships';
import styles from 'styles/schema-manager/tables/SchemaFormTablesView.module.scss';
import { Table } from 'types/schema/schemaType';
import { collectionOperations } from 'utils/forms/collectionUtils';
import { useValidationFeedback } from 'hooks/common/feedback/useValidationFeedback';
import { Column } from 'types/common/tableTypes';

// Add this type at the top
type TableWithKey = Table & { key: string };

interface SchemaFormTablesViewProps {
  tables: Record<string, Table>;
  updateField: (path: string, value: any) => void;
}

const SchemaFormTables: React.FC<SchemaFormTablesViewProps> = ({
  tables,
  updateField,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedTableIndex, setSelectedTableIndex] = useState<number | null>(
    null
  );
  const [modalTab, setModalTab] = useState<string>('general');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  const { feedback, showFeedback, clearFeedback } = useValidationFeedback();

  // Keep tables state in sync with parent
  const [localTables, setLocalTables] = useState<Record<string, Table>>(tables);

  // Synchronize local state with props when tables change
  useEffect(() => {
    setLocalTables(tables);
  }, [tables]);

  // Convert Record to array for display, keeping name as a separate property
  const tablesArray = useMemo<TableWithKey[]>(() => (
    Object.entries(tables).map(([key, tableData]) => ({
      key,
      ...tableData
    }))
  ), [tables]);

  const handleStateUpdate = useCallback((updatedTables: Record<string, Table>) => {
    // Ensure we preserve existing column data
    const updatedWithColumns = Object.entries(updatedTables).reduce((acc, [key, table]) => ({
      ...acc,
      [key]: {
        ...table,
        columns: table.columns || {},  // Ensure columns is always an object
      }
    }), {});

    setLocalTables(updatedWithColumns);
    updateField('tables', updatedWithColumns);
  }, [updateField]);

  const { handleAdd, handleUpdate, handleRemove, handleRename } = collectionOperations(
    tables, // Use tables prop directly
    handleStateUpdate,
    updateField,
    '',
    'tables',
    {
      onError: (message) => showFeedback(message, 'error'),
      onSuccess: (message) => showFeedback(message, 'success'),
      errorMessages: {
        addFailed: 'Failed to add table',
        removeFailed: 'Failed to remove table',
        renameFailed: 'Failed to rename table',
        itemNotFound: 'Table not found',
      },
      successMessages: {
        addSuccess: 'Table added successfully',
        removeSuccess: 'Table removed successfully',
        renameSuccess: 'Table renamed successfully',
      }
    }
  );

  const handleViewTable = useCallback((index: number) => {
    setSelectedTableIndex(index);
    setModalTab('general');
    setModalOpen(true);
  }, []);

  const getTableByIndex = useCallback(
    (index: number): Table | undefined => {
      return tablesArray[index];
    },
    [tablesArray]
  );

  const handleAddTable = useCallback(() => {
    const tableName = `table_${Date.now()}`;
    const newTable: Table = {
      description: '',
      synonyms: [],
      columns: {}, 
      relationships: {},
      exclude_description_on_generate_sql: false,
    };

    handleAdd(tableName, newTable);
  }, [handleAdd]);

  const handleRemoveTable = useCallback((tableName: string) => {
    handleRemove(tableName);
  }, [handleRemove]);

  const handleTableRename = useCallback((oldKey: string, newKey: string, tableData: Table) => {
    handleRename(oldKey, newKey, tableData);
  }, [handleRename]);

  // Update getTableContent to remove array handling
  const getTableContent = useCallback(
    (tableIndex: number): TabItem<string>[] => {
      const tableEntry = tablesArray[tableIndex];
      if (!tableEntry) return [];

      const tablePath = `tables.${tableEntry.key}`;
      const { key, ...tableData } = tableEntry;

      return [
        {
          value: 'general',
          label: 'General Info',
          content: (
            <SchemaFormTablesGeneralInfo
              table={tableData}
              tableName={key}
              pathPrefix={tablePath}
              updateField={updateField}
              onNameChange={handleTableRename}
            />
          ),
        },
        {
          value: 'columns',
          label: 'Columns',
          content: (
            <SchemaFormTablesColumnsDefinition
              table={tableData}
              pathPrefix={tablePath}
              updateField={updateField}
            />
          ),
        },
        {
          value: 'relationships',
          label: 'Relationships',
          content: (
            <SchemaFormTablesRelationships
              table={tableData}
              allTables={tablesArray.map(({ key, ...rest }) => ({ key, ...rest }))}
              pathPrefix={tablePath}
              updateField={updateField}
            />
          ),
        },
      ];
    },
    [tablesArray, updateField, handleTableRename]
  );

  const modalTabs: TabItem<string>[] =
    selectedTableIndex !== null ? getTableContent(selectedTableIndex) : [];

  // Update columns definition to use key instead of name
  const columns: Column<TableWithKey>[] = [
    {
      id: 'name',
      label: 'Table Name',
      width: '40%',
      render: (item: TableWithKey) => (
        <Box component="span" sx={{ fontWeight: 500 }}>
          {item.key}
        </Box>
      ),
    },
    {
      id: 'description',
      label: 'Description',
      width: '40%',
      render: (item: TableWithKey) => item.description || 'No description',
    },
    {
      id: 'columns',
      label: 'Columns',
      width: '20%',
      align: 'center' as const,
      render: (item: TableWithKey) => {
        const count = item.columns ? Object.keys(item.columns).length : 0;
        return <Box component="span">{count}</Box>;
      },
    },
  ];

  const filteredTables = useMemo(() => {
    const search = searchTerm.toLowerCase();
    if (!search) return tablesArray;

    return tablesArray.filter(
      (table) =>
        table?.key?.toLowerCase().includes(search) ||
        table?.description?.toLowerCase().includes(search) ||
        table?.synonyms?.some((syn: string) => syn.toLowerCase().includes(search))
    );
  }, [tablesArray, searchTerm]);

  const startIndex = page * pageSize;
  const paginatedTables = useMemo(() => {
    const slicedTables = filteredTables.slice(
      startIndex,
      startIndex + pageSize
    );
    return slicedTables;
  }, [filteredTables, startIndex, pageSize]);

  const getRowCountOptions = () => {
    const total = Array.isArray(filteredTables) ? filteredTables.length : 0;
    if (total <= 5) return [5];
    if (total <= 10) return [5, 10];
    if (total <= 25) return [5, 10, 25];
    return [5, 10, 25, 50];
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        gap: 2,
      }}
    >
      <TextField
        placeholder="Search tables..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        size="small"
        fullWidth
        sx={{ mb: 2 }}
      />
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          // Restore old table styles
          '& .MuiTableContainer-root': {
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1,
            boxShadow: 1,
          },
          '& .MuiTableHead-root': {
            bgcolor: 'background.default',
            '& .MuiTableCell-head': {
              fontWeight: 'bold',
            },
          },
          '& .MuiTableBody-root .MuiTableRow-root:hover': {
            bgcolor: 'action.hover',
          },
          '& .MuiTablePagination-root': {
            bgcolor: 'background.paper',
            borderTop: '1px solid',
            borderColor: 'divider',
          },
        }}
      >
        <DataTable<TableWithKey>
          items={paginatedTables}
          columns={columns}
          total={filteredTables.length}
          page={page}
          pageSize={pageSize}
          onPageChange={setPage}
          onPageSizeChange={(e) => {
            const newSize = parseInt(e.target.value, 10);
            setPageSize(newSize);
            setPage(0);
          }}
          rowActions={(item: TableWithKey) => {
            const index = tablesArray.findIndex((t) => t.key === item.key);
            return (
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                <IconButton
                  size="small"
                  onClick={() => handleViewTable(index)}
                  aria-label="Edit table"
                >
                  <EditIcon />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => handleRemoveTable(item.key)}
                  color="error"
                  aria-label="Delete table"
                >
                  <DeleteIcon />
                </IconButton>
              </Box>
            );
          }}
          noDataMessage={
            searchTerm ? 'No matching tables found' : 'No tables defined yet'
          }
          rowsPerPageOptions={getRowCountOptions()}
          key={`tables-${tablesArray.length}`}
        />
      </Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
        <Button variant="contained" onClick={handleAddTable}>
          Add Table
        </Button>
      </Box>
      {selectedTableIndex !== null && (
        <MultiTabModal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          value={modalTab}
          onTabChange={setModalTab}
          tabs={modalTabs}
          footer={
            <Button variant="contained" onClick={() => setModalOpen(false)}>
              Close
            </Button>
          }
        />
      )}
    </Box>
  );
};

export default SchemaFormTables;
