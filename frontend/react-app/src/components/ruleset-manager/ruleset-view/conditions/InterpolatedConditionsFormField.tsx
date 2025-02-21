import React, { useState, useEffect, useCallback } from 'react';
import { TextField, Box, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';

interface InterpolatedConditionsFormFieldProps {
  value: string;
  onChange: (value: string) => void;
  onDelete?: () => void;
  label?: string;
  placeholder?: string;
}

export const InterpolatedConditionsFormField: React.FC<InterpolatedConditionsFormFieldProps> = ({
  value,
  onChange,
  onDelete,
  label = 'Condition Expression',
  placeholder = 'Enter condition expression...'
}) => {
  const [localValue, setLocalValue] = useState(value);

  // Sync with parent value
  useEffect(() => {
    if (value !== localValue) {
      setLocalValue(value);
    }
  }, [value]);

  // Handle blur with memoized callback
  const handleBlur = useCallback(() => {
    if (localValue !== value) {
      onChange(localValue);
    }
  }, [localValue, value, onChange]);

  return (
    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
      <TextField
        fullWidth
        multiline
        rows={2}
        label={label}
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        onBlur={handleBlur}
        placeholder={placeholder}
        InputProps={{
          sx: {
            fontFamily: 'monospace'
          }
        }}
      />
      {onDelete && (
        <IconButton 
          onClick={onDelete}
          color="error"
          size="small"
        >
          <DeleteIcon />
        </IconButton>
      )}
    </Box>
  );
};

export default InterpolatedConditionsFormField;
