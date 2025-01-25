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
import { SchemaSummary } from '../../../../types/sqlexecutor-playground/schemaModalContent';

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

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!open) return;

      const currentIndex = schemas.findIndex(
        (schema) => schema.schema_name === selected?.schema_name
      );

      switch (event.key) {
        case 'ArrowUp':
          event.preventDefault();
          if (currentIndex > 0) {
            setSelected(schemas[currentIndex - 1]);
          }
          break;
        case 'ArrowDown':
          event.preventDefault();
          if (currentIndex < schemas.length - 1) {
            setSelected(schemas[currentIndex + 1]);
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
  }, [open, selected, schemas]);

  const handleSelect = () => {
    if (selected) {
      onSelectSchema(selected);
    }
    onClose();
  };

  return (
    <Modal 
      open={open} 
      onClose={onClose}
      aria-labelledby="schema-selector-modal"
    >
      <Box sx={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: 600,
        bgcolor: 'background.paper',
        borderRadius: 2,
        boxShadow: 24,
        p: 4,
      }}>
        <Typography 
          variant="h6" 
          id="schema-selector-modal"
          sx={{ 
            mb: 3,
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}
        >
          Select Schema
          <Tooltip title="Choose a schema to generate SQL queries for specific database tables">
            <InfoIcon sx={{ fontSize: 20, color: 'action.active', ml: 1 }} />
          </Tooltip>
        </Typography>

        <TableContainer 
          component={Paper} 
          sx={{ 
            maxHeight: 400,
            mb: 3,
            '& .MuiTableCell-head': {
              fontWeight: 600,
              backgroundColor: theme.palette.background.default,
            }
          }}
        >
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell align="left" sx={{ width: '30%' }}>Schema</TableCell>
                <TableCell align="left" sx={{ width: '60%' }}>Description</TableCell>
                <TableCell align="right" sx={{ width: '10%' }}>Select</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {schemas.map((schema) => (
                <TableRow
                  key={schema.schema_name}
                  onClick={() => setSelected(schema)}
                  onMouseEnter={() => setHoveredRow(schema.schema_name)}
                  onMouseLeave={() => setHoveredRow(null)}
                  sx={{
                    cursor: 'pointer',
                    backgroundColor: selected?.schema_name === schema.schema_name
                      ? `${theme.palette.primary.main}15`
                      : hoveredRow === schema.schema_name
                      ? `${theme.palette.action.hover}`
                      : 'inherit',
                    '&:hover': {
                      backgroundColor: selected?.schema_name === schema.schema_name
                        ? `${theme.palette.primary.main}25`
                        : theme.palette.action.hover,
                    },
                    transition: 'background-color 0.2s ease',
                  }}
                >
                  <TableCell sx={{ py: 2 }}>{schema.schema_name}</TableCell>
                  <TableCell>{schema.description}</TableCell>
                  <TableCell align="right">
                    <Radio
                      checked={selected?.schema_name === schema.schema_name}
                      onChange={() => setSelected(schema)}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'flex-end',
          gap: 2 
        }}>
          <Button
            variant="outlined"
            onClick={onClose}
            sx={{ minWidth: 100 }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSelect}
            disabled={!selected}
            sx={{ minWidth: 100 }}
          >
            Select
          </Button>
        </Box>
      </Box>
    </Modal>
  );
};

export default SchemaSelectorModal;
