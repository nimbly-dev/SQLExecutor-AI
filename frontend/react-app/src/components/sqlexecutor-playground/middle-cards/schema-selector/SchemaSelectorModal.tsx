import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Modal,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Radio,
  Paper,
  Tooltip,
  useTheme,
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import SortIcon from '@mui/icons-material/Sort';
import { SchemaSummary } from '../../../../types/sqlexecutor-playground/schemaModalContent';
import '../../../../styles/sqlexecutor-playground/middle-cards/SchemaSelectorModal.scss';
import useSortableData from '../../../../hooks/common/useSortableData';

interface SchemaSelectModalProps {
  open: boolean;
  onClose: () => void;
  schemas: SchemaSummary[];
  onSelectSchema: (schema: SchemaSummary) => void;
  selectedSchema: SchemaSummary | null;
}

const SchemaSelectorModal: React.FC<SchemaSelectModalProps> = ({
  open,
  onClose,
  schemas,
  onSelectSchema,
  selectedSchema,
}) => {
  const theme = useTheme();
  const [selected, setSelected] = useState<SchemaSummary | null>(selectedSchema);
  const [hoveredRow, setHoveredRow] = useState<string | null>(null);

  // Initialize sorting with useSortableData hook
  const { items: sortedSchemas, requestSort, sortConfig } = useSortableData(schemas);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!open) return;
      const currentIndex = sortedSchemas.findIndex(
        (schema) => schema.schema_name === selected?.schema_name
      );
      switch (event.key) {
        case 'ArrowUp':
          event.preventDefault();
          if (currentIndex > 0) {
            setSelected(sortedSchemas[currentIndex - 1]);
          }
          break;
        case 'ArrowDown':
          event.preventDefault();
          if (currentIndex < sortedSchemas.length - 1) {
            setSelected(sortedSchemas[currentIndex + 1]);
          }
          break;
        case 'Enter':
          event.preventDefault();
          if (selected) handleSelect();
          break;
        case 'Escape':
          event.preventDefault();
          onClose();
          break;
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [open, selected, sortedSchemas]);

  const handleSelect = () => {
    if (selected) {
      onSelectSchema(selected);
    }
    onClose();
  };

  const handleSort = (field: keyof SchemaSummary) => {
    requestSort(field);
  };

  return (
    <Modal open={open} onClose={onClose} aria-labelledby="schema-selector-modal">
      <Box
        sx={{
          position: 'absolute',  
          top: '50%',            
          left: '50%',           
          transform: 'translate(-50%, -50%)', 
          width: { xs: '90%', md: '1000px' },
          maxHeight: '80vh',
          overflowY: 'auto',
          backgroundColor: theme.palette.background.paper,
          borderRadius: theme.shape.borderRadius,
          boxShadow: theme.shadows[5],
          padding: theme.spacing(2),
        }}
      >
        <Typography
          variant="h6"
          id="schema-selector-modal"
          sx={{ mb: 3, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}
        >
          Select Schema
          <Tooltip title="Choose a schema to generate SQL queries for specific database tables">
            <InfoIcon sx={{ fontSize: 20, color: 'action.active', ml: 1 }} />
          </Tooltip>
        </Typography>

        <TableContainer component={Paper} sx={{ maxHeight: 400, mb: 3, overflowY: 'auto' }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell align="left" className="table-cell-header" sx={{ width: '25%' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }} onClick={() => handleSort('schema_name')}>
                    Schema
                    <SortIcon fontSize="small" sx={{ ml: 0.5 }} />
                  </Box>
                </TableCell>
                <TableCell align="left" className="table-cell-header" sx={{ width: '35%' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }} onClick={() => handleSort('description')}>
                    Description
                    <Tooltip title="Details about the schema">
                      <InfoIcon fontSize="small" sx={{ ml: 0.5 }} />
                    </Tooltip>
                    <SortIcon fontSize="small" sx={{ ml: 0.5 }} />
                  </Box>
                </TableCell>
                <TableCell align="left" className="table-cell-header" sx={{ width: '20%' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }} onClick={() => handleSort('context_type')}>
                    Context Type
                    <SortIcon fontSize="small" sx={{ ml: 0.5 }} />
                  </Box>
                </TableCell>
                <TableCell align="left" className="table-cell-header" sx={{ width: '20%' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }} onClick={() => handleSort('user_identifier')}>
                    User Identifier
                    <Tooltip title="A unique identifier for the schema.">
                      <InfoIcon fontSize="small" sx={{ ml: 0.5 }} />
                    </Tooltip>
                    <SortIcon fontSize="small" sx={{ ml: 0.5 }} />
                  </Box>
                </TableCell>
                <TableCell align="right" className="table-cell-header" sx={{ width: '10%' }}>
                  Select
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedSchemas.map((schema) => (
                <TableRow
                  key={schema.schema_name}
                  className="table-row"
                  onClick={() => setSelected(schema)}
                  onMouseEnter={() => setHoveredRow(schema.schema_name)}
                  onMouseLeave={() => setHoveredRow(null)}
                  sx={{
                    backgroundColor:
                      selected?.schema_name === schema.schema_name
                        ? `${theme.palette.primary.main}15`
                        : hoveredRow === schema.schema_name
                        ? `${theme.palette.action.hover}`
                        : 'inherit',
                    '&:hover': {
                      backgroundColor:
                        selected?.schema_name === schema.schema_name
                          ? `${theme.palette.primary.main}25`
                          : theme.palette.action.hover,
                    },
                  }}
                >
                  <TableCell sx={{ py: 2 }}>{schema.schema_name}</TableCell>
                  <TableCell sx={{ py: 2 }}>{schema.description}</TableCell>
                  <TableCell sx={{ py: 2 }}>{schema.context_type}</TableCell>
                  <TableCell sx={{ py: 2 }}>{schema.user_identifier}</TableCell>
                  <TableCell align="right">
                    <Radio
                      sx={{ transform: 'scale(1.2)' }}
                      checked={selected?.schema_name === schema.schema_name}
                      onChange={() => setSelected(schema)}
                      inputProps={{ 'aria-label': `Select schema ${schema.schema_name}` }}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
          <Button variant="outlined" onClick={onClose} sx={{ minWidth: 100, backgroundColor: '#f0f0f0' }}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleSelect} disabled={!selected} sx={{ minWidth: 100 }}>
            Select
          </Button>
        </Box>
      </Box>
    </Modal>  );
};

export default SchemaSelectorModal;
