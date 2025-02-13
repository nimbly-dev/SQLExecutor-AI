import React, { useCallback, useEffect, useState, SyntheticEvent, useMemo } from 'react';
import { 
  Autocomplete,
  AutocompleteProps,
  TextField,
  TextFieldProps,
} from '@mui/material';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';

// Type for the autocomplete options handler
export type AutocompleteHandler<T> = () => {
  options: T[];
  getOptionLabel?: (option: T) => string;
  isOptionEqualToValue?: (option: T, value: T) => boolean;
  groupBy?: (option: T) => string;
  filterOptions?: (options: T[], { inputValue }: { inputValue: string }) => T[];
};

// Update BaseAutocompleteProps to use freeSolo as boolean and omit it
type BaseAutocompleteProps<T> = Omit<
  AutocompleteProps<T, false, false, boolean>,
  'renderInput' | 'options' | 'onChange' | 'freeSolo'
>;

// Update interface: allow local state to hold T | string | null
interface LocalStateType<T> {
  value: T | string | null;
}

interface DynamicAutocompleteFormFieldProps<T> extends BaseAutocompleteProps<T> {
  value: T | null;
  onChange: (value: T | string | null) => void; // updated to accept string as well
  optionsHandler: AutocompleteHandler<T>;
  label?: string;
  placeholder?: string;
  helperText?: string;
  required?: boolean;
  error?: boolean;
  updateInterval?: number;
  TextFieldProps?: Partial<TextFieldProps>;
  maxOptionsBeforeSearch?: number; // Number of options before showing search
  freeSolo?: boolean; // allow freeSolo prop
}

/**
 * A form field component that wraps MUI's Autocomplete with dynamic options handling.
 * 
 * @example
 * ```tsx
 * <DynamicAutocompleteFormField
 *   value={selectedValue}
 *   onChange={handleChange}
 *   optionsHandler={() => ({
 *     options: availableOptions,
 *     getOptionLabel: (option) => option.label,
 *     isOptionEqualToValue: (option, value) => option.id === value.id,
 *     groupBy: (option) => option.category,
 *   })}
 *   label="Select Option"
 *   placeholder="Choose an option..."
 * />
 * ```
 */
function DynamicAutocompleteFormField<T>({
  value,
  onChange,
  optionsHandler,
  label,
  placeholder,
  helperText,
  required = false,
  error = false,
  updateInterval,
  TextFieldProps = {},
  maxOptionsBeforeSearch = 8,
  freeSolo = false,
  ...autocompleteProps
}: DynamicAutocompleteFormFieldProps<T>) {
  const [inputValue, setInputValue] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [localState, setField] = useLocalFormState<LocalStateType<T>>({ value });

  // Helper to compute config and cast to correct Autocomplete props
  const computeHandlerConfig = useCallback(() => {
    const config = optionsHandler();
    return {
      ...config,
      options: config.options ?? [], // ensure options is always defined
      isOptionEqualToValue: (option: T, val: T): boolean => {
        return config.isOptionEqualToValue?.(option, val) ?? option === val;
      },
    } as Partial<AutocompleteProps<T, false, false, boolean>>;
  }, [optionsHandler]);

  const [handlerConfig, setHandlerConfig] = useState(() => computeHandlerConfig());

  // Update handler config when dependencies change
  useEffect(() => {
    setHandlerConfig(computeHandlerConfig());
  }, [computeHandlerConfig]);

  // Update options at an interval if specified
  useEffect(() => {
    if (!updateInterval) return undefined;
    const intervalId = setInterval(() => {
      setHandlerConfig(computeHandlerConfig());
    }, updateInterval);
    return () => clearInterval(intervalId);
  }, [updateInterval, computeHandlerConfig]);

  // Explicitly annotate the callback so newValue is type string | T | null
  const handleChange: (
    event: SyntheticEvent<Element, Event>,
    newValue: string | T | null,
  ) => void = useCallback(
    (event, newValue) => {
      // Do not cast newValue to T; forward union type onChange
      setField('value', newValue);
      onChange(newValue);
    },
    [onChange, setField]
  );

  // Filter options regardless of template mode
  const getFilteredOptions = useCallback((options: readonly T[]) => {
    if (!handlerConfig.filterOptions) {
      return [...options].filter(opt => 
        String(handlerConfig.getOptionLabel?.(opt) || opt)
          .toLowerCase()
          .includes(inputValue.toLowerCase())
      );
    }
    return handlerConfig.filterOptions([...options], { 
      inputValue,
      getOptionLabel: handlerConfig.getOptionLabel || String
    });
  }, [handlerConfig, inputValue]);

  return (
    <Autocomplete<T, false, false, boolean> 
      freeSolo={freeSolo}
      value={localState.value}
      onChange={handleChange}
      inputValue={inputValue}
      onInputChange={(event, newInputValue) => {
        setInputValue(newInputValue);
      }}
      {...handlerConfig}
      {...autocompleteProps}
      options={getFilteredOptions(handlerConfig.options || [])}
      filterOptions={(x) => x} // Let our custom filtering handle it
      handleHomeEndKeys
      open={isOpen}
      onOpen={() => setIsOpen(true)}
      onClose={() => setIsOpen(false)}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          placeholder={placeholder}
          helperText={helperText}
          required={required}
          error={error}
          {...TextFieldProps}
          value={localState.value || ''} // Ensure empty string as fallback
        />
      )}
    />
  );
}

export default DynamicAutocompleteFormField;
