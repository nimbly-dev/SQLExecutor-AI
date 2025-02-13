// SchemaJsonTablesView.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { Box, TextareaAutosize, Button, Typography } from '@mui/material';

interface SchemaJsonTablesViewProps {
  tables: Record<string, any>; // Accept object format for JSON view
  updateField: (path: string, value: any) => void;
}

const SchemaJsonTables: React.FC<SchemaJsonTablesViewProps> = React.memo(({ tables, updateField }) => {
  const [jsonValue, setJsonValue] = useState<string>(JSON.stringify(tables, null, 2));
  useEffect(() => {
    setJsonValue(JSON.stringify(tables, null, 2));
  }, [tables]);
  const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setJsonValue(newValue);
    try {
      const parsed = JSON.parse(newValue);
      updateField('tables', parsed);
    } catch (err) {}
  }, [updateField]);
  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2 }}>
        JSON Schema Editor
      </Typography>
      <TextareaAutosize
        minRows={15}
        style={{ width: '100%', border: '1px solid #ddd', padding: 8, borderRadius: 4 }}
        value={jsonValue}
        onChange={handleChange}
      />
      <Box sx={{ mt: 2 }}>
        <Button variant="contained" size="small" color="success">
          Save Changes
        </Button>
      </Box>
    </Box>
  );
});

export default SchemaJsonTables;
