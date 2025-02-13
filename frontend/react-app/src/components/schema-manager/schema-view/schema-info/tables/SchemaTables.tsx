import React, { useState, memo } from 'react';
import { Box, Button } from '@mui/material';
import SchemaFormTables from 'components/schema-manager/schema-view/schema-info/tables/tables-forms/SchemaFormTables';
import SchemaJsonTables from 'components/schema-manager/schema-view/schema-info/tables/tables-forms/SchemaJsonTables';
import { Table } from 'types/schema/schemaType';
import { useFormUpdate } from 'contexts/form/FormUpdateProvider'; 
import styles from 'styles/schema-manager/tables/SchemaTablesView.module.scss';

interface SchemaTablesViewProps {
  tables: Record<string, Table>;
}

const SchemaTablesView: React.FC<SchemaTablesViewProps> = memo(({ tables = {} }) => {
  const [viewMode, setViewMode] = useState<'form' | 'json'>('form');
  const { updateField } = useFormUpdate();

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 2, p: 2 }}>
      <Box sx={{ display: 'flex', gap: 1, borderBottom: '1px solid', borderColor: 'divider', pb: 1 }}>
        <Button 
          variant={viewMode === 'form' ? 'contained' : 'outlined'} 
          onClick={() => setViewMode('form')}
          size="small"
        >
          SCHEMA VIEW
        </Button>
        <Button 
          variant={viewMode === 'json' ? 'contained' : 'outlined'} 
          onClick={() => setViewMode('json')}
          size="small"
        >
          JSON VIEW
        </Button>
      </Box>
      
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        {viewMode === 'form' ? (
          <SchemaFormTables 
            tables={tables}
            updateField={updateField} // Pass updateField directly
          />
        ) : (
          <SchemaJsonTables 
            tables={tables}
            updateField={updateField}
          />
        )}
      </Box>
    </Box>
  );
});

SchemaTablesView.displayName = 'SchemaTablesView';
export default SchemaTablesView;
