// DynamicSelectFormField.tsx
import React, { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import {
  TextField,
  Popover,
  List,
  ListItemButton,
  ListItemText,
  CircularProgress,
  Box,
  FormHelperText,
  TextFieldProps,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';

export interface DynamicSelectOption {
  value: string;
  label?: string;
  disabled?: boolean;
}

export type OptionsLoader = () => Promise<DynamicSelectOption[]> | DynamicSelectOption[];

type OmittedTextFieldProps = Omit<TextFieldProps, 'onChange' | 'value' | 'label'>;

export interface DynamicSelectFieldFormProps {
  value: string;
  label: string;
  options?: DynamicSelectOption[];
  optionsLoader?: OptionsLoader;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  loading?: boolean;
  error?: string;
  TextFieldProps?: OmittedTextFieldProps;
  /** Number of options visible before scrolling (default: 5) */
  defaultPageSize?: number;
}

const ITEM_HEIGHT = 48;

/**
 * A dynamic select form field component that supports both static and dynamically loaded options.
 * 
 * @component
 * @param {Object} props - Component props
 * @param {string} props.value - Current value of the select field
 * @param {string} props.label - Label text for the field
 * @param {DynamicSelectOption[]} [props.options=[]] - Static options array
 * @param {() => Promise<DynamicSelectOption[]>} [props.optionsLoader] - Async function to load options dynamically
 * @param {(value: string) => void} props.onChange - Callback when value changes
 * @param {string} [props.placeholder='Select an option'] - Placeholder text when no value is selected
 * @param {boolean} [props.disabled=false] - Whether the field is disabled
 * @param {boolean} [props.loading=false] - External loading state
 * @param {string} [props.error] - Error message to display
 * @param {Object} [props.TextFieldProps={}] - Props to pass to the underlying TextField component
 * @param {number} [props.defaultPageSize=5] - Number of items to show in dropdown before scrolling
 * 
 * @typedef {Object} DynamicSelectOption
 * @property {string} value - Option value
 * @property {string} [label] - Option display label
 * @property {boolean} [disabled] - Whether the option is disabled
 * 
 * @returns {React.ReactElement} Rendered form field component
 */
const DynamicSelectFormField: React.FC<DynamicSelectFieldFormProps> = ({
  value,
  label,
  options: staticOptions = [],
  optionsLoader,
  onChange,
  placeholder = 'Select an option',
  disabled = false,
  loading: externalLoading = false,
  error,
  TextFieldProps = {},
  defaultPageSize = 5,
}) => {
  const theme = useTheme();
  const [options, setOptions] = useState<DynamicSelectOption[]>(staticOptions);
  const [loading, setLoading] = useState(false);
  const [internalError, setInternalError] = useState('');
  const [inputValue, setInputValue] = useState(value);
  const [open, setOpen] = useState(false);
  const anchorRef = useRef<HTMLDivElement | null>(null);

  const loadOptions = useCallback(async () => {
    if (!optionsLoader) return;
    try {
      setLoading(true);
      const loaded = await optionsLoader();
      setOptions(loaded);
      setInternalError('');
    } catch (err) {
      setInternalError('Failed to load options');
      console.error('Error loading options:', err);
    } finally {
      setLoading(false);
    }
  }, [optionsLoader]);

  useEffect(() => {
    if (optionsLoader) loadOptions();
  }, [loadOptions, optionsLoader]);

  useEffect(() => {
    setOptions(staticOptions);
  }, [staticOptions]);

  useEffect(() => {
    setInputValue(value);
  }, [value]);

  const filteredOptions = useMemo(() => {
    return options.filter((opt) =>
      (opt.label || opt.value).toLowerCase().includes(inputValue.toLowerCase())
    );
  }, [options, inputValue]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
    if (!open) setOpen(true);
  };

  const handleOptionSelect = (option: DynamicSelectOption) => {
    if (option.disabled) return;
    setInputValue(option.label || option.value);
    onChange(option.value);
    setOpen(false);
  };

  const isLoading = loading || externalLoading;
  const displayError = error || internalError;

  return (
    <div ref={anchorRef}>
      <TextField
        label={label}
        value={inputValue}
        onChange={handleInputChange}
        placeholder={placeholder}
        disabled={disabled || isLoading}
        onFocus={() => setOpen(true)}
        fullWidth
        {...TextFieldProps}
      />
      {displayError && <FormHelperText error>{displayError}</FormHelperText>}
      <Popover
        open={open}
        anchorEl={anchorRef.current}
        onClose={() => setOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
        disableAutoFocus
        disableEnforceFocus
        disableRestoreFocus
      >
        <Box
          sx={{
            width: anchorRef.current ? anchorRef.current.clientWidth : 200,
            maxHeight: defaultPageSize * ITEM_HEIGHT,
            overflowY: 'auto',
          }}
        >
          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
              <CircularProgress size={20} />
            </Box>
          ) : filteredOptions.length > 0 ? (
            <List>
              {filteredOptions.map((option) => (
                <ListItemButton
                  key={option.value}
                  onClick={() => handleOptionSelect(option)}
                  disabled={option.disabled}
                >
                  <ListItemText primary={option.label || option.value} />
                </ListItemButton>
              ))}
            </List>
          ) : (
            <Box sx={{ p: 2 }}>
              <ListItemText primary="No options" />
            </Box>
          )}
        </Box>
      </Popover>
    </div>
  );
};

export default React.memo(DynamicSelectFormField);
