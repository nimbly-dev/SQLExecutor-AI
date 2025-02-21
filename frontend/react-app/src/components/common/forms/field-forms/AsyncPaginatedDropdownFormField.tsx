import React, { useEffect, useMemo, useCallback } from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Box,
  CircularProgress,
  Typography,
  Pagination,
  SelectChangeEvent,
} from '@mui/material';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import { createDebouncedUpdate } from 'utils/forms/formUtils';

export interface AsyncPaginatedDropdownOption {
  value: string;
  label: string;
}

interface LocalState {
  searchTerm: string;
  page: number;
  pageSize: number;
}

interface AsyncPaginatedDropdownFormFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  onSearch: (
    searchTerm: string,
    page: number,
    pageSize: number
  ) => Promise<{ options: AsyncPaginatedDropdownOption[]; total: number }>;
  loading?: boolean;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  defaultPageSize?: number;
  pageSizeOptions?: number[];
  placeholder?: string;
  customOpen?: () => void;
  customClose?: () => void;
  onError?: (error: string) => void;
  renderValue?: () => React.ReactNode;
}

export default function AsyncPaginatedDropdownFormField({
  label,
  value,
  onChange,
  onSearch,
  loading: externalLoading,
  error: externalError,
  disabled = false,
  required = false,
  defaultPageSize = 10,
  pageSizeOptions = [5, 10, 25, 50],
  placeholder = 'Search...',
  customOpen,
  customClose,
  onError,
  renderValue,
}: AsyncPaginatedDropdownFormFieldProps) {
  const [localState, setField] = useLocalFormState<LocalState>({
    searchTerm: '',
    page: 1,
    pageSize: defaultPageSize,
  });

  const [options, setOptions] = React.useState<AsyncPaginatedDropdownOption[]>([]);
  const [total, setTotal] = React.useState(0);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [isOpen, setIsOpen] = React.useState(false);

  const debouncedFetch = React.useMemo(() => createDebouncedUpdate(300), []);

  const fetchOptions = useCallback(
    async (search: string, currentPage: number, currentPageSize: number) => {
      try {
        setLoading(true);
        const result = await onSearch(search, currentPage, currentPageSize);
        let fetchedOptions = result.options;
        // Ensure current value is always present
        if (value && !result.options.some(opt => opt.value === value)) {
          fetchedOptions = [
            { value, label: renderValue ? renderValue() as string : value },
            ...result.options,
          ];
        }
        setOptions(fetchedOptions);
        setTotal(result.total);
        setError(null);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Failed to fetch options';
        setError(errorMessage);
        onError?.(errorMessage);
      } finally {
        setLoading(false);
      }
    },
    [value, renderValue, onSearch, onError]
  );

  // Fetch initial options if a value is provided
  useEffect(() => {
    if (value) {
      fetchOptions('', 1, defaultPageSize);
    }
  }, [value, defaultPageSize, fetchOptions]);

  useEffect(() => {
    if (isOpen) {
      fetchOptions(localState.searchTerm, localState.page, localState.pageSize);
    }
  }, [localState.searchTerm, localState.page, localState.pageSize, isOpen, fetchOptions]);

  const handleOpen = () => {
    customOpen?.();
    setIsOpen(true);
  };

  const handleClose = () => {
    customClose?.();
    setIsOpen(false);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setField('searchTerm', event.target.value);
    setField('page', 1); // Reset to first page on new search
  };

  const handlePageChange = (_: React.ChangeEvent<unknown>, newPage: number) => {
    setField('page', newPage);
  };

  const handlePageSizeChange = (event: SelectChangeEvent<number>) => {
    setField('pageSize', Number(event.target.value));
    setField('page', 1);
  };

  const handleChange = (event: SelectChangeEvent<string>) => {
    const newValue = event.target.value;
    onChange(newValue);
    handleClose();
  };
  
  const mergedOptions = useMemo(() => {
    if (value && !options.some(opt => opt.value === value)) {
      return [{ value, label: renderValue ? renderValue() as string : value }, ...options];
    }
    return options;
  }, [value, options, renderValue]);

  return (
    <FormControl fullWidth disabled={disabled}>
      <InputLabel required={required}>{label}</InputLabel>
      <Select
        value={value || ''}
        onChange={handleChange}
        onOpen={handleOpen}
        onClose={handleClose}
        open={isOpen}
        label={label}
        renderValue={renderValue}
        MenuProps={{
          PaperProps: { sx: { zIndex: 1400 } }, // increased to be above modal (modal z-index = 1300)
        }}
      >
        {/* Render search input at the top when open */}
        {isOpen && (
          <Box
            sx={{
              p: 2,
              position: 'sticky',
              top: 0,
              bgcolor: 'background.paper',
              zIndex: 1,
            }}
          >
            <TextField
              fullWidth
              value={localState.searchTerm}
              onChange={handleSearchChange}
              placeholder={placeholder}
              size="small"
              onClick={(e) => e.stopPropagation()}
            />
          </Box>
        )}

        {/* Render available options */}
        {mergedOptions.map((option) => (
          <MenuItem key={option.value} value={option.value}>
            {option.label}
          </MenuItem>
        ))}

        {/* Render loading or error state if present */}
        {loading || externalLoading ? (
          <MenuItem disabled>
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2, width: '100%' }}>
              <CircularProgress size={24} />
            </Box>
          </MenuItem>
        ) : error || externalError ? (
          <MenuItem disabled>
            <Typography color="error" sx={{ p: 2 }}>
              {error || externalError}
            </Typography>
          </MenuItem>
        ) : null}

        {/* Render pagination controls in a non-disabled container */}
        {!loading && !externalLoading && !error && !externalError && mergedOptions.length > 0 && (
          <Box
            component="li"
            sx={{
              listStyle: 'none',
              width: '100%',
              position: 'sticky',
              bottom: 0,
              bgcolor: 'background.paper',
              p: 2,
              borderTop: 1,
              borderColor: 'divider',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <Select
              size="small"
              value={localState.pageSize}
              onChange={handlePageSizeChange}
            >
              {pageSizeOptions.map((size) => (
                <MenuItem key={size} value={size}>
                  {size} per page
                </MenuItem>
              ))}
            </Select>
            <Pagination
              count={Math.ceil(total / localState.pageSize)}
              page={localState.page}
              onChange={handlePageChange}
              size="small"
            />
          </Box>
        )}
      </Select>
    </FormControl>
  );
}
