import React from 'react';
import {
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
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
  return (
    <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
      <TextField
        placeholder="Search..."
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
        size="small"
        sx={{ flexGrow: 1 }}
      />
      <FormControl size="small" sx={{ minWidth: 150 }}>
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
      <Button variant="contained" onClick={onSearch} size="small">
        Search
      </Button>
    </Stack>
  );
};

export default SearchSection;
