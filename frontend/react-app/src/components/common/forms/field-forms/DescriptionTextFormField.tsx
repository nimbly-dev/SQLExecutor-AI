import React, { useCallback } from 'react';
import { TextField } from '@mui/material';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';

interface DescriptionTextFormFieldProps {
  description: string;
  onChange: (value: string) => void;
  onValidationError?: (message: string) => void;
  label?: string;
  minRows?: number;
  maxRows?: number;
  validate?: (value: string) => { type: string; message: string };
  placeholder?: string;
  required?: boolean;  // Add optional required prop
}

interface LocalStateType {
  description: string;
}

export default function DescriptionTextFormField({
  description,
  onChange,
  onValidationError,
  label = 'Description',
  minRows = 2,
  maxRows = 4,
  validate,
  placeholder,
  required = false,  // Add default value
}: DescriptionTextFormFieldProps) {
  const [localState, setField] = useLocalFormState<LocalStateType>({
    description: description || '',
  });

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setField('description', e.target.value);
  }, [setField]);

  const handleBlur = useCallback(() => {
    const value = localState.description;
    if (validate) {
      const validationResult = validate(value);
      if (validationResult.type === 'error') {
        onValidationError?.(validationResult.message);
        return;
      }
    }
    onChange(value);
  }, [localState.description, onChange, validate, onValidationError]);

  const validationResult = validate ? validate(localState.description) : null;
  const hasError = validationResult?.type === 'error';

  return (
    <TextField
      label={label}
      value={localState.description}
      onChange={handleChange}
      onBlur={handleBlur}
      placeholder={placeholder}
      required={required}  // Add required prop
      fullWidth
      multiline
      minRows={minRows}
      maxRows={maxRows}
      variant="outlined"
      size="small"
      error={hasError}
      helperText={hasError ? validationResult.message : ''}
    />
  );
}
