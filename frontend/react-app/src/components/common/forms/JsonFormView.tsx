import React, { useState, useEffect } from 'react';
import { Box, Paper } from '@mui/material';
import MonacoEditor from '@monaco-editor/react';

export interface JsonFormViewProps<T extends Record<string, any>> {
  data: T;
  onChange: (newData: T) => void;
  height?: string | number;
  readOnly?: boolean;
}

export function JsonFormView<T extends Record<string, any>>({ 
  data, 
  onChange, 
  height = '400px',
  readOnly = false 
}: JsonFormViewProps<T>): React.ReactElement {
  const [localValue, setLocalValue] = useState<string>('');
  const [hasError, setHasError] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  // Only sync external data when not actively editing
  useEffect(() => {
    if (!isEditing) {
      try {
        const formattedJson = JSON.stringify(data, null, 2);
        const currentParsed = JSON.parse(localValue || '{}');
        const newParsed = JSON.parse(formattedJson);
        
        if (JSON.stringify(currentParsed) !== JSON.stringify(newParsed)) {
          setLocalValue(formattedJson);
          setHasError(false);
        }
      } catch (error) {
        console.error('Error formatting JSON:', error);
        setHasError(true);
      }
    }
  }, [data, isEditing, localValue]);

  const handleEditorChange = (value: string | undefined) => {
    if (!value) return;
    
    setLocalValue(value);
    setIsEditing(true);

    try {
      const parsedValue = JSON.parse(value) as T;
      setHasError(false);
      onChange(parsedValue);
    } catch (error) {
      setHasError(true);
    }

    // Reset editing state after a short delay
    setTimeout(() => setIsEditing(false), 100);
  };

  return (
    <Paper 
      elevation={0} 
      sx={{ 
        border: 1,
        borderColor: hasError ? 'error.main' : 'divider',
        borderRadius: 1,
        overflow: 'hidden'
      }}
    >
      <Box sx={{ height }}>
        <MonacoEditor
          language="json"
          theme="vs-light"
          value={localValue}
          onChange={handleEditorChange}
          options={{
            minimap: { enabled: false },
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            readOnly,
            formatOnPaste: true,
            formatOnType: true,
          }}
        />
      </Box>
    </Paper>
  );
}

export default JsonFormView;
