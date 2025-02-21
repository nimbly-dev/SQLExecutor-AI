import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { 
  Box, 
  TextField,
  Typography,
  TablePagination,
  Paper,
  IconButton
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { InjectorTableRule } from 'types/ruleset/rulesetType';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import { collectionOperations } from 'utils/forms/collectionUtils';
import AsyncPaginatedDropdownFormField from 'components/common/forms/field-forms/AsyncPaginatedDropdownFormField';

interface RulesetFormInjectorTablesProps {
  tables: Record<string, InjectorTableRule>;
  onChange: (tables: Record<string, InjectorTableRule>) => void;
  connectedSchemaName: string;
  availableTables: string[];  // Add availableTables prop
}

const DEFAULT_TABLE_RULE: InjectorTableRule = {
  filters: ''
};

const RulesetFormInjectorTables: React.FC<RulesetFormInjectorTablesProps> = ({
  tables,
  onChange,
  connectedSchemaName,
  availableTables
}) => {
  const [localTables, , , , updateState] = useLocalFormState(tables);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  const { handleAdd, handleUpdate, handleRemove } = collectionOperations(
    localTables,
    updateState,
    (_path: string, value: any) => onChange(value),
    '',
    'tables'
  );

  // Replace searchTables callback with simpler version using availableTables
  const searchTables = useCallback(async (searchTerm: string) => {
    const existingTableNames = Object.keys(localTables);
    
    const options = availableTables
      .filter(tableName => !existingTableNames.includes(tableName))
      .filter(tableName => 
        tableName.toLowerCase().includes(searchTerm.toLowerCase())
      )
      .map(tableName => ({
        value: tableName,
        label: tableName
      }));

    return { options, total: options.length };
  }, [availableTables, localTables]);

  // Filter and paginate table cards
  const filteredAndPaginatedTables = useMemo(() => {
    const filteredTables = Object.entries(localTables).filter(([tableName]) =>
      tableName.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return {
      items: filteredTables.slice(page * rowsPerPage, (page + 1) * rowsPerPage),
      total: filteredTables.length
    };
  }, [localTables, searchTerm, page, rowsPerPage]);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header with Search and Add Table */}
      <Box sx={{ 
        display: 'flex', 
        gap: 2, 
        mb: 3,
        '& .MuiFormControl-root': {
          minHeight: '40px'  // Use minHeight instead of height
        }
      }}>
        <TextField
          size="small"
          placeholder="Filter tables..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setPage(0);
          }}
          sx={{ 
            flex: 7,
            '& .MuiInputBase-root': {
              height: '40px'
            }
          }}
        />
        <Box sx={{ 
          flex: 3,
          '& .MuiFormControl-root': {
            '& .MuiInputBase-root': {
              height: '40px'
            }
          }
        }}> 
          <AsyncPaginatedDropdownFormField
            label="Add Table"  
            value="Add Table"  
            onChange={(value) => value && handleAdd(value, DEFAULT_TABLE_RULE)}
            onSearch={searchTables}
            placeholder="Search to add table..."
          />
        </Box>
      </Box>

      {/*  Table Cards */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {filteredAndPaginatedTables.items.map(([tableName, tableRule]) => (
          <Paper key={tableName} sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="h6">{tableName}</Typography>
              <IconButton 
                onClick={() => handleRemove(tableName)}
                size="small"
              >
                <DeleteIcon />
              </IconButton>
            </Box>
            <TextField
              fullWidth
              size="small"
              multiline
              rows={2}
              label="Filters"
              value={tableRule.filters}  
              onChange={(e) => handleUpdate(tableName, { 
                ...tableRule, 
                filters: e.target.value 
              })}
              sx={{
                '& .MuiOutlinedInput-root': {
                  fontSize: '0.875rem'
                }
              }}
            />
          </Paper>
        ))}
      </Box>

      {/* Pagination */}
      {filteredAndPaginatedTables.total > 0 && (
        <TablePagination
          component="div"
          count={filteredAndPaginatedTables.total}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
          rowsPerPageOptions={[5, 10]}
        />
      )}

      {/* Empty State */}
      {filteredAndPaginatedTables.total === 0 && (
        <Box sx={{ textAlign: 'center', py: 3 }}>
          <Typography color="text.secondary">
            {Object.keys(localTables).length === 0 
              ? 'No tables added yet' 
              : 'No tables match your search'}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default RulesetFormInjectorTables;
