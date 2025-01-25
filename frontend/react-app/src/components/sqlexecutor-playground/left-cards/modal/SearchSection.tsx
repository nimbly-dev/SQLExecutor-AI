import React from 'react';
import {
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Tooltip,
} from '@mui/material';

interface SearchSectionProps {
  searchQuery: string;
  selectedField: string;
  allFields: string[];
  onSearchChange: (value: string) => void;
  onFieldChange: (value: string) => void;
  onSearch: () => void;
}

const SearchSection: React.FC<SearchSectionProps> = ({
  searchQuery,
  selectedField,
  allFields,
  onSearchChange,
  onFieldChange,
  onSearch,
}) => {
  const integrationType = sessionStorage.getItem('chatInterfaceIntegrationType');
  const isApiIntegration = integrationType === 'api';

  return (
    <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
      <Tooltip
        title={isApiIntegration ? "Search is not supported for API Context Integration" : ""}
        arrow
      >
        <TextField
          placeholder={isApiIntegration ? "Search not available for API integration" : "Search..."}
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          size="small"
          sx={{ flexGrow: 1 }}
          disabled={isApiIntegration}
        />
      </Tooltip>
      <FormControl size="small" sx={{ minWidth: 150 }} disabled={isApiIntegration}>
        <InputLabel id="search-field-label">Search Field</InputLabel>
        <Select
          labelId="search-field-label"
          value={selectedField}
          onChange={(e) => onFieldChange(e.target.value)}
          label="Search Field"
          displayEmpty
        >
          {allFields.map((field) => (
            <MenuItem key={field} value={field}>
              {field}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <Button
        variant="contained"
        onClick={onSearch}
        size="small"
        disabled={isApiIntegration}
      >
        Search
      </Button>
    </Stack>
  );
};

export default SearchSection;
