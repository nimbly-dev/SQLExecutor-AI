import React, { useState, useMemo } from 'react';
import { 
  Grid, Paper, Typography, IconButton, 
  TextField, Button, Box, Pagination,
  FormControl, Select, MenuItem, SelectChangeEvent,
  InputAdornment, Popover
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import { Ruleset } from 'types/ruleset/rulesetType';
import { useFormUpdate } from 'contexts/form/FormUpdateProvider';
import InterpolatedConditionsFormField from './InterpolatedConditionsFormField';
import ConditionOutlineHelpIcon from 'components/ruleset-manager/common/ConditionOutlineHelpIcon';

export interface RulesetConditionsProps {
  ruleset: Ruleset;
}

export const RulesetInterpolatedConditions: React.FC<RulesetConditionsProps> = ({ ruleset }) => {
  const { updateField } = useFormUpdate();
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);

  const conditionsState = useMemo(() => {
    const conditions = ruleset.conditions || {};
    return Object.entries(conditions).map(([key, value]) => ({
      key,
      value: { value } 
    }));
  }, [ruleset.conditions]);

  // Filter and paginate conditions
  const filteredAndPaginatedConditions = useMemo(() => {
    const filtered = conditionsState.filter(({ key, value }) => 
      key.toLowerCase().includes(searchTerm.toLowerCase()) ||
      value.value.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const total = filtered.length;
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    
    return {
      conditions: filtered.slice(startIndex, endIndex),
      total,
      totalPages: Math.ceil(total / pageSize)
    };
  }, [conditionsState, searchTerm, page, pageSize]);

  const handleUpdate = (key: string, value: string) => {
    updateField(`conditions.${key}`, value);
  };

  const handleRename = (oldKey: string, newKey: string, value: string) => {
    if (oldKey !== newKey) {
      updateField(`conditions.${oldKey}`, undefined); 
      updateField(`conditions.${newKey}`, value); 
    }
  };

  const handleRemove = (key: string) => {
    const updatedConditions = { ...ruleset.conditions };
    delete updatedConditions[key];
    updateField('conditions', updatedConditions);
    
    // Recalculate pagination
    const newTotal = filteredAndPaginatedConditions.total - 1;
    const newTotalPages = Math.ceil(newTotal / pageSize);
    if (page > newTotalPages && newTotalPages > 0) {
      setPage(newTotalPages);
    }
  };

  const handleAddCondition = () => {
    const newKey = `condition_${conditionsState.length + 1}`;
    updateField(`conditions.${newKey}`, '');
  };

  const handlePageChange = (_: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handlePageSizeChange = (event: SelectChangeEvent<number>) => {
    const newPageSize = Number(event.target.value);
    setPageSize(newPageSize);
    setPage(1); 
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Grid container spacing={2}>
            {/* Header with Add Button and Search */}
            <Grid item xs={12}>
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                alignItems: 'center',
                mb: 2 
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="h6">Interpolated Conditions</Typography>
                  <ConditionOutlineHelpIcon />
                </Box>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <TextField
                    size="small"
                    placeholder="Search conditions..."
                    value={searchTerm}
                    onChange={(e) => {
                      setSearchTerm(e.target.value);
                      setPage(1); 
                    }}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <SearchIcon />
                        </InputAdornment>
                      ),
                    }}
                  />
                  <Button
                    startIcon={<AddIcon />}
                    onClick={handleAddCondition}
                    variant="contained"
                  >
                    Add Condition
                  </Button>
                </Box>
              </Box>
            </Grid>
            

            {/* Conditions List */}
            {filteredAndPaginatedConditions.conditions.map(({ key, value }) => (
              <Grid item xs={12} key={key}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs>
                      <TextField
                        fullWidth
                        label="Condition Name"
                        value={key}
                        onChange={(e) => handleRename(key, e.target.value, value.value)}
                      />
                    </Grid>
                    <Grid item xs={12} sm={8}>
                      <InterpolatedConditionsFormField
                        value={value.value}
                        onChange={(newValue) => handleUpdate(key, newValue)}
                        onDelete={() => handleRemove(key)}
                      />
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
            ))}

            {/* Pagination Controls */}
            {filteredAndPaginatedConditions.total > 0 && (
              <Grid item xs={12}>
                <Box sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  mt: 2
                }}>
                  <FormControl size="small">
                    <Select
                      value={pageSize}
                      onChange={handlePageSizeChange}
                      sx={{ minWidth: 120 }}
                    >
                      {[5, 10, 25, 50].map((size) => (
                        <MenuItem key={size} value={size}>
                          {size} per page
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <Pagination
                    count={filteredAndPaginatedConditions.totalPages}
                    page={page}
                    onChange={handlePageChange}
                    color="primary"
                    size="small"
                  />
                </Box>
              </Grid>
            )}
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default RulesetInterpolatedConditions;
